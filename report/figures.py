"""Draws the report's diagrams into ../figures/ (run: .venv\\Scripts\\python report\\figures.py).

values_hierarchy.png      Figure 1: values -> norms -> design rules
pipeline.png              Figure 2: how a suggestion is made
groups_screen_sketch.png  Figure 3: the new Groups screen for user 1 (personalisation off and on)
Final report (24 Nov): values_hierarchy_final.png (R8's age bands), pipeline_final.png (groups and people, as built),
boing_screens.png (the Discover page in BOING's local test copy, from tests/windows/stack/fe3/recs-real/)

Figures 1 and 2 are drawings: no data is read for them. Figure 3 draws the layout as a sketch, but its groups and
reasons are the final design's own output for user 1 of the synthetic community (results/final_user1.csv, written by
notebook 11: the default list and the personalised list, noise draw 0), so run notebook 11 first.

Draw one figure only by naming it: .venv\\Scripts\\python report\\figures.py groups_screen_sketch
"""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parent.parent / 'figures'
RESULTS = Path(__file__).resolve().parent.parent / 'results'
BLUE, BLUE_LIGHT, GREY, INK, MUTED = '#2a78d6', '#dbe8f8', '#e9e8e4', '#1d1d1b', '#5f5e5a'
GREEN, GREEN_LIGHT, AMBER, AMBER_LIGHT = '#2e8b57', '#dcefe3', '#9a6a00', '#fbecc8'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})


def rounded(ax, x, y, w, h, face, edge='none', radius=0.012, lw=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={radius}',
                                facecolor=face, edgecolor=edge, linewidth=lw))


def arrow(ax, x0, y0, x1, y1, color=MUTED):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='-|>', mutation_scale=10,
                                 color=color, linewidth=1, shrinkA=0, shrinkB=0))


def values_hierarchy():
    _values_hierarchy(OUT / 'values_hierarchy.png')


def _values_hierarchy(path, teen_rule='R8 shared group'):
    tree = [
        ('Privacy', [('Private spaces\nstay private', 'R2 public data'),
                     ('No profiling\nwithout consent', 'R1 opt-in only'),
                     ('No one exposed\nthrough others', 'R10 noise (ε)')]),
        ('Equity &\ninclusion', [('Newcomers get\na real chance', 'R4 quota q'),
                                 ('No group takes\nall attention', 'R4 cap c'),
                                 ("Money can't\nbuy reach", 'R3 no paid rank')]),
        ('Autonomy &\ndiversity', [('Members steer\nsuggestions', 'R7 controls'),
                                   ('No one locked\nin a bubble', 'R5 cluster cap n'),
                                   ('Interests chosen,\nnot guessed', 'R11 own topics')]),
        ('Transparency\n& trust', [('Every suggestion\nis justified', 'R6 "Why this?"'),
                                   ("People know it's\nan algorithm", 'R6 label'),
                                   ('Ranking resists\nfake accounts', 'R9 level ≥ L')]),
        ('Safety &\nwell-being', [('Hidden or blocked\nnever returns', 'R8 hard filters'),
                                  ('No strangers\npushed to teens', 'R8 shared group'),
                                  ('Not an\nattention trap', 'R11 short list')]),
    ]
    # Drawn at 8 in wide for a 6.5 in column: every label prints at 7 pt or more
    fig, ax = plt.subplots(figsize=(8, 3.9))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    rounded(ax, 0.1, 0.91, 0.8, 0.085, INK)
    ax.text(0.5, 0.952, 'Aim: suggestions that help members reach their own goals', ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')
    n, gap = len(tree), 0.012
    col_w = (1 - gap * (n - 1)) / n
    for i, (value, norms) in enumerate(tree):
        x = i * (col_w + gap)
        arrow(ax, 0.5, 0.91, x + col_w / 2, 0.835)
        rounded(ax, x, 0.705, col_w, 0.13, BLUE)
        ax.text(x + col_w / 2, 0.77, value, ha='center', va='center', fontsize=10.5, fontweight='bold', color='white')
        for j, (norm, rule) in enumerate(norms):
            y = 0.465 - j * 0.232
            rounded(ax, x, y, col_w, 0.205, BLUE_LIGHT, BLUE)
            ax.text(x + col_w / 2, y + 0.14, norm, ha='center', va='center', fontsize=8.6, color=INK, linespacing=1.1)
            rounded(ax, x + 0.005, y + 0.017, col_w - 0.01, 0.072, GREEN_LIGHT, GREEN, radius=0.008)
            ax.text(x + col_w / 2, y + 0.053, rule, ha='center', va='center', fontsize=8.1,
                    fontweight='bold', color=GREEN)
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def pipeline():
    steps = [
        ('Data', 'memberships,\nlikes, friends,\npublic posts,\npicked topics', 'R2'),
        ('Statistics', 'group sizes,\n"also joined",\ntaste model;\nreal accounts\nonce; noise', 'R9, R10'),
        ('Score', 'also joined\n+ similar texts\n+ hidden tastes', 'machine learning'),
        ('Filter', 'remove joined,\nnot interested,\nblocked, hidden,\nsensitive', 'R7, R8, R11'),
        ('Re-rank', 'room for new &\nsmall groups,\n≤ n per cluster,\nkeep 5', 'R4, R5, R11'),
        ('Show', '5 cards, each\nwith "Why this?"\nand ✕', 'R6, R7'),
    ]
    fig, ax = plt.subplots(figsize=(8, 2.9))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    w, h, y = 0.153, 0.54, 0.25
    step = (1 - w) / (len(steps) - 1)
    for i, (title, body, rules) in enumerate(steps):
        x = i * step
        learned = rules == 'machine learning'
        rounded(ax, x, y, w, h, AMBER_LIGHT if learned else BLUE_LIGHT, AMBER if learned else BLUE)
        ax.text(x + w / 2, y + h - 0.075, title, ha='center', va='center', fontsize=9.2, fontweight='bold', color=INK)
        ax.text(x + w / 2, y + h / 2 - 0.06, body, ha='center', va='center', fontsize=8, color=INK, linespacing=1.25)
        ax.text(x + w / 2, y - 0.075, 'learned' if learned else rules, ha='center', va='center', fontsize=8.6,
                color=AMBER if learned else GREEN, fontweight='bold')
        if i < len(steps) - 1:
            arrow(ax, x + w + 0.003, y + h / 2, x + step - 0.003, y + h / 2)
    for x0, x1, label in ((0, step + w, 'once a night'), (2 * step, 1, 'each time a member opens Groups')):
        ax.plot([x0, x1], [0.9, 0.9], color=MUTED, linewidth=0.9)
        ax.plot([x0, x0], [0.87, 0.9], color=MUTED, linewidth=0.9)
        ax.plot([x1, x1], [0.87, 0.9], color=MUTED, linewidth=0.9)
        ax.text((x0 + x1) / 2, 0.955, label, ha='center', va='center', fontsize=9, color=MUTED)
    ax.text(0.5, 0.02, 'Personalisation off (default, R1): no profile; Filter, Re-rank and Show run on new, active and curated groups.',
            ha='center', va='center', fontsize=8.8, color=INK, style='italic')
    fig.savefig(OUT / 'pipeline.png', dpi=200, bbox_inches='tight')
    plt.close(fig)


def user1_lists():
    """User 1's two lists from the final design, as notebook 11 saved them: {'off': [...], 'on': [...]},
    each a list of (group name, reason text) in rank order."""
    rows = list(csv.DictReader(open(RESULTS / 'final_user1.csv', encoding='utf-8')))
    pick = lambda label: [(r['group'], r['reason_text']) for r in sorted((r for r in rows if r['list'] == label),
                                                                          key=lambda r: int(r['rank']))]
    return {'off': pick('Default: personalisation off'), 'on': pick('Final design: personalisation on')}


def groups_screen_sketch():
    """The new Groups screen for user 1: the default list (personalisation off) and the personalised list, with the
    groups and the reasons the final design gives (results/final_user1.csv). Only the layout is a sketch."""
    lists = user1_lists()
    W, gap = 7.4, 0.22                       # inches; drawn in an inch-based coordinate system
    pw = (W - gap) / 2                       # panel width
    FS_NAME, FS_REASON, FS_SMALL = 10, 9, 8.6
    fig = plt.figure(figsize=(W, 8))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    renderer = fig.canvas.get_renderer()

    def width(text, **kw):
        # printed width of a text, in inches
        t = ax.text(0, 0, text, **kw)
        w = t.get_window_extent(renderer).width / fig.dpi
        t.remove()
        return w

    def wrap(text, first, rest, **kw):
        # greedy word wrap: the first line has `first` inches, the others `rest`
        lines, cur = [], ''
        for word in text.split():
            trial = (cur + ' ' + word).strip()
            if cur and width(trial, **kw) > (first if not lines else rest):
                lines.append(cur)
                cur = word
            else:
                cur = trial
        return lines + [cur]

    reason_kw = dict(fontsize=FS_REASON, style='italic')
    why_w = width('Why this?', fontsize=FS_REASON, fontweight='bold') + 0.07
    pad_x, line_h, name_h, pad_y, card_gap = 0.12, 0.155, 0.19, 0.05, 0.05
    inner = pw - 2 * 0.1 - 2 * pad_x         # text width inside a card
    panels = []
    for key, x0, title in (('off', 0.0, 'Off (the default)'), ('on', pw + gap, 'On (the member chose it)')):
        on = key == 'on'
        cards = []
        for name, reason in lists[key]:
            lines = wrap(reason, inner - (why_w if on else 0), inner, **reason_kw)
            cards.append((name, lines, 2 * pad_y + name_h + line_h * len(lines)))
        panels.append((key, x0, title, cards))
    top_h, foot_h = 0.64, 0.26               # header (Groups, switch, subtitle) and footer, inside the panel
    body = max(sum(c[2] for c in cards) + card_gap * (len(cards) - 1) for *_, cards in panels)
    ph = top_h + body + foot_h               # panel height
    H = ph + 0.32                            # plus the title above the panels

    for key, x0, title, cards in panels:
        on = key == 'on'
        ax.text(x0 + pw / 2, ph + 0.1, title, ha='center', va='bottom', fontsize=11, fontweight='bold', color=INK)
        rounded(ax, x0, 0, pw, ph, 'white', MUTED, radius=0.08, lw=1.2)
        y = ph - 0.21
        ax.text(x0 + 0.18, y, 'Groups', fontsize=12, fontweight='bold', va='center', color=INK)
        sw_w, sw_r = 0.42, x0 + pw - 0.16
        rounded(ax, sw_r - sw_w, y - 0.1, sw_w, 0.2, BLUE if on else '#c9c8c3', radius=0.1)
        knob = sw_r - 0.1 if on else sw_r - sw_w + 0.1
        ax.plot([knob], [y], marker='o', markersize=7, color='white', zorder=4)
        ax.text(sw_r - sw_w - 0.08, y, 'Personalised', fontsize=FS_SMALL, va='center', ha='right', color=INK)
        ax.text(x0 + 0.18, ph - 0.47, 'Suggested for you  ·  by an algorithm' if on else 'New and active  ·  the same for everyone',
                fontsize=FS_SMALL, color=MUTED, va='center')
        y = ph - top_h
        for name, lines, h in cards:
            cx = x0 + 0.1
            rounded(ax, cx, y - h, pw - 0.2, h, BLUE_LIGHT if on else GREY, radius=0.05)
            ny = y - pad_y - name_h / 2
            ax.text(cx + pad_x, ny, name, fontsize=FS_NAME, fontweight='bold', color=INK, va='center')
            ax.text(cx + pw - 0.2 - pad_x, ny, 'Join', fontsize=FS_SMALL, color='white', ha='right', va='center', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=BLUE, edgecolor='none'))
            if on:
                ax.text(cx + pw - 0.2 - pad_x - 0.5, ny, '✕', fontsize=9, color=MUTED, ha='right', va='center')
            for i, line in enumerate(lines):
                ly = y - pad_y - name_h - line_h * (i + 0.5)
                lx = cx + pad_x
                if on and i == 0:
                    ax.text(lx, ly, 'Why this?', fontsize=FS_REASON, color=BLUE, va='center', fontweight='bold')
                    lx += why_w
                ax.text(lx, ly, line, color=INK if on else MUTED, va='center', **(reason_kw if on else dict(fontsize=FS_REASON)))
            y -= h + card_gap
        ax.text(x0 + pw / 2, foot_h / 2, 'Not interested  ·  Hide a topic  ·  Reset  ·  What is used' if on else 'No profile used',
                ha='center', va='center', fontsize=FS_SMALL, color=BLUE if on else MUTED)
    fig.set_size_inches(W, H)
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    fig.savefig(OUT / 'groups_screen_sketch.png', dpi=200, bbox_inches='tight')
    plt.close(fig)


def values_hierarchy_final():
    """Figure 1 of the final report: as values_hierarchy(), with R8's second norm now met by the age bands of the
    people suggestions (19 Nov 2026)."""
    _values_hierarchy(OUT / 'values_hierarchy_final.png', teen_rule='R8 age bands')


def pipeline_final():
    """Figure 2 of the final report: how a group suggestion and a people suggestion are made, as built in BOING."""
    groups = [
        ('Data', 'memberships,\nlikes, friends,\npublic posts,\ngroup texts', 'R2'),
        ('Statistics', 'sizes, "also\njoined", tastes;\nonly accounts\nthat count;\nnoise', 'R9, R10'),
        ('Score', '"also joined"\n+ similar texts\n+ friends\n+ hidden tastes', 'learned'),
        ('Filter', 'remove joined,\ndismissed,\nhidden, closed;\nblocked owners', 'R7, R8'),
        ('Re-rank', '1 slot new or\nsmall; cap 5%;\n≤ 2 per cluster;\nkeep 5', 'R4, R5, R11'),
        ('Show', '5 cards, each\nwith its reason,\n"Why this?"\nand ✕', 'R6, R7'),
    ]
    people = [
        ('Candidates', 'friends of\nfriends; members\nof my groups\nand courses', 'R8'),
        ('Filter', 'friends, requests,\nblocked,\nsuspended,\nprivate, off;\nage bands', 'R1, R8'),
        ('Score', 'mutual friends\n+ shared groups\n(no learning)', ''),
        ('Show', '≤ 5; ≤ 2 per\ngroup; reason;\n✕; no alerts', 'R5, R6, R7, R11'),
    ]
    fig, ax = plt.subplots(figsize=(8, 4.0))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    x0 = 0.085
    w, h = 0.135, 0.3
    step = (1 - x0 - w) / (len(groups) - 1)

    def row(steps, y, step):
        for i, (title, body, rules) in enumerate(steps):
            x = x0 + i * step
            learned = rules == 'learned'
            rounded(ax, x, y, w, h, AMBER_LIGHT if learned else BLUE_LIGHT, AMBER if learned else BLUE)
            ax.text(x + w / 2, y + h - 0.04, title, ha='center', va='center', fontsize=9, fontweight='bold', color=INK)
            ax.text(x + w / 2, y + h / 2 - 0.03, body, ha='center', va='center', fontsize=6.9, color=INK, linespacing=1.15)
            ax.text(x + w / 2, y - 0.04, rules, ha='center', va='center', fontsize=8.2,
                    color=AMBER if learned else GREEN, fontweight='bold')
            if i < len(steps) - 1:
                arrow(ax, x + w + 0.003, y + h / 2, x + step - 0.003, y + h / 2)
    row(groups, 0.535, step)
    row(people, 0.115, step)
    ax.text(0.0, 0.535 + h / 2, 'Groups', ha='left', va='center', fontsize=9.5, fontweight='bold', color=INK, rotation=90)
    ax.text(0.0, 0.115 + h / 2, 'People', ha='left', va='center', fontsize=9.5, fontweight='bold', color=INK, rotation=90)
    for a, b, label in ((x0, x0 + step + w, 'daily; noisy part weekly'), (x0 + 2 * step, 1, 'each time a member opens Discover')):
        ax.plot([a, b], [0.92, 0.92], color=MUTED, linewidth=0.9)
        ax.plot([a, a], [0.895, 0.92], color=MUTED, linewidth=0.9)
        ax.plot([b, b], [0.895, 0.92], color=MUTED, linewidth=0.9)
        ax.text((a + b) / 2, 0.96, label, ha='center', va='center', fontsize=8.6, color=MUTED)
    ax.text(0.5, 0.005, 'Personalisation off (the default, R1): no profile and no people; groups ranked by newness and recent activity.',
            ha='center', va='center', fontsize=8.4, color=INK, style='italic')
    fig.savefig(OUT / 'pipeline_final.png', dpi=200, bbox_inches='tight')
    plt.close(fig)


SCREENS = OUT / 'boing'      # copies of BOING's tests/windows/stack/fe3/recs-real/ screenshots (19 Nov 2026)


def boing_screens():
    """Figure 3 of the final report: the Discover page in BOING's local test copy (fake members only), from the
    frontend's phone screenshots (copied into figures/boing/), cropped to the same height."""
    from PIL import Image
    crops = [('phone-off.png', (0, 300, 780, 1380), '(a) Off (the default)'),
             ('phone-on.png', (0, 300, 780, 1380), '(b) Switched on'),
             ('phone-why.png', (0, 300, 780, 1380), '(c) "Why this?"')]
    ims = [(Image.open(SCREENS / f).convert('RGB').crop(box), label) for f, box, label in crops]
    W = 6.5
    fig, axes = plt.subplots(1, 3, figsize=(W, 3.2), gridspec_kw={'wspace': 0.05})
    for ax, (im, label) in zip(axes, ims):
        ax.imshow(im)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_edgecolor('#c9c8c3'); s.set_linewidth(0.8)
        ax.set_title(label, fontsize=9, fontweight='bold', color=INK, loc='left')
    fig.savefig(OUT / 'boing_screens.png', dpi=220, bbox_inches='tight')
    plt.close(fig)


FIGURES = {'values_hierarchy': values_hierarchy, 'pipeline': pipeline, 'groups_screen_sketch': groups_screen_sketch,
           'values_hierarchy_final': values_hierarchy_final, 'pipeline_final': pipeline_final, 'boing_screens': boing_screens}

if __name__ == '__main__':
    for name in sys.argv[1:] or FIGURES:
        FIGURES[name]()
    print('saved to', OUT)


