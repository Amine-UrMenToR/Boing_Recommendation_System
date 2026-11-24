"""Builds T5 (appended to notebooks/03_baseline.ipynb) and notebooks/04_methods.ipynb (T6, T7).

Run from anywhere with the project's venv python:  python build_t5_t7.py
Idempotent: notebook 03 is cut back to its T4 cells before T5 is appended; notebook 04 is rewritten.
"""
from pathlib import Path
import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

NB = Path('C:/Users/houar/Desktop/2027/HOPPY/Bs/ECSE557/notebooks')
md, code = new_markdown_cell, new_code_cell

# ============================================================================================
# Notebook 03: T5
# ============================================================================================
nb3 = nbformat.read(NB / '03_baseline.ipynb', as_version=4)
ids = [c.get('id') for c in nb3.cells]
last_t4 = ids.index('9cb290a7')            # the "What's next" cell that ended T4
nb3.cells = nb3.cells[:last_t4 + 1]

nb3.cells[0].source = """# 03 · Score today's BOING (T4) and see who it shows (T5)

**Steps T4 and T5 of the project plan.** Our first recommender is what BOING does today on its Discover page: **show the biggest groups first**.
We give it the quiz prepared in T3 and count how many hidden groups it finds (T4). Every better recommender (T6, T9) will have to beat this score.
Then we count **who gets shown** (T5, sections 7 to 9): how many of the suggestions go to new and small groups, the unfairness rule R4 must fix.

Run notebooks 01 and 02 first. Only the training files are used to make suggestions; the test file is used only to score them."""

nb3.cells[last_t4].source = """## What's next

- **T5, who gets shown** (below): count how often each group appears in the suggestions. Today's ranking shows almost everyone the same few groups,
  so new and small groups never appear.
- **T6, two better recommenders** (notebook 04): "people in X also joined Y" and "similar descriptions". They take the same quiz, and the scores above are the ones to beat."""

nb3.cells += [
md("""## 7 · T5: who gets shown

**Step T5 of the project plan.** Each time a group appears in someone's 5 suggestions, it gets *exposure*: a chance to be seen and joined.
We count where the 7,030 slots go (1,406 tested users × 5 suggestions):

- **Newcomer share:** the share of slots that go to **new** groups (created in the last 30 days) or **small** ones (fewer than 10 members in the training data).
  Rule R4 asks for at least *q* of them (we will try 20% and 40%).
- **Gini of exposure:** one number for how unequally the slots are shared among the 129 groups on Discover, counting those never shown.
  0 = every group is shown equally often; close to 1 = one group gets every slot.
- **Coverage:** how many different groups are ever shown. **Largest share:** the share of all slots taken by the most-shown group
  (R4's cap *c*: we will try 5% and 10%).

From here on, the notebooks share their code in one file, `boingrec.py` (in this folder). First we check that it gives exactly the T4 scores above.
It also does one thing T4 did not: it never suggests a group the user marked "not interested" (rule R7)."""),
code("""# Colab only: also upload boingrec.py (from the notebooks folder). Locally this does nothing.
if 'google.colab' in sys.modules and not Path('boingrec.py').exists():
    from google.colab import files
    files.upload()
import boingrec as br

vis = br.load_visible()    # what a recommender may read
ans = br.load_answers()    # the answer key (hidden memberships, hidden topics): only for scoring
t5_lists = {'popularity': br.top_k(br.popularity_scores(vis, tested_users), vis),
            'random': br.random_lists(vis, tested_users)}
t5 = pd.DataFrame({br.label(m): br.evaluate(lists, ans.test, vis, ans.group_topic) for m, lists in t5_lists.items()}).T

same_scores = (t5.loc['Popularity (today)', br.RELEVANCE].round(3) == results.loc['Popularity (today)', br.RELEVANCE]).all()
n_changed = sum(t5_lists['popularity'][u] != pop[u] for u in tested_users)
print('Popularity scored with boingrec:', t5.loc['Popularity (today)', br.RELEVANCE].round(3).to_dict())
print(f'Same scores as T4: {same_scores}. Skipping "not interested" groups changes {n_changed} of the '
      f'{len(tested_users)} lists, but none of the scores.')
assert same_scores, 'boingrec does not reproduce T4: find out why before going on'"""),
md("""### Where the slots go"""),
code("""disc = br.discover_groups(vis.groups)          # the 129 groups on Discover
n_members = br.group_sizes(vis)                # members in the training data
newcomers = br.newcomer_groups(vis) & set(disc)
created = vis.groups.set_index('group_id').created_day
shown = pd.DataFrame({br.label(m): br.exposure(lists, disc) for m, lists in t5_lists.items()})
slots = K * len(tested_users)

t5_table = t5[['users', 'newcomer_share', 'gini', 'coverage', 'largest_share']].assign(
    slots=slots, discover_groups=len(disc), new_or_small_groups=len(newcomers)).astype({'users': int, 'coverage': int})
br.save_table(t5_table, 't5_exposure.csv')
per_group = pd.DataFrame({'name': name[disc], 'members': n_members[disc], 'created_day': created[disc],
                          'new_or_small': [int(g in newcomers) for g in disc]}).join(shown)
per_group.sort_values('members', ascending=False, kind='stable').to_csv(RESULTS / 't5_exposure_per_group.csv')

p5, r5 = t5_table.loc['Popularity (today)'], t5_table.loc['Random (floor)']
print(f'{len(disc)} groups on Discover, {len(newcomers)} of them new or small; {slots:,} slots in all.')
for label_, row in [('Popularity', p5), ('Random', r5)]:
    print(f'{label_:10}: newcomer share {row.newcomer_share:5.1%} | Gini {row.gini:.3f} | {row.coverage:3.0f} groups ever shown | '
          f'the most-shown group takes {row.largest_share:.1%} of all slots')
most = shown['Popularity (today)'].sort_values(ascending=False, kind='stable').head(10)
print('\\nThe only groups popularity ever shows:')
print(pd.DataFrame({'members': n_members[most.index].values, 'times shown': most.values,
                    'share of slots': (most / slots).map('{:.1%}'.format).values},
                   index=name[most.index].values).to_string())"""),
md("""## 8 · The picture

Left: every group on Discover, from the biggest to the smallest, and how many of the 7,030 slots it gets. Right: the same counts as a
**Lorenz curve**: groups are lined up from the least shown to the most shown, and the curve adds up their slots. If every group got the same
number of slots, the curve would follow the diagonal. The further it sags below, the more unequal; the Gini is the size of that gap."""),
code("""by_size = n_members[disc].sort_values(ascending=False, kind='stable').index      # biggest first; ties: smaller id first
x = np.arange(1, len(by_size) + 1)
is_newcomer = np.array([g in newcomers for g in by_size])
counts_pop, counts_rnd = shown['Popularity (today)'][by_size], shown['Random (floor)'][by_size]

br.use_style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(br.WIDTH, 2.7), gridspec_kw=dict(width_ratios=[1.75, 1]))
start = x[is_newcomer].min() - 0.5
a1.axvspan(start, x[-1] + 0.5, color='#f0efec', linewidth=0, zorder=0)
bars = a1.bar(x, counts_pop, width=0.85, color=br.colour('popularity'), label=br.label('popularity'), zorder=2)
line, = a1.step(x, counts_rnd, where='mid', color=br.colour('random'), linewidth=1.3, label=br.label('random'), zorder=3)
a1.text((start + x[-1]) / 2, counts_pop.max() * 0.62,
        f'{is_newcomer.sum()} new or small groups:\\npopularity never shows them', ha='center', va='center', fontsize=8.5, color=br.MUTED)
a1.set_xlim(0, x[-1] + 1)
a1.set_ylim(0, counts_pop.max() * 1.08)
a1.set_xlabel(f'The {len(disc)} groups on Discover, biggest to smallest')
a1.set_ylabel(f'Times shown (of {slots:,} slots)')
a1.yaxis.grid(True)
a1.legend(handles=[bars, line], loc='upper center', bbox_to_anchor=(0.42, 1.0))
a1.set_title('Where the slots go')

a2.plot([0, 100], [0, 100], color=br.MUTED, linewidth=0.8)
a2.text(50, 56, 'equal shares', rotation=37, ha='center', va='bottom', fontsize=8, color=br.MUTED,
        rotation_mode='anchor', transform_rotates_text=True)
for m in ['random', 'popularity']:
    fx, fy = br.lorenz_curve(shown[br.label(m)])
    a2.plot(fx * 100, fy * 100, color=br.colour(m), linewidth=2)
gini_txt = {m: t5_table.loc[br.label(m), 'gini'] for m in ['random', 'popularity']}
a2.text(58, 38, f'Random\\nGini {gini_txt["random"]:.2f}', ha='left', va='center', fontsize=8.5)
a2.text(5, 9, f'Popularity: Gini {gini_txt["popularity"]:.2f}', ha='left', va='center', fontsize=8.5)
a2.set_xlim(0, 100)
a2.set_ylim(0, 100)
a2.set_xlabel('Groups, least shown first (%)')
a2.set_ylabel('Share of all slots (%)')
a2.set_title('How unequal')
fig.tight_layout(w_pad=2.5)
br.save_fig(fig, 't5_exposure.png')
plt.show()"""),
md("""## 9 · Checks (T5)"""),
code("""t4_random = {u: [int(g) for g in s] for u, s in suggestions['Random (for comparison)'].items()}
checks = {
    'boingrec rebuilds T4\\'s popularity lists exactly when the "not interested" filter is off':
        br.top_k(br.popularity_scores(vis, tested_users), vis, not_interested=False) == pop,
    'boingrec rebuilds T4\\'s random lists exactly when the "not interested" filter is off':
        br.random_lists(vis, tested_users, not_interested=False) == t4_random,
    'every slot is counted once: 5 per tested user': (shown.sum() == slots).all(),
    'no suggestion is a group the user marked "not interested"':
        not set(zip(vis.not_interested.user_id, vis.not_interested.group_id)) & {(u, g) for u, s in t5_lists['popularity'].items() for g in s},
    'Gini by hand: equal shares give 0': br.gini([3, 3, 3, 3]) == 0,
    'Gini by hand: one of 4 groups gets every slot gives 3/4': abs(br.gini([0, 0, 0, 8]) - 0.75) < 1e-12,
    'new or small: created in the last 30 days or fewer than 10 members':
        newcomers == {g for g in disc if created[g] > br.TODAY - br.NEW_DAYS or n_members[g] < br.SMALL},
    'newcomer share, Gini and largest share are between 0 and 1':
        bool(t5_table[['newcomer_share', 'gini', 'largest_share']].stack().between(0, 1).all()),
    'a recommender never gets a hidden column':
        not {'interests', 'is_fake'} & set(vis.users.columns) and 'topic' not in vis.groups.columns,
}
for check, ok in checks.items():
    print('✓' if ok else '✗', check)
assert all(checks.values()), 'Some checks failed (see ✗ above)'"""),
md("""## What we learned

- **T4:** today's BOING (biggest groups first) finds a hidden group for **22%** of users, against 5% for random suggestions:
  P@5 = 0.044, R@5 = 0.207, NDCG@5 = 0.131.
- **T5:** it shows almost everyone the same few groups. Only **10 of the 129** groups on Discover are ever suggested, the **53 new or small groups
  get 0%** of the 7,030 slots (random suggestions would give them 42%), and the Gini of exposure is **0.953** (random: 0.079).
  Five groups take about 17% of all slots each (the largest, *Japanese in 90 days*, **17.4%**): together, 85% of all slots.
- So ranking by size is both unfair to newcomers and not very relevant. This is the "rich get richer" problem that rule R4 must fix, measured.
- Files: `results/t4_baseline.csv`, `results/t5_exposure.csv`, `results/t5_exposure_per_group.csv`, `figures/t4_hit_rate.png`, `figures/t5_exposure.png`.

**Next:** notebook 04 builds two better recommenders (T6) and the first comparison table (T7)."""),
]
for cell in nb3.cells:                     # keep every cell id; new ones get theirs from nbformat
    if cell.cell_type == 'code' and 'execution_count' not in cell:
        cell.execution_count = None
nbformat.validate(nb3)
nbformat.write(nb3, NB / '03_baseline.ipynb')

# ============================================================================================
# Notebook 04: T6 and T7
# ============================================================================================
cells = [
md("""# 04 · Two better recommenders (T6) and the first comparison table (T7)

**Steps T6 and T7 of the project plan.** Today's BOING suggests the same biggest groups to everyone (notebook 03).
Here we build two recommenders that look at *the user*:

- **"Also joined"** (T6a): people in the groups you are in also joined these groups.
- **Similar descriptions** (T6b): groups whose names and descriptions use the same words as your groups.

Then we score every method on the same quiz (T7): how often it finds the hidden groups, and who gets shown.
This table is the first version of experiment E1 for the report.

Run notebooks 01 and 02 first. The code shared by all notebooks is in `boingrec.py`, in this folder."""),
md("""## 0 · Settings and data"""),
code("""# Colab only: upload sim_v1.zip and sim_v1_split.zip (from notebooks 01 and 02) and boingrec.py (from the notebooks folder),
# all three at once. Locally this cell does nothing.
import sys, zipfile
from pathlib import Path
if 'google.colab' in sys.modules and not Path('boingrec.py').exists():
    from google.colab import files
    for fname in files.upload():
        if fname.endswith('.zip'):
            with zipfile.ZipFile(fname) as z:
                z.extractall('data')"""),
code("""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import boingrec as br

SEED, K = br.SEED, br.K      # 0 and 5, the same in every notebook
br.use_style()

vis = br.load_visible()      # what a recommender may read: no test file, no hidden column
ans = br.load_answers()      # the answer key: only the scoring code below reads it
tested = sorted(ans.test.user_id.unique())
name = vis.groups.set_index('group_id').name
print(f'{len(vis.train)} visible memberships, {len(ans.test)} hidden ones, {len(tested)} users to test, '
      f'{len(br.discover_groups(vis.groups))} groups on Discover')"""),
md("""## 1 · A practice quiz for choosing settings

Some methods have a setting to choose. Choosing it by looking at the test scores would be peeking at the answers.
So we carve a **practice quiz** (a *validation set*) out of the training data, the same way notebook 02 made the test:
users with 3 or more training groups get 20% of them hidden (at least 1), and the posts and likes that would give them away are dropped.
Settings are chosen on the practice quiz; the test is used once, at the end."""),
code("""fit, val = br.val_split(vis)     # fit: the training data minus the practice answers; val: the practice answers
val_users = sorted(val.user_id.unique())
print(f'Practice quiz: {len(val)} memberships hidden for {len(val_users)} users; {len(fit.train)} left to learn from '
      f'({len(vis.posts) - len(fit.posts)} posts and {len(vis.likes) - len(fit.likes)} likes dropped so they give nothing away)')"""),
md("""## 2 · "Also joined" (T6a)

If many members of *Finals countdown* also joined *Midterms countdown*, we suggest Midterms countdown to the Finals members who are not in it yet.

1. A users × groups table of 0s and 1s (1 = member), from the training data.
2. For each pair of groups, the **overlap** (Jaccard) = members in both ÷ members in either: 0 = nobody in common, 1 = the same members.
3. A user's score for a group = the **sum** of its overlaps with each group the user is in. We keep the 5 best groups they can join.

The example below is checked by hand."""),
code("""x = br.membership_matrix(vis)     # users x groups, 0/1
jac = br.jaccard_matrix(vis)      # groups x groups overlaps
a, b = 4, 23                      # Finals countdown and Midterms countdown, two of user 1's groups
both, either = int((x[a] & x[b]).sum()), int((x[a] | x[b]).sum())
print(f'{name[a]}: {x[a].sum()} members; {name[b]}: {x[b].sum()} members; {both} in both, {either} in either')
print(f'Overlap = {both} ÷ {either} = {both / either:.3f}   (boingrec: {jac.loc[a, b]:.3f})')
print(f'\\nThe groups that overlap most with {name[a]}:')
print(jac.loc[a].nlargest(5).rename(name).round(3).to_string())"""),
md("""## 3 · Similar descriptions (T6b)

This one reads the groups' **names and descriptions**, not who joined them, so it also works for a brand-new group nobody has joined yet.

1. **TF-IDF** (scikit-learn's `TfidfVectorizer`, default settings) turns each group's name + description into numbers. A word weighs more when it is
   rare across groups ("Korean") than when it is everywhere ("group", "the").
2. **Cosine similarity** says how alike two texts are: 1 = the same words, 0 = no word in common.
3. A user's score for a group = its **average** similarity to the user's groups.
4. The **topics a user chose to share** (`topics.csv`, for example *exam prep*) can count as one more "group" made of those words.
   How much they count (`topic_weight`) is a setting, chosen on the practice quiz in section 4."""),
code("""sim = br.description_similarity(vis)
g = 47     # Entrance exams accountability group: user 1's hidden group
print(f'"{br.group_texts(vis)[g]}"  is most similar to:')
print(sim.loc[g].drop(g).nlargest(5).rename(name).round(3).to_string())

vectorizer, _ = br.tfidf_model(vis)
topic_words = sorted({w for t in vis.topics.topic.unique() for w in t.split('_')})
known = [w for w in topic_words if w in vectorizer.vocabulary_]
print(f'\\n{vis.topics.user_id.nunique()} users shared topics. Topic words that appear in some group text: {", ".join(known)}.')
print(f'Never in any group text: {", ".join(w for w in topic_words if w not in known)}.')"""),
md("""## 4 · Choosing the setting on the practice quiz

Popularity and "also joined" have nothing to tune. Similar descriptions has one setting: how much the shared topics count
(0 = not at all, 1 = like one more group). We try 0, 0.5, 1 and 2 on the practice quiz and keep the one with the best NDCG@5.
The other methods are scored on the practice quiz too, as a sanity check: it should rank them the same way as the test."""),
code("""TOPIC_WEIGHTS = [0, 0.5, 1, 2]
val_rows = {br.label('random'): br.evaluate(br.random_lists(fit, val_users), val, fit, ans.group_topic),
            br.label('popularity'): br.evaluate(br.top_k(br.popularity_scores(fit, val_users), fit), val, fit, ans.group_topic),
            br.label('also_joined'): br.evaluate(br.top_k(br.also_joined_scores(fit, val_users), fit), val, fit, ans.group_topic)}
for w in TOPIC_WEIGHTS:
    lists_w = br.top_k(br.similar_descriptions_scores(fit, val_users, topic_weight=w), fit)
    val_rows[f'{br.label("descriptions")}, topic weight {w}'] = br.evaluate(lists_w, val, fit, ans.group_topic)
val_table = pd.DataFrame(val_rows).T
br.save_table(val_table, 't6_validation.csv')

ndcg_by_weight = [val_table.loc[f'{br.label("descriptions")}, topic weight {w}', 'ndcg@5'] for w in TOPIC_WEIGHTS]
TOPIC_WEIGHT = TOPIC_WEIGHTS[int(np.argmax(ndcg_by_weight))]       # the best on the practice quiz (ties: the smaller weight)
print(f'Chosen topic weight: {TOPIC_WEIGHT}')
val_table[['hit_rate', 'ndcg@5', 'newcomer_share', 'gini', 'coverage']].round(3)"""),
md("""The shared topics do not help: their words rarely appear in group texts (*coding*, *languages* or *fitness* appear in none), and when they do
they are vague ("exam" is also in the language groups' "a trip or an exam in Korean"). So the best setting on the practice quiz ignores them.
They stay available (`topic_weight`) for members with no group yet (experiment E5), where they are the only clue we have."""),
md("""## 5 · The first comparison table (T7, experiment E1 version 1)

Now the real quiz: each method suggests 5 groups to each of the 1,406 tested users, learning only from the training data,
and we score them against the hidden test memberships with the measures of T4 and T5.

| Column | Meaning |
|---|---|
| hit_rate | share of users with at least one right suggestion |
| precision@5, recall@5, ndcg@5 | as in notebook 03 |
| newcomer_share | share of all slots that go to new or small groups (R4) |
| gini | how unequal the slots are across the 129 groups on Discover (0 = equal) |
| coverage | how many different groups are ever shown |
| largest_share | share of all slots taken by the most-shown group (R4's cap) |
| topics_per_list | how many different topics a list of 5 covers (R5; uses the hidden topics, so only for scoring) |"""),
code("""ORDER = ['random', 'popularity', 'also_joined', 'descriptions']
test_lists = {
    'random': br.random_lists(vis, tested),
    'popularity': br.top_k(br.popularity_scores(vis, tested), vis),
    'also_joined': br.top_k(br.also_joined_scores(vis, tested), vis),
    'descriptions': br.top_k(br.similar_descriptions_scores(vis, tested, topic_weight=TOPIC_WEIGHT), vis),
}
e1 = pd.DataFrame({br.label(m): br.evaluate(test_lists[m], ans.test, vis, ans.group_topic) for m in ORDER}).T
e1[['users', 'coverage']] = e1[['users', 'coverage']].astype(int)
br.save_table(e1, 'e1_v1.csv')
e1.round(3)"""),
md("""**How sure are we?** An average over 1,406 users still depends a little on which users happen to be tested. The ranges below (95%,
from resampling the users 2,000 times) show which differences are real. The random floor also moves with the seed: we redraw it 20 times."""),
code("""per_user = {m: br.relevance_per_user(test_lists[m], ans.test) for m in ORDER}
ci_rows = {}
for m in ORDER:
    row = {}
    for metric in ['hit_rate', 'ndcg@5']:
        low, high = br.bootstrap_ci(per_user[m][metric])
        row.update({metric: per_user[m][metric].mean(), f'{metric} low': low, f'{metric} high': high})
    ci_rows[br.label(m)] = row
ci = pd.DataFrame(ci_rows).T
br.save_table(ci, 'e1_v1_ci.csv')

floor = pd.Series([br.evaluate(br.random_lists(vis, tested, seed=s), ans.test, vis)['hit_rate'] for s in range(20)])
print(f'Random floor over 20 seeds: hit rate {floor.mean():.3f} on average, from {floor.min():.3f} to {floor.max():.3f}')
ci.round(3)"""),
md("""## 6 · The chart

Relevance (NDCG@5) and the newcomer share, side by side, with the same colour for each method as in every other figure."""),
code("""labels = [br.label(m) for m in ORDER]
y = np.arange(len(ORDER))[::-1]                       # first method at the top
panels = [('ndcg@5', 'Relevance (NDCG@5)', 'NDCG@5 (1 = perfect)', '{:.3f}'),
          ('newcomer_share', 'Slots for new or small groups', 'Newcomer share', '{:.0%}')]
fig, axes = plt.subplots(1, 2, figsize=(br.WIDTH, 2.25), sharey=True)
for ax, (col, title, xlabel, fmt) in zip(axes, panels):
    values = e1.loc[labels, col].to_numpy()
    ax.barh(y, values, height=0.56, color=[br.colour(m) for m in ORDER])
    for yi, v in zip(y, values):
        ax.text(v + values.max() * 0.02, yi, fmt.format(v), va='center', fontsize=8.5, color=br.INK)
    ax.set_xlim(0, values.max() * 1.22)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.xaxis.grid(True)
    ax.tick_params(axis='y', length=0)
axes[0].set_yticks(y, labels)
axes[1].xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
fig.tight_layout(w_pad=2)
br.save_fig(fig, 't7_comparison.png')
plt.show()"""),
md("""## 7 · An example: user 1

User 1 again (the example of T3 and T4): every method sees the same four groups and must guess the hidden one."""),
code("""br.print_example(1, {m: test_lists[m] for m in ['popularity', 'also_joined', 'descriptions']}, vis, ans.test)"""),
md("""No method finds *Entrance exams accountability group* in its top 5 here, but the lists are no longer the same for everyone:
"also joined" offers two other exam groups (*SAT prep squad*, *MCAT countdown*), because members of Finals countdown and Midterms countdown often joined them.
Similar descriptions follows words: *Better Journaling* matches Journaling streak, *Beat the Finals* matches Finals countdown, and three language groups
share Korean conversation club's description ("Getting ready for a trip or an exam in ...? Practise here.")."""),
md("""## 8 · Checks"""),
code("""from sklearn.metrics import ndcg_score

gids = br.group_ids(vis)
hidden = ans.test.groupby('user_id').group_id.apply(set)
t4 = pd.read_csv(br.RESULTS / 't4_baseline.csv', index_col=0)
allowed = br.candidate_mask(vis, tested)

def ndcg_sklearn(suggested, hidden_set):
    # scikit-learn's NDCG@5: true relevance 1 for the hidden groups; scores 5, 4, ..., 1 for the 5 suggestions, 0 elsewhere
    y_true = np.isin(gids, list(hidden_set)).astype(float)
    y_score = np.zeros(len(gids))
    y_score[np.searchsorted(gids, suggested)] = np.arange(len(suggested), 0, -1)
    return ndcg_score([y_true], [y_score], k=K)

with_hit = [u for u in tested if hidden[u] & set(test_lists['also_joined'][u])]
some = with_hit[:20] + tested[:20]
full = pd.concat([vis.train, ans.test]).sort_values(['user_id', 'group_id']).reset_index(drop=True)
again_train, again_test = br.split_memberships(full, vis.users, vis.groups)
pairs = lambda df: set(zip(df.user_id, df.group_id))
like_pairs = set(zip(fit.likes.user_id, fit.likes.post_id.map(fit.posts.set_index('post_id').group_id)))
again = {'random': br.random_lists(vis, tested),
         'also_joined': br.top_k(br.also_joined_scores(vis, tested), vis),
         'descriptions': br.top_k(br.similar_descriptions_scores(vis, tested, topic_weight=TOPIC_WEIGHT), vis)}
toy = br.popularity_scores(vis, [1]) * 0            # every score equal

checks = {
    'every tested user gets exactly 5 different groups from every method':
        all(len(set(lists[u])) == K == len(lists[u]) for lists in test_lists.values() for u in tested),
    'every suggestion is allowed: on Discover, not joined, not marked "not interested"':
        all(allowed.loc[u, g] for lists in test_lists.values() for u in tested for g in lists[u]),
    'our NDCG@5 equals scikit-learn\\'s ndcg_score (40 users, every method)':
        all(abs(br.relevance(lists[u], hidden[u])['ndcg@5'] - ndcg_sklearn(lists[u], hidden[u])) < 1e-12
            for lists in test_lists.values() for u in some),
    'popularity gives exactly the T4 scores': (e1.loc['Popularity (today)', br.RELEVANCE].round(3) == t4.loc['Popularity (today)', br.RELEVANCE]).all(),
    'the overlap example matches the hand count': abs(jac.loc[a, b] - both / either) < 1e-12,
    'equal scores: the smaller group id comes first': br.top_k(toy, vis)[1] == br.candidates(vis, 1)[:K],
    'a recommender never gets a hidden column or a test membership':
        not {'interests', 'is_fake'} & set(vis.users.columns) and 'topic' not in vis.groups.columns
        and not pairs(vis.train) & pairs(ans.test),
    'boingrec\\'s split rebuilds notebook 02\\'s test set exactly': again_test.equals(ans.test) and again_train.equals(vis.train),
    'practice quiz: its answers come from the training data, and are not visible any more':
        pairs(val) <= pairs(vis.train) and not pairs(val) & pairs(fit.train) and len(fit.train) + len(val) == len(vis.train),
    'practice quiz: no post or like gives a practice answer away':
        not pairs(fit.posts[fit.posts.group_id > 0]) & pairs(val) and not like_pairs & pairs(val),
    'the practice quiz ranks the methods like the test (by NDCG@5)':
        list(val_table.loc[[br.label(m) for m in ORDER[:3]] + [f'{br.label("descriptions")}, topic weight {TOPIC_WEIGHT}'], 'ndcg@5'].rank())
        == list(e1['ndcg@5'].rank()),
    'same seed, same results: running the methods again gives the same lists': all(again[m] == test_lists[m] for m in again),
}
for check, ok in checks.items():
    print('✓' if ok else '✗', check)
assert all(checks.values()), 'Some checks failed (see ✗ above)'"""),
md("""## What we learned

- **"Also joined" is by far the most relevant.** It finds a hidden group for **64%** of users (popularity 22%, random 5%), with NDCG@5 = **0.499**
  against 0.131 for popularity (95% ranges 0.476–0.522 and 0.117–0.146). But it shows newcomers little: **2.7%** of slots go to new or small groups,
  the Gini of exposure is 0.599, and 94 of the 129 groups are ever shown.
- **Similar descriptions is the fairest, but only a little more relevant than popularity:** NDCG@5 = **0.159** (hit rate 26%), with **41.6%** of slots
  for new or small groups (as many as random suggestions), a Gini of 0.502 and 125 groups shown. It can suggest a group nobody has joined yet.
- **Both personal methods narrow the lists** to about 2 topics in 5 suggestions (popularity 3.2, random 4.1). Rule R5 (at most *n* per topic) is there for this.
- The topics members shared did not help on the practice quiz (topic weight 0 was chosen): their words rarely appear in group texts.
- **A caution for the report:** the hidden answers come from a simulator in which bigger groups attract more joins, so only 2.7% of the hidden memberships
  are in new or small groups. A quiz like this rewards favouring big groups, so it understates what showing newcomers is worth.
- **The tension for E2:** the most relevant method is also the one that shows newcomers least. Next: the hidden-tastes model (T9), a hybrid,
  and a re-ranker that reserves *q*% of the slots for new or small groups.
- Files: `results/e1_v1.csv` (the table), `results/e1_v1_ci.csv` (the 95% ranges), `results/t6_validation.csv` (the practice quiz), `figures/t7_comparison.png`."""),
]
nb4 = new_notebook(cells=cells, metadata=nb3.metadata)
nbformat.validate(nb4)
nbformat.write(nb4, NB / '04_methods.ipynb')
print('built 03 (T5) and 04 (T6, T7)')
