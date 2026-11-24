"""Build the LaTeX version of the report (a self-contained Overleaf project) from the Markdown source.

    py md2tex.py SRC.md OUTDIR --title "Final Report" --date "November 24, 2026"
        [--students "Students: Amine Houari and [[Teammate’s full name]]  ·  Group 14"]
        [--template ../../Repport.docx]

Writes OUTDIR/main.tex, copies the figures it uses into OUTDIR/figures/ together with the frog header image
and the McGill logo taken from Repport.docx (read only), and writes OUTDIR.zip next to OUTDIR (upload it to
Overleaf with New Project > Upload Project). main.tex compiles with pdfLaTeX and only common packages.
Every non-ASCII character is turned into a safe LaTeX form; an unknown one stops the build with its line.
Run check_tex.py OUTDIR afterwards.
"""
import argparse
import io
import re
import shutil
import sys
import textwrap
import unicodedata
import zipfile
from pathlib import Path

import docx
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mdreport as md  # noqa: E402

HERE = Path(__file__).resolve().parent
DEFAULT_TEMPLATE = HERE.parent.parent / 'Repport.docx'
DEFAULT_STUDENTS = 'Students: Amine Houari and [[Teammate’s full name]]  ·  Group 14'
FROG_FILE, LOGO_FILE = 'boing-frog.png', 'mcgill-logo.png'

# ------------------------------------------------------------------------------------------ characters
# Math-mode replacements (wrapped in $...$; neighbours are merged into one $...$).
MATH = {
    'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'δ': r'\delta', 'ε': r'\varepsilon', 'ϵ': r'\epsilon',
    'ζ': r'\zeta', 'η': r'\eta', 'θ': r'\theta', 'ι': r'\iota', 'κ': r'\kappa', 'λ': r'\lambda', 'μ': r'\mu',
    'µ': r'\mu', 'ν': r'\nu', 'ξ': r'\xi', 'π': r'\pi', 'ρ': r'\rho', 'σ': r'\sigma', 'ς': r'\varsigma',
    'τ': r'\tau', 'υ': r'\upsilon', 'φ': r'\varphi', 'ϕ': r'\phi', 'χ': r'\chi', 'ψ': r'\psi', 'ω': r'\omega',
    'Γ': r'\Gamma', 'Δ': r'\Delta', 'Θ': r'\Theta', 'Λ': r'\Lambda', 'Ξ': r'\Xi', 'Π': r'\Pi', 'Σ': r'\Sigma',
    'Υ': r'\Upsilon', 'Φ': r'\Phi', 'Ψ': r'\Psi', 'Ω': r'\Omega',
    '≥': r'\geq', '≤': r'\leq', '≠': r'\neq', '≈': r'\approx', '≡': r'\equiv', '∼': r'\sim', '≪': r'\ll',
    '≫': r'\gg', '×': r'\times', '÷': r'\div', '±': r'\pm', '∓': r'\mp', '−': '-', '∈': r'\in',
    '∉': r'\notin', '∞': r'\infty', '∑': r'\sum', '∏': r'\prod', '√': r'\surd', '∝': r'\propto',
    '∂': r'\partial', '∇': r'\nabla', '∀': r'\forall', '∃': r'\exists', '∅': r'\emptyset', '∩': r'\cap',
    '∪': r'\cup', '⊂': r'\subset', '⊆': r'\subseteq', '⊃': r'\supset', '⊇': r'\supseteq', '∧': r'\wedge',
    '∨': r'\vee', '¬': r'\neg', '→': r'\rightarrow', '←': r'\leftarrow', '↔': r'\leftrightarrow',
    '⇒': r'\Rightarrow', '⇐': r'\Leftarrow', '⇔': r'\Leftrightarrow', '↑': r'\uparrow', '↓': r'\downarrow',
    '↦': r'\mapsto', '·': r'\cdot', '⋅': r'\cdot', '∗': r'\ast', '∘': r'\circ', '°': r'^{\circ}',
    '′': r'^{\prime}', '″': r'^{\prime\prime}', '²': r'^{2}', '³': r'^{3}', '¹': r'^{1}', '½': r'\frac{1}{2}',
    '¼': r'\frac{1}{4}', '¾': r'\frac{3}{4}', '⟨': r'\langle', '⟩': r'\rangle', '∣': r'\mid', '‖': r'\|',
    '∫': r'\int', '≅': r'\cong', '∖': r'\setminus', '⊕': r'\oplus', '⊗': r'\otimes',
}
# Plain-text spellings for PDF bookmarks.
MATH_PLAIN = {
    '≥': '>=', '≤': '<=', '≠': '!=', '≈': '~', '×': 'x', '÷': '/', '±': '+/-', '−': '-', '∈': 'in',
    '∞': 'infinity', '→': '->', '←': '<-', '↔': '<->', '⇒': '=>', '·': '-', '⋅': '-', '°': ' deg',
}
# Text-mode replacements.
TEXT = {
    '“': '``', '”': "''", '‘': '`', '’': "'", '„': r'\quotedblbase{}', '‚': ',',
    '–': '--', '—': '---', '‒': '--', '―': '---', '‐': '-', '‑': r'\mbox{-}', '…': r'\ldots{}',
    ' ': '~', ' ': r'\,', ' ': r'\,', ' ': r'\enskip{}', ' ': r'\quad{}',
    '​': '', '‌': '', '‍': '', '﻿': '', '­': r'\-',
    '•': r'\textbullet{}', '§': r'\S{}', '¶': r'\P{}', '©': r'\textcopyright{}', '®': r'\textregistered{}',
    '™': r'\texttrademark{}', '†': r'\dag{}', '‡': r'\ddag{}', '«': r'\guillemotleft{}',
    '»': r'\guillemotright{}', '‹': r'\guilsinglleft{}', '›': r'\guilsinglright{}', '£': r'\pounds{}',
    '¿': r'\textquestiondown{}', '¡': r'\textexclamdown{}',
    '\\': r'\textbackslash{}', '{': r'\{', '}': r'\}', '$': r'\$', '&': r'\&', '%': r'\%', '#': r'\#',
    '_': r'\_', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}', '<': r'\textless{}',
    '>': r'\textgreater{}', '|': r'\textbar{}', '"': r'\textquotedbl{}', '`': r'\`{}',
}
# Letters that utf8 inputenc + T1 fontenc typeset directly (kept as they are, for a readable main.tex).
LATIN = set(chr(c) for c in range(0xC0, 0x100)) - {'×', '÷'}
LATIN |= set('ĂăĄąĆćČčĎďĐđĘęĚěĞğİıĹĺĽľŁłŃńŇňŊŋŐőŒœŔŕŘřŚśŞşŠšŢţŤťŮůŰűŸŹźŻżŽž')
# Combining marks -> LaTeX accent commands (for other accented letters).
ACCENTS = {'̀': '`', '́': "'", '̂': '^', '̃': '~', '̈': '"', '̄': '=',
           '̇': '.', '̊': 'r', '̧': 'c', '̨': 'k', '̌': 'v', '̆': 'u',
           '̋': 'H', '̣': 'd'}


class TexError(Exception):
    pass


def _char(ch, where):
    """(mode, latex) for one character: mode is 't' (text) or 'm' (math)."""
    if ch in MATH:
        return 'm', MATH[ch]
    if ch in TEXT:
        return 't', TEXT[ch]
    if ch == '\n':
        return 't', ' '
    if 32 <= ord(ch) < 127:
        return 't', ch
    if ch in LATIN:
        return 't', ch
    dec = unicodedata.normalize('NFD', ch)
    if len(dec) == 2 and dec[0].isascii() and dec[0].isalpha() and dec[1] in ACCENTS:
        acc = ACCENTS[dec[1]]
        base = dec[0]
        if base in 'ij' and acc not in 'cdk':     # accents above i and j use the dotless letters
            base = '\\' + base
        return 't', '\\' + acc + '{' + base + '}'
    raise TexError(f'{where}: no LaTeX form for the character {ch!r} (U+{ord(ch):04X} '
                   f'{unicodedata.name(ch, "?")}); add it to MATH or TEXT in md2tex.py or avoid it')


def tex_text(s, where='?'):
    """Escape plain text for LaTeX: specials escaped, non-ASCII converted, math merged into $...$."""
    chunks = []                                   # [mode, text]
    for ch in s:
        mode, out = _char(ch, where)
        if mode == 'm' and chunks and chunks[-1][0] == 'm':
            chunks[-1][1] += ' ' + out if out[0].isalpha() or out[0] == '\\' else out
        elif mode == 'm' and len(chunks) >= 2 and chunks[-2][0] == 'm' and chunks[-1][1] in (' ',):
            chunks[-2][1] += ' ' + out            # "≤ ≥" -> one math group
            chunks.pop()
        else:
            chunks.append([mode, out])
    out = ''
    for mode, text in chunks:
        piece = '$' + text + '$' if mode == 'm' else text
        # break TeX ligatures between characters that were separate in the source:
        # quote + quote (`` '' would merge), ?` and !` (Spanish marks), ,, (low quote), -- and ---
        if out and piece and (
                (out[-1] in "`'" and piece[0] in "`'") or (out[-1] in '?!' and piece[0] == '`')
                or (out[-1] == ',' and piece[0] == ',') or (out[-1] == '-' and piece[0] == '-')):
            piece = '{}' + piece
        out += piece
    return out


def tex_plain(s, where='?'):
    """Text for PDF strings (bookmarks, metadata): math characters spelled in ASCII."""
    out = []
    for ch in s:
        if ch in MATH_PLAIN:
            out.append(MATH_PLAIN[ch])
        elif ch in MATH:
            name = unicodedata.name(ch, '')
            out.append(name.split()[-1].lower() if name.startswith('GREEK') else '')
        else:
            out.append(ch)
    return tex_text(''.join(out), where)


URL = re.compile(r'https?://[A-Za-z0-9./:_?=~+\-]+[A-Za-z0-9/_=~+\-]')


def runs_tex(text, where, in_heading=False, in_caption=False):
    """Inline Markdown -> LaTeX."""
    out = []
    for r in md.inline(text):
        if r.br:
            out.append(' ' if (in_heading or in_caption) else r'\mbox{}\newline ')
            continue
        if r.hl:
            body = _placeholder(r.text, where, r.bold, r.italic)
        else:
            body = _urls(r.text, where) if not in_heading else tex_text(r.text, where)
            if r.italic:
                body = r'\textit{' + body + '}'
            if r.bold:
                body = r'\textbf{' + body + '}'
        out.append(body)
    return ''.join(out)


def _urls(text, where):
    out, pos = [], 0
    for m in URL.finditer(text):
        out.append(tex_text(text[pos:m.start()], where))
        out.append(r'\url{' + m.group(0) + '}')
        pos = m.end()
    out.append(tex_text(text[pos:], where))
    return ''.join(out)


def _placeholder(text, where, bold, italic):
    """[text] highlighted yellow; words are boxes joined by yellow, breakable gaps."""
    parts = re.split(r'(\s+)', text)
    out = []
    for p in parts:
        if not p:
            continue
        if p.isspace():
            out.append(r'\phgap{}')
            continue
        w = tex_text(p, where)
        if italic:
            w = r'\textit{' + w + '}'
        if bold:
            w = r'\textbf{' + w + '}'
        out.append(r'\phword{' + w + '}')
    return ''.join(out)


def guard(s):
    """Text placed right after \\item, \\\\ or at the start of a table cell must not start with [ or *."""
    return '{}' + s if s[:1] in '[*' else s


def wrap(s, width=110):
    return '\n'.join(textwrap.wrap(s, width=width, break_long_words=False, break_on_hyphens=False))


# ------------------------------------------------------------------------------------------ preamble
PREAMBLE = r"""% !TEX program = pdflatex
% Generated by md2tex.py from @SOURCE@. Edit the Markdown source and rebuild, not this file.
\documentclass[11pt,letterpaper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{newtxtext}
\usepackage{newtxmath}
\usepackage[letterpaper,margin=1in,headheight=14pt,headsep=0.25in,footskip=0.5in]{geometry}
\usepackage{graphicx}
\usepackage{array}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{caption}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{microtype}
\usepackage[hidelinks]{hyperref}

\hypersetup{pdftitle={@PDFTITLE@}}

% ---------------------------------------------------------------- colours (as in the Word version)
\definecolor{boinggreen}{RGB}{0,176,80}
\definecolor{phyellow}{RGB}{255,255,0}
\definecolor{boxfill}{HTML}{F2F8EE}
\definecolor{boxline}{HTML}{A9D18E}

% ---------------------------------------------------------------- paragraphs
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt plus 1pt minus 1pt}
\setlength{\emergencystretch}{1.5em}
\widowpenalty=3000
\clubpenalty=3000

% ---------------------------------------------------------------- headings (they carry their own numbers)
\setcounter{secnumdepth}{0}
\titleformat{\section}{\normalfont\fontsize{14}{17}\selectfont\bfseries\color{boinggreen}\raggedright}{}{0pt}{}
\titlespacing*{\section}{0pt}{12pt plus 3pt minus 2pt}{2pt}
\titleformat{\subsection}{\normalfont\fontsize{11.5}{14}\selectfont\bfseries\raggedright}{}{0pt}{}
\titlespacing*{\subsection}{0pt}{9pt plus 2pt minus 1pt}{1pt}
\titleformat{\subsubsection}{\normalfont\normalsize\bfseries\itshape\raggedright}{}{0pt}{}
\titlespacing*{\subsubsection}{0pt}{7pt plus 2pt minus 1pt}{0pt}

% ---------------------------------------------------------------- lists, captions, tables
\setlist{leftmargin=0.3in,itemsep=2pt,parsep=0pt,topsep=2pt,partopsep=0pt}
\setlist[enumerate]{label=\arabic*.}
\captionsetup{font=small,labelfont=bf,justification=raggedright,singlelinecheck=false}
\captionsetup[table]{position=top,skip=4pt}
\captionsetup[figure]{position=bottom,skip=4pt}
\setlength{\tabcolsep}{4pt}
\newcommand{\rowrule}{\midrule[0.2pt]}
\setlength{\textfloatsep}{12pt plus 2pt minus 2pt}
\setlength{\floatsep}{10pt plus 2pt minus 2pt}
\setlength{\intextsep}{10pt plus 2pt minus 2pt}
\renewcommand{\topfraction}{0.9}
\renewcommand{\bottomfraction}{0.8}
\renewcommand{\textfraction}{0.07}
\renewcommand{\floatpagefraction}{0.75}

% ---------------------------------------------------------------- placeholders: [text] highlighted yellow
% Each word is a yellow box; the gaps are yellow leaders that can still break across lines.
\DeclareRobustCommand{\phword}[1]{{\setlength{\fboxsep}{0pt}\colorbox{phyellow}{\strut #1}}}
\DeclareRobustCommand{\phgap}{{\color{phyellow}\leaders\hrule height\ht\strutbox depth\dp\strutbox\hskip 0.3em plus 0.15em minus 0.08em}}

% ---------------------------------------------------------------- a light box (<!-- box -->)
\newsavebox{\reportboxbin}
\newlength{\reportboxsep}
\setlength{\reportboxsep}{6pt}
\newenvironment{reportbox}
  {\par\smallskip\noindent\begin{lrbox}{\reportboxbin}%
   \begin{minipage}{\dimexpr\linewidth-2\reportboxsep-1.2pt\relax}%
   \small\setlength{\parskip}{4pt plus 1pt}\setlength{\parindent}{0pt}}
  {\end{minipage}\end{lrbox}%
   {\setlength{\fboxsep}{\reportboxsep}\setlength{\fboxrule}{0.6pt}%
    \fcolorbox{boxline}{boxfill}{\usebox{\reportboxbin}}}\par\medskip}

% ---------------------------------------------------------------- references: hanging indent
\newenvironment{references}
  {\par\small\raggedright\setlength{\parskip}{3pt plus 1pt}\setlength{\parindent}{0pt}}
  {\par}
\newcommand{\refentry}{\par\noindent\hangindent=0.3in\hangafter=1\relax}

% ---------------------------------------------------------------- header (the frog) and page numbers
\newcommand{\headerfrog}{\makebox[0pt][l]{\hspace*{-0.19in}\raisebox{-0.33in}[0pt][0pt]{%
  \includegraphics[width=1in]{figures/@FROG@}}}}
\newcommand{\coverlogo}{\makebox[0pt][l]{\hspace*{-0.44in}\raisebox{-0.355in}[0pt][0pt]{%
  \includegraphics[width=2.49in]{figures/@LOGO@}}}}
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyhead[R]{\headerfrog}
\fancyfoot[C]{\fontsize{9}{11}\selectfont\thepage}
\fancypagestyle{cover}{%
  \fancyhf{}%
  \renewcommand{\headrulewidth}{0pt}%
  \renewcommand{\footrulewidth}{0pt}%
  \fancyhead[L]{\coverlogo}%
  \fancyhead[R]{\headerfrog}}

\begin{document}
"""

COVER = r"""
% ================================================================ cover page (as in Repport.docx)
\thispagestyle{cover}
\vspace*{2.95in}
{\centering\fontsize{22}{27}\selectfont\bfseries @COURSE@\par}
\vspace{6pt}
{\centering\fontsize{16}{19}\selectfont\bfseries @PROJECT@\par}
\vspace{4pt}
{\centering\fontsize{16}{19}\selectfont\bfseries\underline{@TITLE@}\par}
\vfill
{\fontsize{14}{17}\selectfont @PROFESSOR@\par}
\vspace{4pt}
{\fontsize{14}{17}\selectfont @STUDENTS@\par}
\vspace{28pt}
{\centering\fontsize{14}{17}\selectfont @DATE@\par}
\vspace*{0.05in}
\clearpage
"""


def fill(template, values):
    for k, v in values.items():
        template = template.replace('@' + k + '@', v)
    left = re.findall(r'@[A-Z]+@', template)
    if left:
        raise TexError(f'unfilled template fields: {left}')
    return template


# ------------------------------------------------------------------------------------------ writer
class TexWriter:
    def __init__(self, doc, outdir):
        self.doc = doc
        self.outdir = outdir
        self.lines = []
        self.figures = {}                     # source path -> published name
        self.in_box = False
        self.in_refs = False

    def where(self, b):
        return f'{self.doc.source.name}:{b.line}'

    def emit(self, s=''):
        self.lines.append(s)

    def fig_name(self, path):
        if path in self.figures:
            return self.figures[path]
        stem = re.sub(r'[^a-z0-9]+', '-', path.stem.lower()).strip('-') or 'figure'
        name = f'{stem}{path.suffix.lower()}'
        used = set(self.figures.values()) | {FROG_FILE, LOGO_FILE}
        k = 2
        while name in used:
            name = f'{stem}-{k}{path.suffix.lower()}'
            k += 1
        self.figures[path] = name
        return name

    # ---- groups that span several blocks
    def close_groups(self, b):
        if self.in_refs and not (isinstance(b, md.Para) and b.refs):
            self.emit(r'\end{references}')
            self.emit()
            self.in_refs = False
        if self.in_box and not getattr(b, 'inbox', False):
            self.emit(r'\end{reportbox}')
            self.emit()
            self.in_box = False

    def open_box(self):
        if not self.in_box:
            self.emit(r'\begin{reportbox}')
            self.in_box = True

    # ---- blocks
    def heading(self, b):
        w = self.where(b)
        latex = runs_tex(b.text, w, in_heading=True)
        if b.inbox:                               # a sub-heading inside a box: a bold line
            self.open_box()
            self.emit(r'\par\textbf{' + latex + r'}\par\nopagebreak')
            self.emit()
            return
        if b.page_break:
            self.emit(r'\clearpage')
        cmd = {1: 'section', 2: 'subsection', 3: 'subsubsection'}[b.level]
        plain = tex_plain(md.plain(b.text), w)
        title = latex if latex == plain else r'\texorpdfstring{' + latex + '}{' + plain + '}'
        self.emit(f'\\{cmd}{{{title}}}')
        self.emit()
        if b.box:
            self.open_box()

    def para(self, b):
        w = self.where(b)
        text = runs_tex(b.text, w)
        if b.refs:
            if not self.in_refs:
                self.emit(r'\begin{references}')
                self.in_refs = True
            self.emit(wrap(r'\refentry ' + text))
            self.emit()
            return
        if b.inbox:
            self.open_box()
        self.emit(wrap(text))
        self.emit()

    def listing(self, b):
        if b.inbox:
            self.open_box()
        env = 'enumerate' if b.ordered else 'itemize'
        opt = f'[start={b.start}]' if b.ordered and b.start != 1 else ''
        self.emit(f'\\begin{{{env}}}{opt}')
        for text in b.items:
            self.emit(wrap(r'\item ' + guard(runs_tex(text, self.where(b)))))
        self.emit(f'\\end{{{env}}}')
        self.emit()

    def caption(self, label, text, w, kind, floating):
        body = (r'\textbf{' + tex_text(label, w) + '} ' if label else '') + runs_tex(text, w, in_caption=True)
        if floating:
            return wrap(r'\caption*{' + body + '}')
        return wrap(r'\captionof*{' + kind + '}{' + body + '}')

    def figure(self, b):
        w = self.where(b)
        name = self.fig_name(b.path)
        width = f'{b.width:g}in'
        inc = rf'\includegraphics[width={width},height=0.75\textheight,keepaspectratio]{{figures/{name}}}'
        if b.inbox:
            self.open_box()
            self.emit(r'\par\smallskip')
            self.emit(r'{\centering' + inc.replace(f'width={width}', rf'width={min(b.width, 6.0) / 6.5:.3f}\linewidth'))
            self.emit(r'\par}')
            self.emit(self.caption(b.label, b.caption, w, 'figure', floating=False))
            self.emit()
            return
        self.emit(r'\begin{figure}[!htbp]')
        self.emit(r'\centering')
        self.emit(inc)
        self.emit(self.caption(b.label, b.caption, w, 'figure', floating=True))
        self.emit(r'\end{figure}')
        self.emit()

    def table(self, b):
        w = self.where(b)
        cols = []
        for frac, al in zip(b.widths, b.aligns):
            align = {'l': r'\raggedright', 'c': r'\centering', 'r': r'\raggedleft'}[al]
            cols.append(rf'>{{{align}\arraybackslash}}p{{\dimexpr {frac:.4f}\linewidth-2\tabcolsep\relax}}')
        size = r'\scriptsize' if b.small else r'\footnotesize'

        def row(cells, header=False):
            out = []
            for c in cells:
                t = runs_tex(c, w)
                if header and t:
                    t = r'\textbf{' + t + '}'
                out.append(guard(t))
            return ' & '.join(out) + r' \\'

        body = [r'\toprule', row(b.header, header=True), r'\midrule']
        for k, r in enumerate(b.rows):
            body.append(row(r))
            if k < len(b.rows) - 1:
                body.append(r'\rowrule')
        body.append(r'\bottomrule')

        if b.inbox:
            self.open_box()
            self.emit(r'\par\smallskip')
            self.emit(self.caption(b.label, b.caption, w, 'table', floating=False))
            self.emit('{' + size)
        else:
            self.emit(r'\begin{table}[!htbp]')
            self.emit(r'\centering')
            self.emit(self.caption(b.label, b.caption, w, 'table', floating=True))
            self.emit(size)
        self.emit(r'\begin{tabular}{' + ''.join('\n  ' + c for c in cols) + '\n}')
        for line in body:
            self.emit(line)
        self.emit(r'\end{tabular}')
        if b.inbox:
            self.emit(r'\par}')
        else:
            self.emit(r'\end{table}')
        self.emit()

    def pagebreak(self, b):
        if b.inbox:
            print(f'md2tex: {self.where(b)}: <!-- pagebreak --> inside a box is ignored', file=sys.stderr)
            return
        self.emit(r'\clearpage')
        self.emit()

    def render(self):
        for b in self.doc.blocks:
            self.close_groups(b)
            if isinstance(b, md.Heading):
                self.heading(b)
            elif isinstance(b, md.Para):
                self.para(b)
            elif isinstance(b, md.ListBlock):
                self.listing(b)
            elif isinstance(b, md.Table):
                self.table(b)
            elif isinstance(b, md.Figure):
                self.figure(b)
            elif isinstance(b, md.PageBreak):
                self.pagebreak(b)
        self.close_groups(None)


# ------------------------------------------------------------------------------------------ template bits
def template_bits(template):
    """Cover texts and the two images from Repport.docx (opened read only)."""
    d = docx.Document(str(template))
    texts = [p.text.strip() for p in d.paragraphs]
    try:
        k = texts.index('FINAL PROJECT')
    except ValueError:
        sys.exit('md2tex: the template does not look like Repport.docx (no FINAL PROJECT line)')
    course = next(t for t in reversed(texts[:k]) if t)
    professor = next((t for t in texts if t.startswith('Professor:')), 'Professor:')
    frog = logo = None
    with zipfile.ZipFile(template) as z:
        rels = z.read('word/_rels/header1.xml.rels').decode('utf-8')
        m = re.search(r'Target="(media/[^"]+)"', rels)
        if m:
            frog = z.read('word/' + m.group(1))
        rels = z.read('word/_rels/document.xml.rels').decode('utf-8')
        m = re.search(r'Type="[^"]+/image" Target="(media/[^"]+)"', rels) or \
            re.search(r'Target="(media/[^"]+)"[^>]*Type="[^"]+/image"', rels)
        if m:
            logo = z.read('word/' + m.group(1))
    if frog is None or logo is None:
        sys.exit('md2tex: could not find the frog (header) and logo (cover) images in the template')
    return course, 'FINAL PROJECT', professor, frog, logo


def save_frog(data, path):
    im = Image.open(io.BytesIO(data)).convert('RGBA')
    if im.width > 600:
        im = im.resize((600, round(im.height * 600 / im.width)), Image.LANCZOS)
    im.save(path, optimize=True)


def save_logo(data, path):
    im = Image.open(io.BytesIO(data)).convert('RGBA')
    box = im.getchannel('A').getbbox() or (0, 0, im.width, im.height)
    im = im.crop(box)
    bg = Image.new('RGB', im.size, (255, 255, 255))
    bg.paste(im, mask=im.getchannel('A'))
    bg.save(path, optimize=True)


# ------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('src', help='the Markdown source (.md)')
    ap.add_argument('outdir', help='folder to write main.tex and figures/ into (OUTDIR.zip is written next to it)')
    ap.add_argument('--title', required=True, help='the cover title, e.g. "Final Report"')
    ap.add_argument('--date', required=True, help='the cover date, e.g. "November 24, 2026"')
    ap.add_argument('--students', default=DEFAULT_STUDENTS,
                    help='the cover students line; [[...]] is highlighted (default: %(default)s)')
    ap.add_argument('--template', default=str(DEFAULT_TEMPLATE), help='Repport.docx, read for the cover and images')
    a = ap.parse_args()

    src, outdir, template = Path(a.src), Path(a.outdir).resolve(), Path(a.template)
    if not template.is_file():
        sys.exit(f'md2tex: template not found: {template}')
    try:
        doc = md.parse(src)
        course, project, professor, frog, logo = template_bits(template)
        wr = TexWriter(doc, outdir)
        wr.render()
        students = runs_tex(a.students, '--students', in_heading=True)
        # the Word line has two spaces on each side of the middle dot: keep that room
        students = re.sub(r'\s*\$\\cdot\$\s*', lambda m: r'\enskip$\cdot$\enskip ', students)
        cover = fill(COVER, {
            'COURSE': tex_text(course, 'cover'), 'PROJECT': tex_text(project, 'cover'),
            'TITLE': runs_tex(a.title, '--title', in_heading=True), 'PROFESSOR': tex_text(professor, 'cover'),
            'STUDENTS': students, 'DATE': runs_tex(a.date, '--date', in_heading=True),
        })
        pre = fill(PREAMBLE, {
            'SOURCE': tex_text(src.name, 'name'), 'FROG': FROG_FILE, 'LOGO': LOGO_FILE,
            'PDFTITLE': tex_plain(f'{course.split(":")[0]}: {md.plain(a.title)}', '--title'),
        })
    except (md.MdError, TexError) as e:
        sys.exit(f'md2tex: {e}')

    tex = pre + cover + '\n' + '\n'.join(wr.lines).rstrip() + '\n\n\\end{document}\n'
    tex = re.sub(r'\n{3,}', '\n\n', tex)

    # write the project
    if outdir.exists():
        for p in [outdir / 'main.tex', outdir / 'figures']:
            if p.is_dir():
                shutil.rmtree(p)
            elif p.exists():
                p.unlink()
    figdir = outdir / 'figures'
    figdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'main.tex').write_text(tex, encoding='utf-8', newline='\n')
    for path, name in wr.figures.items():
        shutil.copyfile(path, figdir / name)
    save_frog(frog, figdir / FROG_FILE)
    save_logo(logo, figdir / LOGO_FILE)

    zpath = outdir.with_name(outdir.name + '.zip')
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(outdir / 'main.tex', 'main.tex')
        for f in sorted(figdir.iterdir()):
            z.write(f, f'figures/{f.name}')
    print('wrote', outdir / 'main.tex')
    print(f'copied {len(wr.figures) + 2} images into', figdir)
    print('wrote', zpath)


if __name__ == '__main__':
    main()
