"""Strict checker for the LaTeX project written by md2tex.py (no TeX compiler is needed).

    py check_tex.py OUTDIR [--main main.tex] [--quiet]

Checks OUTDIR/main.tex for what would make pdfLaTeX (Overleaf, TeX Live 2024+) stop or print wrong text:
  - characters outside the allow-list (ASCII, plus accented Latin letters that utf8 inputenc + T1 handle)
  - balanced braces, $...$ and [ ] options; matching \\begin/\\end; nothing after \\end{document}
  - unescaped specials in text: & outside tables, # outside definitions, _ and ^ outside math,
    a % that would swallow text, math-only commands outside math, blank lines inside arguments
  - only allow-listed packages, with known options; option clashes; hyperref last; one font setup
  - every command and environment is known (LaTeX, a loaded package, or defined in the file)
  - \\newcommand of an existing name, \\renewcommand of a missing one, \\setlength of an unknown length
  - colours are defined; page styles exist; \\item only in lists; \\caption only in floats; no float in a box;
    table rows have no more cells than columns; table rules only at the start of a row; \\\\ never starts
    a paragraph and is never followed by a [ by accident
  - every \\includegraphics file exists (png/jpg/pdf, readable, safe file name); every \\ref has a \\label;
    labels are unique; OUTDIR.zip (if present) holds the same files
Prints every problem with its line and exits 1 if there is any error (warnings alone exit 0).
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path

# ===================================================================================== allow-lists
LATIN = set(chr(c) for c in range(0xC0, 0x100)) - {'×', '÷'}
LATIN |= set('ĂăĄąĆćČčĎďĐđĘęĚěĞğİıĹĺĽľŁłŃńŇňŊŋŐőŒœŔŕŘřŚśŞşŠšŢţŤťŮůŰűŸŹźŻżŽž')

CLASSES = {'article': {'10pt', '11pt', '12pt', 'letterpaper', 'a4paper', 'oneside', 'twoside', 'onecolumn',
                       'twocolumn', 'titlepage', 'notitlepage', 'final', 'draft', 'fleqn', 'leqno'}}

ANY = None   # any key
PACKAGES = {
    'inputenc': {'utf8'},
    'fontenc': {'T1', 'OT1', 'LY1', 'TS1'},
    'newtxtext': {'osf', 'lining', 'tabular', 'proportional', 'scaled', 'scale', 'sups', 'helvratio',
                  'tighter', 'looser', 'p', 'defaultsups', 'largesc', 'nofontinfo', 'theoremfont',
                  'trueslanted', 'thrm'},
    'newtxmath': {'varg', 'cmintegrals', 'uprightGreek', 'slantedGreek', 'vvarbb', 'smallerops',
                  'nosymbolsc', 'bigdelims', 'varbb', 'noamssymbols', 'libertine', 'nofontinfo', 'subscriptcorrection'},
    'lmodern': set(),
    'geometry': {'letterpaper', 'a4paper', 'margin', 'left', 'right', 'top', 'bottom', 'hmargin', 'vmargin',
                 'headheight', 'headsep', 'footskip', 'includehead', 'includefoot', 'includeheadfoot',
                 'textwidth', 'textheight', 'body', 'total', 'lmargin', 'rmargin', 'tmargin', 'bmargin',
                 'inner', 'outer', 'paper', 'papersize', 'landscape', 'portrait', 'marginparwidth',
                 'marginparsep', 'heightrounded', 'showframe', 'twoside', 'bindingoffset', 'hscale', 'vscale',
                 'scale', 'nohead', 'nofoot', 'noheadfoot', 'centering', 'hcentering', 'vcentering',
                 'footnotesep', 'includemp', 'includeall', 'ignoreall', 'pass', 'verbose'},
    'graphicx': {'final', 'draft'},
    'booktabs': set(),
    'tabularx': set(),
    'array': set(),
    'xcolor': {'dvipsnames', 'svgnames', 'x11names', 'usenames', 'hyperref', 'rgb', 'cmyk', 'gray', 'HTML'},
    'hyperref': {'hidelinks', 'colorlinks', 'linkcolor', 'citecolor', 'urlcolor', 'filecolor', 'allcolors',
                 'pdftitle', 'pdfauthor', 'pdfsubject', 'pdfkeywords', 'pdfcreator', 'pdfproducer', 'pdflang',
                 'bookmarks', 'bookmarksopen', 'bookmarksopenlevel', 'bookmarksnumbered', 'pdfpagemode',
                 'pdfstartview', 'unicode', 'pdfencoding', 'breaklinks', 'hypertexnames', 'pdfusetitle',
                 'linktocpage', 'pdfborder', 'plainpages', 'pageanchor', 'naturalnames', 'psdextra',
                 'pdfdisplaydoctitle', 'final', 'draft', 'hyperfootnotes', 'linktoc'},
    'caption': {'font', 'labelfont', 'textfont', 'justification', 'singlelinecheck', 'skip', 'position',
                'labelsep', 'format', 'margin', 'width', 'indention', 'hypcap', 'belowskip', 'aboveskip',
                'labelformat', 'list', 'size', 'parskip', 'hangindent', 'name', 'type', 'listformat'},
    'enumitem': {'shortlabels', 'inline', 'loadonly', 'ignoredisplayed', 'sizes'},
    'fancyhdr': {'headings', 'myheadings', 'nocheck', 'compatV3'},
    'titlesec': {'compact', 'raggedright', 'center', 'rm', 'sf', 'tt', 'md', 'bf', 'up', 'it', 'sl', 'sc',
                 'big', 'medium', 'small', 'tiny', 'pagestyles', 'newparttoc', 'clearempty', 'rigidchapters',
                 'calcwidth', 'nobottomtitles', 'nobottomtitles*', 'toctitles', 'newlinetospace',
                 'indentafter', 'noindentafter'},
    'microtype': {'protrusion', 'expansion', 'tracking', 'kerning', 'spacing', 'final', 'draft', 'babel',
                  'factor', 'stretch', 'shrink', 'step', 'selected', 'auto', 'letterspace', 'verbose',
                  'config', 'disable', 'nopatch', 'unit', 'activate', 'deactivate', 'patch'},
}
# packages that other packages load for themselves (giving options to them later is an option clash)
IMPLICIT = {'tabularx': ['array']}
FONT_SETUPS = [{'newtxtext', 'newtxmath'}, {'lmodern'}]

# ===================================================================================== commands
# command -> package that defines it (None = LaTeX kernel / TeX primitive)
K = None
KNOWN = {}


def _add(pkg, names):
    for n in names.split():
        KNOWN[n] = pkg


_add(K, '''documentclass usepackage RequirePackage newcommand* renewcommand* providecommand* begin end par noindent indent newline linebreak nolinebreak
pagebreak nopagebreak newpage clearpage cleardoublepage vspace vspace* hspace hspace* vfill hfill hfil vfil
smallskip medskip bigskip quad qquad enskip enspace thinspace negthinspace relax centering raggedright raggedleft
textbf textit texttt textsc textsf textrm textup textmd textsl textnormal emph underline mbox makebox fbox framebox
parbox raisebox rule strut textwidth linewidth textheight columnwidth paperwidth paperheight baselineskip parindent
parskip fboxsep fboxrule tabcolsep arraystretch arrayrulewidth item label ref pageref caption footnote section
section* subsection subsection* subsubsection subsubsection* paragraph subparagraph title author date maketitle
today thepage thesection thesubsection appendix setlength addtolength settowidth settoheight newlength newcommand
renewcommand providecommand DeclareRobustCommand newenvironment renewenvironment newsavebox sbox savebox usebox
newcounter setcounter addtocounter stepcounter refstepcounter value arabic roman Roman alph Alph fnsymbol
selectfont fontsize normalfont bfseries itshape mdseries upshape slshape scshape rmfamily sffamily ttfamily tiny
scriptsize footnotesize small normalsize large Large LARGE huge Huge ldots dots textbullet textbackslash textless
textgreater textbar textquotedbl textasciitilde textasciicircum textquoteleft textquoteright textquotedblleft
textquotedblright quotedblbase guillemotleft guillemotright guilsinglleft guilsinglright textexclamdown
textquestiondown pounds S P dag ddag textcopyright textregistered texttrademark textsuperscript textsubscript
dimexpr numexpr glueexpr ht dp wd strutbox hangindent hangafter leaders cleaders xleaders hrule vrule hskip vskip
kern penalty widowpenalty clubpenalty displaywidowpenalty emergencystretch tolerance pretolerance hbadness
topfraction bottomfraction textfraction floatpagefraction dblfloatpagefraction dbltopfraction textfloatsep
floatsep intextsep dbltextfloatsep dblfloatsep topnumber bottomnumber totalnumber i j l L o O ae AE oe OE aa AA
ss u v H c d b t k r normalcolor nobreak allowbreak hbox vbox vtop setbox box copy unskip ignorespaces
protect thispagestyle pagestyle markboth markright null empty space nobreakspace smallskipamount medskipamount
bigskipamount topsep partopsep itemsep parsep leftmargin rightmargin listparindent itemindent labelwidth labelsep
headheight headsep footskip topmargin oddsidemargin evensidemargin marginparwidth marginparsep columnsep
footnotesep abovecaptionskip belowcaptionskip unitlength lineskip lineskiplimit normallineskip hsize vsize
jot baselinestretch familydefault rmdefault sfdefault ttdefault itdefault bfdefault mathrm mathbf mathit mathsf
mathtt mathcal mathnormal frac sqrt left right big Big bigg Bigg ensuremath textvisiblespace textperiodcentered
textendash textemdash textellipsis TeX LaTeX LaTeXe hyphenation sloppy fussy footnotemark footnotetext
cleardoublepage enlargethispage samepage nopagebreak clubpenalties interlinepenalty
labelitemi labelitemii labelenumi theenumi''')
MATH_ONLY = set('''alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa lambda mu nu xi pi
varpi rho varrho sigma varsigma tau upsilon phi varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Upsilon
Phi Psi Omega geq leq ge le neq ne approx equiv sim simeq ll gg times div pm mp in notin ni infty sum prod surd
sqrt propto partial nabla forall exists emptyset varnothing cap cup subset subseteq supset supseteq wedge vee neg
lnot rightarrow leftarrow leftrightarrow Rightarrow Leftarrow Leftrightarrow longrightarrow uparrow downarrow
mapsto to gets cdot ast star circ bullet prime frac langle rangle mid int oint cong setminus oplus otimes
mathrm mathbf mathit mathsf mathtt mathcal mathnormal left right big Big bigg Bigg cdots ldotp vdots ddots
lfloor rfloor lceil rceil vert Vert hat bar tilde vec dot ddot overline underbrace overbrace'''.split())
for _m in MATH_ONLY:
    KNOWN.setdefault(_m, K)
_add('graphicx', 'includegraphics includegraphics* graphicspath rotatebox scalebox resizebox reflectbox')
_add('xcolor', 'color textcolor colorbox fcolorbox definecolor colorlet pagecolor')
_add('booktabs', 'toprule midrule bottomrule cmidrule addlinespace specialrule aboverulesep belowrulesep '
                 'heavyrulewidth lightrulewidth cmidrulewidth')
_add('array', 'arraybackslash newcolumntype extrarowheight firsthline lasthline')
_add('tabularx', 'tabularxcolumn')
_add('caption', 'captionsetup captionof captionof* caption* DeclareCaptionFormat DeclareCaptionLabelFormat')
_add('enumitem', 'setlist setlistdepth newlist')
_add('fancyhdr', 'fancyhead fancyfoot fancyhf fancypagestyle headrulewidth footrulewidth fancyheadoffset '
                 'lhead chead rhead lfoot cfoot rfoot')
_add('titlesec', 'titleformat titleformat* titlespacing titlespacing* titlerule titlelabel')
_add('hyperref', 'href url nolinkurl hypersetup texorpdfstring hyperref autoref phantomsection hyperlink '
                 'hypertarget')
_add('geometry', 'geometry newgeometry restoregeometry')
_add('microtype', 'microtypesetup textls lsstyle')

CONTROL_SYMBOLS = set('\\,;:! %&$#_{}\'`^"~=.-/@|[]()\n')

ENVS = {'document': K, 'figure': K, 'figure*': K, 'table': K, 'table*': K, 'center': K, 'flushleft': K,
        'flushright': K, 'itemize': K, 'enumerate': K, 'description': K, 'tabular': K, 'tabular*': K,
        'minipage': K, 'lrbox': K, 'quote': K, 'quotation': K, 'titlepage': K, 'abstract': K, 'list': K,
        'trivlist': K, 'math': K, 'displaymath': K, 'equation': K, 'array': K, 'tabularx': 'tabularx'}
LIST_ENVS = {'itemize', 'enumerate', 'description', 'list', 'trivlist'}
TABULAR_ENVS = {'tabular', 'tabular*', 'tabularx', 'array'}
FLOAT_ENVS = {'figure', 'figure*', 'table', 'table*'}
BOX_ENVS = {'minipage', 'lrbox'} | TABULAR_ENVS | FLOAT_ENVS
MATH_ENVS = {'math', 'displaymath', 'equation', 'array'}

RULES = {'toprule', 'midrule', 'bottomrule', 'cmidrule', 'specialrule', 'addlinespace', 'hline', 'cline'}

# argument signatures: o = optional [..], m = mandatory {..}; R = raw (not checked as text), D = definition body
SIG = {
    'textbf': 'm', 'textit': 'm', 'texttt': 'm', 'textsc': 'm', 'textsf': 'm', 'textrm': 'm', 'textup': 'm',
    'textmd': 'm', 'textsl': 'm', 'textnormal': 'm', 'emph': 'm', 'underline': 'm', 'mbox': 'm', 'fbox': 'm',
    'textsuperscript': 'm', 'textsubscript': 'm',
    'makebox': 'ooR', 'framebox': 'ooR', 'raisebox': 'RooR', 'parbox': 'oooRm', 'rule': 'oRR',
    'section': 'om', 'subsection': 'om', 'subsubsection': 'om', 'paragraph': 'om', 'subparagraph': 'om',
    'section*': 'm', 'subsection*': 'm', 'subsubsection*': 'm',
    'caption': 'om', 'caption*': 'm', 'captionof': 'RoM', 'captionof*': 'RM', 'footnote': 'om',
    'includegraphics': 'oR', 'includegraphics*': 'oR', 'graphicspath': 'R',
    'colorbox': 'oRm', 'fcolorbox': 'oRRm', 'textcolor': 'oRm', 'color': 'oR', 'pagecolor': 'oR',
    'definecolor': 'oRRR', 'colorlet': 'oRR',
    'hspace': 'R', 'hspace*': 'R', 'vspace': 'R', 'vspace*': 'R', 'setlength': 'RR', 'addtolength': 'RR',
    'settowidth': 'Rm', 'settoheight': 'Rm',
    'fontsize': 'RR', 'usepackage': 'oRo', 'RequirePackage': 'oRo', 'documentclass': 'oRo',
    'label': 'R', 'ref': 'R', 'pageref': 'R', 'autoref': 'R', 'hyperref': 'om',
    'newsavebox': 'R', 'newlength': 'R', 'usebox': 'R', 'sbox': 'Rm', 'savebox': 'RooM',
    'newcounter': 'Ro', 'setcounter': 'RR', 'addtocounter': 'RR', 'stepcounter': 'R', 'refstepcounter': 'R',
    'arabic': 'R', 'roman': 'R', 'Roman': 'R', 'alph': 'R', 'Alph': 'R', 'value': 'R',
    'thispagestyle': 'R', 'pagestyle': 'R',
    'fancyhead': 'om', 'fancyfoot': 'om', 'fancyhf': 'o', 'fancypagestyle': 'RD', 'fancyheadoffset': 'oR',
    'titleformat': 'RoDDDDo', 'titleformat*': 'RD', 'titlespacing': 'RRRRo', 'titlespacing*': 'RRRRo',
    'titlerule': 'o',
    'setlist': 'oR', 'captionsetup': 'oR', 'hypersetup': 'R', 'geometry': 'R',
    'texorpdfstring': 'mm', 'url': 'R', 'nolinkurl': 'R', 'href': 'Rm',
    'midrule': 'o', 'toprule': 'o', 'bottomrule': 'o', 'specialrule': 'RRR', 'addlinespace': 'o',
    'newcolumntype': 'RoD', 'frac': 'mm', 'sqrt': 'om', 'mathrm': 'm', 'mathbf': 'm', 'mathit': 'm',
    'mathsf': 'm', 'mathtt': 'm', 'mathcal': 'm', 'ensuremath': 'm', 'hyphenation': 'R',
    'markboth': 'mm', 'markright': 'm', 'enlargethispage': 'R', 'title': 'om', 'author': 'm', 'date': 'm',
    'footnotetext': 'om', 'end': 'R', 'microtypesetup': 'R',
    'rotatebox': 'oRm', 'scalebox': 'RoM', 'resizebox': 'RRm',
}
# arguments that may hold paragraphs (blank lines)
LONG_CMDS = {'parbox', 'fancypagestyle', 'newcommand', 'renewcommand', 'DeclareRobustCommand', 'providecommand',
             'newenvironment', 'renewenvironment', 'footnote', 'footnotetext'}
STARRED = {'section', 'subsection', 'subsubsection', 'caption', 'captionof', 'hspace', 'vspace', 'includegraphics',
           'titleformat', 'titlespacing', 'newcommand', 'renewcommand', 'providecommand', '\\'}

BASE_COLORS = {'black', 'white', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'gray', 'darkgray',
               'lightgray', 'brown', 'lime', 'olive', 'orange', 'pink', 'purple', 'teal', 'violet', '.'}
LENGTHS = set('''parindent parskip tabcolsep fboxsep fboxrule textfloatsep floatsep intextsep emergencystretch
arrayrulewidth baselineskip columnsep headheight headsep footskip textwidth textheight linewidth topsep itemsep
parsep leftmargin abovecaptionskip belowcaptionskip aboverulesep belowrulesep heavyrulewidth lightrulewidth
cmidrulewidth unitlength hsize jot labelsep labelwidth marginparwidth oddsidemargin evensidemargin topmargin
footnotesep smallskipamount medskipamount bigskipamount partopsep rightmargin listparindent itemindent lineskip
normallineskip extrarowheight dbltextfloatsep dblfloatsep columnwidth paperwidth paperheight hangindent'''.split())
PAGESTYLES = {'empty', 'plain', 'headings', 'myheadings'}
UNIT_WORDS = {'pt', 'in', 'em', 'ex', 'cm', 'mm', 'bp', 'sp', 'pc', 'dd', 'cc', 'mu', 'plus', 'minus', 'fil',
              'fill', 'filll', 'true', 'height', 'depth', 'width', 'to', 'spread'}


# ===================================================================================== tokenizer
class Tok:
    __slots__ = ('kind', 'text', 'pos', 'line', 'col')

    def __init__(self, kind, text, pos, line, col):
        self.kind, self.text, self.pos, self.line, self.col = kind, text, pos, line, col

    def __repr__(self):
        return f'{self.kind}:{self.text!r}@{self.line}'


# A comment is replaced by \x01 plus spaces: like TeX, a commented line then neither ends a paragraph nor
# counts as blank, while "text%" followed by an empty line still does.
TOKEN_RE = re.compile(r'''
   (?P<cs>\\(?:[A-Za-z@]+|.|\n))
 | (?P<par>\n[ \t]*\n(?:[ \t]*\n)*)
 | (?P<ws>[ \t\x01]+|\n(?![ \t]*\n))
 | (?P<lb>\{) | (?P<rb>\})
 | (?P<math>\$\$?)
 | (?P<amp>&) | (?P<hash>\#) | (?P<sup>\^) | (?P<sub>_) | (?P<tilde>~)
 | (?P<lbr>\[) | (?P<rbr>\])
 | (?P<star>\*)
 | (?P<word>[A-Za-z]+)
 | (?P<other>.)
''', re.S | re.X)


def strip_comments(text):
    """Blank out comments (keeping positions) and return the comment positions."""
    out, comments = [], []
    pos = 0
    for line in text.split('\n'):
        i = 0
        cut = None
        while i < len(line):
            if line[i] == '\\':
                i += 2
                continue
            if line[i] == '%':
                cut = i
                break
            i += 1
        if cut is None:
            out.append(line)
        else:
            comments.append((pos + cut, line[:cut], line[cut + 1:]))
            out.append(line[:cut] + '\x01' + ' ' * (len(line) - cut - 1))
        pos += len(line) + 1
    return '\n'.join(out), comments


def tokenize(masked):
    toks = []
    line_starts = [0] + [m.end() for m in re.finditer('\n', masked)]
    import bisect
    for m in TOKEN_RE.finditer(masked):
        pos = m.start()
        ln = bisect.bisect_right(line_starts, pos)
        col = pos - line_starts[ln - 1] + 1
        toks.append(Tok(m.lastgroup, m.group(), pos, ln, col))
    return toks


# ===================================================================================== checker
class Checker:
    def __init__(self, outdir, main):
        self.outdir = outdir
        self.path = outdir / main
        self.errors = []
        self.warnings = []

    def err(self, line, msg):
        self.errors.append((line, msg))

    def warn(self, line, msg):
        self.warnings.append((line, msg))

    # ------------------------------------------------------------------ helpers
    def find_close(self, toks, i, open_kind, close_kind):
        """toks[i] is an opener; return the index of its matching closer (braces nest inside [..])."""
        depth = 0
        bdepth = 0
        for j in range(i, len(toks)):
            k = toks[j].kind
            if open_kind == 'lb':
                if k == 'lb':
                    depth += 1
                elif k == 'rb':
                    depth -= 1
                    if depth == 0:
                        return j
            else:
                if k == 'lb':
                    bdepth += 1
                elif k == 'rb':
                    bdepth -= 1
                elif k == 'lbr' and bdepth == 0:
                    depth += 1
                elif k == 'rbr' and bdepth == 0:
                    depth -= 1
                    if depth == 0:
                        return j
        return None

    def read_args(self, toks, i, sig, name, line):
        """Read the arguments after toks[i-1] (the command). Returns ([(letter, start, end) or None], next i)."""
        args = []
        for letter in sig:
            j = i
            while j < len(toks) and toks[j].kind == 'ws':
                j += 1
            if j >= len(toks):
                if letter != 'o':
                    self.err(line, f'\\{name}: missing argument at the end of the file')
                args.append(None)
                continue
            t = toks[j]
            if letter == 'o':
                if t.kind == 'lbr':
                    k = self.find_close(toks, j, 'lbr', 'rbr')
                    if k is None:
                        self.err(t.line, f'\\{name}: [ option is never closed with ]')
                        return args, len(toks)
                    args.append(('o', j + 1, k))
                    i = k + 1
                else:
                    args.append(None)
                continue
            if t.kind == 'lb':
                k = self.find_close(toks, j, 'lb', 'rb')
                if k is None:
                    self.err(t.line, f'\\{name}: {{ argument is never closed')
                    return args, len(toks)
                args.append((letter, j + 1, k))
                i = k + 1
            else:
                self.err(t.line, f'\\{name}: expected a {{...}} argument here, found {t.text!r}')
                args.append(None)
        return args, i

    def raw(self, toks, a):
        if a is None:
            return ''
        _, s, e = a
        if s >= e:
            return ''
        return self.masked[toks[s].pos:toks[e].pos].replace('\x01', '')

    # ------------------------------------------------------------------ main
    def run(self):
        if not self.path.is_file():
            self.err(0, f'{self.path} does not exist')
            return
        data = self.path.read_bytes()
        if data.startswith(b'\xef\xbb\xbf'):
            self.err(1, 'the file starts with a byte-order mark; save it as UTF-8 without BOM')
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError as e:
            self.err(0, f'not valid UTF-8: {e}')
            return
        if '\r' in text:
            self.warn(0, 'the file has Windows line endings (CR); harmless but unexpected')
            text = text.replace('\r\n', '\n').replace('\r', '\n')
        self.text = text
        self.check_chars(text)
        self.masked, self.comments = strip_comments(text)
        self.check_comments()
        self.toks = tokenize(self.masked)
        self.walk()
        self.check_files()
        self.check_zip()

    def check_chars(self, text):
        for ln, line in enumerate(text.split('\n'), 1):
            for col, ch in enumerate(line, 1):
                o = ord(ch)
                if 32 <= o < 127 or ch == '\t':
                    continue
                if ch in LATIN:
                    self.has_latin = True
                    continue
                self.err(ln, f'column {col}: character {ch!r} (U+{o:04X}) is not allowed; '
                             f'pdfLaTeX needs a LaTeX form for it')

    def check_comments(self):
        for pos, before, after in self.comments:
            ln = self.text.count('\n', 0, pos) + 1
            if not before.strip() or not after.strip():
                continue                        # a whole-line comment, or a % ending the line
            if before[-1:].isspace() and after[:1] == ' ':
                continue                        # "  % a comment"
            self.err(ln, f'an unescaped % hides the rest of the line ({(before[-12:] + "%" + after[:12])!r}); '
                         f'write \\% for a percent sign')

    # ------------------------------------------------------------------ walk
    def walk(self):
        toks = self.toks
        self.user_cmds = {}            # name -> signature
        self.rule_macros = set()
        self.user_envs = {}            # name -> boxy?
        self.lengths = set(LENGTHS)
        self.colors = set(BASE_COLORS)
        self.any_colors = False
        self.styles = set(PAGESTYLES)
        self.labels = {}
        self.refs = []
        self.graphics = []             # (line, path)
        self.packages = []             # (name, options set, line)
        self.has_latin = getattr(self, 'has_latin', False)
        cls = None
        in_doc = False
        ended = False
        seen_docclass = False

        braces = []                    # frames: dict(kind='arg'|'group', cmd, long, line)
        envs = []                      # frames: dict(name, line, depth, cols, amps, row_start)
        math = None                    # None | ('$', line)
        para_start = True
        raw_skip = {}                  # token index -> index to jump to (exclusive)
        arg_open = {}                  # token index of '{' -> (cmd, long)

        def in_env(names):
            return any(e['name'] in names for e in envs)

        def innermost_tabular():
            for e in reversed(envs):
                if e['name'] in TABULAR_ENVS:
                    return e
                if e['name'] in ('minipage', 'lrbox'):
                    return None
            return None

        def tab_level(tab):
            return tab is not None and len(braces) == tab['depth']

        i = 0
        n = len(toks)
        while i < n:
            if i in raw_skip:
                i = raw_skip.pop(i)
                continue
            t = toks[i]
            k = t.kind
            tab = innermost_tabular()

            if ended:
                if k not in ('ws', 'par'):
                    self.err(t.line, f'text after \\end{{document}}: {t.text!r}')
                    break
                i += 1
                continue

            # ---------------------------------------------------------- whitespace and paragraphs
            if k == 'ws':
                i += 1
                continue
            if k == 'par':
                for f in braces:
                    if f['kind'] == 'arg' and not f['long']:
                        self.err(t.line, f'blank line inside the argument of \\{f["cmd"]} (opened on line '
                                         f'{f["line"]}): "Paragraph ended before ... was complete"')
                        break
                if math:
                    self.err(t.line, f'blank line inside math (opened on line {math[1]}): missing $')
                    math = None
                if tab is not None:
                    self.err(t.line, 'blank line inside a table')
                para_start = True
                i += 1
                continue

            # ---------------------------------------------------------- preamble text
            if not in_doc and not braces and k in ('word', 'other', 'star', 'lbr', 'rbr', 'amp', 'tilde', 'math'):
                ok = (k == 'word' and t.text in UNIT_WORDS) or (k == 'other' and t.text in '0123456789=.-+,')
                if not ok:
                    self.err(t.line, f'text in the preamble (before \\begin{{document}}): {t.text!r}')
                i += 1
                continue

            # ---------------------------------------------------------- braces
            if k == 'lb':
                cmd, long_ = arg_open.pop(i, (None, False))
                braces.append({'kind': 'arg' if cmd else 'group', 'cmd': cmd, 'long': long_, 'line': t.line})
                i += 1
                continue
            if k == 'rb':
                if not braces:
                    self.err(t.line, 'a } closes nothing (unbalanced braces)')
                else:
                    braces.pop()
                    if tab is not None and len(braces) < tab['depth']:
                        self.err(t.line, f'a }} closes a group opened outside the table that starts on line '
                                         f'{tab["line"]}')
                i += 1
                continue

            # ---------------------------------------------------------- math
            if k == 'math':
                if t.text == '$$':
                    self.err(t.line, '$$ display math: use \\[ ... \\] (or check for two inline formulas in a row)')
                    i += 1
                    continue
                if math:
                    if math[0] != '$':
                        self.err(t.line, f'$ closes math opened with {math[0]} on line {math[1]}')
                    math = None
                else:
                    if not in_doc:
                        self.err(t.line, '$ in the preamble')
                    math = ('$', t.line, len(braces))
                para_start = False
                i += 1
                continue

            # ---------------------------------------------------------- specials
            if k == 'amp':
                if math and not in_env({'array'}):
                    self.err(t.line, f'& inside math opened on line {math[1]} (a $ is probably missing)')
                elif tab is None:
                    self.err(t.line, 'unescaped & outside a table: write \\&')
                elif not tab_level(tab):
                    self.err(t.line, '& inside a {...} group in a table cell')
                else:
                    tab['amps'] += 1
                    tab['row_start'] = False
                i += 1
                continue
            if k == 'hash':
                inside_def = any(f['kind'] == 'arg' and f['long'] for f in braces)
                nxt = toks[i + 1] if i + 1 < n else None
                if not inside_def or nxt is None or not re.match(r'[1-9]', nxt.text):
                    self.err(t.line, 'unescaped # : write \\#')
                i += 1
                continue
            if k in ('sup', 'sub'):
                if not math:
                    fix = '\\textasciicircum{}' if t.text == '^' else '\\_'
                    self.err(t.line, f'unescaped {t.text} outside math: write {fix}')
                i += 1
                continue
            if k in ('word', 'other', 'tilde', 'star', 'lbr', 'rbr'):
                if not in_doc:
                    i += 1
                    continue
                if k == 'other' and t.text == '"' and not math:
                    self.warn(t.line, 'straight double quote " in text (prints as a straight mark); use `` and \'\'')
                para_start = False
                if tab is not None and tab_level(tab):
                    tab['row_start'] = False
                i += 1
                continue

            # ---------------------------------------------------------- control sequences
            if k != 'cs':
                i += 1
                continue
            name = t.text[1:]
            if name == '\n':
                name = ' '
            i += 1
            if (name in STARRED or name.rstrip('*') in self.user_cmds) and i < n and toks[i].kind == 'star':
                name += '*'
                i += 1
            line = t.line

            # control symbols
            if len(name) == 1 or name in ('\\*',) or name == '\\':
                if name in ('\\', '\\*'):
                    j = i
                    while j < n and toks[j].kind == 'ws':
                        j += 1
                    if tab is not None and tab_level(tab):
                        cols = tab['cols']
                        if cols and tab['amps'] > cols - 1:
                            self.err(line, f'this table row has {tab["amps"] + 1} cells but the table has {cols} '
                                           f'columns ("Extra alignment tab")')
                        tab['amps'] = 0
                        if j < n and toks[j].kind == 'lbr':
                            k2 = self.find_close(toks, j, 'lbr', 'rbr')
                            opt = self.raw(toks, ('o', j + 1, k2)) if k2 else ''
                            if not re.fullmatch(r'\s*-?[\d.]+\s*(pt|em|ex|in|cm|mm|bp)\s*', opt):
                                self.err(toks[j].line, '\\\\ followed by [ : the [ is read as a spacing option; '
                                                       'put {} before it')
                            i = (k2 or j) + 1
                        tab['row_start'] = True
                        continue
                    if para_start and in_doc:
                        self.err(line, '\\\\ at the start of a paragraph: "There\'s no line here to end"')
                    if j < n and toks[j].kind == 'lbr':
                        self.warn(toks[j].line, '\\\\ followed by [ is read as a spacing option')
                    continue
                if name not in CONTROL_SYMBOLS:
                    self.err(line, f'unknown control symbol \\{name}')
                if name in ('(', '['):
                    if math:
                        self.err(line, f'\\{name} inside math')
                    math = ('\\' + name, line, len(braces))
                elif name in (')', ']'):
                    if not math or math[0] != '\\' + {')': '(', ']': '['}[name]:
                        self.err(line, f'\\{name} closes no math')
                    math = None
                if in_doc and name not in (' ', '\n', ',', ';', ':', '!', '-', '/', '@'):
                    para_start = False
                if tab is not None and tab_level(tab):
                    tab['row_start'] = False
                continue

            base = name
            pkg_known = base in KNOWN or base in self.user_cmds
            if not pkg_known:
                self.err(line, f'unknown command \\{name} (not LaTeX, not an allowed package, not defined here)')
                continue
            pkg = KNOWN.get(base)
            if pkg and base not in self.user_cmds and pkg not in [p[0] for p in self.packages]:
                self.err(line, f'\\{name} needs \\usepackage{{{pkg}}}')
            if base in MATH_ONLY and not math and base not in ('mathrm',):
                if not any(f['kind'] == 'arg' and f['long'] for f in braces):
                    self.err(line, f'\\{name} works only in math: wrap it in $...$ ("Missing $ inserted")')

            # -------------------------------------------- preamble-only and structure
            if base == 'documentclass':
                args, i = self.read_args(toks, i, 'oRo', name, line)
                if seen_docclass:
                    self.err(line, 'a second \\documentclass')
                seen_docclass = True
                cls = self.raw(toks, args[1]).strip()
                opts = self.split_opts(self.raw(toks, args[0]))
                if cls not in CLASSES:
                    self.err(line, f'document class {cls!r} is not allowed (use article)')
                else:
                    for o in opts:
                        if o not in CLASSES[cls]:
                            self.err(line, f'unknown \\documentclass option {o!r}')
                continue
            if not seen_docclass:
                self.err(line, f'\\{name} before \\documentclass')
                seen_docclass = True
            if base in ('usepackage', 'RequirePackage'):
                args, i = self.read_args(toks, i, 'oRo', name, line)
                if in_doc:
                    self.err(line, '\\usepackage after \\begin{document}')
                self.use_package(self.raw(toks, args[0]), self.raw(toks, args[1]), line)
                continue

            # -------------------------------------------- definitions
            if base in ('newcommand', 'renewcommand', 'providecommand', 'DeclareRobustCommand',
                        'newcommand*', 'renewcommand*', 'providecommand*'):
                args, i = self.read_args(toks, i, 'Roo' + 'D', name, line)
                target = self.raw(toks, args[0]).strip()
                if not re.fullmatch(r'\\[A-Za-z@]+', target):
                    self.err(line, f'\\{name}: the first argument must be one command name, got {target!r}')
                    continue
                tname = target[1:]
                exists = tname in KNOWN or tname in self.user_cmds
                if base.startswith('newcommand') and exists:
                    self.err(line, f'\\newcommand{{{target}}}: {target} is already defined; use another name')
                if base.startswith('renewcommand') and not exists:
                    self.err(line, f'\\renewcommand{{{target}}}: {target} is not defined; use \\newcommand')
                nargs = self.raw(toks, args[1]).strip() if args[1] else '0'
                if not re.fullmatch(r'[0-9]', nargs or '0'):
                    self.err(line, f'{target}: the number of arguments must be 0 to 9')
                    nargs = '0'
                nargs = int(nargs or 0)
                body = self.raw(toks, args[3])
                self.check_def_body(body, line, nargs)
                sig = ('o' if args[2] else '') + 'm' * (nargs - (1 if args[2] else 0))
                if tname not in KNOWN:
                    self.user_cmds[tname] = sig
                    if re.match(r'\s*\\(' + '|'.join(RULES) + r')\b', body):
                        self.rule_macros.add(tname)
                continue
            if base in ('newenvironment', 'renewenvironment'):
                args, i = self.read_args(toks, i, 'RooDD', name, line)
                ename = self.raw(toks, args[0]).strip()
                exists = ename in ENVS or ename in self.user_envs
                if base == 'newenvironment' and exists:
                    self.err(line, f'\\newenvironment{{{ename}}}: already defined')
                if base == 'renewenvironment' and not exists:
                    self.err(line, f'\\renewenvironment{{{ename}}}: not defined')
                nargs = int(self.raw(toks, args[1]).strip() or 0) if args[1] else 0
                begin, end = self.raw(toks, args[3]), self.raw(toks, args[4])
                self.check_def_body(begin, line, nargs)
                self.check_def_body(end, line, 0)
                opened = re.findall(r'\\begin\{([^}]*)\}', begin)
                closed = re.findall(r'\\end\{([^}]*)\}', end)
                if sorted(opened) != sorted(closed):
                    self.err(line, f'environment {ename}: the begin code opens {opened} but the end code closes '
                                   f'{closed}')
                self.user_envs[ename] = bool(set(opened) & BOX_ENVS)
                continue
            if base in ('newsavebox', 'newlength'):
                args, i = self.read_args(toks, i, 'R', name, line)
                target = self.raw(toks, args[0]).strip()
                if not re.fullmatch(r'\\[A-Za-z@]+', target):
                    self.err(line, f'\\{name}: expected one command name, got {target!r}')
                    continue
                if target[1:] in KNOWN or target[1:] in self.user_cmds:
                    self.err(line, f'\\{name}{{{target}}}: {target} is already defined')
                self.user_cmds[target[1:]] = ''
                if base == 'newlength':
                    self.lengths.add(target[1:])
                continue
            if base == 'newcounter':
                args, i = self.read_args(toks, i, 'Ro', name, line)
                self.user_cmds['the' + self.raw(toks, args[0]).strip()] = ''
                continue
            if base == 'definecolor':
                args, i = self.read_args(toks, i, 'oRRR', name, line)
                cname, model, spec = (self.raw(toks, a).strip() for a in args[1:])
                self.check_color_def(cname, model, spec, line)
                self.colors.add(cname)
                continue
            if base == 'colorlet':
                args, i = self.read_args(toks, i, 'RR', name, line)
                self.check_color_use(self.raw(toks, args[1]).strip(), line)
                self.colors.add(self.raw(toks, args[0]).strip())
                continue
            if base == 'fancypagestyle':
                args, i = self.read_args(toks, i, 'RD', name, line)
                self.styles.add(self.raw(toks, args[0]).strip())
                self.check_def_body(self.raw(toks, args[1]), line, 0, allow_hash=False)
                continue
            if base in ('setlength', 'addtolength'):
                args, i = self.read_args(toks, i, 'RR', name, line)
                target = self.raw(toks, args[0]).strip()
                if not re.fullmatch(r'\\[A-Za-z@]+', target):
                    self.err(line, f'\\{name}: the first argument must be a length like \\parskip, got {target!r}')
                elif target[1:] not in self.lengths:
                    self.err(line, f'\\{name}{{{target}}}: {target} is not a known length')
                self.check_dimen(self.raw(toks, args[1]), line, name)
                continue
            if base in ('pagestyle', 'thispagestyle'):
                args, i = self.read_args(toks, i, 'R', name, line)
                st = self.raw(toks, args[0]).strip()
                if st not in self.styles and not (st == 'fancy' and self.loaded('fancyhdr')):
                    self.err(line, f'\\{name}{{{st}}}: unknown page style')
                continue
            if base in ('color', 'textcolor', 'colorbox', 'fcolorbox', 'pagecolor'):
                sig = SIG[base]
                args, i = self.read_args(toks, i, sig, name, line)
                for a in args:
                    if a and a[0] == 'R':
                        self.check_color_use(self.raw(toks, a).strip(), line)
                for a in args:
                    if a and a[0] == 'm':
                        arg_open[a[1] - 1] = (base, False)
                        i = min(i, a[1] - 1)
                if tab is not None and tab_level(tab):
                    tab['row_start'] = False
                para_start = False if in_doc else para_start
                continue
            if base in ('label',):
                args, i = self.read_args(toks, i, 'R', name, line)
                key = self.raw(toks, args[0]).strip()
                if key in self.labels:
                    self.err(line, f'\\label{{{key}}} is used twice (also on line {self.labels[key]})')
                self.labels[key] = line
                continue
            if base in ('ref', 'pageref', 'autoref'):
                args, i = self.read_args(toks, i, 'R', name, line)
                self.refs.append((line, self.raw(toks, args[0]).strip()))
                para_start = False
                continue
            if base in ('includegraphics', 'includegraphics*'):
                args, i = self.read_args(toks, i, 'oR', name, line)
                self.check_graphics_opts(self.raw(toks, args[0]), line)
                self.graphics.append((line, self.raw(toks, args[1]).strip()))
                para_start = False
                if tab is not None and tab_level(tab):
                    tab['row_start'] = False
                continue
            if base == 'hypersetup':
                args, i = self.read_args(toks, i, 'R', name, line)
                for o in self.split_opts(self.raw(toks, args[0])):
                    if o.split('=')[0].strip() not in PACKAGES['hyperref']:
                        self.err(line, f'\\hypersetup: unknown key {o!r}')
                continue
            if base in ('url', 'nolinkurl'):
                args, i = self.read_args(toks, i, 'R', name, line)
                u = self.raw(toks, args[0])
                if re.search(r'[\s{}\\%#]', u):
                    self.err(line, f'\\{name}{{{u}}}: spaces, braces, \\, % or # break \\url')
                if braces:
                    if any(f['kind'] == 'arg' for f in braces) and re.search(r'[%#~^]', u):
                        self.err(line, f'\\{name} inside another argument cannot hold % # ~ ^')
                para_start = False
                continue

            # -------------------------------------------- environments
            if base == 'begin':
                args, i = self.read_args(toks, i, 'R', name, line)
                ename = self.raw(toks, args[0]).strip()
                if ename == 'document':
                    if in_doc:
                        self.err(line, 'a second \\begin{document}')
                    if braces:
                        self.err(line, f'\\begin{{document}} inside an open {{ group (line {braces[-1]["line"]})')
                    in_doc = True
                    envs.append({'name': ename, 'line': line, 'depth': len(braces)})
                    para_start = True
                    continue
                if ename not in ENVS and ename not in self.user_envs:
                    self.err(line, f'unknown environment {ename!r}')
                    envs.append({'name': ename, 'line': line, 'depth': len(braces)})
                    continue
                pkg = ENVS.get(ename)
                if pkg and not self.loaded(pkg):
                    self.err(line, f'environment {ename} needs \\usepackage{{{pkg}}}')
                if not in_doc:
                    self.err(line, f'\\begin{{{ename}}} in the preamble')
                frame = {'name': ename, 'line': line, 'depth': len(braces)}
                boxy_parent = [e['name'] for e in envs if e['name'] in BOX_ENVS or self.user_envs.get(e['name'])]
                if ename in FLOAT_ENVS:
                    if boxy_parent:
                        self.err(line, f'a {ename} float inside {boxy_parent[-1]} ("Not in outer par mode")')
                    if math:
                        self.err(line, f'{ename} inside math')
                    j = i
                    while j < n and toks[j].kind == 'ws':
                        j += 1
                    if j < n and toks[j].kind == 'lbr':
                        k2 = self.find_close(toks, j, 'lbr', 'rbr')
                        spec = self.raw(toks, ('o', j + 1, k2))
                        if not re.fullmatch(r'[htbp!]+', spec.strip()):
                            self.err(line, f'\\begin{{{ename}}}[{spec}]: placement may use only h t b p !')
                        i = k2 + 1
                elif ename in ('tabular', 'array'):
                    args2, i = self.read_args(toks, i, 'oR', ename, line)
                    frame.update(self.table_frame(self.raw(toks, args2[1]), line))
                elif ename == 'tabular*' or ename == 'tabularx':
                    args2, i = self.read_args(toks, i, 'RoR', ename, line)
                    self.check_dimen(self.raw(toks, args2[0]), line, ename)
                    frame.update(self.table_frame(self.raw(toks, args2[2]), line))
                elif ename == 'minipage':
                    args2, i = self.read_args(toks, i, 'oooR', ename, line)
                    self.check_dimen(self.raw(toks, args2[3]), line, ename)
                elif ename == 'lrbox':
                    args2, i = self.read_args(toks, i, 'R', ename, line)
                    b = self.raw(toks, args2[0]).strip()
                    if b[1:] not in self.user_cmds:
                        self.err(line, f'\\begin{{lrbox}}{{{b}}}: {b} needs \\newsavebox first')
                elif ename == 'enumerate' or ename == 'itemize':
                    pass
                if ename in TABULAR_ENVS:
                    frame['depth'] = len(braces)
                envs.append(frame)
                para_start = True
                continue
            if base == 'end':
                args, i = self.read_args(toks, i, 'R', name, line)
                ename = self.raw(toks, args[0]).strip()
                if not envs:
                    self.err(line, f'\\end{{{ename}}} without \\begin')
                    continue
                top = envs[-1]
                if top['name'] != ename:
                    self.err(line, f'\\end{{{ename}}} but the open environment is {top["name"]} '
                                   f'(line {top["line"]})')
                if len(braces) != top['depth']:
                    self.err(line, f'\\end{{{ename}}} while a {{ group opened on line {braces[-1]["line"]} '
                                   f'is still open' if braces else f'\\end{{{ename}}}: braces do not match')
                if math and ename not in MATH_ENVS:
                    self.err(line, f'\\end{{{ename}}} inside math opened on line {math[1]}')
                    math = None
                envs.pop()
                if ename == 'document':
                    ended = True
                    if envs:
                        self.err(line, f'\\end{{document}} while {envs[-1]["name"]} (line {envs[-1]["line"]}) '
                                       f'is open')
                para_start = True
                continue

            # -------------------------------------------- context rules
            if base in RULES or base in self.rule_macros:
                if tab is None:
                    self.err(line, f'\\{name} outside a table')
                elif not tab_level(tab) or not tab['row_start']:
                    self.err(line, f'\\{name} must start a table row (right after \\\\): "Misplaced \\noalign"')
                if base in SIG:
                    args, i = self.read_args(toks, i, SIG[base], name, line)
                elif base == 'cmidrule':
                    j = i
                    while j < n and toks[j].kind in ('ws',):
                        j += 1
                    if j < n and toks[j].kind == 'lbr':
                        j = self.find_close(toks, j, 'lbr', 'rbr') + 1
                    while j < n and toks[j].kind == 'ws':
                        j += 1
                    if j < n and toks[j].text == '(':
                        while j < n and toks[j].text != ')':
                            j += 1
                        j += 1
                    args, i = self.read_args(toks, j, 'R', name, line)
                continue
            if base == 'item':
                lists = [e for e in envs if e['name'] in LIST_ENVS or e['name'] in BOX_ENVS
                         or e['name'] in self.user_envs]
                if not lists or lists[-1]['name'] not in LIST_ENVS:
                    self.err(line, '\\item outside itemize/enumerate')
                j = i
                while j < n and toks[j].kind == 'ws':
                    j += 1
                if j < n and toks[j].kind == 'lbr':
                    self.warn(line, '\\item [ ... ] is read as a custom label; put {} after \\item if the text '
                                    'starts with [')
                para_start = False
                continue
            if base in ('caption', 'caption*'):
                if not in_env(FLOAT_ENVS):
                    self.err(line, f'\\{name} outside a figure or table (use \\captionof)')
            if base in ('section', 'subsection', 'subsubsection', 'section*', 'subsection*', 'subsubsection*'):
                bad = [e['name'] for e in envs if e['name'] in TABULAR_ENVS | FLOAT_ENVS | {'lrbox'}]
                if bad:
                    self.err(line, f'\\{name} inside {bad[-1]}')
                if math:
                    self.err(line, f'\\{name} inside math')
            if base in ('fontsize',):
                args, i = self.read_args(toks, i, 'RR', name, line)
                j = i
                while j < n and toks[j].kind == 'ws':
                    j += 1
                if not (j < n and toks[j].text == '\\selectfont'):
                    self.warn(line, '\\fontsize without \\selectfont right after it has no effect')
                continue

            # -------------------------------------------- generic argument handling
            sig = SIG.get(base)
            if sig is None and base in self.user_cmds:
                sig = self.user_cmds[base]
            if sig:
                args, nxt = self.read_args(toks, i, sig, name, line)
                for a in args:
                    if a is None:
                        continue
                    letter, s, e = a
                    if letter in ('R', 'o'):
                        raw_skip_from = s - 1
                        raw_skip[raw_skip_from] = e + 1
                        if letter == 'R' and base in ('hspace', 'hspace*', 'vspace', 'vspace*', 'raisebox',
                                                      'enlargethispage'):
                            self.check_dimen(self.raw(toks, a), line, name)
                    elif letter == 'D':
                        raw_skip[s - 1] = e + 1
                        self.check_def_body(self.raw(toks, a), line, 9)
                    else:                          # m / M: walked as text; mark the brace as an argument
                        arg_open[s - 1] = (base, base in LONG_CMDS)
                # continue walking right after the command; raw args are jumped over
            if in_doc and base not in ('par', 'noindent', 'centering', 'raggedright', 'raggedleft', 'small',
                                       'footnotesize', 'scriptsize', 'normalsize', 'large', 'Large', 'relax',
                                       'smallskip', 'medskip', 'bigskip', 'vfill', 'clearpage', 'newpage',
                                       'nopagebreak', 'pagebreak', 'selectfont', 'bfseries', 'itshape'):
                para_start = False
            if base in ('par', 'clearpage', 'newpage'):
                para_start = True
            if tab is not None and tab_level(tab):
                tab['row_start'] = False

        # ---------------------------------------------------------- end of file
        if not seen_docclass:
            self.err(1, 'no \\documentclass')
        if not in_doc:
            self.err(0, 'no \\begin{document}')
        elif not ended:
            self.err(len(self.text.split('\n')), 'no \\end{document}')
        for f in braces:
            self.err(f['line'], 'a { opened here is never closed')
        for e in envs:
            if e['name'] != 'document' or not ended:
                self.err(e['line'], f'\\begin{{{e["name"]}}} is never closed')
        if math:
            self.err(math[1], 'math opened here is never closed')
        for line, key in self.refs:
            if key not in self.labels:
                self.err(line, f'\\ref{{{key}}} has no \\label{{{key}}}')
        self.check_packages()

    # ------------------------------------------------------------------ pieces
    def loaded(self, pkg):
        return any(p[0] == pkg for p in self.packages)

    @staticmethod
    def split_opts(s):
        out, depth, cur = [], 0, ''
        for ch in s:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
            if ch == ',' and depth == 0:
                if cur.strip():
                    out.append(cur.strip())
                cur = ''
            else:
                cur += ch
        if cur.strip():
            out.append(cur.strip())
        return out

    def use_package(self, opts_raw, names_raw, line):
        opts = self.split_opts(opts_raw)
        for name in [x.strip() for x in names_raw.split(',') if x.strip()]:
            if name not in PACKAGES:
                self.err(line, f'package {name!r} is not on the allow-list ({", ".join(sorted(PACKAGES))})')
                self.packages.append((name, frozenset(opts), line))
                continue
            allowed = PACKAGES[name]
            for o in opts:
                key = o.split('=')[0].strip()
                if allowed is not ANY and key not in allowed:
                    self.err(line, f'\\usepackage[{o}]{{{name}}}: unknown option {key!r}')
            if name == 'inputenc' and opts != ['utf8']:
                self.err(line, 'use \\usepackage[utf8]{inputenc}')
            if name == 'xcolor' and 'table' in opts:
                self.err(line, 'xcolor[table] loads colortbl, which is not on the allow-list')
            if name == 'graphicx' and 'draft' in opts:
                self.warn(line, 'graphicx[draft] prints boxes instead of the images')
            if name == 'geometry' and any(o.startswith('showframe') for o in opts):
                self.warn(line, 'geometry[showframe] draws the page frame')
            for prev_name, prev_opts, prev_line in self.packages:
                if prev_name == name:
                    if frozenset(opts) - prev_opts:
                        self.err(line, f'option clash: {name} was loaded on line {prev_line} with '
                                       f'[{",".join(sorted(prev_opts))}] and again with [{",".join(opts)}]')
                    else:
                        self.warn(line, f'{name} is loaded twice (also line {prev_line})')
                if name in IMPLICIT.get(prev_name, []) and opts:
                    self.err(line, f'option clash: {prev_name} (line {prev_line}) already loaded {name} without '
                                   f'options; load {name} with its options before {prev_name}')
            self.packages.append((name, frozenset(opts), line))

    def check_packages(self):
        names = [p[0] for p in self.packages]
        if 'hyperref' in names and names[-1] != 'hyperref':
            after = names[names.index('hyperref') + 1:]
            self.err(dict((p[0], p[2]) for p in self.packages)['hyperref'],
                     f'load hyperref last (loaded before: {", ".join(after)})')
        setups = [s for s in FONT_SETUPS if s & set(names)]
        if len(setups) > 1:
            self.err(0, f'two font setups loaded: {sorted(set().union(*setups) & set(names))}; keep one')
        if 'newtxmath' in names and 'newtxtext' in names and names.index('newtxmath') < names.index('newtxtext'):
            self.warn(0, 'load newtxtext before newtxmath')
        if 'microtype' in names:
            fonts = [x for x in ('newtxtext', 'newtxmath', 'lmodern', 'fontenc') if x in names]
            if fonts and names.index('microtype') < max(names.index(x) for x in fonts):
                self.warn(0, 'load microtype after the font packages')
        fontenc = [p for p in self.packages if p[0] == 'fontenc']
        if getattr(self, 'has_latin', False):
            if not fontenc or 'T1' not in fontenc[-1][1]:
                self.err(0, 'accented letters need \\usepackage[T1]{fontenc}')
            if not self.loaded('inputenc'):
                self.warn(0, 'accented letters: \\usepackage[utf8]{inputenc} is recommended')

    def check_def_body(self, body, line, nargs, allow_hash=True):
        masked, _ = strip_comments(body)
        for m in re.finditer(r'\\([A-Za-z@]+)\*?', masked):
            nm = m.group(1)
            if nm not in KNOWN and nm not in self.user_cmds:
                self.err(line, f'unknown command \\{nm} in a definition')
            elif KNOWN.get(nm) and nm not in self.user_cmds and not self.loaded(KNOWN[nm]):
                self.err(line, f'\\{nm} (in a definition) needs \\usepackage{{{KNOWN[nm]}}}')
        for m in re.finditer(r'(?<!\\)#(.)', masked):
            if not allow_hash or not m.group(1).isdigit() or int(m.group(1)) > max(nargs, 0) and nargs != 9:
                self.err(line, f'#{m.group(1)} in a definition that takes {nargs} arguments')
        depth = 0
        for m in re.finditer(r'\\.|[{}]', masked, re.S):
            if m.group() == '{':
                depth += 1
            elif m.group() == '}':
                depth -= 1
                if depth < 0:
                    self.err(line, 'unbalanced braces in a definition')
                    break
        for m in re.finditer(r'\\color\{([^}]*)\}|\\colorbox\{([^}]*)\}|\\fcolorbox\{([^}]*)\}\{([^}]*)\}', masked):
            for g in m.groups():
                if g:
                    self.check_color_use(g, line)
        for m in re.finditer(r'\\includegraphics\*?(\[[^\]]*\])?\{([^}]*)\}', masked):
            self.graphics.append((line, m.group(2).strip()))
        for m in re.finditer(r'\\setlength\{\\([A-Za-z@]+)\}', masked):
            if m.group(1) not in self.lengths:
                self.err(line, f'\\setlength{{\\{m.group(1)}}} in a definition: not a known length')

    def check_color_def(self, name, model, spec, line):
        ok = False
        if model == 'RGB':
            parts = [p.strip() for p in spec.split(',')]
            ok = len(parts) == 3 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
        elif model == 'rgb' or model == 'cmy':
            parts = [p.strip() for p in spec.split(',')]
            ok = len(parts) == 3 and all(re.fullmatch(r'[01]?(\.\d+)?|1(\.0+)?', p) and p for p in parts)
        elif model == 'cmyk':
            parts = [p.strip() for p in spec.split(',')]
            ok = len(parts) == 4 and all(re.fullmatch(r'[01]?(\.\d+)?', p) and p for p in parts)
        elif model == 'HTML':
            ok = bool(re.fullmatch(r'[0-9A-Fa-f]{6}', spec))
        elif model == 'gray':
            ok = bool(re.fullmatch(r'0?(\.\d+)?|1(\.0+)?', spec)) and spec != ''
        if not ok:
            self.err(line, f'\\definecolor{{{name}}}{{{model}}}{{{spec}}}: bad colour model or value')
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9-]*', name):
            self.err(line, f'colour name {name!r}: use letters, digits and -')

    def check_color_use(self, expr, line):
        if any(p[0] == 'xcolor' and p[1] & {'dvipsnames', 'svgnames', 'x11names'} for p in self.packages):
            return
        parts = expr.lstrip('-').split('!')
        for k, p in enumerate(parts):
            p = p.strip()
            if k % 2 == 0:
                if p not in self.colors:
                    self.err(line, f'colour {p!r} is not defined (in {expr!r})')
            elif not re.fullmatch(r'\d{1,3}(\.\d+)?', p) or float(p) > 100:
                self.err(line, f'colour mix {expr!r}: {p!r} must be a percentage 0 to 100')

    def check_dimen(self, s, line, where):
        s = s.strip()
        unit = r'(pt|in|em|ex|cm|mm|bp|sp|pc|dd|cc)'
        num = r'-?\s*(\d+(\.\d*)?|\.\d+)'
        reg = r'\\[A-Za-z@]+'
        simple = rf'({num}\s*{unit}|{num}?\s*{reg})'
        glue = rf'{simple}(\s*plus\s*{num}\s*(fil{{1,3}}|{unit}))?(\s*minus\s*{num}\s*{unit})?'
        if re.fullmatch(glue, s):
            for r in re.findall(reg, s):
                if r[1:] not in self.lengths and r[1:] not in ('fill', 'stretch') and r[1:] not in self.user_cmds:
                    self.err(line, f'{where}: {r} is not a known length')
            return
        if s.startswith('\\dimexpr'):
            body = s[len('\\dimexpr'):]
            if body.rstrip().endswith('\\relax'):
                body = body.rstrip()[:-len('\\relax')]
            if not re.fullmatch(rf'(\s*[-+]?\s*({num})?\s*(\*\s*)?({unit}|{reg}|\(\s*)\s*\)?)+\s*', body):
                self.err(line, f'{where}: cannot read the \\dimexpr {s!r}')
            for r in re.findall(reg, body):
                if r[1:] not in self.lengths and r[1:] not in self.user_cmds:
                    self.err(line, f'{where}: {r} in \\dimexpr is not a known length')
            return
        if re.fullmatch(rf'{num}\s*\\(textheight|textwidth|linewidth|columnwidth|paperheight|paperwidth)', s):
            return
        self.err(line, f'{where}: {s!r} is not a length')

    def table_frame(self, spec, line):
        """Count the columns of a tabular preamble and check the commands in it."""
        masked, _ = strip_comments(spec)
        for m in re.finditer(r'\\([A-Za-z@]+)', masked):
            nm = m.group(1)
            if nm not in KNOWN and nm not in self.user_cmds:
                self.err(line, f'unknown command \\{nm} in the table preamble')
            elif KNOWN.get(nm) and not self.loaded(KNOWN[nm]):
                self.err(line, f'\\{nm} in the table preamble needs \\usepackage{{{KNOWN[nm]}}}')
        if re.search(r'[<>]\{', masked) and not self.loaded('array'):
            self.err(line, 'a >{...} or <{...} column needs \\usepackage{array}')
        cols = 0
        i = 0
        s = masked

        def skip_group(j):
            if j >= len(s) or s[j] != '{':
                self.err(line, f'table preamble: expected {{ at {s[j:j + 10]!r}')
                return j
            depth = 0
            while j < len(s):
                if s[j] == '\\':
                    j += 2
                    continue
                if s[j] == '{':
                    depth += 1
                elif s[j] == '}':
                    depth -= 1
                    if depth == 0:
                        return j + 1
                j += 1
            self.err(line, 'table preamble: unbalanced braces')
            return j

        while i < len(s):
            ch = s[i]
            if ch.isspace() or ch == '|':
                i += 1
            elif ch in '><@!':
                i = skip_group(i + 1)
            elif ch in 'lcr':
                cols += 1
                i += 1
            elif ch in 'pmb':
                if ch in 'mb' and not self.loaded('array'):
                    self.err(line, f'{ch}{{...}} columns need \\usepackage{{array}}')
                cols += 1
                i = skip_group(i + 1)
            elif ch == 'X':
                if not self.loaded('tabularx'):
                    self.err(line, 'X columns need tabularx')
                cols += 1
                i += 1
            elif ch == '*':
                j = skip_group(i + 1)
                count = s[i + 2:j - 1]
                k2 = skip_group(j)
                inner = self.table_frame(s[j + 1:k2 - 1], line)['cols']
                cols += int(count) * inner if count.strip().isdigit() else 0
                i = k2
            else:
                self.err(line, f'table preamble: unknown column type {ch!r}')
                i += 1
        if cols == 0:
            self.err(line, 'table preamble has no columns')
        return {'cols': cols, 'amps': 0, 'row_start': True}

    def check_graphics_opts(self, raw, line):
        keys = {'width', 'height', 'totalheight', 'keepaspectratio', 'scale', 'angle', 'trim', 'clip', 'page',
                'viewport', 'origin', 'draft', 'interpolate'}
        for o in self.split_opts(raw):
            key = o.split('=')[0].strip()
            if key not in keys:
                self.err(line, f'\\includegraphics: unknown option {key!r}')
            if key in ('width', 'height', 'totalheight') and '=' in o:
                self.check_dimen(o.split('=', 1)[1], line, f'\\includegraphics {key}')

    def check_files(self):
        used = set()
        for line, rel in self.graphics:
            if not rel:
                self.err(line, '\\includegraphics with an empty file name')
                continue
            if re.search(r'[^A-Za-z0-9._/-]', rel):
                self.err(line, f'\\includegraphics{{{rel}}}: use only letters, digits, - _ . / in file names')
            if rel.count('.') > 1 or rel.startswith('/') or '..' in rel:
                self.err(line, f'\\includegraphics{{{rel}}}: keep one dot and a path inside the project')
            p = self.outdir / rel
            cands = [p] if p.suffix else [p.with_suffix(x) for x in ('.pdf', '.png', '.jpg', '.jpeg')]
            found = next((c for c in cands if c.is_file()), None)
            if not found:
                self.err(line, f'\\includegraphics{{{rel}}}: the file is not in the project folder')
                continue
            used.add(found.resolve())
            ext = found.suffix.lower()
            if ext not in ('.png', '.jpg', '.jpeg', '.pdf'):
                self.err(line, f'{rel}: pdfLaTeX takes only png, jpg or pdf images')
                continue
            head = found.read_bytes()[:32]
            if ext == '.png' and not head.startswith(b'\x89PNG\r\n\x1a\n'):
                self.err(line, f'{rel}: not a real PNG file')
            elif ext in ('.jpg', '.jpeg') and not head.startswith(b'\xff\xd8'):
                self.err(line, f'{rel}: not a real JPEG file')
            elif ext == '.pdf' and not head.startswith(b'%PDF'):
                self.err(line, f'{rel}: not a real PDF file')
            if ext == '.png' and len(head) >= 29:
                depth, color, interlace = head[24], head[25], head[28]
                if depth == 16:
                    self.warn(line, f'{rel}: 16-bit PNG (works, but slower; 8-bit is safer)')
                if interlace:
                    self.warn(line, f'{rel}: interlaced PNG (works, but slower)')
            try:
                from PIL import Image
                if ext != '.pdf':
                    with Image.open(found) as im:
                        im.verify()
            except ImportError:
                pass
            except Exception as e:  # noqa: BLE001
                self.err(line, f'{rel}: the image cannot be read ({e})')
        figdir = self.outdir / 'figures'
        if figdir.is_dir():
            for f in figdir.iterdir():
                if f.is_file() and f.resolve() not in used:
                    self.warn(0, f'figures/{f.name} is in the project but not used')
        total = sum(f.stat().st_size for f in self.outdir.rglob('*') if f.is_file())
        if total > 50 * 1024 * 1024:
            self.warn(0, f'the project is {total / 1e6:.0f} MB; Overleaf uploads are limited to 50 MB')

    def check_zip(self):
        z = self.outdir.with_name(self.outdir.name + '.zip')
        if not z.is_file():
            self.warn(0, f'{z.name} not found next to the folder (nothing to upload to Overleaf)')
            return
        with zipfile.ZipFile(z) as zf:
            names = set(zf.namelist())
            local = {str(f.relative_to(self.outdir)).replace('\\', '/') for f in self.outdir.rglob('*') if f.is_file()}
            if names != local:
                self.err(0, f'{z.name} and the folder differ: only in zip {sorted(names - local)}, '
                            f'only in folder {sorted(local - names)}')
            for nm in names & local:
                if zf.read(nm) != (self.outdir / nm).read_bytes():
                    self.err(0, f'{z.name}: {nm} differs from the folder copy')
            if 'main.tex' not in names:
                self.err(0, f'{z.name} has no main.tex at its top level')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('outdir')
    ap.add_argument('--main', default='main.tex')
    ap.add_argument('--quiet', action='store_true', help='print only the summary and errors')
    a = ap.parse_args()
    c = Checker(Path(a.outdir).resolve(), a.main)
    c.run()
    for line, msg in sorted(c.errors):
        print(f'ERROR   main.tex:{line}: {msg}')
    if not a.quiet:
        for line, msg in sorted(c.warnings):
            print(f'warning main.tex:{line}: {msg}')
    print(f'check_tex: {len(c.errors)} error(s), {len(c.warnings)} warning(s)')
    sys.exit(1 if c.errors else 0)


if __name__ == '__main__':
    main()
