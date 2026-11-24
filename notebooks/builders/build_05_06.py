"""Builds notebooks/05_ai_model.ipynb (T9) and notebooks/06_hybrid_rerank.ipynb (hybrid, re-ranking, reasons,
personalisation off, and the full E1 table).

Run with the project's venv python:  python build_05_06.py      (then run_nb.py to execute them)
Idempotent: both notebooks are rewritten from scratch.
"""
from pathlib import Path
import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

NB = Path('C:/Users/houar/Desktop/2027/HOPPY/Bs/ECSE557/notebooks')
md, code = new_markdown_cell, new_code_cell
metadata = nbformat.read(NB / '04_methods.ipynb', as_version=4).metadata

COLAB = r"""# Colab only: upload sim_v1.zip and sim_v1_split.zip (from notebooks 01 and 02) and boingrec.py (from the notebooks folder),
# all three at once. Locally this cell does nothing.
import sys, zipfile
from pathlib import Path
if 'google.colab' in sys.modules and not Path('boingrec.py').exists():
    from google.colab import files
    for fname in files.upload():
        if fname.endswith('.zip'):
            with zipfile.ZipFile(fname) as z:
                z.extractall('data')"""

# ============================================================================================
# Notebook 05: T9, the AI model
# ============================================================================================
nb5 = [
md("""# 05 · The AI model: hidden tastes (T9)

**Step T9 of the project plan.** This is the clearly-AI part of the project. The model looks only at who joined which groups and learns, by itself,
a short list of *hidden tastes*: patterns such as "people who join exam groups also join other exam groups". Nobody tells it the topics.
A user's score for a group is how well the group fits the tastes of the user's groups. This family of methods (matrix factorisation) won the Netflix Prize.

What this notebook does:

1. learns the tastes with an exact method that BOING's JavaScript can redo, and checks that it gives the same scores as scikit-learn's `TruncatedSVD`;
2. chooses the number of tastes on the practice quiz, then scores the model on the test, like the other methods (notebook 04);
3. the **nice check**: do the tastes match the real topics, which the model never saw? If they do, the AI found people's interests without being told:
   exactly the profiling the ethics part of the project is about;
4. shows how each suggestion gets an honest reason ("Because you're in Daily coding").

Run notebooks 01 and 02 first. The code shared by all notebooks is in `boingrec.py`, in this folder."""),
md("""## 0 · Settings and data"""),
code(COLAB),
code(r"""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import boingrec as br

SEED, K = br.SEED, br.K          # 0 and 5, the same in every notebook
K_CHOICES = [5, 10, 20, 40]      # numbers of hidden tastes to try (the plan says 5, 10 and 20; we add 40)
br.use_style()

vis = br.load_visible()          # what a recommender may read: no test file, no hidden column
ans = br.load_answers()          # the answer key: only the scoring code reads it (sections 3 to 5)
tested = sorted(ans.test.user_id.unique())
gids = br.group_ids(vis)
name = vis.groups.set_index('group_id').name
print(f'{len(vis.train)} visible memberships, {len(ans.test)} hidden ones, {len(tested)} users to test, '
      f'{len(gids)} groups ({len(br.discover_groups(vis.groups))} on Discover)')"""),
md("""## 1 · How the model learns tastes

1. **X** is the users × groups table of 0s and 1s from the training data (1 = member), as in notebook 04.
2. **X<sup>T</sup>X** is a groups × groups table: how many members each pair of groups shares. On its diagonal: each group's size.
3. **The tastes** are the strongest patterns in that table (its *eigenvectors*). A taste gives every group a number, its *loading*:
   far from 0 for groups that tend to be joined together. We keep the *k* strongest; their *strength* says how much of the table each one explains.
4. **A user's scores** = the user's row of X projected on the tastes: X V V<sup>T</sup>, where the columns of V are the tastes.
   Groups that fit the tastes of the user's own groups get high scores; we keep the 5 best the user can join.

The plan names scikit-learn's `TruncatedSVD`, which finds the same tastes with an iterative method. We use `numpy.linalg.eigh` instead: it is exact,
gives the same answer every time, and is easy to port to JavaScript for BOING. Section 2 checks that both give the same scores.

Note for the privacy part: the model needs nothing about other members except X<sup>T</sup>X, a count of shared members.
That is the table rule R10 will protect with noise (experiment E3)."""),
code(r"""X = br.membership_matrix(vis)                   # users x groups, 0/1 (training data)
gram = X.T @ X                                  # groups x groups: members each pair of groups shares
a, b = 4, 23                                    # Finals countdown and Midterms countdown, two of user 1's groups
print(f'X: {X.shape[0]} users x {X.shape[1]} groups, {int(X.to_numpy().sum())} memberships')
print(f'X^T X for {name[a]} and {name[b]}: {gram.loc[a, b]} members in both. '
      f'For {name[a]} with itself: {gram.loc[a, a]}, its size.')

strength10, tastes10 = br.taste_model(gram.to_numpy(), k=10)
print('\nStrength of the 10 strongest tastes:', ', '.join(str(int(round(s))) for s in strength10))
print('Each group gets one loading per taste, for example:')
pd.DataFrame(tastes10, index=gids, columns=pd.Index(range(1, 11), name='taste')).loc[[4, 7, 10]].rename(index=name).round(2)"""),
md("""## 2 · The same as scikit-learn's `TruncatedSVD`

For each number of tastes we compute every tested user's scores both ways and look at the largest difference.
`TruncatedSVD(algorithm='arpack')` is fitted on the same X; its scores are `transform(X) @ components_`.
Its *singular values*, squared, should equal our strengths."""),
code(r"""from sklearn.decomposition import TruncatedSVD

x_all = X.to_numpy(dtype=float)
x_tested = br.membership_matrix(vis, tested).to_numpy(dtype=float)
same_rows = {}
for k in K_CHOICES:
    ours = br.hidden_tastes_scores(vis, tested, k=k).to_numpy()
    svd = TruncatedSVD(n_components=k, algorithm='arpack', random_state=SEED).fit(x_all)
    theirs = svd.transform(x_tested) @ svd.components_
    strength_k, _ = br.taste_model(gram.to_numpy(), k)
    same_rows[f'{k} tastes'] = {
        'largest score difference': np.abs(ours - theirs).max(),
        'largest score': np.abs(ours).max(),
        'largest strength difference (relative)': np.abs(strength_k - svd.singular_values_ ** 2).max() / strength_k.max()}
same = pd.DataFrame(same_rows).T
same.map(lambda v: f'{v:.1e}')"""),
md("""The scores agree to about 10<sup>-14</sup>, the rounding error of a computer: it is the same model."""),
md("""## 3 · How many tastes? The practice quiz decides

As in notebook 04, settings are chosen on a **practice quiz** carved from the training data (users with 3 or more training groups get 20% hidden),
never on the test. We try 5, 10, 20 and 40 tastes and keep the best NDCG@5."""),
code(r"""fit, val = br.val_split(vis)       # fit: the training data minus the practice answers; val: the practice answers
val_users = sorted(val.user_id.unique())
val_rows = {}
for k in K_CHOICES:
    lists_k = br.top_k(br.hidden_tastes_scores(fit, val_users, k=k), fit)
    val_rows[f'{k} tastes'] = br.evaluate(lists_k, val, fit, ans.group_topic)
val_table = pd.DataFrame(val_rows).T
val_table[['users', 'coverage']] = val_table[['users', 'coverage']].astype(int)
br.save_table(val_table, 't9_validation.csv')

TASTES = K_CHOICES[int(np.argmax(val_table['ndcg@5'].to_numpy()))]    # ties: the fewer tastes
t6 = pd.read_csv(br.RESULTS / 't6_validation.csv', index_col=0)
print(f'Chosen: {TASTES} tastes (boingrec.TASTES = {br.TASTES}). On the same practice quiz, NDCG@5 of "also joined" = '
      f'{t6.loc[br.label("also_joined"), "ndcg@5"]:.3f}, popularity = {t6.loc[br.label("popularity"), "ndcg@5"]:.3f}.')
val_table[['hit_rate', 'ndcg@5', 'newcomer_share', 'gini', 'coverage']].round(3)"""),
md("""**Ten tastes** work best. With 5, the model only knows the broadest patterns. With more, it starts to copy each user's own groups back
(with as many tastes as groups, X V V<sup>T</sup> = X exactly), and those groups can't be suggested: at 40 tastes it is no better than popularity
(NDCG@5 0.119 against 0.122).
On the practice quiz the AI model is good, but not as good as "also joined"."""),
md("""## 4 · The test: the AI model in the comparison table

The real quiz, once, with 10 tastes learned from all the training data. The other rows are notebook 04's table (E1, version 1)."""),
code(r"""strength, tastes = br.taste_model(gram.to_numpy(), TASTES)
scores = br.hidden_tastes_scores(vis, tested, k=TASTES)
test_lists = br.top_k(scores, vis)
row = br.evaluate(test_lists, ans.test, vis, ans.group_topic)
per_user = br.relevance_per_user(test_lists, ans.test)
for metric in ['hit_rate', 'ndcg@5']:
    row[f'{metric} low'], row[f'{metric} high'] = br.bootstrap_ci(per_user[metric])
row['tastes'] = TASTES
t9 = row.to_frame(br.label('hidden_tastes')).T
t9[['users', 'coverage', 'tastes']] = t9[['users', 'coverage', 'tastes']].astype(int)
br.save_table(t9, 't9_ai_model.csv')

e1_v1 = pd.read_csv(br.RESULTS / 'e1_v1.csv', index_col=0)
print(f'NDCG@5 of the AI model: {row["ndcg@5"]:.3f} (95% range {row["ndcg@5 low"]:.3f} to {row["ndcg@5 high"]:.3f})')
pd.concat([e1_v1, t9[e1_v1.columns]]).round(3)"""),
md("""**Who gets shown.** The AI model is far more relevant than popularity, close to "also joined", and it shows 76 different groups instead of 10.
But it gives new or small groups even fewer slots than "also joined": a group needs members before the model can learn where it fits,
and its first taste is simply group size (section 5). So it favours established groups much like "also joined" does,
though far less than popularity (Gini 0.645 against 0.953)."""),
md("""## 5 · The nice check: did the AI find the topics nobody told it?

Each taste has **two ends**: the groups with the highest loadings and the groups with the lowest (most negative) ones.
For each end we take its 10 groups and count their **hidden topics**, the answer key from notebook 01 (scoring code only: the model never saw them).
If one topic dominates an end, the model discovered that topic by itself. For comparison, 10 groups drawn at random share their most common topic
about 3 times in 10 (computed below)."""),
code(r"""topic = ans.group_topic.reindex(gids)               # scoring code only: the hidden topics
TOPICS = sorted(topic.unique())
TOP = 10
size = br.group_sizes(vis)
pole_rows = []
for t in range(TASTES):
    loading = pd.Series(tastes[:, t], index=gids)
    ends = [('+', loading)] + ([('-', -loading)] if t > 0 else [])   # taste 1 has one end: every loading is >= 0
    for end, values in ends:
        top = values.sort_values(ascending=False, kind='stable').index[:TOP]
        counts = topic[top].value_counts().sort_index().sort_values(ascending=False, kind='stable')
        pole_rows.append({'taste': t + 1, 'end': end, 'main topic': counts.index[0], 'share': counts.iloc[0] / TOP,
                          'top groups': ', '.join(name[top[:4]]), **{tp: int(counts.get(tp, 0)) for tp in TOPICS}})
poles = pd.DataFrame(pole_rows)
poles.to_csv(br.RESULTS / 't9_tastes.csv', index=False)

rng = np.random.default_rng(SEED)
joined = gids[size.to_numpy() > 0]
chance = np.mean([topic[rng.choice(joined, TOP, replace=False)].value_counts().iloc[0] / TOP for _ in range(2000)])
best_per_topic = poles[TOPICS].max().sort_values(ascending=False)
size_corr = np.corrcoef(tastes[:, 0], size.to_numpy())[0, 1]
print(f'Taste 1 follows group size: correlation {size_corr:.2f} between its loadings and the groups\' sizes.')
print(f'Chance: 10 random groups share their most common topic {chance * TOP:.1f} times in 10 on average.')
print('Best end for each hidden topic (groups of 10 in that topic):',
      ', '.join(f'{tp} {n}' for tp, n in best_per_topic.items()))
poles[['taste', 'end', 'main topic', 'share', 'top groups']]"""),
code(r"""def short(text, n=26):
    return text if len(text) <= n else text[:n - 1] + '…'

heat = poles[TOPICS].to_numpy()
row_labels = ['1   group size' if r.taste == 1 else
              f'{r.taste}{"+" if r.end == "+" else "−"}  {short(r["top groups"].split(", ")[0])}' for _, r in poles.iterrows()]
fig, ax = plt.subplots(figsize=(br.WIDTH, 4.9))
im = ax.imshow(heat, cmap='Blues', vmin=0, vmax=TOP, aspect='auto')
for (r, c), v in np.ndenumerate(heat):
    if v > 0:
        ax.text(c, r, v, ha='center', va='center', fontsize=7.5, color='white' if v >= 6 else br.INK)
ax.set_xticks(range(len(TOPICS)), [tp.replace('_', ' ') for tp in TOPICS], rotation=35, ha='right')
ax.set_yticks(range(len(row_labels)), row_labels)
ax.tick_params(length=0)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_xlabel('Hidden topic of the group (the answer key: the model never saw it)')
ax.set_ylabel('Learned taste and end (+ or −), with its top group')
ax.set_title('Each learned taste picks out a hidden topic')
cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label('Of the end\'s 10 top groups, how many are in the topic')
cbar.outline.set_visible(False)
fig.tight_layout()
br.save_fig(fig, 't9_tastes.png')
plt.show()"""),
md("""**Yes, it found them.** Taste 1 is group size. Most other ends are dominated by one hidden topic, far above chance:
one end of taste 2 is 10 language groups out of 10, and fitness, coding, music and art each fill 7 to 9 of the 10 groups at some end.
The model was never told any topic: it inferred them from who joins what. That is the profiling the ethics part is about.
It is accurate, but it learns things about members they never said, so rules R1 (opt-in) and R10 (noise on the counts) apply to it.
Physics is the topic it finds least, probably because its groups are few and small, so they leave little trace in X<sup>T</sup>X."""),
md("""## 6 · Why this suggestion? An honest reason

A user's score for group *g* is a sum over the user's own groups *j* of (V V<sup>T</sup>)[*j*, *g*]: how strongly the model links *j* to *g*.
So the score splits exactly into one contribution per group the user is in, and the largest one is a true reason:
"Because you're in *j*". Here is user 1's first suggestion."""),
code(r"""links = br.taste_links(tastes, gids)                   # V V^T: groups x groups
u = 1
mine = sorted(vis.train.group_id[vis.train.user_id == u])
g = test_lists[u][0]
adds = links.loc[mine, g]
print(f'User {u}\'s first suggestion: {name[g]}, score {scores.loc[u, g]:.4f}')
print(f'Sum of the contributions below: {adds.sum():.4f}')
print(f'Reason shown: "Because you\'re in {name[adds.idxmax()]}"\n')
adds.rename(index=name).sort_values(ascending=False).round(4).to_frame('adds to the score')"""),
md("""## 7 · Checks"""),
code(r"""all_strengths = np.sort(np.linalg.eigvalsh(gram.to_numpy(dtype=float)))[::-1]
allowed = br.candidate_mask(vis, tested)
again = br.top_k(br.hidden_tastes_scores(vis, tested, k=TASTES), vis)
pairs = lambda df: set(zip(df.user_id, df.group_id))

checks = {
    'our scores equal scikit-learn TruncatedSVD (arpack) for every k (difference below 1e-9)':
        bool((same['largest score difference'] < 1e-9).all()),
    'our strengths equal TruncatedSVD\'s singular values squared': bool((same['largest strength difference (relative)'] < 1e-9).all()),
    'the tastes are orthonormal (length 1, at right angles to each other)': np.allclose(tastes.T @ tastes, np.eye(TASTES)),
    'the tastes are well defined: the 10th and 11th strengths differ':
        all_strengths[TASTES - 1] - all_strengths[TASTES] > 1e-6 * all_strengths[0],
    'every score is exactly the sum of its contributions (the reasons add up)':
        np.allclose(x_tested @ links.to_numpy(), scores.to_numpy()),
    'every tested user gets 5 different groups, all allowed (on Discover, not joined, not "not interested")':
        all(len(set(test_lists[u])) == K and all(allowed.loc[u, g] for g in test_lists[u]) for u in tested),
    'boingrec.TASTES is the number chosen on the practice quiz': TASTES == br.TASTES,
    'same seed, same results: running it again gives the same lists': again == test_lists,
    'a recommender never gets a hidden column or a test membership':
        not {'interests', 'is_fake'} & set(vis.users.columns) and 'topic' not in vis.groups.columns
        and not pairs(vis.train) & pairs(ans.test),
}
for check, ok in checks.items():
    print('✓' if ok else '✗', check)
assert all(checks.values()), 'Some checks failed (see ✗ above)'"""),
md("""## What we learned

- **The AI model** (matrix factorisation with **10 hidden tastes**, chosen on the practice quiz from 5, 10, 20 and 40) finds a hidden group for **61%**
  of users on the test, with NDCG@5 = **0.475** (95% range 0.452 to 0.496): far above popularity (0.131), a little below "also joined" (0.499).
- Our exact method (`numpy.linalg.eigh` on X<sup>T</sup>X) gives the same scores as scikit-learn's `TruncatedSVD` to about 10<sup>-14</sup>,
  so BOING's JavaScript can redo it.
- **It favours established groups:** only **0.5%** of its slots go to new or small groups (also joined: 2.7%, popularity: 0%), with a Gini of 0.645
  and 76 groups ever shown. Its first taste is group size (correlation 0.96).
- **The nice check:** without being told any topic, it found them. Most ends of its tastes are dominated by one hidden topic (10 of 10 language groups,
  9 of 10 fitness groups, 8 of 10 coding, 8 of 10 music), where chance gives about 3 of 10. It profiles members' interests from what they join,
  which is why it needs the opt-in (R1) and the privacy noise (R10).
- **Explanations:** each score is exactly a sum of contributions from the user's own groups, so "Because you're in X" is a true reason (R6).
- Files: `results/t9_validation.csv` (the practice quiz), `results/t9_ai_model.csv` (the test row), `results/t9_tastes.csv` (the nice check),
  `figures/t9_tastes.png`.

**Next:** notebook 06 mixes the four scores into a hybrid, adds the fair re-ranking, the reasons and the list for members who keep personalisation off,
and makes the full comparison table (E1)."""),
]

# ============================================================================================
# Notebook 06: hybrid, re-ranking, reasons, personalisation off, E1
# ============================================================================================
nb6 = [
md("""# 06 · The proposed recommender, and the full comparison (E1)

**Experiment E1 of the project plan**, with the parts it needs (steps 4, 5 and 8 of the plan's list of algorithms):

- a **hybrid** that mixes four scores: "also joined", similar descriptions, the hidden tastes of notebook 05, and a new one, **friends**;
- a **fair re-ranking** that keeps at least one slot in five for new or small groups (rule R4), no more than 2 groups of one topic per list (R5),
  and no group with more than 10% of all slots (R4);
- an **honest reason** for every suggestion (R6);
- the list members see **with personalisation off**, the default (R1): no profile, only recent activity and newness.

Then every method is scored on the test, the comparison table and chart for the report (E1).
All of it sits behind one function, `br.recommend(user_ids, data, config)`, which the experiments E2 to E6 call with other settings.

Run notebooks 01, 02 and 05 first. The code shared by all notebooks is in `boingrec.py`, in this folder."""),
md("""## 0 · Settings and data

`br.Config()` holds every setting of the proposed design. Its defaults are the choices made on the practice quiz in this notebook and in notebook 05;
the checks at the end make sure they match."""),
code(COLAB),
code(r"""import itertools
import json
from dataclasses import asdict, replace
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import boingrec as br

SEED, K = br.SEED, br.K          # 0 and 5, the same in every notebook
br.use_style()
cfg = br.Config()                # the proposed design

vis = br.load_visible()          # what a recommender may read: no test file, no hidden column
ans = br.load_answers()          # the answer key: only the scoring code reads it
tested = sorted(ans.test.user_id.unique())
gids = br.group_ids(vis)
name = vis.groups.set_index('group_id').name
print(f'{len(vis.train)} visible memberships, {len(ans.test)} hidden ones, {len(tested)} users to test')
pd.Series(asdict(cfg), dtype=object).to_frame('setting').T"""),
md("""## 1 · The practice quiz

The same practice quiz as notebooks 04 and 05: 20% of the training groups of users with 3 or more are hidden. Every setting below is chosen on it."""),
code(r"""fit, val = br.val_split(vis)
val_users = sorted(val.user_id.unique())
stats_fit = br.stats_for(fit, cfg)        # the statistics about other members, from the practice training data
print(f'Practice quiz: {len(val)} memberships hidden for {len(val_users)} users; {len(fit.train)} left to learn from')"""),
md("""## 2 · Statistics about other members, in one place

Everything the recommender knows about *other* members comes from one function, `br.group_stats()`: the group sizes, how many members each pair of
groups shares (X<sup>T</sup>X, used by "also joined" **and** by the AI model), and each group's recent activity. The rules about whose data counts act there,
so they reach every part at once:

- **R8:** suspended accounts never count;
- **R9:** only accounts at level *L* or more count (here *L* = 1, everyone; experiment E4 raises it and down-weights bursts of joins);
- **R10:** each member's contribution can be capped and the counts get noise (off here; experiment E3 turns it on).

With the suspended accounts left out, the "also joined" and AI-model scores are exactly those of notebooks 04 and 05."""),
code(r"""stats = br.stats_for(vis, cfg)            # from all the training data, for the test
suspended = vis.users.user_id[vis.users.suspended == 1]
print(f'{len(stats.counted)} of {len(vis.users)} accounts count: the {len(suspended)} suspended ones never do '
      f'(they hold {vis.train.user_id.isin(suspended).sum()} of the {len(vis.train)} memberships).')
print(f'{len(stats.newcomers)} of the {len(gids)} groups are new (created in the last {br.NEW_DAYS} days) or small (fewer than '
      f'{br.SMALL} members); {len(stats.newcomers & set(br.discover_groups(vis.groups)))} of them are on Discover.')

no_suspended = replace(vis, train=vis.train[~vis.train.user_id.isin(suspended)])
raw = br.raw_parts(vis, tested, cfg, stats)
diff_cf = np.abs(raw['cf'] - br.also_joined_scores(no_suspended, tested)).to_numpy().max()
diff_mf = np.abs(raw['mf'] - br.hidden_tastes_scores(no_suspended, tested, k=cfg.k)).to_numpy().max()
print(f'Largest difference from "also joined" (notebook 04): {diff_cf:.1e}; from the AI model (notebook 05): {diff_mf:.1e}')"""),
md("""## 3 · A fourth score: friends

A user's **friends** score for a group = how many of the user's friends are members. Only friends who may be counted and named (R6, R8):

- the friend's profile is **public** (a private profile is never counted, not even as a number);
- the friend's account counts (not suspended; level *L* or more);
- neither of the two has **blocked** the other."""),
code(r"""f = vis.friendships
links = pd.concat([pd.DataFrame({'user_id': f.user_a, 'friend_id': f.user_b}),
                   pd.DataFrame({'user_id': f.user_b, 'friend_id': f.user_a})])
user = vis.users.set_index('user_id')
blocked = set(zip(vis.blocks.user_id, vis.blocks.blocked_id)) | set(zip(vis.blocks.blocked_id, vis.blocks.user_id))
ok = br.public_friends(vis, user.index, stats.counted)
print(f'{len(f)} friendships, so {len(links)} links "my friend": {len(ok)} may count.')
print(f'Left out: {(user.privacy[links.friend_id].to_numpy() == "private").sum()} links to a private profile, '
      f'{(user.suspended[links.friend_id].to_numpy() == 1).sum()} to a suspended account, '
      f'{sum((u, v) in blocked for u, v in zip(links.user_id, links.friend_id))} between people who blocked each other.')

social = br.social_scores(vis, [1], stats.counted).iloc[0]
mine = links.friend_id[links.user_id == 1]
print(f'\nUser 1 has {len(mine)} friends; {len(ok[ok.user_id == 1])} have a public profile and count. Their groups:')
social[social > 0].sort_values(ascending=False, kind='stable').rename(index=name).astype(int).to_frame('public friends in it').head(8)"""),
md("""## 4 · The hybrid: mixing the four scores

The four scores have different scales (a sum of overlaps, an average similarity, a count of friends, a projection), so each is first **rescaled per user**
to 0-1 over the user's candidates (the best candidate gets 1, the worst 0). Then

  *s* = α · "also joined" + β · similar descriptions + γ · friends + δ · AI model.

Only the proportions matter, so the weights add up to 1. We try **every split in steps of 0.1** (286 mixes) on the practice quiz and keep the best NDCG@5.
The table shows the 10 best mixes, then each score alone."""),
code(r"""parts = br.hybrid_parts(fit, val_users, cfg, stats_fit)     # the four scores, rescaled to 0-1 per user
WEIGHTS = ['alpha', 'beta', 'gamma', 'delta']
STEP = 10
grid = [tuple(w / STEP for w in ws) for ws in itertools.product(range(STEP + 1), repeat=4) if sum(ws) == STEP]
grid_rows = []
for w in grid:
    r = br.evaluate(br.top_k(br.hybrid_scores(parts, weights=w), fit), val, fit, ans.group_topic)
    grid_rows.append({**dict(zip(WEIGHTS, w)), **r.drop('users').to_dict()})
hybrid_grid = pd.DataFrame(grid_rows).astype({'coverage': int}).sort_values('ndcg@5', ascending=False, kind='stable')
hybrid_grid.index = pd.RangeIndex(1, len(hybrid_grid) + 1, name='rank')
br.save_table(hybrid_grid, 'hybrid_validation.csv', decimals=4)

best = tuple(hybrid_grid.iloc[0][WEIGHTS])
alone = hybrid_grid[(hybrid_grid[WEIGHTS] == 1).any(axis=1)]
best_lists = br.top_k(br.hybrid_scores(parts, weights=best), fit)
low, high = br.bootstrap_ci(br.relevance_per_user(best_lists, val)['ndcg@5'])
print(f'Best mix: alpha = {best[0]}, beta = {best[1]}, gamma = {best[2]}, delta = {best[3]} '
      f'(boingrec.Config: {cfg.alpha}, {cfg.beta}, {cfg.gamma}, {cfg.delta}); its 95% range: {low:.3f} to {high:.3f}')
pd.concat([hybrid_grid.head(10), alone])[WEIGHTS + ['hit_rate', 'ndcg@5', 'newcomer_share', 'gini', 'coverage']].round(3)"""),
md("""The best mix leans on **"also joined" and friends**, with a little of the AI model and of similar descriptions. It beats each score alone on the practice
quiz. The top 10 mixes are within a few thousandths of each other, less than the uncertainty of the quiz itself, so the exact weights matter little;
what matters is that mixing helps. The hybrid still shows newcomers almost nothing (about 2% of slots): that is the re-ranker's job."""),
md("""## 5 · Public topics, for rule R5

Rule R5 limits how many groups of one topic a list may hold. The recommender may not read the hidden topics, so it makes its own **public topics**:
it sorts the groups into 10 clusters by the words of their names and descriptions (KMeans on the TF-IDF vectors of notebook 04, seed 0).
The scoring code then checks how well these clusters match the hidden topics: *purity* is the share of groups that belong to their cluster's main topic."""),
code(r"""from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

clusters = br.topic_clusters(vis, cfg.clusters)       # public: from names and descriptions only
topic = ans.group_topic.reindex(clusters.index)       # scoring code only
cross = pd.crosstab(clusters, topic)
match = {'clusters': int(cfg.clusters), 'seed': SEED,
         'purity': round(float(cross.max(axis=1).sum() / len(clusters)), 4),
         'normalized_mutual_info': round(float(normalized_mutual_info_score(topic, clusters)), 4),
         'adjusted_rand_index': round(float(adjusted_rand_score(topic, clusters)), 4)}
(br.RESULTS / 'topic_clusters_match.json').write_text(json.dumps(match, indent=2))
clusters.to_frame().assign(name=name).to_csv(br.RESULTS / 'topic_clusters.csv')
print(f'Purity {match["purity"]:.2f} (1 = each cluster is one topic), normalised mutual information {match["normalized_mutual_info"]:.2f}')
pd.DataFrame({'groups': cross.sum(axis=1), 'main hidden topic': cross.idxmax(axis=1),
              'its share': (cross.max(axis=1) / cross.sum(axis=1)).round(2),
              'examples': clusters.groupby(clusters).apply(lambda s: ', '.join(name[s.index[:3]]))})"""),
md("""The public topics are only half right (purity about 0.5). Group descriptions in this community reuse the same phrases across topics
("Practice sessions and honest feedback", "Getting ready for a trip or an exam in ..."), so some clusters group by wording rather than subject.
R5 is therefore a looser diversity rule than "at most 2 per real topic"; better public topics (members choosing a group's topic when they create it)
would make it sharper."""),
md("""## 6 · Fair re-ranking (R4, R5)

The re-ranker builds each list **one slot at a time**. For the next slot it takes the candidate with the best

  λ · relevance − (1 − λ) · (its highest similarity to the groups already picked)

(this is *MMR*: with λ = 1 only relevance counts; lower λ favours groups unlike those already in the list). Among the candidates, it keeps three rules:

- **quota q = 20%** (R4): at least 1 slot in 5 goes to a new or small group, the most relevant one, if no newcomer made the list on its own;
- **topic cap n = 2** (R5): at most 2 groups of one public topic per list;
- **global cap c = 10%** (R4): no group gets more than 10% of all slots. Users are served in a fixed shuffled order (seed 0); once a group reaches its cap it is skipped.

If no candidate could keep every rule, the rules would be relaxed in that order (the counts are printed below: they stay at 0).
λ is chosen on the practice quiz from 1, 0.9, 0.8, 0.7 and 0.5. Besides the usual columns: *diversity* = 1 − the average description similarity of
the pairs in a list; *clusters_per_list* = public topics per list; *quota_slots* = share of slots the quota changed."""),
code(r"""sim = br.description_similarity(vis)
created = vis.groups.set_index('group_id').created_day
new_ids = set(created.index[created > br.TODAY - br.NEW_DAYS])

def score_lists(recs, truth, v):
    # evaluate() plus the diversity measures and what the re-ranker did
    lists = br.lists_from(recs)
    row = br.evaluate(lists, truth, v, ans.group_topic)
    row['diversity'] = br.list_diversity(lists, sim)
    row['clusters_per_list'] = float(np.mean([clusters[l].nunique() for l in lists.values()]))
    row['quota_slots'] = recs.forced.mean()
    row['new_groups_shown'] = len({g for l in lists.values() for g in l} & new_ids)
    row['times_relaxed'] = sum(recs.attrs['relaxed'].values())
    return row

NO_RERANK = dict(q=0, c=None, n=None, lam=1.0)
LAMBDAS = [1.0, 0.9, 0.8, 0.7, 0.5]
rerank_rows = {'Hybrid, no re-ranking': score_lists(br.recommend(val_users, fit, replace(cfg, **NO_RERANK), stats_fit), val, fit)}
for lam in LAMBDAS:
    rerank_rows[f'lambda = {lam}'] = score_lists(br.recommend(val_users, fit, replace(cfg, lam=lam), stats_fit), val, fit)
rerank_table = pd.DataFrame(rerank_rows).T
br.save_table(rerank_table, 'rerank_validation.csv', decimals=4)

LAM = LAMBDAS[int(np.argmax(rerank_table.loc[[f'lambda = {lam}' for lam in LAMBDAS], 'ndcg@5'].to_numpy()))]   # ties: the larger
print(f'Chosen: lambda = {LAM} (boingrec.Config: {cfg.lam})')
rerank_table[['ndcg@5', 'newcomer_share', 'gini', 'coverage', 'largest_share', 'topics_per_list', 'clusters_per_list',
              'diversity', 'quota_slots', 'times_relaxed']].round(3)"""),
md("""The re-ranking lifts the newcomer share from about 2% to **20%** for a small loss of accuracy, and spreads the slots over more groups
(lower Gini, higher coverage). λ = 1 is the most accurate: the topic cap (n = 2) already keeps lists varied, and pushing for more variety (lower λ)
costs accuracy on this quiz. MMR stays in the design as a dial; experiment E2 sweeps λ and q together."""),
md("""## 7 · Personalisation off (R1): what every member sees by default

With personalisation off, nothing about the member is used except which groups they already joined and marked "not interested" (they are never suggested).
Every member gets the same scores:

- **recent activity**: posts and likes on posts of the last 30 days (log scale; the most active group gets 1);
- **newness**: 1 for a group created today, falling to 0 at 30 days old;

  score = (1 − *w*) · activity + *w* · newness,

then the same filters and re-ranking. Accuracy alone would always pick *w* = 0 (active groups are big groups): that is the popularity trap.
So the rule is: pick the *w* whose share of slots for new or small groups is closest to what a fair lottery (random suggestions) gives them on the
practice quiz, so that newcomers get a real chance without the list becoming only empty new groups."""),
code(r"""OFF_WEIGHTS = [0, 0.25, 0.5, 0.75, 1]
off_rows = {f'newness weight {w}': score_lists(br.recommend(val_users, fit, replace(cfg, personal=False, off_new_w=w), stats_fit), val, fit)
            for w in OFF_WEIGHTS}
off_table = pd.DataFrame(off_rows).T
br.save_table(off_table, 'off_validation.csv', decimals=4)

lottery = pd.read_csv(br.RESULTS / 't6_validation.csv', index_col=0).loc[br.label('random'), 'newcomer_share']
OFF_W = OFF_WEIGHTS[int(np.argmin(np.abs(off_table['newcomer_share'].to_numpy() - lottery)))]
print(f'Random suggestions give new or small groups {lottery:.0%} of the slots on the practice quiz. '
      f'Chosen: newness weight {OFF_W} (boingrec.Config: {cfg.off_new_w})')
off_table[['hit_rate', 'ndcg@5', 'newcomer_share', 'new_groups_shown', 'gini', 'coverage', 'largest_share', 'topics_per_list']].round(3)"""),
md("""With *w* = 0.5, about 40% of the slots go to new or small groups, as with a lottery, and the rest to the most active groups.
Because every member sees the same list, it is unequal (high Gini): the global cap (no group above 10% of all slots) is what spreads it over more than
10 groups. It is much less accurate than the personal methods, which is the honest price of not profiling anyone."""),
md("""## 8 · Reasons (R6)

Each suggestion shows one reason, from a fixed template, never generated text. The reason is the part that adds the most to the score
(each part's contribution is returned by `recommend()`, so experiment E6 can check this); a slot that came from the quota says so.

| reason_code | Example | When |
|---|---|---|
| shared_members | "85 members of Finals countdown are in it" | "also joined" adds the most |
| similar_group | "Similar to Journaling streak, which you joined" or "Because you're in Finals countdown" | similar descriptions, or the AI model, adds the most |
| friend | "Your friend user 68 is a member" | friends add the most (public profiles only) |
| topic | "Matches a topic you picked: languages" | the member's chosen topics add the most (off here: topic weight 0, notebook 04) |
| new_group | "A new group: we show new groups so they get a fair chance" ("A small group: ...") | the slot came from the quota, or newness adds the most |
| active | "Active this week" ("Active this month") | personalisation off, activity adds the most |

User 1 again: the proposed design, then the default list with personalisation off."""),
code(r"""show = ['rank', 'group_id', 'score', 'reason_code', 'reason_text', 'forced'] + [f'part_{p}' for p in br.PARTS]
one = br.recommend([1], vis, cfg, stats)          # alone, so the global cap does not apply
print('User 1 is in:', ', '.join(name[sorted(vis.train.group_id[vis.train.user_id == 1])]))
print('Hidden (the answer):', ', '.join(name[sorted(ans.test.group_id[ans.test.user_id == 1])]))
one.assign(group=one.group_id.map(name))[['rank', 'group'] + show[2:]].round(3)"""),
code(r"""off_one = br.recommend([1], vis, replace(cfg, personal=False), stats)
off_one.assign(group=off_one.group_id.map(name))[['rank', 'group', 'score', 'reason_code', 'reason_text', 'part_active', 'part_new']].round(3)"""),
md("""## 9 · Experiment E1: the full comparison on the test set

Every method suggests 5 groups to each of the 1,406 tested users, learning only from the training data, with the settings chosen on the practice quiz.
The first four rows are notebook 04's table (unchanged), the fifth is notebook 05's AI model. The last three come from `recommend()`:
the hybrid without re-ranking, **the proposed design** (hybrid + fair re-ranking), and personalisation off (served together, so the 10% cap is shared
by all 1,406 users)."""),
code(r"""ORDER = ['random', 'popularity', 'also_joined', 'descriptions', 'hidden_tastes', 'hybrid', 'reranked', 'off']
recs = {'hybrid': br.recommend(tested, vis, replace(cfg, **NO_RERANK), stats),
        'reranked': br.recommend(tested, vis, cfg, stats),
        'off': br.recommend(tested, vis, replace(cfg, personal=False), stats)}
test_lists = {
    'random': br.random_lists(vis, tested),
    'popularity': br.top_k(br.popularity_scores(vis, tested), vis),
    'also_joined': br.top_k(br.also_joined_scores(vis, tested), vis),
    'descriptions': br.top_k(br.similar_descriptions_scores(vis, tested, topic_weight=cfg.topic_weight), vis),
    'hidden_tastes': br.top_k(br.hidden_tastes_scores(vis, tested, k=cfg.k), vis),
    **{m: br.lists_from(r) for m, r in recs.items()}}
e1 = pd.DataFrame({br.label(m): br.evaluate(test_lists[m], ans.test, vis, ans.group_topic) for m in ORDER}).T
e1[['users', 'coverage']] = e1[['users', 'coverage']].astype(int)
br.save_table(e1, 'e1_methods.csv')
e1.round(3)"""),
md("""**How sure are we?** 95% ranges from resampling the users (as in notebook 04), and the **price of fairness**: how much NDCG@5 the re-ranking costs
each user, compared with the hybrid alone (a paired range: the same resampled users for both)."""),
code(r"""per_user = {m: br.relevance_per_user(test_lists[m], ans.test) for m in ORDER}
ci_rows = {}
for m in ORDER:
    row = {}
    for metric in ['hit_rate', 'ndcg@5']:
        low, high = br.bootstrap_ci(per_user[m][metric])
        row.update({metric: per_user[m][metric].mean(), f'{metric} low': low, f'{metric} high': high})
    ci_rows[br.label(m)] = row
ci = pd.DataFrame(ci_rows).T
br.save_table(ci, 'e1_methods_ci.csv')

cost = per_user['hybrid']['ndcg@5'] - per_user['reranked']['ndcg@5']
low, high = br.bootstrap_ci(cost)
fairness = {'ndcg@5 hybrid': e1.loc[br.label('hybrid'), 'ndcg@5'], 'ndcg@5 proposed': e1.loc[br.label('reranked'), 'ndcg@5'],
            'cost': float(cost.mean()), 'cost low': low, 'cost high': high,
            'relative cost': float(cost.mean() / e1.loc[br.label('hybrid'), 'ndcg@5']),
            'newcomer share hybrid': e1.loc[br.label('hybrid'), 'newcomer_share'],
            'newcomer share proposed': e1.loc[br.label('reranked'), 'newcomer_share']}
fairness = {k: round(float(v), 4) for k, v in fairness.items()}
(br.RESULTS / 'e1_price_of_fairness.json').write_text(json.dumps(fairness, indent=2))
print(f'The re-ranking costs {fairness["cost"]:.3f} NDCG@5 ({fairness["relative cost"]:.1%} of the hybrid\'s; 95% range '
      f'{low:.3f} to {high:.3f}) and lifts the newcomer share from {fairness["newcomer share hybrid"]:.1%} to {fairness["newcomer share proposed"]:.1%}.')
ci.round(3)"""),
md("""## 10 · The chart

Relevance (NDCG@5) and the share of slots for new or small groups, with the same colour for each method as in every other figure.
The dashed line is the quota (q = 20%)."""),
code(r"""labels = [br.label(m) for m in ORDER]
y = np.arange(len(ORDER))[::-1]                       # first method at the top
percent = lambda v: '0%' if v == 0 else f'{v:.1%}' if v < 0.1 else f'{v:.0%}'   # one decimal below 10%
panels = [('ndcg@5', 'Relevance (NDCG@5)', 'NDCG@5 (1 = perfect)', '{:.3f}'.format),
          ('newcomer_share', 'Slots for new or small groups', 'Newcomer share', percent)]
fig, axes = plt.subplots(1, 2, figsize=(br.WIDTH, 3.1), sharey=True)
for ax, (col, title, xlabel, fmt) in zip(axes, panels):
    values = e1.loc[labels, col].to_numpy()
    ax.barh(y, values, height=0.62, color=[br.colour(m) for m in ORDER])
    for yi, v in zip(y, values):
        ax.text(v + values.max() * 0.02, yi, fmt(v), va='center', fontsize=8, color=br.INK)
    ax.set_xlim(0, values.max() * 1.25)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.xaxis.grid(True)
    ax.tick_params(axis='y', length=0)
axes[0].set_yticks(y, labels)
axes[1].axvline(cfg.q, color=br.MUTED, linestyle='--', linewidth=0.9)
axes[1].text(cfg.q, y[ORDER.index('popularity')], f'  quota q = {cfg.q:.0%}', color=br.MUTED, fontsize=7.5, va='center')
axes[1].xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
fig.tight_layout(w_pad=2)
br.save_fig(fig, 'e1_methods.png')
plt.show()"""),
md("""## 11 · What the reasons say, and what members see by default

How often each reason is shown on the test, for the proposed design and for personalisation off; then the groups the default list shows most."""),
code(r"""reasons = pd.DataFrame({br.label(m): recs[m].reason_code.value_counts() for m in ['reranked', 'off']}).reindex(br.REASON_CODES).fillna(0).astype(int)
reasons = pd.concat([reasons, (reasons / reasons.sum()).add_suffix(' (share)')], axis=1)
br.save_table(reasons, 'e1_reasons.csv')

shown = br.exposure(test_lists['off'], br.discover_groups(vis.groups))
default_list = pd.DataFrame({'group': name[shown.index], 'members': stats.sizes[shown.index].astype(int),
                             'new': created[shown.index] > br.TODAY - br.NEW_DAYS, 'slots': shown,
                             'share of slots': (shown / shown.sum()).round(3)})
display(reasons.round(3))
default_list[default_list.slots > 0].sort_values('slots', ascending=False, kind='stable')"""),
md("""## 12 · Checks"""),
code(r"""from collections import Counter

allowed = br.candidate_mask(vis, tested)
proposed = recs['reranked']
newcomer = stats.newcomers
user_groups = vis.train.groupby('user_id').group_id.apply(set)
friend_pairs = set(zip(links.user_id, links.friend_id))
members = set(zip(vis.train.user_id, vis.train.group_id))
part_cols = [f'part_{p}' for p in br.PARTS + ['active', 'new']]

def reason_matches(row):
    # the reason names the part that adds the most (a quota slot says new_group)
    if row.forced:
        return row.reason_code == 'new_group'
    if not row.personal:
        top = 'active' if row.part_active >= row.part_new else 'new'
        return row.reason_code == {'active': 'active', 'new': 'new_group'}[top]
    top = max(br.PARTS, key=lambda p: row[f'part_{p}'])
    expected = {'cf': [('shared_members', '')], 'content': [('similar_group', 'Similar to'), ('topic', '')],
                'social': [('friend', '')], 'mf': [('similar_group', 'Because')]}[top]
    return any(row.reason_code == code and row.reason_text.startswith(start) for code, start in expected)

def friend_ok(row):
    v = row.reason_ref
    return (user.privacy[v] == 'public' and user.suspended[v] == 0 and (row.user_id, v) in friend_pairs
            and (row.user_id, v) not in blocked and (v, row.group_id) in members)

hooks_work = []   # E3 and E4 (notebooks 08, 09) filled the hooks: each must change the statistics, never be silently ignored
for change in [dict(eps=1.0, m=5), dict(m=5), dict(burst_w=0.5)]:
    hooks_work.append(not np.array_equal(br.stats_for(vis, replace(cfg, **change)).co.to_numpy(), stats.co.to_numpy()))
try:
    br.stats_for(vis, replace(cfg, eps=1.0))      # noise without a cap m gives no guarantee: it must stop with a clear message
    hooks_work.append(False)
except ValueError:
    hooks_work.append(True)
again = br.recommend(tested, vis, cfg, stats)
hybrid_top_k = br.top_k(br.hybrid_scores(br.hybrid_parts(vis, tested, cfg, stats), cfg), vis)

checks = {
    'every tested user gets exactly 5 different groups from every method':
        all(len(set(lists[u])) == K == len(lists[u]) for lists in test_lists.values() for u in tested),
    'every suggestion is allowed: on Discover, not joined, not marked "not interested" (R7, R8)':
        all(allowed.loc[u, g] for lists in test_lists.values() for u in tested for g in lists[u]),
    'quota (R4): every proposed list has at least ceil(q x 5) new or small groups, and the newcomer share is at least q':
        all(sum(g in newcomer for g in test_lists['reranked'][u]) >= np.ceil(cfg.q * K - 1e-9) for u in tested)
        and e1.loc[br.label('reranked'), 'newcomer_share'] >= cfg.q,
    'topic cap (R5): no proposed list has more than n groups of one public topic':
        all(max(Counter(clusters[test_lists['reranked'][u]]).values()) <= cfg.n for u in tested),
    'global cap (R4): no group gets more than c of all slots (proposed and personalisation off)':
        all(e1.loc[br.label(m), 'largest_share'] <= cfg.c + 1e-12 for m in ['reranked', 'off']),
    'no rule had to be relaxed on the test': all(sum(r.attrs['relaxed'].values()) == 0 for r in recs.values()),
    'the parts add up to the score, on every row': all(np.allclose(r[part_cols].sum(axis=1), r.score) for r in recs.values()),
    'the reason is always the part that adds the most, or the quota (R6, by construction)':
        all(r.apply(reason_matches, axis=1).all() for r in recs.values()),
    'every friend reason names a public, not suspended, not blocked friend who is in the group (R6, R8)':
        all(proposed[proposed.reason_code == 'friend'].apply(friend_ok, axis=1)),
    'every "shared members" or "similar group" reason names a group the user is in':
        all(row.reason_ref in user_groups[row.user_id]
            for row in proposed[proposed.reason_code.isin(['shared_members', 'similar_group'])].itertuples()),
    'the hybrid beats each of its four scores alone on the practice quiz':
        hybrid_grid['ndcg@5'].iloc[0] > alone['ndcg@5'].max(),
    'recommend() without re-ranking gives exactly the hybrid\'s top 5': test_lists['hybrid'] == hybrid_top_k,
    'group_stats() rebuilds "also joined" and the AI model exactly (without the suspended accounts)': diff_cf < 1e-12 and diff_mf < 1e-9,
    'the first four rows equal notebook 04\'s table (E1 version 1)':
        e1.iloc[:4].round(3).equals(pd.read_csv(br.RESULTS / 'e1_v1.csv', index_col=0).round(3).set_axis(e1.index[:4])),
    'boingrec.Config holds the choices made here and in notebook 05 (weights, lambda, newness weight, tastes)':
        best == (cfg.alpha, cfg.beta, cfg.gamma, cfg.delta) and LAM == cfg.lam and OFF_W == cfg.off_new_w and cfg.k == br.TASTES,
    'the privacy and fake-account hooks are not silently ignored: m, eps and burst_w change the statistics, eps without m stops with a clear message':
        all(hooks_work),
    'same seed, same results: recommend() run again gives the same rows': again.equals(proposed),
    'a recommender never gets a hidden column or a test membership':
        not {'interests', 'is_fake'} & set(vis.users.columns) and 'topic' not in vis.groups.columns
        and not set(zip(vis.train.user_id, vis.train.group_id)) & set(zip(ans.test.user_id, ans.test.group_id)),
}
for check, ok_ in checks.items():
    print('✓' if ok_ else '✗', check)
assert all(checks.values()), 'Some checks failed (see ✗ above)'"""),
md("""## What we learned

- **The hybrid is the most relevant method:** on the test, NDCG@5 = **0.541** and a hit rate of **69%**, against 0.499 for "also joined" alone,
  0.475 for the AI model and 0.131 for today's BOING. The weights chosen on the practice quiz are 0.4 "also joined", 0.1 similar descriptions,
  0.3 friends, 0.2 AI model; mixing beats each score alone, but the exact weights matter little.
- **The proposed design (hybrid + fair re-ranking) gives new or small groups 20% of the slots** (the hybrid alone: 2%; today's BOING: 0%) for a cost of
  **0.013 NDCG@5** (2.3% of the hybrid's; 95% range 0.008 to 0.017), and shows 125 of the 129 Discover groups (today: 10), with a Gini of 0.511 (today: 0.953).
  No group takes more than 3.3% of the slots and no list has more than 2 groups of one public topic. λ = 1 was best: the topic cap already keeps lists varied.
- **Personalisation off** (the default, R1) uses no profile at all: NDCG@5 = 0.058, still above random (0.025), with 55% of slots for new or small groups
  but only 14 groups shown, because everyone sees nearly the same list; the 10% cap is what spreads it.
- **Every suggestion has a true reason** from a fixed template. In the proposed design most say how many members of one of your groups are in it,
  about a quarter name a public friend, and about one in five is a quota slot that says it is there to give a new or small group a fair chance.
- The public topic clusters match the hidden topics only half the time (purity about 0.5), so R5 is a loose diversity rule here.
- Files: `results/e1_methods.csv` (the table), `results/e1_methods_ci.csv` (95% ranges), `results/e1_price_of_fairness.json`, `results/e1_reasons.csv`,
  `results/hybrid_validation.csv`, `results/rerank_validation.csv`, `results/off_validation.csv`, `results/topic_clusters.csv`,
  `results/topic_clusters_match.json`, `figures/e1_methods.png`.

**For the experiments:** `br.recommend(user_ids, vis, br.Config(...))` runs the whole design with any setting. E2 sweeps `q` and `lam` (and `c`, `n`);
E3 fills in the noise and clipping hooks (`eps`, `m`) in `br.group_stats()`; E4 the fake-account hooks (`L` already works, `burst_w` is a hook);
E6 checks the reasons with the `part_*` columns."""),
]

for name_, cells in [('05_ai_model.ipynb', nb5), ('06_hybrid_rerank.ipynb', nb6)]:
    nb = new_notebook(cells=cells, metadata=metadata)
    nbformat.validate(nb)
    nbformat.write(nb, NB / name_)
print('built 05 and 06')
