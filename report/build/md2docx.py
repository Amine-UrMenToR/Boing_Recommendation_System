"""Build the Word version of the report from the Markdown source.

    py md2docx.py SRC.md OUT.docx --title "Final Report" --date "November 24, 2026"
        [--students "Students: Amine Houari and [[Teammate’s full name]]  ·  Group 14"]
        [--template ../../Repport.docx] [--doc-title "..."]

Starts from the owner's Repport.docx (read only): keeps its cover page (McGill logo, course name, FINAL
PROJECT, professor) and its header with the frog, replaces the title, students and date lines, then renders
the Markdown body in the same look as the interim draft: Calibri, green underlined section headings,
11 pt justified body, 9 pt tables (8 pt with <!-- small -->), yellow placeholders, centred page numbers
from page 2, references with a hanging indent, and a light box for a section marked <!-- box -->.
"""
import argparse
import sys
from pathlib import Path

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mdreport as md  # noqa: E402

HERE = Path(__file__).resolve().parent
DEFAULT_TEMPLATE = HERE.parent.parent / 'Repport.docx'
PROTECTED = {'repport.docx', 'interim report - draft.docx'}
DEFAULT_STUDENTS = 'Students: Amine Houari and [[Teammate’s full name]]  ·  Group 14'

GREEN = RGBColor(0x00, 0xB0, 0x50)
BODY_PT, BOX_PT, REF_PT, TABLE_PT, SMALL_PT, CAPTION_PT = 11, 10, 10, 9, 8, 9.5
TEXT_WIDTH_IN = 6.5
MAX_FIG_HEIGHT_IN = 8.0
BOX_FILL, BOX_LINE, BOX_PAD_IN = 'F2F8EE', 'A9D18E', 0.1
ALIGN = {'l': WD_ALIGN_PARAGRAPH.LEFT, 'c': WD_ALIGN_PARAGRAPH.CENTER, 'r': WD_ALIGN_PARAGRAPH.RIGHT}
# order of the children of w:tcPr in the WordprocessingML schema
TCPR_ORDER = ['tcW', 'gridSpan', 'hMerge', 'vMerge', 'tcBorders', 'shd', 'noWrap', 'tcMar', 'textDirection',
              'tcFitText', 'vAlign', 'hideMark']


def tcpr_insert(cell, el):
    """Insert a child into the cell's tcPr at its schema position (replacing one of the same kind)."""
    tcPr = cell._tc.get_or_add_tcPr()
    name = el.tag.split('}')[1]
    old = tcPr.find(qn('w:' + name))
    if old is not None:
        tcPr.remove(old)
    later = TCPR_ORDER[TCPR_ORDER.index(name) + 1:]
    for child in tcPr:
        if child.tag.split('}')[1] in later:
            child.addprevious(el)
            return el
    tcPr.append(el)
    return el


class Builder:
    def __init__(self, template):
        self.d = docx.Document(str(template))
        self.page_break_pending = False
        self.box_cell = None              # the cell of the open box, if any
        self.box_first = None             # the empty first paragraph of that cell

    # ------------------------------------------------------------------ cover
    def cover(self, title, date, students):
        paras = self.d.paragraphs
        try:
            t = next(p for p in paras if p.text.strip() == 'Report')
            stud = next(p for p in paras if p.text.startswith('Students:'))
            year = next(p for p in paras if p.text.strip() == '2026 - 2027')
            intro = next(p for p in paras if p.text.strip().startswith('INTRODUCTION'))
        except StopIteration:
            sys.exit('md2docx: the template does not look like Repport.docx (cover lines not found)')
        t.runs[0].text = title
        for r in t.runs[1:]:
            r.text = ''
        size = stud.runs[0].font.size or Pt(14)
        for r in stud.runs[1:]:
            r.text = ''
        stud.runs[0].text = ''
        for run in md.inline(students):
            r = stud.add_run(run.text)
            r.font.size = size
            r.bold = run.bold or None
            r.italic = run.italic or None
            if run.hl:
                r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        year.runs[0].text = date
        for r in year.runs[1:]:
            r.text = ''
        # remove the template's old body (everything after the cover)
        body = self.d.element.body
        started = False
        for el in list(body):
            if el is intro._p:
                started = True
            if started and el.tag != qn('w:sectPr'):
                body.remove(el)
        self.page_break_pending = True          # the report starts on page 2

    # ------------------------------------------------------------------ containers
    def width_in(self):
        return TEXT_WIDTH_IN - 2 * BOX_PAD_IN - 0.05 if self.box_cell is not None else TEXT_WIDTH_IN

    def _add_par(self):
        if self.box_cell is not None:
            if self.box_first is not None:
                p, self.box_first = self.box_first, None
                return p
            return self.box_cell.add_paragraph()
        return self.d.add_paragraph()

    def _add_table(self, rows, cols):
        if self.box_cell is not None:
            self.box_first = None
            return self.box_cell.add_table(rows, cols)
        return self.d.add_table(rows=rows, cols=cols)

    def open_box(self):
        tb = self.d.add_table(rows=1, cols=1)
        tb.alignment = WD_TABLE_ALIGNMENT.CENTER
        tb.autofit = False
        tb.columns[0].width = Inches(TEXT_WIDTH_IN)
        cell = tb.cell(0, 0)
        cell.width = Inches(TEXT_WIDTH_IN)
        self.cell_border(cell, **{e: (6, BOX_LINE) for e in ('top', 'left', 'bottom', 'right')})
        self.shade(cell, BOX_FILL)
        mar = OxmlElement('w:tcMar')
        for side in ('top', 'left', 'bottom', 'right'):
            e = OxmlElement(f'w:{side}')
            e.set(qn('w:w'), str(int(BOX_PAD_IN * 1440 * (0.8 if side in ('top', 'bottom') else 1))))
            e.set(qn('w:type'), 'dxa')
            mar.append(e)
        tcpr_insert(cell, mar)
        if self.page_break_pending:              # a page break before the box goes on a paragraph above it
            self.spacer(before_table=True)
        self.box_cell = cell
        self.box_first = cell.paragraphs[0]

    def close_box(self):
        if self.box_first is not None:           # an empty box: give its paragraph a size
            self.box_first.paragraph_format.space_after = Pt(0)
        self.box_cell = None
        self.box_first = None
        self.spacer()

    def spacer(self, before_table=False):
        p = self.d.add_paragraph()
        pf = p.paragraph_format
        pf.space_before, pf.space_after = Pt(0), Pt(0 if before_table else 4)
        pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        pf.line_spacing = Pt(2)
        if before_table and self.page_break_pending:
            # move the spacer in front of the box table and let it carry the page break
            pf.page_break_before = True
            self.page_break_pending = False
            tbl = self.d.element.body.findall(qn('w:tbl'))[-1]
            tbl.addprevious(p._p)

    # ------------------------------------------------------------------ paragraph helpers
    def new_par(self, after=5, before=0, line=1.0, align=WD_ALIGN_PARAGRAPH.JUSTIFY, keep=False):
        p = self._add_par()
        pf = p.paragraph_format
        pf.space_after, pf.space_before, pf.line_spacing = Pt(after), Pt(before), line
        pf.keep_with_next = keep or None
        p.alignment = align
        if self.page_break_pending and self.box_cell is None:
            pf.page_break_before = True
            self.page_break_pending = False
        return p

    @staticmethod
    def add_runs(p, text, size=BODY_PT, base_bold=False, base_italic=False):
        for run in md.inline(text, base_bold=base_bold, base_italic=base_italic):
            if run.br:
                if p.runs:
                    p.runs[-1].add_break()
                else:
                    p.add_run().add_break()
                continue
            r = p.add_run(run.text)
            r.font.size = Pt(size)
            r.bold = run.bold or None
            r.italic = run.italic or None
            if run.hl:
                r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        return p

    @staticmethod
    def outline(p, level):
        ppr = p._p.get_or_add_pPr()
        o = OxmlElement('w:outlineLvl')
        o.set(qn('w:val'), str(level))
        ppr.append(o)

    # ------------------------------------------------------------------ blocks
    def heading(self, h):
        if h.page_break:
            self.page_break_pending = True
        first_in_box = self.box_cell is not None and self.box_first is not None
        if h.level == 1:
            p = self.new_par(before=0 if first_in_box else 10, after=4, align=WD_ALIGN_PARAGRAPH.LEFT, keep=True)
            self.add_runs(p, h.text, size=14, base_bold=True)
            for r in p.runs:
                r.underline = True
                r.font.color.rgb = GREEN
        elif h.level == 2:
            p = self.new_par(before=0 if first_in_box else 8, after=3, align=WD_ALIGN_PARAGRAPH.LEFT, keep=True)
            self.add_runs(p, h.text, size=11.5, base_bold=True)
        else:
            p = self.new_par(before=0 if first_in_box else 6, after=2, align=WD_ALIGN_PARAGRAPH.LEFT, keep=True)
            self.add_runs(p, h.text, size=11, base_bold=True, base_italic=True)
        self.outline(p, h.level - 1)

    def para(self, b, nxt):
        if b.refs:
            p = self.new_par(after=3, align=WD_ALIGN_PARAGRAPH.LEFT)
            pf = p.paragraph_format
            pf.left_indent, pf.first_line_indent = Inches(0.3), Inches(-0.3)
            self.add_runs(p, b.text, size=REF_PT)
            return
        keep = isinstance(nxt, (md.ListBlock, md.Figure)) or (
            isinstance(nxt, md.Table) and len(md.plain(b.text)) < 450)
        after = 3 if isinstance(nxt, md.ListBlock) else 5
        if b.inbox and (nxt is None or not getattr(nxt, 'inbox', False)):
            after = 1                            # the last line of a box
        p = self.new_par(after=after, keep=keep)
        self.add_runs(p, b.text, size=BOX_PT if b.inbox else BODY_PT)

    def listing(self, b, nxt):
        size = BOX_PT if b.inbox else BODY_PT
        last = len(b.items) - 1
        for k, text in enumerate(b.items):
            after = 2
            if k == last:
                after = 1 if b.inbox and not getattr(nxt, 'inbox', False) else 6
            p = self.new_par(after=after, align=WD_ALIGN_PARAGRAPH.LEFT,
                             keep=(k == last and isinstance(nxt, (md.Table, md.Figure))))
            pf = p.paragraph_format
            pf.left_indent, pf.first_line_indent = Inches(0.3), Inches(-0.22)
            pf.tab_stops.add_tab_stop(Inches(0.3))
            marker = f'{b.start + k}.' if b.ordered else '•'
            r = p.add_run(marker + '\t')
            r.font.size = Pt(size)
            self.add_runs(p, text, size=size)

    def caption(self, label, text, before, after, keep):
        p = self.new_par(before=before, after=after, align=WD_ALIGN_PARAGRAPH.LEFT, keep=keep)
        if label:
            r = p.add_run(label + ' ')
            r.bold, r.font.size = True, Pt(CAPTION_PT)
        self.add_runs(p, text, size=CAPTION_PT)
        return p

    def figure(self, f):
        with Image.open(f.path) as im:
            w_px, h_px = im.size
        width = min(f.width, self.width_in())
        if width * h_px / w_px > MAX_FIG_HEIGHT_IN:
            width = MAX_FIG_HEIGHT_IN * w_px / h_px
        p = self.new_par(after=0, before=4, align=WD_ALIGN_PARAGRAPH.CENTER, keep=True)
        p.add_run().add_picture(str(f.path), width=Inches(width))
        self.caption(f.label, f.caption, before=2, after=8, keep=False)

    @staticmethod
    def cell_border(cell, **edges):
        borders = cell._tc.get_or_add_tcPr().find(qn('w:tcBorders'))
        if borders is None:
            borders = tcpr_insert(cell, OxmlElement('w:tcBorders'))
        for edge in ('top', 'left', 'bottom', 'right'):          # schema order of the edges
            if edge not in edges:
                continue
            sz, color = edges[edge]
            e = OxmlElement(f'w:{edge}')
            e.set(qn('w:val'), 'single')
            e.set(qn('w:sz'), str(sz))
            e.set(qn('w:space'), '0')
            e.set(qn('w:color'), color)
            borders.append(e)

    @staticmethod
    def shade(cell, fill):
        s = OxmlElement('w:shd')
        s.set(qn('w:val'), 'clear')
        s.set(qn('w:color'), 'auto')
        s.set(qn('w:fill'), fill)
        tcpr_insert(cell, s)

    def table(self, t):
        size = SMALL_PT if t.small else TABLE_PT
        self.caption(t.label, t.caption, before=6, after=3, keep=True)
        widths = [w * self.width_in() for w in t.widths]
        rows = t.rows
        tb = self._add_table(1 + len(rows), len(t.header))
        tb.alignment = WD_TABLE_ALIGNMENT.CENTER
        tb.autofit = False
        for j, w in enumerate(widths):
            tb.columns[j].width = Inches(w)
        for i, row in enumerate([t.header] + rows):
            trPr = tb.rows[i]._tr.get_or_add_trPr()
            trPr.append(OxmlElement('w:cantSplit'))
            if i == 0:
                trPr.append(OxmlElement('w:tblHeader'))
            for j, value in enumerate(row):
                cell = tb.cell(i, j)
                cell.width = Inches(widths[j])
                p = cell.paragraphs[0]
                pf = p.paragraph_format
                pf.space_after, pf.space_before, pf.line_spacing = Pt(1), Pt(1), 1.0
                # short tables (or <!-- keep --> ones) stay on one page; long ones may break between rows
                pf.keep_with_next = (i == 0 or ((len(rows) <= 6 or t.keep) and i < len(rows))) or None
                p.alignment = ALIGN[t.aligns[j]]
                self.add_runs(p, value, size=size, base_bold=(i == 0))
                if i == 0:
                    self.cell_border(cell, top=(8, '00B050'), bottom=(6, '00B050'))
                    self.shade(cell, 'E2F0D9')
                else:
                    last = i == len(rows)
                    self.cell_border(cell, bottom=(8 if last else 2, '00B050' if last else 'BFBFBF'))
        spacer = self._add_par()
        pf = spacer.paragraph_format
        pf.space_after, pf.space_before, pf.line_spacing = Pt(4), Pt(0), 1.0

    # ------------------------------------------------------------------ footer
    def page_numbers(self):
        sec = self.d.sections[0]
        sec.footer.is_linked_to_previous = False
        fp = sec.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in list(fp._p.findall(qn('w:r'))):
            fp._p.remove(r)

        def fld(kind, text=None):
            r = OxmlElement('w:r')
            if kind in ('begin', 'separate', 'end'):
                c = OxmlElement('w:fldChar')
                c.set(qn('w:fldCharType'), kind)
            elif kind == 'instr':
                c = OxmlElement('w:instrText')
                c.set(qn('xml:space'), 'preserve')
                c.text = text
            else:
                c = OxmlElement('w:t')
                c.set(qn('xml:space'), 'preserve')
                c.text = text
            r.append(c)
            fp._p.append(r)

        # { IF { PAGE } > 1 "{ PAGE }" "" }: no number on the cover
        fld('begin'); fld('instr', ' IF ')
        fld('begin'); fld('instr', ' PAGE '); fld('separate'); fld('text', '2'); fld('end')
        fld('instr', ' > 1 "')
        fld('begin'); fld('instr', ' PAGE '); fld('separate'); fld('text', '2'); fld('end')
        fld('instr', '" "" ')
        fld('separate'); fld('text', '2'); fld('end')
        for r in fp._p.findall(qn('w:r')):
            rpr = OxmlElement('w:rPr')
            sz = OxmlElement('w:sz')
            sz.set(qn('w:val'), '18')
            rpr.append(sz)
            r.insert(0, rpr)

    # ------------------------------------------------------------------ all
    def render(self, doc):
        blocks = doc.blocks
        for k, b in enumerate(blocks):
            nxt = blocks[k + 1] if k + 1 < len(blocks) else None
            if self.box_cell is not None and not b.inbox:
                self.close_box()
            if b.inbox and self.box_cell is None:
                self.open_box()
            if isinstance(b, md.Heading):
                self.heading(b)
            elif isinstance(b, md.Para):
                self.para(b, nxt)
            elif isinstance(b, md.ListBlock):
                self.listing(b, nxt)
            elif isinstance(b, md.Table):
                self.table(b)
            elif isinstance(b, md.Figure):
                self.figure(b)
            elif isinstance(b, md.PageBreak):
                if b.inbox:
                    print(f'md2docx: line {b.line}: <!-- pagebreak --> inside a box is ignored', file=sys.stderr)
                else:
                    self.page_break_pending = True
        if self.box_cell is not None:
            self.close_box()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('src', help='the Markdown source (.md)')
    ap.add_argument('out', help='the Word file to write (.docx)')
    ap.add_argument('--title', required=True, help='the cover title, e.g. "Final Report"')
    ap.add_argument('--date', required=True, help='the cover date, e.g. "November 24, 2026"')
    ap.add_argument('--students', default=DEFAULT_STUDENTS,
                    help='the cover students line; [[...]] is highlighted (default: %(default)s)')
    ap.add_argument('--template', default=str(DEFAULT_TEMPLATE), help='the cover/header template (read only)')
    ap.add_argument('--doc-title', default=None, help='the document title stored in the file properties')
    ap.add_argument('--ref-pt', type=float, default=REF_PT, help='font size of the reference list (default: %(default)s)')
    a = ap.parse_args()
    globals()['REF_PT'] = a.ref_pt

    src, out, template = Path(a.src), Path(a.out), Path(a.template)
    if out.suffix.lower() != '.docx':
        sys.exit('md2docx: the output must end in .docx')
    if out.name.lower() in PROTECTED or out.resolve() == template.resolve():
        sys.exit(f'md2docx: refusing to overwrite {out.name} (it is read only)')
    if not template.is_file():
        sys.exit(f'md2docx: template not found: {template}')
    try:
        doc = md.parse(src)
    except md.MdError as e:
        sys.exit(f'md2docx: {e}')

    b = Builder(template)
    b.cover(a.title, a.date, a.students)
    b.render(doc)
    b.page_numbers()
    b.d.core_properties.title = a.doc_title or f'ECSE 557: {md.plain(a.title)}'
    out.parent.mkdir(parents=True, exist_ok=True)
    b.d.save(str(out))
    print('saved', out)


if __name__ == '__main__':
    main()
