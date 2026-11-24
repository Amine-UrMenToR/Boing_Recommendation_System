"""Shared reader for the report's Markdown subset (used by md2docx.py and md2tex.py).

The subset (see README.md):
  # / ## / ###            headings (they carry their own numbers, nothing is auto-numbered)
  paragraphs              lines joined until a blank line
  **bold**, *italic*      inline; [[text]] is a placeholder, shown as [text] highlighted yellow
  - item / 1. item        bullet and numbered lists (an indented line continues the item)
  Table N. caption        immediately followed by a pipe table; optional <!-- widths: 1.2, 3, 1 --> and
                          <!-- small --> lines before the caption; <br> breaks a line inside a cell
  ![Figure N. caption](../figures/x.png){width=6.0}     width in inches, path relative to the .md file
  <!-- pagebreak -->      new page
  <!-- box -->            the section it is placed in (or the one right below it) is drawn in a light box
  # References            its paragraphs get a hanging indent
  # Appendix ...          starts the appendices (on a new page)
  any other <!-- ... -->  is a comment and is ignored
  \\* \\_ \\| \\[ \\] \\\\ \\#  backslash escapes for literal characters
"""
import re
from dataclasses import dataclass, field
from pathlib import Path

# ----------------------------------------------------------------------------------------------- blocks


@dataclass
class Heading:
    level: int
    text: str
    page_break: bool = False
    box: bool = False          # the body of this heading's section is drawn in a box
    kind: str = 'normal'       # 'normal' | 'references' | 'appendix'
    line: int = 0
    inbox: bool = False        # the heading itself sits inside a box (a sub-heading of a boxed section)


@dataclass
class Para:
    text: str
    refs: bool = False         # inside the References section
    line: int = 0
    inbox: bool = False        # inside a boxed section


@dataclass
class ListBlock:
    ordered: bool
    start: int
    items: list
    line: int = 0
    inbox: bool = False


@dataclass
class Table:
    label: str                 # 'Table 1.'
    caption: str
    header: list
    rows: list
    aligns: list               # 'l' | 'c' | 'r' per column
    widths: list               # relative weights (normalised to sum 1)
    small: bool = False
    line: int = 0
    inbox: bool = False
    keep: bool = False         # <!-- keep -->: never break this table across pages


@dataclass
class Figure:
    label: str                 # 'Figure 1.' (or '' when the caption has no label)
    caption: str
    path: Path                 # absolute
    src: str                   # path as written in the .md
    width: float               # inches
    line: int = 0
    inbox: bool = False


@dataclass
class PageBreak:
    line: int = 0
    inbox: bool = False


@dataclass
class Doc:
    blocks: list = field(default_factory=list)
    source: Path = None


class MdError(Exception):
    pass


# ----------------------------------------------------------------------------------------------- escapes
# Backslash escapes become private-use characters while parsing, and are restored at the end.
_ESC = {'*': '\ue001', '_': '\ue002', '|': '\ue003', '[': '\ue004', ']': '\ue005', '\\': '\ue006',
        '#': '\ue007', '<': '\ue008', '>': '\ue009', '!': '\ue00a', '`': '\ue00b'}
_UNESC = {v: k for k, v in _ESC.items()}


def protect(s):
    return re.sub(r'\\([*_|\[\]\\#<>!`])', lambda m: _ESC[m.group(1)], s)


def restore(s):
    for k, v in _UNESC.items():
        s = s.replace(k, v)
    return s


# ----------------------------------------------------------------------------------------------- inline


def smart_quotes(text):
    """Straight quotes to typographic ones (text that already has curly quotes is left alone)."""
    text = re.sub(r"(^|[\s(\[“*])'(\d\d)\b", '\\1’\\2', text)      # '17 -> ’17
    text = re.sub(r'(^|[\s(\[“‘*/—–-])"', '\\1“', text)
    text = text.replace('"', '”')
    text = re.sub(r"(^|[\s(\[“*/—–-])'", '\\1‘', text)
    return text.replace("'", '’')


@dataclass
class Run:
    text: str
    bold: bool = False
    italic: bool = False
    hl: bool = False           # placeholder highlight
    br: bool = False           # a line break (text is empty)


def _pair_delims(s, delim):
    """Positions of matched opening/closing emphasis delimiters ('**' or '*')."""
    pos = []
    i = 0
    n = len(delim)
    while i < len(s):
        if s.startswith(delim, i) and (delim == '**' or not s.startswith('**', i)):
            pos.append(i)
            i += n
        elif delim == '*' and s.startswith('**', i):
            i += 2
        else:
            i += 1
    pairs = []
    stack = None
    for p in pos:
        before = s[p - 1] if p > 0 else ' '
        after = s[p + n] if p + n < len(s) else ' '
        if stack is None:
            if not after.isspace():
                stack = p
        else:
            if not before.isspace():
                pairs.append((stack, p))
                stack = None
            elif not after.isspace():
                stack = p
    return pairs


def inline(text, base_bold=False, base_italic=False):
    """Parse **bold**, *italic*, [[placeholder]] and <br> into a list of Runs (straight quotes become curly)."""
    s = smart_quotes(protect(text))
    marks = {}                                     # position -> (length, kind)
    for a, b in _pair_delims(s, '**'):
        marks[a] = (2, 'b')
        marks[b] = (2, 'b')
    masked = list(s)
    for p, (n, _) in marks.items():
        for k in range(n):
            masked[p + k] = '\0'
    for a, b in _pair_delims(''.join(masked), '*'):
        marks[a] = (1, 'i')
        marks[b] = (1, 'i')
    for m in re.finditer(r'\[\[(.+?)\]\]', s):
        marks[m.start()] = (2, 'h')
        marks[m.end() - 2] = (2, 'h')
    for m in re.finditer(r'<br\s*/?>', s, flags=re.I):
        marks[m.start()] = (m.end() - m.start(), 'br')

    runs = []
    bold, italic, hl = base_bold, base_italic, False
    buf = []

    def flush():
        if buf:
            runs.append(Run(restore(''.join(buf)), bold, italic, hl))
            buf.clear()

    i = 0
    while i < len(s):
        if i in marks:
            n, kind = marks[i]
            flush()
            if kind == 'b':
                bold = not bold if not base_bold else True
            elif kind == 'i':
                italic = not italic if not base_italic else True
            elif kind == 'h':
                if not hl:
                    hl = True
                    buf.append('[')
                else:
                    buf.append(']')
                    flush()
                    hl = False
            elif kind == 'br':
                runs.append(Run('', bold, italic, hl, br=True))
            i += n
            continue
        buf.append(s[i])
        i += 1
    flush()
    # merge neighbours with the same look
    merged = []
    for r in runs:
        if merged and not r.br and not merged[-1].br and (r.bold, r.italic, r.hl) == (
                merged[-1].bold, merged[-1].italic, merged[-1].hl):
            merged[-1].text += r.text
        else:
            merged.append(r)
    return [r for r in merged if r.br or r.text]


def plain(text):
    """Text without markup (for bookmarks and metadata)."""
    return ''.join(r.text if not r.br else ' ' for r in inline(text))


# ----------------------------------------------------------------------------------------------- blocks

_TABLE_CAP = re.compile(r'^(Table\s+[A-Z]?\d+[a-z]?\.)\s+(.+)$')
_FIG_CAP = re.compile(r'^(Figure\s+[A-Z]?\d+[a-z]?\.)\s+(.+)$', re.S)
_FIGURE = re.compile(r'^!\[(.*)\]\(([^)\s]+)\)\s*(\{\s*width\s*=\s*([\d.]+)\s*(in)?\s*\})?\s*$')
_BULLET = re.compile(r'^[-+]\s+(.*)$')
_NUMBER = re.compile(r'^(\d+)[.)]\s+(.*)$')
_HEADING = re.compile(r'^(#{1,3})\s+(.+?)\s*#*\s*$')
_COMMENT = re.compile(r'^<!--(.*?)-->\s*$')


def _split_row(line):
    s = protect(line.strip())
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    # restore escapes except the pipe (kept literal in the cell)
    return [restore(c.strip()) for c in s.split('|')]


def _is_sep_row(cells):
    return all(re.fullmatch(r':?-{2,}:?', c.replace(' ', '')) for c in cells) and cells


def _starts_block(line, in_para):
    """True when this line cannot continue a paragraph (it starts another block)."""
    s = line.strip()
    if not s or _HEADING.match(s) or s.startswith('|') or s.startswith('![') or s.startswith('<!--'):
        return True
    if _BULLET.match(s):
        return True
    m = _NUMBER.match(s)
    # like CommonMark, only a list starting at 1 may interrupt a paragraph
    return bool(m) and (not in_para or m.group(1) == '1')


def parse(path):
    path = Path(path)
    raw = path.read_text(encoding='utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
    if '\t' in raw:
        raw = raw.replace('\t', '    ')
    lines = raw.split('\n')
    doc = Doc(source=path)
    out = doc.blocks

    st = {
        'widths': None, 'small': False, 'keep': False, 'box_next': False, 'break': False,
        'box_level': 0,            # 0 = not in a box, else the level of the heading whose section is boxed
        'refs': False, 'appendix': False, 'fresh_heading': None,
    }

    def where(ln):
        return f'{path.name}:{ln}'

    def add(block):
        if st['break']:
            if isinstance(block, Heading):
                block.page_break = True
            else:
                out.append(PageBreak(line=block.line, inbox=st['box_level'] > 0))
        st['break'] = False
        if not isinstance(block, Heading):
            block.inbox = st['box_level'] > 0
            st['fresh_heading'] = None
        out.append(block)

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()
        ln = i + 1

        if not s:
            i += 1
            continue

        # ---- comments and directives
        if s.startswith('<!--'):
            text = s
            j = i
            while '-->' not in text and j + 1 < n:
                j += 1
                text += ' ' + lines[j].strip()
            if '-->' not in text:
                raise MdError(f'{where(ln)}: unclosed <!-- comment')
            if text[text.index('-->') + 3:].strip():
                raise MdError(f'{where(j + 1)}: put nothing after --> on the same line')
            body = text[4:text.index('-->')].strip()
            low = body.lower()
            if low == 'pagebreak':
                st['break'] = True
            elif low == 'small':
                st['small'] = True
            elif low == 'keep':
                st['keep'] = True
            elif low == 'box':
                h = st['fresh_heading']
                if h is not None:                 # right below a heading: box that heading's section
                    h.box = True
                    st['box_level'] = h.level
                else:                             # otherwise: box the section of the next heading
                    st['box_next'] = True
            elif low.startswith('widths:'):
                try:
                    ws = [float(x) for x in body.split(':', 1)[1].split(',') if x.strip()]
                except ValueError:
                    raise MdError(f'{where(ln)}: widths must be numbers, e.g. <!-- widths: 1.2, 3, 1 -->')
                if not ws or any(w <= 0 for w in ws):
                    raise MdError(f'{where(ln)}: widths must be positive numbers')
                st['widths'] = ws
            i = j + 1
            continue

        if (st['widths'] or st['small'] or st['keep']) and not (_TABLE_CAP.match(s) and i + 1 < n
                                                                and lines[i + 1].strip().startswith('|')):
            raise MdError(f'{where(ln)}: <!-- widths -->, <!-- small --> and <!-- keep --> must come right before a '
                          f'"Table N. caption" line followed by its table')

        # ---- headings
        m = _HEADING.match(s)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            h = Heading(level=level, text=text, line=ln)
            if st['box_level'] and level <= st['box_level']:
                st['box_level'] = 0               # a heading at the same or a higher level ends the box
            h.inbox = st['box_level'] > 0
            if level == 1:
                low = plain(text).strip().lower()
                st['refs'] = low in ('references', 'reference list', 'bibliography', 'works cited')
                if st['refs']:
                    h.kind = 'references'
                elif low.startswith('appendix') or low.startswith('appendices'):
                    h.kind = 'appendix'
                    if not st['appendix']:
                        h.page_break = True
                    st['appendix'] = True
            if st['box_next']:
                if h.inbox:
                    raise MdError(f'{where(ln)}: a box cannot start inside another box')
                h.box = True
                st['box_level'] = level
                st['box_next'] = False
            add(h)
            st['fresh_heading'] = h
            i += 1
            continue

        # ---- figure
        if s.startswith('!['):
            m = _FIGURE.match(s)
            if not m:
                raise MdError(f'{where(ln)}: a figure is ![Figure N. caption](../figures/file.png){{width=6.0}}')
            alt, src, width = m.group(1), m.group(2), m.group(4)
            fm = _FIG_CAP.match(alt.strip())
            label, cap = (fm.group(1), fm.group(2)) if fm else ('', alt.strip())
            p = (path.parent / src).resolve()
            if not p.is_file():
                raise MdError(f'{where(ln)}: figure file not found: {src} (looked for {p})')
            if p.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.pdf'):
                raise MdError(f'{where(ln)}: figures must be .png, .jpg or .pdf: {src}')
            w = float(width) if width else 6.0
            if not 0.3 <= w <= 6.5:
                raise MdError(f'{where(ln)}: figure width {w} in is outside 0.3 to 6.5 inches '
                              f'(the text is 6.5 in wide)')
            add(Figure(label=label, caption=cap, path=p, src=src, width=w, line=ln))
            i += 1
            continue

        # ---- table: caption line + pipe rows
        m = _TABLE_CAP.match(s)
        if m and i + 1 < n and lines[i + 1].strip().startswith('|'):
            label, cap = m.group(1), m.group(2)
            j = i + 1
            rows = []
            while j < n and lines[j].strip().startswith('|'):
                rows.append(_split_row(lines[j]))
                j += 1
            if len(rows) < 2 or not _is_sep_row(rows[1]):
                raise MdError(f'{where(ln)}: a table needs a header row and then a |---|---| row')
            header, sep, body = rows[0], rows[1], rows[2:]
            ncol = len(header)
            if not body:
                raise MdError(f'{where(ln)}: the table has no rows')
            if len(sep) != ncol:
                raise MdError(f'{where(ln + 2)}: the |---| row has {len(sep)} cells, the header has {ncol}')
            for k, r in enumerate(body):
                if len(r) != ncol:
                    raise MdError(f'{where(ln + 3 + k)}: this row has {len(r)} cells, the header has {ncol}')
            aligns = []
            for c in sep:
                c = c.replace(' ', '')
                aligns.append('c' if c.startswith(':') and c.endswith(':') else 'r' if c.endswith(':') else 'l')
            if st['widths']:
                if len(st['widths']) != ncol:
                    raise MdError(f'{where(ln)}: widths has {len(st["widths"])} numbers but the table has '
                                  f'{ncol} columns')
                widths = st['widths']
            else:
                widths = []
                for c in range(ncol):
                    longest = max([len(plain(r[c])) for r in body] + [len(plain(header[c])) * 0.8, 4])
                    widths.append(min(longest, 60) ** 0.8)
            tot = sum(widths)
            add(Table(label=label, caption=cap, header=header, rows=body, aligns=aligns,
                      widths=[w / tot for w in widths], small=st['small'], keep=st['keep'], line=ln))
            st['widths'], st['small'], st['keep'] = None, False, False
            i = j
            continue
        if s.startswith('|'):
            raise MdError(f'{where(ln)}: a pipe table must come right after its "Table N. caption" line')

        # ---- lists
        mb, mn = _BULLET.match(s), _NUMBER.match(s)
        if mb or mn:
            ordered = bool(mn)
            start = int(mn.group(1)) if mn else 1
            items = []
            j = i
            while j < n:
                t = lines[j]
                ts = t.strip()
                b2, n2 = _BULLET.match(ts), _NUMBER.match(ts)
                if ordered and n2:
                    items.append(n2.group(2))
                elif not ordered and b2:
                    items.append(b2.group(1))
                elif ts and items and not (b2 or n2) and (t[:1] == ' ' or not _starts_block(t, True)):
                    items[-1] += ' ' + ts           # a continuation line of the item
                else:
                    break
                j += 1
            add(ListBlock(ordered=ordered, start=start, items=items, line=ln))
            i = j
            continue

        # ---- paragraph
        buf = [s]
        j = i + 1
        while j < n and not _starts_block(lines[j], True):
            if _TABLE_CAP.match(lines[j].strip()) and j + 1 < n and lines[j + 1].strip().startswith('|'):
                break
            buf.append(lines[j].strip())
            j += 1
        add(Para(text=' '.join(buf), refs=st['refs'], line=ln))
        i = j

    if st['break']:
        out.append(PageBreak(line=n))
    if st['widths'] or st['small'] or st['keep']:
        raise MdError(f'{path.name}: <!-- widths -->, <!-- small --> or <!-- keep --> at the end of the file without a table')
    if st['box_next']:
        raise MdError(f'{path.name}: <!-- box --> at the end of the file without a heading below it')
    return doc


if __name__ == '__main__':          # debugging aid: py mdreport.py file.md
    import sys
    for b in parse(sys.argv[1]).blocks:
        print(type(b).__name__, {k: (v if not isinstance(v, str) else v[:60]) for k, v in vars(b).items()
                                 if k not in ('rows',)})
