"""boingrec: the code every notebook of the BOING recommender project shares (ECSE 557, Group 14).

Import it from a notebook in the notebooks/ folder:   import boingrec as br

What is inside, in order:
  1. Paths and constants: SEED, K, TODAY, NEW_DAYS, SMALL
  2. Loading the data, through two separate doors:
       load_visible()  what a recommender may read
       load_answers()  the answer key (test memberships, hidden columns): for the scoring code only
  3. Splits: split_memberships() is notebook 02's split; val_split() uses it to carve a practice quiz
     (a validation set) out of the training data, for tuning
  4. Candidates: the groups a user may be shown (on Discover, not joined yet, not marked "not interested")
  5. Recommenders: each one gives a users x groups table of scores; top_k() turns it into lists of 5
  6. Metrics and evaluate(): relevance and exposure, one row per method
  7. Method names and colours (the same colour for a method in every figure), and the figure style
  8. The AI model, "hidden tastes" (T9, notebook 05)
  9. The proposed recommender (notebook 06): group_stats() -> four scores -> hybrid -> re-ranking ->
     5 suggestions with reasons, all behind one entry point: recommend(user_ids, data, config)
 10. Privacy (R10, experiment E3, notebook 08): contribution clipping and Laplace noise, used by group_stats();
     PRIVATE holds the setting chosen there (eps 2, m 3), off by default
 11. Newcomers and the rules (experiments E5 and E6, notebook 10): newcomer_quiz(), check_rules() (counts every
     violation of the rules; its "fidelity" = faithful to the computed score), check_facts() (is each reason TRUE of
     the raw data, and does each list meet the quota on the real sizes), and make_test_cases() / verify_test_cases()
     for BOING's JavaScript port (testcases/: a small world, a larger one, and a case with the noise draws as data)
 12. The final design (notebook 11): FINAL_CONFIG, every dial and weight as chosen by the experiments (Config's
     defaults stay notebook 06's), FINAL_CONFIG_BEFORE_REVIEW, and test_cases_readme() for testcases/
 13. People suggestions (experiment E7, notebook 12): BOING's "People you may know" with the owner's age bands
     (19 Nov 2026), the E7 additions to the synthetic community (ages, course rooms, the switch; PEOPLE_ASSUME and
     AGE_SHARES), the friendship split, the baselines, relevance and exposure, check_people() and the planted age grid

Options added after the review of 1 November (all off in Config's defaults, so notebooks 03 to 10 keep their results):
small_from ('public': "small" from the member count Discover shows; 'r9', after the second review: the same count, but
only of the accounts R9 counts, so fake accounts R9 ignores cannot push a group over the line), r9_scope ('all': R9 also
on posts, likes and friends), act_eps (noise on the recent activity too), count_under_noise (False: with noise on, a
"shared members" reason names the group without its noisy count). GroupStats now keeps its noise draws, so check_rules()
can rebuild the noisy counts itself.

Rules this file keeps: only synthetic data; every random step takes a seed; a recommender is only ever
handed what load_visible() returns. Several people edit this file: add new options and functions,
never change what an existing function returns.
"""
import math
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------------------------------
# 1. Paths and constants
# ---------------------------------------------------------------------------------------------------

def _project_root():
    # The ECSE557 folder, whether we run from notebooks/, from ECSE557/ or from Colab's /content
    here = Path(__file__).resolve().parent.parent
    if (here / 'data').exists():
        return here
    cwd = Path.cwd()
    return cwd.parent if cwd.name == 'notebooks' else cwd


ROOT = _project_root()
DATA = ROOT / 'data' / 'sim_v1'
RESULTS = ROOT / 'results'
FIGS = ROOT / 'figures'

SEED = 0         # every random step uses this seed unless told otherwise
K = 5            # every recommender suggests 5 groups
TODAY = 365      # days count from the launch (day 0) to today (day 365)
NEW_DAYS = 30    # "new" = created in the last 30 days: created_day > TODAY - NEW_DAYS (days 336 to 365)
SMALL = 10       # "small" = fewer than 10 members in the training data

# ---------------------------------------------------------------------------------------------------
# 2. Loading the data: two separate doors
# ---------------------------------------------------------------------------------------------------

# The answer key. A recommender must never read these columns.
HIDDEN_COLUMNS = {'users.csv': ['interests', 'is_fake'], 'groups.csv': ['topic']}

# The only files a recommender may read (README, "The data files")
VISIBLE_FILES = {'train': 'train_memberships.csv', 'posts': 'train_posts.csv', 'likes': 'train_likes.csv',
                 'friendships': 'friendships.csv', 'blocks': 'blocks.csv', 'topics': 'topics.csv',
                 'not_interested': 'not_interested.csv', 'users': 'users.csv', 'groups': 'groups.csv'}


@dataclass
class Visible:
    """Everything a recommender may read. Each field is a pandas table."""
    train: pd.DataFrame           # memberships it may see: user_id, group_id, joined_day
    posts: pd.DataFrame           # posts, without those that give a hidden membership away
    likes: pd.DataFrame           # likes, same
    friendships: pd.DataFrame
    blocks: pd.DataFrame
    topics: pd.DataFrame          # topics members chose to share (public input)
    not_interested: pd.DataFrame
    users: pd.DataFrame           # without interests and is_fake
    groups: pd.DataFrame          # without topic, sorted by group_id


@dataclass
class Answers:
    """The answer key. Only the scoring code may read it."""
    test: pd.DataFrame            # the hidden memberships: user_id, group_id, joined_day
    group_topic: pd.Series        # group_id -> its topic
    user_interests: pd.Series     # user_id -> e.g. 'languages:0.70|fitness:0.30'
    user_is_fake: pd.Series       # user_id -> 0/1


def _read_without(path, drop):
    # Read a CSV but never load the columns in `drop` (they are not even read from disk)
    header = pd.read_csv(path, nrows=0).columns
    return pd.read_csv(path, usecols=[c for c in header if c not in drop])


def load_visible(data=DATA):
    """Load what a recommender may read, and nothing else."""
    data = Path(data)
    tables = {}
    for field, fname in VISIBLE_FILES.items():
        tables[field] = _read_without(data / fname, HIDDEN_COLUMNS.get(fname, []))
    tables['groups'] = tables['groups'].sort_values('group_id').reset_index(drop=True)
    tables['users'] = tables['users'].sort_values('user_id').reset_index(drop=True)
    for fname, cols in HIDDEN_COLUMNS.items():
        field = fname.replace('.csv', '')
        assert not set(cols) & set(tables[field].columns), f'hidden column loaded from {fname}'
    return Visible(**tables)


def load_answers(data=DATA):
    """Load the answer key: the test memberships and the hidden columns. For scoring only."""
    data = Path(data)
    users = pd.read_csv(data / 'users.csv', usecols=['user_id', 'interests', 'is_fake']).set_index('user_id')
    groups = pd.read_csv(data / 'groups.csv', usecols=['group_id', 'topic']).set_index('group_id')
    return Answers(test=pd.read_csv(data / 'test_memberships.csv'), group_topic=groups.topic,
                   user_interests=users.interests, user_is_fake=users.is_fake)

# ---------------------------------------------------------------------------------------------------
# 3. Splits: the test set (notebook 02) and a validation set carved from the training data
# ---------------------------------------------------------------------------------------------------

def split_memberships(m, users, groups, frac=0.2, min_groups=3, seed=SEED):
    """Notebook 02's split, unchanged. Returns (kept, hidden), both with a fresh 0, 1, 2... index.

    Users with at least `min_groups` groups (not suspended) get `frac` of their groups hidden, rounded,
    at least 1. Memberships in groups hidden by moderators are never hidden (no method may suggest them).
    """
    m = m.reset_index(drop=True)
    rng = np.random.default_rng(seed)
    n_groups = m.groupby('user_id').size()
    suspended = set(users.user_id[users.suspended == 1])
    off_limits = set(groups.group_id[groups.hidden_by_mods == 1])
    hideable = m[~m.group_id.isin(off_limits)]
    hidden_rows = []
    for uid, rows in hideable.groupby('user_id'):            # users in id order, so the result never changes
        n = int(n_groups[uid])
        if n < min_groups or uid in suspended:
            continue
        k = min(max(1, round(frac * n)), len(rows))           # 20%, rounded, at least 1
        hidden_rows += list(rng.choice(rows.index, size=k, replace=False))
    hidden = m.loc[sorted(hidden_rows)]
    kept = m.drop(index=hidden.index)
    return kept.reset_index(drop=True), hidden.reset_index(drop=True)


def drop_leaks(posts, likes, hidden):
    """Remove the posts and likes that would give a hidden membership away (as notebook 02 did)."""
    hidden_pairs = set(zip(hidden.user_id, hidden.group_id))
    leaky_post = np.array([(u, g) in hidden_pairs for u, g in zip(posts.user_id, posts.group_id)], dtype=bool)
    kept_posts = posts[~leaky_post].copy()
    post_group = posts.set_index('post_id').group_id
    leaky_like = np.array([(u, g) in hidden_pairs for u, g in zip(likes.user_id, likes.post_id.map(post_group))],
                          dtype=bool)
    kept_likes = likes[~leaky_like & likes.post_id.isin(kept_posts.post_id)].copy()
    kept_posts['likes'] = kept_posts.post_id.map(kept_likes.groupby('post_id').size()).fillna(0).astype(int)
    return kept_posts.reset_index(drop=True), kept_likes.reset_index(drop=True)


def val_split(vis, frac=0.2, seed=SEED, min_groups=3):
    """Carve a validation set (a practice quiz, for tuning) out of the training data.

    Same rule as the test set: users with 3+ training groups (not suspended) get 20% of them hidden
    (at least 1). Returns (fit, val): `fit` is a Visible whose memberships, posts and likes no longer
    show the validation memberships; `val` is the hidden memberships (user_id, group_id, joined_day).
    """
    kept, val = split_memberships(vis.train, vis.users, vis.groups, frac=frac, min_groups=min_groups, seed=seed)
    posts, likes = drop_leaks(vis.posts, vis.likes, val)
    return replace(vis, train=kept, posts=posts, likes=likes), val

# ---------------------------------------------------------------------------------------------------
# 4. Candidates: which groups a user may be shown
# ---------------------------------------------------------------------------------------------------

def group_ids(vis):
    """All group ids, in id order: the columns of every score table."""
    return vis.groups.group_id.to_numpy()


def all_users(vis):
    """All user ids, in id order."""
    return vis.users.user_id.to_numpy()


def discover_groups(groups):
    """The groups on Discover: open to anyone and not hidden by moderators (ids, in id order)."""
    return np.sort(groups.group_id[(groups.open == 1) & (groups.hidden_by_mods == 0)].to_numpy())


def group_sizes(vis):
    """Members of each group in the training data (0 if none), indexed by group_id."""
    return vis.train.groupby('group_id').size().reindex(group_ids(vis), fill_value=0)


def newcomer_groups(vis, config=None):
    """Set of 'new or small' group ids: created in the last NEW_DAYS days, or fewer than SMALL members (training data).
    config: None (the default, the yardstick every notebook scores with) counts every member, as Discover shows; a Config
    with small_from = 'r9' counts only the accounts R9 counts (member_counts), the definition that design uses."""
    created = vis.groups.set_index('group_id').created_day
    size = group_sizes(vis)
    if config is not None and config.small_from == 'r9':
        size = member_counts(vis.train, vis.users, config, group_ids(vis))
    is_newcomer = (created > TODAY - NEW_DAYS) | (size < SMALL)
    return set(is_newcomer.index[is_newcomer])


def member_counts(train, users, config, gids):
    """Each group's member count as R9 sees it (for "small", rule R4, with small_from = 'r9'): only the accounts R9 counts
    (not suspended, level config.L or more), each once; an account younger than config.young_days days counts burst_w of
    a member (0: not until it is older). So accounts that R9 ignores everywhere else cannot push a group over the "small"
    line either. No clipping, no noise: like the count Discover shows, it is not covered by the privacy noise.
    Returns a Series group_id -> count, over gids."""
    ok = users.user_id[(users.suspended == 0) & (users.level >= config.L)]
    kept = train[train.user_id.isin(ok) & train.group_id.isin(gids)].drop_duplicates(['user_id', 'group_id'])
    created = users.set_index('user_id').created_day.reindex(kept.user_id).to_numpy()
    w = np.where(created > TODAY - config.young_days, config.burst_w, 1.0)
    count = pd.Series(w, index=kept.group_id.to_numpy()).groupby(level=0).sum()
    return count.reindex(gids, fill_value=0.0).rename_axis('group_id').rename('members')


def candidate_mask(vis, user_ids=None, not_interested=True):
    """users x groups table of True/False: True where the group may be suggested to the user.

    A group may be suggested if it is on Discover, the user is not in it (training data) and, with
    not_interested=True (the default, rule R7), the user did not mark it "not interested".
    not_interested=False reproduces T4, written before that button existed.
    """
    users = all_users(vis) if user_ids is None else np.asarray(user_ids)
    gids = group_ids(vis)
    allowed = np.broadcast_to(np.isin(gids, discover_groups(vis.groups)), (len(users), len(gids))).copy()
    row = pd.Series(np.arange(len(users)), index=users)
    col = pd.Series(np.arange(len(gids)), index=gids)
    excluded = [vis.train[['user_id', 'group_id']]]
    if not_interested:
        excluded.append(vis.not_interested[['user_id', 'group_id']])
    pairs = pd.concat(excluded)
    pairs = pairs[pairs.user_id.isin(row.index) & pairs.group_id.isin(col.index)]
    allowed[row[pairs.user_id].to_numpy(), col[pairs.group_id].to_numpy()] = False
    return pd.DataFrame(allowed, index=pd.Index(users, name='user_id'), columns=pd.Index(gids, name='group_id'))


def candidates(vis, user_id, not_interested=True):
    """The groups a user may be shown, as a list of ids in id order."""
    row = candidate_mask(vis, [user_id], not_interested=not_interested).iloc[0]
    return [int(g) for g in row.index[row.to_numpy()]]

# ---------------------------------------------------------------------------------------------------
# 5. Recommenders. Each *_scores function returns a users x groups table (index = user_id,
#    columns = group_id): higher = better. top_k() turns any such table into lists of 5.
# ---------------------------------------------------------------------------------------------------

def top_k(scores, vis, k=K, user_ids=None, not_interested=True):
    """Turn a users x groups score table into each user's top-k list: {user_id: [group_id, ...]}.

    Only candidates are kept (see candidate_mask). Highest score first; equal scores: smaller group id
    first. Scores are rounded to 10 decimals first, so that two equal scores computed in a different
    order (tiny rounding differences) still count as a tie. Missing scores (NaN) rank last.
    """
    users = scores.index.to_numpy() if user_ids is None else np.asarray(user_ids)
    gids = group_ids(vis)
    s = scores.reindex(index=users, columns=gids).to_numpy(dtype=float)
    s = np.where(np.isnan(s), -np.inf, np.round(s, 10))
    allowed = candidate_mask(vis, users, not_interested=not_interested).to_numpy()
    lists = {}
    for i, u in enumerate(users):
        order = np.lexsort((gids, -s[i], ~allowed[i]))   # last key first: candidates, then score, then id
        lists[int(u)] = [int(gids[j]) for j in order[:k] if allowed[i, j]]
    return lists


def membership_matrix(vis, user_ids=None):
    """users x groups table of 0/1 from the training data (1 = member)."""
    users = all_users(vis) if user_ids is None else np.asarray(user_ids)
    gids = group_ids(vis)
    # Built with numpy: the same table as pd.crosstab(...).clip(upper=1) gave (checked in notebook 08), 25x faster
    members = pd.Index(np.unique(vis.train.user_id))
    col = pd.Index(gids).get_indexer(vis.train.group_id)
    ok = col >= 0
    x = np.zeros((len(members) + 1, len(gids)), dtype=np.int64)          # the last row stays 0
    x[members.get_indexer(vis.train.user_id[ok]), col[ok]] = 1
    row = members.get_indexer(users)                                     # -1: a user with no groups
    return pd.DataFrame(x[np.where(row >= 0, row, len(members))], index=pd.Index(users, name='user_id'),
                        columns=pd.Index(gids, name='group_id'))


def popularity_scores(vis, user_ids=None):
    """Today's BOING (T4): every user gets the same scores, the groups' sizes in the training data."""
    users = all_users(vis) if user_ids is None else np.asarray(user_ids)
    size = group_sizes(vis).to_numpy(dtype=float)
    return pd.DataFrame(np.broadcast_to(size, (len(users), len(size))).copy(),
                        index=pd.Index(users, name='user_id'), columns=pd.Index(group_ids(vis), name='group_id'))


def random_lists(vis, user_ids, k=K, seed=SEED, not_interested=True):
    """The random floor, exactly as T4 drew it: users in id order, k candidates each, without replacement."""
    rng = np.random.default_rng(seed)
    users = np.sort(np.asarray(user_ids))
    mask = candidate_mask(vis, users, not_interested=not_interested)
    lists = {}
    for u in users:
        options = mask.columns[mask.loc[u].to_numpy()].to_numpy()   # in group-id order
        lists[int(u)] = [int(g) for g in rng.choice(options, size=k, replace=False)]
    return lists


def jaccard_matrix(vis):
    """groups x groups overlap (Jaccard) from the training data: members in both / members in either.

    0 when neither group has members; the diagonal (a group with itself) is set to 0.
    """
    x = membership_matrix(vis).to_numpy(dtype=float)
    both = x.T @ x
    size = np.diag(both)
    either = size[:, None] + size[None, :] - both
    jac = np.divide(both, either, out=np.zeros_like(both), where=either > 0)
    np.fill_diagonal(jac, 0.0)
    gids = group_ids(vis)
    return pd.DataFrame(jac, index=pd.Index(gids, name='group_id'), columns=pd.Index(gids, name='group_id'))


def also_joined_scores(vis, user_ids=None):
    """"Also joined" (T6a, item-item collaborative filtering).

    A user's score for a group = the sum of its overlaps (Jaccard) with each group the user is in.
    """
    x = membership_matrix(vis, user_ids)
    jac = jaccard_matrix(vis)
    return pd.DataFrame(x.to_numpy(dtype=float) @ jac.to_numpy(), index=x.index, columns=x.columns)


def group_texts(vis):
    """Each group's public text: name + ' ' + about, indexed by group_id."""
    g = vis.groups.set_index('group_id')
    return g.name + ' ' + g.about


def topic_texts(vis, user_ids=None):
    """Each user's shared topics as words ('exam_prep' -> 'exam prep'), '' if none, indexed by user_id."""
    users = all_users(vis) if user_ids is None else np.asarray(user_ids)
    words = vis.topics.assign(word=vis.topics.topic.str.replace('_', ' ')).groupby('user_id').word.apply(' '.join)
    return words.reindex(users, fill_value='').rename_axis('user_id')


def tfidf_model(vis):
    """TF-IDF (scikit-learn, default settings) fitted on the groups' texts. Returns (vectorizer, group vectors)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer()
    return vectorizer, vectorizer.fit_transform(group_texts(vis).to_numpy())


def description_similarity(vis):
    """groups x groups cosine similarity of the TF-IDF vectors of their texts (1 = same words, 0 = none shared)."""
    from sklearn.metrics.pairwise import cosine_similarity
    _, vectors = tfidf_model(vis)
    gids = group_ids(vis)
    return pd.DataFrame(cosine_similarity(vectors), index=pd.Index(gids, name='group_id'),
                        columns=pd.Index(gids, name='group_id'))


def similar_descriptions_scores(vis, user_ids=None, topic_weight=1.0):
    """"Similar descriptions" (T6b, content-based).

    A user's score for a group = its average similarity to the user's groups, where the topics the user
    chose to share (topics.csv) count as one more "group" made of those words, weighted by topic_weight
    (0 = ignore topics). Topic words that appear in no group text add nothing.
    """
    from sklearn.metrics.pairwise import cosine_similarity
    x = membership_matrix(vis, user_ids)
    vectorizer, vectors = tfidf_model(vis)
    sim_groups = cosine_similarity(vectors)                                    # groups x groups
    query = vectorizer.transform(topic_texts(vis, x.index).to_numpy())
    sim_topics = cosine_similarity(query, vectors)                             # users x groups
    has_topics = (np.asarray(query.multiply(query).sum(axis=1)).ravel() > 0).astype(float)
    total = x.to_numpy(dtype=float) @ sim_groups + topic_weight * has_topics[:, None] * sim_topics
    count = x.to_numpy(dtype=float).sum(axis=1) + topic_weight * has_topics
    score = np.divide(total, count[:, None], out=np.zeros_like(total), where=count[:, None] > 0)
    return pd.DataFrame(score, index=x.index, columns=x.columns)

# ---------------------------------------------------------------------------------------------------
# 6. Metrics
# ---------------------------------------------------------------------------------------------------

RELEVANCE = ['hit_rate', 'precision@5', 'recall@5', 'ndcg@5']
EXPOSURE = ['newcomer_share', 'gini', 'coverage', 'largest_share', 'topics_per_list']


def relevance(suggested, hidden):
    """Scores of one list against one user's hidden groups (binary relevance), as in notebook 03.

    hit_rate: 1 if any suggestion is hidden; precision: right / suggested; recall: found / hidden;
    ndcg: a right answer at position i is worth 1/log2(i+1), divided by the best possible total.
    """
    hits = [g in hidden for g in suggested]
    dcg = sum(1 / np.log2(i + 2) for i, hit in enumerate(hits) if hit)
    ideal = sum(1 / np.log2(i + 2) for i in range(min(len(hidden), len(suggested))))
    return {'hit_rate': float(any(hits)),
            'precision@5': sum(hits) / len(suggested),
            'recall@5': sum(hits) / len(hidden),
            'ndcg@5': float(dcg / ideal)}


def relevance_per_user(lists, truth):
    """One row of relevance scores per user who has hidden groups in `truth` (a memberships table)."""
    hidden = truth.groupby('user_id').group_id.apply(set)
    users = sorted(hidden.index)
    missing = [u for u in users if u not in lists]
    assert not missing, f'{len(missing)} evaluated users have no list (first: {missing[:3]})'
    return pd.DataFrame([relevance(lists[u], hidden[u]) for u in users], index=pd.Index(users, name='user_id'))


def exposure(lists, groups=None):
    """How many times each group appears across the lists. With `groups` (ids), every one of them is
    listed, 0 for those never shown."""
    shown = pd.Series([g for lst in lists.values() for g in lst], dtype='int64')
    counts = shown.value_counts().sort_index()
    if groups is not None:
        counts = counts.reindex(groups, fill_value=0)
    return counts.rename_axis('group_id').rename('shown')


def gini(values):
    """Gini coefficient: 0 = every group shown equally, close to 1 = one group gets every slot."""
    x = np.sort(np.asarray(values, dtype=float))
    n, total = len(x), x.sum()
    if n == 0 or total == 0:
        return 0.0
    return float(np.sum((2 * np.arange(1, n + 1) - n - 1) * x) / (n * total))


def lorenz_curve(values):
    """Points of the Lorenz curve: share of groups (least shown first) vs share of all slots they get."""
    x = np.sort(np.asarray(values, dtype=float))
    return np.linspace(0, 1, len(x) + 1), np.concatenate([[0.0], np.cumsum(x) / x.sum()])


def evaluate(lists, truth, vis, topic=None):
    """One row of metrics for one method, over the users who have hidden groups in `truth`.

    lists: {user_id: [group_id, ...]}; truth: the hidden memberships (test or validation);
    vis: the Visible the method was given (group sizes come from its training memberships);
    topic: the hidden group_id -> topic (Answers.group_topic), for topics_per_list; scoring only.

    Relevance (averaged over users): hit_rate, precision@5, recall@5, ndcg@5.
    Exposure, over all evaluated users' lists and all Discover groups (never-shown ones count as 0):
      newcomer_share: share of slots that go to new or small groups;
      gini: inequality of exposure; coverage: how many different groups are shown;
      largest_share: share of slots taken by the most-shown group;
      topics_per_list: average number of different topics in a list (needs `topic`).
    """
    per_user = relevance_per_user(lists, truth)
    users = per_user.index
    evaluated = {u: lists[u] for u in users}
    shown = [g for lst in evaluated.values() for g in lst]
    counts = exposure(evaluated, discover_groups(vis.groups))
    assert counts.sum() == len(shown), 'a list contains a group that is not on Discover'
    newcomers = newcomer_groups(vis)
    row = {'users': len(users), **per_user.mean().to_dict(),
           'newcomer_share': float(np.mean([g in newcomers for g in shown])),
           'gini': gini(counts.to_numpy()),
           'coverage': int((counts > 0).sum()),
           'largest_share': float(counts.max() / len(shown)),
           'topics_per_list': (float(np.mean([len({topic[g] for g in lst}) for lst in evaluated.values()]))
                               if topic is not None else np.nan)}
    return pd.Series(row)


def list_diversity(lists, sim):
    """Intra-list diversity (R5): 1 - the average similarity of the pairs of groups in a list, averaged over
    the lists. sim: a groups x groups similarity table (e.g. description_similarity). 0 = five copies of
    the same group, 1 = no two groups share a word."""
    values = []
    for lst in lists.values():
        s = sim.loc[lst, lst].to_numpy()
        pairs = s[np.triu_indices(len(lst), k=1)]
        values.append(1 - pairs.mean() if len(pairs) else np.nan)
    return float(np.nanmean(values))


def bootstrap_ci(values, n_boot=2000, seed=SEED, level=0.95):
    """Range of plausible values for an average (95% by default): resample the users with replacement
    n_boot times (seeded) and keep the middle 95% of the averages. Returns (low, high)."""
    v = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = v[rng.integers(0, len(v), size=(n_boot, len(v)))].mean(axis=1)
    low, high = np.quantile(means, [(1 - level) / 2, 1 - (1 - level) / 2])
    return float(low), float(high)


def save_table(df, name, decimals=3):
    """Save a results table to results/<name> (CSV), rounded like the T4 table."""
    RESULTS.mkdir(exist_ok=True)
    df.round(decimals).to_csv(RESULTS / name)
    return RESULTS / name

# ---------------------------------------------------------------------------------------------------
# 7. Methods' names and colours, and the figure style
# ---------------------------------------------------------------------------------------------------

# One fixed colour per method, in every figure. Colour-blind-safe set (checked: neighbours stay apart for
# the three common kinds of colour blindness). Random is grey, as in T4. Never reuse a colour.
# 'off' took '#b0006e' (berry) instead of the planned red '#e34948': red was too close to orange for every
# reader; berry stays apart from all eight others (checked pair by pair). With all nine in one chart a few
# pairs are close for colour-blind readers (green/orange, blue/violet), so every multi-method chart names
# each bar or point in text (axis labels or direct labels), never by colour alone. No colour is left:
# a new method shares a chart with at most a few others, or folds into a small multiple.
METHODS = {
    'random':        {'label': 'Random (floor)',           'colour': '#a9a8a2'},
    'popularity':    {'label': 'Popularity (today)',       'colour': '#2a78d6'},   # blue, as in T4
    'also_joined':   {'label': '"Also joined"',            'colour': '#eb6834'},   # orange
    'descriptions':  {'label': 'Similar descriptions',     'colour': '#1baf7a'},   # aqua
    'hidden_tastes': {'label': 'Hidden tastes (AI model)', 'colour': '#eda100'},   # yellow (T9)
    'hybrid':        {'label': 'Hybrid',                   'colour': '#e87ba4'},   # magenta (notebook 06)
    'reranked':      {'label': 'Hybrid + fair re-ranking', 'colour': '#008300'},   # green: the proposed design (06, E2)
    'private':       {'label': 'With privacy noise',       'colour': '#6250d6'},   # violet (E3)
    'off':           {'label': 'Personalisation off',      'colour': '#b0006e'},   # berry: the default list (R1)
}


def label(method):
    return METHODS[method]['label']


def colour(method):
    return METHODS[method]['colour']


INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e1e0d9'   # text, secondary text, gridlines
WIDTH = 6.5                                          # inches: a figure fills the page width when printed


def use_style():
    """Matplotlib settings for every figure: readable at 6.5 in wide, quiet axes, no chart junk."""
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        'figure.dpi': 100, 'savefig.dpi': 200, 'font.size': 9, 'axes.titlesize': 10, 'axes.labelsize': 9,
        'xtick.labelsize': 8.5, 'ytick.labelsize': 8.5, 'legend.fontsize': 8.5, 'legend.frameon': False,
        'axes.edgecolor': '#c3c2b7', 'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': MUTED,
        'text.color': INK, 'axes.titlecolor': INK, 'axes.titlelocation': 'left', 'axes.titleweight': 'bold',
        'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': False, 'grid.color': GRID,
        'grid.linewidth': 0.7, 'axes.axisbelow': True,
    })


def save_fig(fig, name):
    """Save a figure to figures/<name> as a 200 dpi PNG."""
    FIGS.mkdir(exist_ok=True)
    fig.savefig(FIGS / name, dpi=200, bbox_inches='tight', facecolor='white')
    return FIGS / name


def print_example(user_id, lists_by_method, vis, truth):
    """Print one user's groups, their hidden groups, and each method's suggestions (right ones ticked)."""
    name = vis.groups.set_index('group_id').name
    size = group_sizes(vis)
    mine = sorted(vis.train.group_id[vis.train.user_id == user_id])
    hidden = set(truth.group_id[truth.user_id == user_id])
    print(f'User {user_id} is in:', ', '.join(name[mine]))
    print('Hidden (the answer):', ', '.join(name[sorted(hidden)]))
    for method, lists in lists_by_method.items():
        print(f'\n{label(method) if method in METHODS else method}:')
        for i, g in enumerate(lists[user_id], 1):
            print(f'  {i}. {name[g]} ({size[g]} members)', '<- right!' if g in hidden else '')

# ---------------------------------------------------------------------------------------------------
# 8. The AI model: hidden tastes (T9, notebook 05)
# ---------------------------------------------------------------------------------------------------

TASTES = 10   # how many hidden tastes the AI model learns: chosen on the practice quiz in notebook 05


def taste_model(gram, k=TASTES):
    """Learn k hidden tastes from `gram` = X^T X: the groups x groups table of how many members each pair
    of groups shares (X = the users x groups table of 0/1; its diagonal holds the group sizes).

    Returns (strength, tastes): the k largest eigenvalues of `gram`, largest first, and their eigenvectors
    (groups x k, one column per taste: how much each group "loads" on it). numpy.linalg.eigh is exact and
    deterministic, so a JavaScript port can redo it; the tastes are TruncatedSVD's right singular vectors
    and the strengths its singular values squared (notebook 05 checks this). A taste and its mirror image
    give the same scores, so each column's sign is fixed to make its largest loading positive: tables and
    a port then agree.
    """
    g = np.asarray(gram, dtype=float)
    values, vectors = np.linalg.eigh((g + g.T) / 2)
    top = np.argsort(-values, kind='stable')[:k]
    tastes = vectors[:, top]
    peak = np.abs(tastes).argmax(axis=0)
    tastes = tastes * np.where(tastes[peak, np.arange(tastes.shape[1])] < 0, -1.0, 1.0)
    return values[top], tastes


def taste_links(tastes, gids):
    """groups x groups table V V^T: how strongly the AI model links group j (row) to group g (column).
    A user's AI-model score for g is the sum of this table's rows j for the user's own groups."""
    v = np.asarray(tastes, dtype=float)
    return pd.DataFrame(v @ v.T, index=pd.Index(gids, name='group_id'), columns=pd.Index(gids, name='group_id'))


def hidden_tastes_scores(vis, user_ids=None, k=TASTES):
    """"Hidden tastes" (T9, the AI model: matrix factorisation of the users x groups table X).

    It learns k tastes from X^T X (training data, every user) and projects each user's groups on them:
    score = X V V^T. So a user's score for group g = the sum, over the user's own groups j, of
    (V V^T)[j, g]: the group j that adds the most is an honest reason ("Because you're in j").
    """
    x_all = membership_matrix(vis).to_numpy(dtype=float)
    _, tastes = taste_model(x_all.T @ x_all, k)
    x = membership_matrix(vis, user_ids)
    return pd.DataFrame(x.to_numpy(dtype=float) @ tastes @ tastes.T, index=x.index, columns=x.columns)

# ---------------------------------------------------------------------------------------------------
# 9. The proposed recommender (notebook 06). The steps, in order:
#      group_stats()   every statistic about other members, in ONE place (rules R8, R9, R10 act here)
#      raw_parts()     four scores: "also joined", similar descriptions, friends, hidden tastes
#      rescale()       each score to 0-1 over the user's candidates; the hybrid adds them with weights
#      rerank()        fair exposure (R4) and diversity (R5), greedily, one slot at a time
#      recommend()     the entry point: 5 rows per user with score, reason and each part's contribution
#    Personalisation off (R1) skips the four scores and ranks by recent activity and newness instead.
# ---------------------------------------------------------------------------------------------------

ACTIVE_DAYS = 30   # "recent activity" = posts and likes on posts of the last 30 days
WEEK = 7           # "Active this week" = a post in the last 7 days
YOUNG_DAYS = 30    # R9: a "young" account was created in the last 30 days (default of Config.young_days)

# Colours for the fake-account figures (notebook 09): one line per level bar L, as darker steps of the green of
# 'reranked' (METHODS), because L is ordered. L = 1 (R9 off) keeps that exact green: it IS the proposed design.
# Checked as an ordinal ramp (one hue, darker for a higher bar): neighbouring steps differ by 17 or more (OKLab x 100)
# for normal vision and for colour-blind vision. Lines also differ by marker and dashes, and are labelled on the figure.
R9_L_COLOURS = {1: '#008300', 3: '#004d00', 5: '#001c00'}


@dataclass(frozen=True)
class Config:
    """Every setting of the proposed recommender. The defaults are the design chosen in notebooks 05 and
    06 on the practice quiz. Change one with Config(q=0.4) or dataclasses.replace(config, q=0.4)."""
    # The hybrid's weights, on scores rescaled to 0-1 per user (notebook 06)
    alpha: float = 0.4           # "also joined" (collaborative filtering)
    beta: float = 0.1            # similar descriptions (content)
    gamma: float = 0.3           # friends (social)
    delta: float = 0.2           # hidden tastes (the AI model)
    k: int = TASTES              # the AI model's number of tastes (notebook 05)
    topic_weight: float = 0.0    # how much a member's chosen topics count in "similar descriptions" (notebook 04)
    # R1: personalisation. False = the list every member sees by default, with no profile
    personal: bool = True
    off_new_w: float = 0.5       # personalisation off: weight of newness (the rest is recent activity)
    # Re-ranking: R4 (fair exposure) and R5 (diversity)
    q: float = 0.2               # at least ceil(q * 5) slots of each list go to new or small groups
    c: float | None = 0.1        # no group gets more than c of all slots (None = no cap)
    n: int | None = 2            # at most n groups of one public topic cluster per list (None = no limit)
    lam: float = 1.0             # MMR: lam * relevance - (1 - lam) * similarity to the groups already picked
    clusters: int = 10           # number of public topic clusters (KMeans on the TF-IDF vectors, seed 0)
    # Whose data counts, and privacy: hooks for experiments E3 and E4 (used in group_stats only)
    L: int = 1                   # R9: only accounts at level L or more count (1 = every account)
    burst_w: float = 1.0         # R9: weight of joins by young accounts (1 = no down-weighting; notebook 09)
    young_days: int = YOUNG_DAYS  # R9: an account is "young" for this many days after it is created (notebook 09)
    eps: float | None = None     # R10: differential privacy budget epsilon (None or inf = no noise; needs m)
    m: int | None = None         # R10: each member counts for at most m groups (None = no clipping)
    size_share: float = 0.25     # R10: share of eps spent on the group sizes; the rest on the pair counts (chosen in notebook 08)
    noise_seed: int | None = None   # R10: seed of the clipping and the noise (None = use seed); notebook 08 varies it
    seed: int = SEED             # the order users are served in (for the cap c), and any noise
    # Added after the review of the final design (notebook 11). Each one is off by default, so notebooks 03 to 10 keep their results.
    small_from: str = 'counted'  # R4: how "small" is judged (the quota and its reason): 'counted' = from the recommender's own counts
                                 # (clipped and noisy when R10 is on); 'public' = from the member count Discover already shows (no noise needed);
                                 # 'r9' = the same count, of the accounts R9 counts only (member_counts: fake accounts R9 ignores cannot change it)
    r9_scope: str = 'joins'      # R9: 'joins' = the level bar and the young-account weight act on memberships only; 'all' = also on
                                 # posts, likes (recent activity) and friends
    act_eps: float | None = None  # R10 for recent activity: None = activity counts posts and likes, with no noise; a number = it counts the
                                  # members who posted in the group (each in at most m groups) plus Laplace noise for this budget.
                                  # One release of the statistics is then (eps + act_eps)-differentially private
    count_under_noise: bool = True  # R6 with noise on (eps): True = a "shared members" reason states the noisy count ("About 17 members of X
                                    # are in it"); False = it names the group only ("Members of X also joined it"), since the noisy count can be
                                    # far from the truth (notebook 11). Without noise the count is stated either way.


@dataclass
class GroupStats:
    """Every statistic that describes other members, made in one place by group_stats()."""
    gids: np.ndarray             # all group ids, in id order (the rows and columns below)
    counted: np.ndarray          # ids of the accounts whose memberships, posts and likes count
    co: pd.DataFrame             # groups x groups: members the two groups share (X^T X); diagonal = sizes
    sizes: pd.Series             # group_id -> members
    jaccard: pd.DataFrame        # groups x groups overlap, from co (diagonal 0): "also joined"
    taste_strength: np.ndarray   # the AI model's k eigenvalues, largest first
    tastes: pd.DataFrame         # groups x k: the AI model's tastes, learned from co
    activity: pd.Series          # group_id -> posts + likes on posts of the last ACTIVE_DAYS days
    posts_week: pd.Series        # group_id -> posts in the last WEEK days
    newcomers: set               # new or small group ids (small = fewer than SMALL members in `sizes`, or in the public
                                 # member count with config.small_from = 'public', or in member_counts() with 'r9')
    noise: dict | None = None    # R10: the Laplace draws added to co ({'sizes': n, 'pairs': n(n-1)/2, in np.triu_indices order}),
                                 # kept so that check_rules() can rebuild co from the raw tables on its own
    act_noise: np.ndarray | None = None   # R10 (act_eps): the draws added to the activity counts
    account_w: pd.Series | None = None    # R9 with r9_scope = 'all': each counted account's weight (1, or burst_w while young)


def group_stats(train, users, config=None, groups=None, posts=None, likes=None, noise=None):
    """Compute every statistic that describes other members, in ONE place.

    train: memberships (user_id, group_id, joined_day); users: the users table (level, suspended);
    groups: the groups table (default: only the groups that appear in train); posts, likes: for the
    recent activity used when personalisation is off (optional).
    noise: the Laplace draws to add instead of drawing them ({'sizes', 'pairs', and 'activity' with act_eps}, as in
    GroupStats.noise): the test cases give them as data, so that a port can check the noise path number for number.
    The rules about other members' data act here, so they reach "also joined", the AI model, the group
    sizes and the activity at once:
      R8   suspended accounts never count;
      R9   only accounts at level config.L or more count, each once; the joins of young accounts (created in
           the last YOUNG_DAYS days) count as burst_w of a member (notebook 09, experiment E4). With
           config.r9_scope = 'all' the same weight also applies to their posts and likes, and to them as friends;
      R10  each member counts for at most m groups, and the sizes and pair counts get noise for budget eps
           (section 10, notebook 08). The recent activity gets noise only with config.act_eps (then it counts the
           members who posted, each in at most m groups); without it, notebook 08 explains what is left out.
    """
    cfg = config or Config()
    assert cfg.small_from in ('counted', 'public', 'r9'), "small_from is 'counted', 'public' or 'r9'"
    assert cfg.r9_scope in ('joins', 'all'), "r9_scope is 'joins' or 'all'"
    gids = np.sort((groups.group_id if groups is not None else train.group_id).unique())
    counted = np.sort(users.user_id[(users.suspended == 0) & (users.level >= cfg.L)].to_numpy())
    # R9 with r9_scope = 'all': each counted account's weight in the activity and as a friend (1, or burst_w while young)
    account_w = None
    if cfg.r9_scope == 'all':
        created_c = users.set_index('user_id').created_day.reindex(counted).to_numpy()
        account_w = pd.Series(np.where(created_c > TODAY - cfg.young_days, cfg.burst_w, 1.0), index=pd.Index(counted, name='user_id'),
                              name='weight')

    # The memberships that count, one weight each (1 = counts fully)
    mem = train[train.user_id.isin(counted) & train.group_id.isin(gids)][['user_id', 'group_id', 'joined_day']]
    mem = mem.drop_duplicates(['user_id', 'group_id']).assign(w=1.0)
    # --- R9 (experiment E4, notebook 09): a burst of brand-new accounts counts less. A young account
    # (created in the last config.young_days days: public data, never is_fake) counts as burst_w of a member in
    # every count. mem.w is the member's entry in X, and co = X^T X multiplies two entries of the same
    # member, so a young member gets sqrt(burst_w): it then adds burst_w to each of its groups' sizes and
    # to each pair count. (L, above, keeps only accounts at level L or more, and each account counts once.)
    if cfg.burst_w != 1:
        assert 0 <= cfg.burst_w <= 1, 'burst_w is a weight between 0 and 1'
        created = users.set_index('user_id').created_day.reindex(mem.user_id).to_numpy()
        mem['w'] = np.where(created > TODAY - cfg.young_days, math.sqrt(cfg.burst_w), mem.w.to_numpy())
    # --- R10 (experiment E3, section 10): each member counts for at most m groups (contribution clipping)
    private = cfg.eps is not None and not math.isinf(cfg.eps)
    if private and cfg.m is None:
        raise ValueError('eps needs m: differential privacy needs a cap m on how many groups one member counts for')
    if private and not cfg.eps > 0:
        raise ValueError('eps must be positive (smaller = more private; None or inf = no noise)')
    noise_seed = cfg.seed if cfg.noise_seed is None else cfg.noise_seed
    rng = np.random.default_rng(noise_seed)
    if cfg.m is not None:
        mem = clip_contributions(mem, cfg.m, noise_seed)

    # X = counted members x groups (the weights); co = X^T X is the one table both "also joined" and the
    # AI model learn from, so noise added to it reaches both
    members = pd.Index(np.unique(mem.user_id))
    x = np.zeros((len(members), len(gids)))
    x[members.get_indexer(mem.user_id), np.searchsorted(gids, mem.group_id)] = mem.w.to_numpy()
    co = x.T @ x
    # --- R10 (experiment E3, section 10): Laplace noise for budget eps on the sizes and the pair counts.
    # Everything below is computed from the noisy co only, so it keeps the guarantee (post-processing).
    drawn = None
    if private:
        assert ((mem.w >= 0) & (mem.w <= 1)).all(), 'the noise assumes each membership weighs between 0 and 1'
        co, drawn = noisy_counts(co, cfg.eps, cfg.m, cfg.size_share, rng, noise=noise, return_noise=True)

    sizes = np.diag(co).copy()
    either = sizes[:, None] + sizes[None, :] - co
    jac = np.divide(co, either, out=np.zeros_like(co), where=either > 0)
    np.fill_diagonal(jac, 0.0)
    strength, tastes = taste_model(co, cfg.k)

    # Recent activity: posts in groups (not hidden by moderators) and the likes on them, counted accounts only
    activity = pd.Series(0.0, index=gids)
    posts_week = pd.Series(0, index=gids)
    act_noise = None
    if cfg.act_eps is not None and (cfg.m is None or not cfg.act_eps > 0):
        raise ValueError('act_eps needs m (each member is counted as active in at most m groups) and must be positive')
    if posts is not None:
        recent = posts[(posts.group_id > 0) & (posts.hidden_by_mods == 0) & posts.user_id.isin(counted)
                       & (posts.day > TODAY - ACTIVE_DAYS)]
        if cfg.act_eps is not None:
            # --- R10 for the activity (act_eps): the members who posted in the group in the last ACTIVE_DAYS days, each
            # member counted in at most m of their groups (the same hash as the clipping), young accounts weighted as in R9;
            # then Laplace noise of scale m / act_eps (one member changes the counts by at most m in all), rounded, at least 0.
            # Likes are left out: a like hangs on another member's post, so one member's rows could change many counts.
            # No weekly count is released, so the reason can only say "Active this month".
            act = recent[['user_id', 'group_id']].drop_duplicates().assign(w=1.0)
            if account_w is not None:
                act['w'] = account_w.reindex(act.user_id).to_numpy()
                act = act[act.w > 0]
            act = clip_contributions(act, cfg.m, noise_seed)
            counts = act.groupby('group_id').w.sum().reindex(gids, fill_value=0.0).to_numpy(float)
            act_noise = (np.asarray(noise['activity'], dtype=float) if noise is not None and 'activity' in noise
                         else rng.laplace(0.0, cfg.m / cfg.act_eps, len(gids)))
            activity = pd.Series(np.maximum(np.round(counts + act_noise), 0.0), index=gids)
        elif account_w is not None:
            # R9 with r9_scope = 'all': a post or like counts with its author's weight (0 for a young account with burst_w = 0)
            pw = account_w.reindex(recent.user_id).to_numpy()
            activity = activity.add(pd.Series(pw, index=recent.group_id.to_numpy()).groupby(level=0).sum(), fill_value=0).reindex(gids)
            if likes is not None:
                liked = likes[likes.post_id.isin(recent.post_id) & likes.user_id.isin(counted)]
                liked_group = liked.post_id.map(recent.set_index('post_id').group_id).to_numpy()
                lw = account_w.reindex(liked.user_id).to_numpy()
                activity = activity.add(pd.Series(lw, index=liked_group).groupby(level=0).sum(), fill_value=0).reindex(gids)
            week = recent[recent.day > TODAY - WEEK]
            posts_week = (pd.Series(account_w.reindex(week.user_id).to_numpy(), index=week.group_id.to_numpy())
                          .groupby(level=0).sum().reindex(gids, fill_value=0.0))
        else:
            activity = activity.add(recent.group_id.value_counts(), fill_value=0).reindex(gids)
            if likes is not None:
                liked = likes[likes.post_id.isin(recent.post_id) & likes.user_id.isin(counted)]
                liked_group = liked.post_id.map(recent.set_index('post_id').group_id)
                activity = activity.add(liked_group.value_counts(), fill_value=0).reindex(gids)
            posts_week = recent[recent.day > TODAY - WEEK].group_id.value_counts().reindex(gids, fill_value=0)
    # (Without act_eps the activity is not covered by R10's noise: it is also a count of other members' actions; notebook 08.)
    if drawn is not None and act_noise is not None:
        drawn = {**drawn, 'activity': act_noise}

    new = np.zeros(len(gids), dtype=bool)
    if groups is not None:
        new = (groups.set_index('group_id').created_day.reindex(gids) > TODAY - NEW_DAYS).to_numpy()
    small = sizes < SMALL
    if cfg.small_from == 'public':
        # R4 with small_from = 'public': "small" from the member count Discover shows (every member, no clipping, no noise:
        # it is already public), the same count the scoring uses (group_sizes)
        public = train[train.group_id.isin(gids)].drop_duplicates(['user_id', 'group_id']).groupby('group_id').size()
        small = public.reindex(gids, fill_value=0).to_numpy() < SMALL
    elif cfg.small_from == 'r9':
        # R4 with small_from = 'r9': the same count, but only of the accounts R9 counts (not suspended, level L or more, young ones
        # weighted burst_w), so the fake accounts R9 ignores cannot push a group over the line (no clipping, no noise)
        small = member_counts(train, users, cfg, gids).to_numpy() < SMALL
    index = pd.Index(gids, name='group_id')
    return GroupStats(
        gids=gids, counted=counted,
        co=pd.DataFrame(co, index=index, columns=index), sizes=pd.Series(sizes, index=index, name='members'),
        jaccard=pd.DataFrame(jac, index=index, columns=index), taste_strength=strength,
        tastes=pd.DataFrame(tastes, index=index, columns=pd.RangeIndex(1, tastes.shape[1] + 1, name='taste')),
        activity=activity.rename_axis('group_id').rename('activity'),
        posts_week=posts_week.rename_axis('group_id').rename('posts_week'),
        newcomers=set(gids[new | small].tolist()),
        noise=drawn if drawn is not None else ({'activity': act_noise} if act_noise is not None else None),
        act_noise=act_noise, account_w=account_w)


def stats_for(vis, config=None, noise=None):
    """group_stats() on everything a Visible holds (memberships, users, groups, posts, likes). noise: see group_stats()."""
    return group_stats(vis.train, vis.users, config, groups=vis.groups, posts=vis.posts, likes=vis.likes, noise=noise)


def friend_accounts(stats):
    """The accounts that may count and be named as friends (R6, R8, R9): the counted accounts, and with r9_scope = 'all'
    only those whose weight is above 0 (a young account with burst_w = 0 waits, as its joins do)."""
    if stats.account_w is None:
        return stats.counted
    return stats.account_w.index[stats.account_w.to_numpy() > 0].to_numpy()


def public_friends(vis, user_ids, counted):
    """The friends who may count and be named in a reason (R6, R8), as (user_id, friend_id) rows: the
    friend's profile is public, the friend's account counts (`counted`: not suspended, level L or more),
    and neither of the two has blocked the other. Private-profile friends never count."""
    f = vis.friendships
    pairs = pd.concat([pd.DataFrame({'user_id': f.user_a, 'friend_id': f.user_b}),
                       pd.DataFrame({'user_id': f.user_b, 'friend_id': f.user_a})])
    public = vis.users.user_id[vis.users.privacy == 'public']
    pairs = pairs[pairs.user_id.isin(np.asarray(user_ids)) & pairs.friend_id.isin(public)
                  & pairs.friend_id.isin(counted)]
    b = vis.blocks
    blocked = set(zip(b.user_id, b.blocked_id)) | set(zip(b.blocked_id, b.user_id))
    keep = np.array([(u, v) not in blocked for u, v in zip(pairs.user_id, pairs.friend_id)], dtype=bool)
    return pairs[keep].drop_duplicates().sort_values(['user_id', 'friend_id']).reset_index(drop=True)


def friends_in_groups(vis, user_ids, counted):
    """(user_id, group_id, friend_id) rows: which of each user's public friends are members of which group."""
    member = vis.train[['user_id', 'group_id']].rename(columns={'user_id': 'friend_id'})
    rows = public_friends(vis, user_ids, counted).merge(member, on='friend_id')
    return rows[['user_id', 'group_id', 'friend_id']].sort_values(['user_id', 'group_id', 'friend_id'])


def social_scores(vis, user_ids=None, counted=None, weights=None):
    """Friends (the social signal): a user's score for a group = how many of their public friends are in it.
    counted: the accounts that may count (default: every account that is not suspended).
    weights: friend_id -> weight (R9 with r9_scope = 'all': a young friend counts burst_w); None = each friend counts 1."""
    users = all_users(vis) if user_ids is None else np.asarray(user_ids)
    if counted is None:
        counted = vis.users.user_id[vis.users.suspended == 0].to_numpy()
    rows = friends_in_groups(vis, users, counted)
    if weights is not None and len(rows):
        rows = rows.assign(w=weights.reindex(rows.friend_id).to_numpy())
        table = rows.groupby(['user_id', 'group_id']).w.sum().unstack(fill_value=0.0)
    else:
        table = rows.groupby(['user_id', 'group_id']).size().unstack(fill_value=0) if len(rows) else pd.DataFrame()
    return (table.reindex(index=users, columns=group_ids(vis), fill_value=0).astype(float)
            .rename_axis(index='user_id', columns='group_id'))


def topic_clusters(vis, n_clusters=10, seed=SEED):
    """Public topics: the groups sorted into n_clusters clusters by their texts (KMeans, scikit-learn, on the
    TF-IDF vectors of name + description). Public text only, never the hidden topic.
    Returns group_id -> cluster number (0 to n_clusters - 1)."""
    from sklearn.cluster import KMeans
    _, vectors = tfidf_model(vis)
    labels = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10).fit_predict(vectors)
    return pd.Series(labels, index=pd.Index(group_ids(vis), name='group_id'), name='cluster')


PARTS = ['cf', 'content', 'social', 'mf']   # the hybrid's four scores, weighted by alpha, beta, gamma, delta
PART_LABELS = {'cf': '"Also joined"', 'content': 'Similar descriptions', 'social': 'Friends',
               'mf': 'Hidden tastes (AI model)'}


def raw_parts(vis, user_ids, config=None, stats=None):
    """The hybrid's four scores before rescaling: {part: users x groups table}.

      cf       "also joined": the sum of the group's overlaps with the user's groups (stats.jaccard)
      content  similar descriptions (public texts; config.topic_weight for the member's chosen topics)
      social   how many of the user's public friends are members (counted accounts only)
      mf       hidden tastes: the user's groups projected on stats.tastes
    Only the user's own groups and public data are read here; everything about other members comes from
    `stats` (default: stats_for(vis, config)).
    """
    cfg = config or Config()
    stats = stats if stats is not None else stats_for(vis, cfg)
    x = membership_matrix(vis, user_ids)
    xa = x.to_numpy(dtype=float)
    v = stats.tastes.to_numpy()
    parts = {'cf': xa @ stats.jaccard.to_numpy(),
             'content': similar_descriptions_scores(vis, x.index, topic_weight=cfg.topic_weight).to_numpy(),
             'social': social_scores(vis, x.index, friend_accounts(stats), stats.account_w).to_numpy(),
             'mf': xa @ v @ v.T}
    return {p: pd.DataFrame(a, index=x.index, columns=x.columns) for p, a in parts.items()}


def rescale(scores, allowed):
    """Rescale each user's scores to 0-1 over the user's candidates (min-max: best candidate 1, worst 0).
    Scores are rounded to 10 decimals first (as in top_k). A score that is the same for every candidate
    of a user says nothing and becomes 0; non-candidates get 0. Takes and returns users x groups tables."""
    a = allowed.reindex(index=scores.index, columns=scores.columns).to_numpy(dtype=bool)
    s = np.where(a, np.round(scores.to_numpy(dtype=float), 10), np.nan)
    has = a.any(axis=1, keepdims=True)
    lo = np.where(has, np.nanmin(np.where(a, s, np.inf), axis=1, keepdims=True), 0.0)
    hi = np.where(has, np.nanmax(np.where(a, s, -np.inf), axis=1, keepdims=True), 0.0)
    span = hi - lo
    out = np.divide(s - lo, span, out=np.zeros(s.shape), where=a & (span > 0))
    return pd.DataFrame(out, index=scores.index, columns=scores.columns)


def hybrid_parts(vis, user_ids, config=None, stats=None):
    """The four scores, each rescaled to 0-1 over the user's candidates: {part: users x groups table}."""
    raw = raw_parts(vis, user_ids, config, stats)
    allowed = candidate_mask(vis, raw['cf'].index)
    return {p: rescale(s, allowed) for p, s in raw.items()}


def hybrid_scores(parts, config=None, weights=None):
    """The hybrid: s = alpha * cf + beta * content + gamma * social + delta * mf, on rescaled parts.
    weights: (alpha, beta, gamma, delta), default from the config."""
    cfg = config or Config()
    w = weights if weights is not None else (cfg.alpha, cfg.beta, cfg.gamma, cfg.delta)
    return sum(wi * parts[p] for wi, p in zip(w, PARTS))


def off_parts(vis, stats, config=None):
    """Personalisation off (R1): no profile, the same two parts for every member, already weighted:
      active  (1 - off_new_w) x recent activity: log(1 + posts and likes of the last 30 days),
              scaled so the most active group on Discover gets 1;
      new     off_new_w x newness: 1 for a group created today, falling to 0 at NEW_DAYS days old.
    Their sum is the score. Returns {'active': array, 'new': array}, over stats.gids."""
    cfg = config or Config()
    act = np.log1p(stats.activity.to_numpy(dtype=float))
    top = act[np.isin(stats.gids, discover_groups(vis.groups))].max()
    active = act / top if top > 0 else np.zeros_like(act)
    age = TODAY - vis.groups.set_index('group_id').created_day.reindex(stats.gids).to_numpy(dtype=float)
    new = np.clip(1 - age / NEW_DAYS, 0, 1)
    return {'active': (1 - cfg.off_new_w) * active, 'new': cfg.off_new_w * new}


def rerank(relevance, allowed, sim, newcomer, cluster, config=None, order=None, k=K):
    """Greedy re-ranking of every user's candidates (R4, R5), one slot at a time.

    relevance: users x groups array (0-1); allowed: users x groups True/False (candidates); sim: groups x
    groups similarity (public descriptions); newcomer: per group, True if new or small; cluster: per group,
    its public topic cluster; order: the order users are served in (row numbers).
    For each slot, the next group maximises  lam * relevance - (1 - lam) * (its highest similarity to the
    groups already picked)  (MMR), among the candidates that keep the rules:
      quota (R4)       when the slots left are just enough for the ceil(q * k) newcomer slots still owed,
                       only newcomer groups may be picked (the most relevant ones, by the same formula);
      topic cap (R5)   at most n groups of one cluster per list;
      global cap (R4)  no group gets more than c of all slots (c x k x users, at least 1).
    If no candidate keeps every rule, the rules are relaxed in this order: the quota, the topic cap, the
    global cap (counted in `relaxed`). Equal values: the smaller group id first.
    Returns (picks, forced, relaxed): picks = users x k column numbers (-1 if no candidate was left);
    forced = True where the quota changed the pick (a newcomer slot); relaxed = {rule: times relaxed}.
    """
    cfg = config or Config()
    rel = np.round(np.asarray(relevance, dtype=float), 10)
    allowed = np.asarray(allowed, dtype=bool)
    sim = np.asarray(sim, dtype=float)
    newcomer = np.asarray(newcomer, dtype=bool)
    _, cluster = np.unique(np.asarray(cluster), return_inverse=True)     # clusters as 0, 1, 2...
    n_users, n_groups = rel.shape
    order = np.arange(n_users) if order is None else np.asarray(order)
    need = math.ceil(cfg.q * k - 1e-9)
    cap = np.inf if cfg.c is None else max(1, math.floor(cfg.c * k * n_users + 1e-9))
    per_topic = k if cfg.n is None else cfg.n
    used = np.zeros(n_groups)
    picks = np.full((n_users, k), -1)
    forced = np.zeros((n_users, k), dtype=bool)
    relaxed = {'quota': 0, 'topic cap': 0, 'global cap': 0}
    everyone = np.ones(n_groups, dtype=bool)
    for i in order:
        avail = allowed[i].copy()
        closest = np.zeros(n_groups)                    # each group's highest similarity to those picked
        per_cluster = np.zeros(cluster.max() + 1)       # groups picked so far in each cluster
        newcomers_picked = 0
        for pos in range(k):
            if not avail.any():
                break
            under_cap = used < cap
            topic_ok = per_cluster[cluster] < per_topic
            owed = need - newcomers_picked
            force = owed > 0 and owed >= k - pos
            tries = [avail & under_cap & topic_ok & (newcomer if force else everyone),   # every rule
                     avail & under_cap & topic_ok,                                       # no quota
                     avail & under_cap,                                                  # no topic cap
                     avail]                                                              # no global cap
            level = next(t for t, mask in enumerate(tries) if mask.any())
            if force and level >= 1:
                relaxed['quota'] += 1
            if level >= 2:
                relaxed['topic cap'] += 1
            if level >= 3:
                relaxed['global cap'] += 1
            mmr = np.round(cfg.lam * rel[i] - (1 - cfg.lam) * closest, 10)
            j = int(np.argmax(np.where(tries[level], mmr, -np.inf)))
            if force and level == 0:
                free = int(np.argmax(np.where(tries[1], mmr, -np.inf)))   # the pick without the quota
                forced[i, pos] = j != free
            picks[i, pos] = j
            avail[j] = False
            used[j] += 1
            per_cluster[cluster[j]] += 1
            newcomers_picked += int(newcomer[j])
            closest = np.maximum(closest, sim[j])
    return picks, forced, relaxed


REASON_CODES = ['shared_members', 'similar_group', 'friend', 'topic', 'new_group', 'active', 'discover']


def recommend(user_ids, data=DATA, config=None, stats=None, clusters=None):
    """The proposed recommender, end to end: every user's 5 suggestions, each with its reason (R6).

    user_ids: the users to serve together (the cap c is shared among them); data: a Visible (what a
    recommender may read) or the folder to load it from; config: a Config (default: the chosen design);
    stats: group_stats() output, to reuse (default: computed here from data and config);
    clusters: each group's public topic cluster, group_id -> number (default: topic_clusters(data),
    as always; the test cases for the JavaScript port give them as data, see make_test_cases).
    Returns a table, one row per suggestion, in each user's order:
      user_id, rank (1-5), group_id, score, reason_code, reason_text,
      reason_ref   the group or friend the reason names (0 if none),
      forced       True if the slot came from the newcomer quota (R4),
      personal     True if the four personal scores were used (False: personalisation off, or a member
                   with nothing to go on, who gets the default list),
      part_cf, part_content, part_social, part_mf, part_active, part_new: each part's weighted
                   contribution; they add up to score. The reason is the largest part (R6), except on a
                   quota slot (new_group).
    Reason codes (fixed templates, never generated text): shared_members, similar_group (also the AI
    model's "Because you're in X"), friend, topic, new_group, active, and discover (a last resort for a
    group with no other true reason; it should not occur).
    """
    cfg = config or Config()
    vis = data if isinstance(data, Visible) else load_visible(data)
    users = np.unique(np.asarray(user_ids))
    gids = group_ids(vis)
    stats = stats if stats is not None else stats_for(vis, cfg)
    allowed_df = candidate_mask(vis, users)
    allowed = allowed_df.to_numpy()
    n_users, n_groups = allowed.shape
    zeros = np.zeros((n_users, n_groups))

    off = off_parts(vis, stats, cfg)
    parts = {'active': np.broadcast_to(off['active'], (n_users, n_groups)),
             'new': np.broadcast_to(off['new'], (n_users, n_groups))}
    personal = np.zeros(n_users, dtype=bool)
    if cfg.personal:
        raw = raw_parts(vis, users, cfg, stats)
        weights = dict(zip(PARTS, (cfg.alpha, cfg.beta, cfg.gamma, cfg.delta)))
        for p in PARTS:
            parts[p] = weights[p] * rescale(raw[p], allowed_df).to_numpy()
        personal_score = sum(parts[p] for p in PARTS)
        personal = (np.where(allowed, personal_score, 0) > 0).any(axis=1)   # else: nothing to go on
    for p in PARTS:
        parts[p] = np.where(personal[:, None], parts.get(p, zeros), 0.0)
    for p in ['active', 'new']:
        parts[p] = np.where(personal[:, None], 0.0, parts[p])
    score = sum(parts.values())

    relevance = rescale(pd.DataFrame(score, index=allowed_df.index, columns=allowed_df.columns), allowed_df)
    newcomer = np.isin(gids, sorted(stats.newcomers))
    cluster = (topic_clusters(vis, cfg.clusters) if clusters is None else clusters).reindex(gids).to_numpy()
    order = np.random.default_rng(cfg.seed).permutation(n_users)
    picks, forced, relaxed = rerank(relevance.to_numpy(), allowed, description_similarity(vis).to_numpy(),
                                    newcomer, cluster, cfg, order)

    # Reasons (R6): what is needed to name the largest part truthfully
    name = vis.groups.set_index('group_id').name.reindex(gids).to_numpy()
    created = vis.groups.set_index('group_id').created_day.reindex(gids).to_numpy()
    x = membership_matrix(vis, users).to_numpy(dtype=bool)
    jac, co = stats.jaccard.to_numpy(), stats.co.to_numpy()
    if cfg.burst_w != 1 and cfg.m is None and (cfg.eps is None or math.isinf(cfg.eps)):
        # R9 with young accounts down-weighted: co is then a weighted count, not a number of members, so a reason
        # states the members the two groups truly share (counted accounts, each once; notebook 10, E6). With
        # clipping or noise (R10) it keeps co, prefixed with "About".
        kept = vis.train[vis.train.user_id.isin(stats.counted)].drop_duplicates(['user_id', 'group_id'])
        xm = pd.crosstab(kept.user_id, kept.group_id).clip(upper=1).reindex(columns=gids, fill_value=0).to_numpy(float)
        co = xm.T @ xm
    noisy = cfg.eps is not None and not math.isinf(cfg.eps)
    links = stats.tastes.to_numpy() @ stats.tastes.to_numpy().T
    text_sim = description_similarity(vis).to_numpy()
    friends = {}                                               # (user, group) -> public friends in it, by id
    for u_, g_, f_ in friends_in_groups(vis, users, friend_accounts(stats)).itertuples(index=False):
        friends.setdefault((u_, g_), []).append(f_)
    topics_sim = None
    if cfg.personal and cfg.topic_weight > 0:
        from sklearn.metrics.pairwise import cosine_similarity
        vectorizer, vectors = tfidf_model(vis)
        # the topic piece of "similar descriptions", exactly as similar_descriptions_scores computes it,
        # and each single topic's similarity, to name the topic that matches best
        topics_sim = cosine_similarity(vectorizer.transform(topic_texts(vis, users).to_numpy()), vectors)
        one_topic = {t: cosine_similarity(vectorizer.transform([t.replace('_', ' ')]), vectors).ravel()
                     for t in vis.topics.topic.unique()}
        chosen = vis.topics.groupby('user_id').topic.apply(list)
    activity = stats.activity.reindex(gids).to_numpy()
    posts_week = stats.posts_week.reindex(gids).to_numpy()

    def fair_chance(j):
        if created[j] > TODAY - NEW_DAYS:
            return 'new_group', 'A new group: we show new groups so they get a fair chance', 0
        return 'new_group', 'A small group: we show small groups so they get a fair chance', 0

    def default_reason(i, j):
        if parts['active'][i, j] >= parts['new'][i, j] and activity[j] > 0:
            return 'active', 'Active this week' if posts_week[j] > 0 else 'Active this month', 0
        if newcomer[j]:
            return fair_chance(j)
        if activity[j] > 0:
            return 'active', 'Active this week' if posts_week[j] > 0 else 'Active this month', 0
        return 'discover', 'Open to everyone on Discover', 0

    def personal_reason(i, u, j):
        mine = np.flatnonzero(x[i])
        top = max(PARTS, key=lambda p: parts[p][i, j])            # ties: the first in PARTS
        if parts[top][i, j] <= 0:
            return default_reason(i, j)
        if top == 'cf':
            src = mine[np.argmax(jac[mine, j])]
            n = int(round(co[src, j]))
            if n < 1 or (noisy and not cfg.count_under_noise):
                # no number: none to state, or (count_under_noise = False) the noisy count could be far from the truth
                return 'shared_members', f'Members of {name[src]} also joined it', int(gids[src])
            # with privacy on (R10) the count is clipped and noisy, so the reason says it is approximate
            about = 'About ' if cfg.m is not None or (cfg.eps is not None and not math.isinf(cfg.eps)) else ''
            return ('shared_members', f'{about}{n} member{"s" if n > 1 else ""} of {name[src]} '
                    f'{"are" if n > 1 else "is"} in it', int(gids[src]))
        if top == 'mf':
            src = mine[np.argmax(links[mine, j])]
            return 'similar_group', f"Because you're in {name[src]}", int(gids[src])
        if top == 'social':
            fr = friends[(u, gids[j])]
            if len(fr) == 1:
                return 'friend', f'Your friend user {fr[0]} is a member', int(fr[0])
            return ('friend', f'Your friend user {fr[0]} and {len(fr) - 1} other friend{"s" if len(fr) > 2 else ""} '
                    f'are members', int(fr[0]))
        # content: the user's own group, or the chosen topics, that add the most (both are divided by the
        # same count in similar_descriptions_scores, so they compare directly)
        best_group = text_sim[mine, j].max() if len(mine) else -1.0
        if topics_sim is not None and u in chosen.index and cfg.topic_weight * topics_sim[i, j] > best_group:
            t = max(chosen[u], key=lambda t: one_topic[t][j])
            return 'topic', f'Matches a topic you picked: {t.replace("_", " ")}', 0
        src = mine[np.argmax(text_sim[mine, j])]
        return 'similar_group', f'Similar to {name[src]}, which you joined', int(gids[src])

    rows = []
    for i, u in enumerate(users):
        for r, j in enumerate(picks[i]):
            if j < 0:
                continue
            if forced[i, r]:
                code, text, ref = fair_chance(j)
            elif personal[i]:
                code, text, ref = personal_reason(i, u, j)
            else:
                code, text, ref = default_reason(i, j)
            rows.append({'user_id': int(u), 'rank': r + 1, 'group_id': int(gids[j]), 'score': float(score[i, j]),
                         'reason_code': code, 'reason_text': text, 'reason_ref': ref,
                         'forced': bool(forced[i, r]), 'personal': bool(personal[i]),
                         **{f'part_{p}': float(parts[p][i, j]) for p in PARTS + ['active', 'new']}})
    recs = pd.DataFrame(rows)
    recs.attrs['relaxed'] = relaxed
    recs.attrs['order'] = [int(u) for u in users[order]]     # the order users were served in (for the cap c)
    return recs


def lists_from(recs):
    """recommend()'s rows -> {user_id: [group_id, ...]} in rank order, the format evaluate() takes."""
    recs = recs.sort_values(['user_id', 'rank'])
    return {int(u): [int(g) for g in rows.group_id] for u, rows in recs.groupby('user_id')}

# ---------------------------------------------------------------------------------------------------
# 10. Privacy: contribution clipping and Laplace noise (rule R10, experiment E3, notebook 08)
#     group_stats() calls these when config.m or config.eps is set. What is protected: the statistics
#     about other members' memberships, i.e. the group sizes and the pair counts in co = X^T X, and so
#     everything computed from them ("also joined", the AI model, which groups count as small).
#     The promise (epsilon-differential privacy): adding or removing one member, with all their
#     memberships, changes the probability of any result by at most a factor e^eps.
# ---------------------------------------------------------------------------------------------------

# The privacy setting chosen in notebook 08 (experiment E3), on the practice quiz: the smallest eps that keeps at
# least 90% of the accuracy and of the newcomer slots. Turn it on with dataclasses.replace(config, **PRIVATE).
# Config's own default stays off (eps = None, m = None), so no other notebook's results change.
PRIVATE = {'eps': 2.0, 'm': 3, 'size_share': 0.25}

# Colours for the privacy figures: one line per cap m, as steps of the violet of 'private' (METHODS), darker for a
# smaller m (fewer groups counted per member), because m is ordered. Re-stepped so that every step stays apart from
# the popularity blue drawn next to them (checked with a palette validator: colour-blind difference 12.8, normal
# vision 17.0). The lightest step is pale on white (contrast 2.2), so charts also tell the lines apart by marker
# shape and name them in a legend.
PRIVACY_M_COLOURS = {3: '#24165f', 5: '#4a33b0', 8: '#b0a4f0'}


def membership_keys(user_ids, group_ids, seed=SEED):
    """A pseudo-random number in [0, 1) for each (member, group) pair: a hash (splitmix64, applied three
    times) of the seed, the member and the group. The same pair always gets the same number, whatever else
    is in the data, so a member's draw never depends on anyone else's rows."""
    def mix(x):
        x = x + np.uint64(0x9E3779B97F4A7C15)
        x = (x ^ (x >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        x = (x ^ (x >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        return x ^ (x >> np.uint64(31))
    u = np.asarray(user_ids).astype(np.uint64)
    g = np.asarray(group_ids).astype(np.uint64)
    with np.errstate(over='ignore'):                            # uint64 arithmetic wraps around, on purpose
        x = mix(mix(mix(np.full(len(u), int(seed) % 2**64, dtype=np.uint64)) ^ u) ^ g)
    return (x >> np.uint64(11)).astype(float) / float(2**53)


def clip_contributions(mem, m, seed=SEED):
    """Keep at most m memberships per member: for a member with more, a random m of them. mem: one row per
    membership (user_id, group_id, ...). Kept rows stay in their order.

    "Random" comes from membership_keys(seed): each member keeps their m groups with the smallest keys. So
    which groups count for a member depends only on that member's own groups and the seed: adding or removing
    one member changes no one else's rows, exactly what dp_sensitivity() assumes. (A shared random stream
    would shift everyone's draws when one row is added.) In BOING the seed must be secret."""
    users = mem.user_id.to_numpy()
    key = membership_keys(users, mem.group_id.to_numpy(), seed)
    order = np.lexsort((key, users))                            # by member, then in a random order
    sorted_users = users[order]
    first = np.r_[True, sorted_users[1:] != sorted_users[:-1]]  # where each member's rows start
    start = np.maximum.accumulate(np.where(first, np.arange(len(order)), 0))
    keep = order[(np.arange(len(order)) - start) < m]           # each member's first m rows, in the random order
    return mem.iloc[np.sort(keep)]


def dp_sensitivity(m):
    """How much one member can change the released counts (sum of absolute changes), when each member
    counts for at most m groups: the group sizes by m (1 per group), the pair counts by m(m-1)/2 (1 per
    pair of their groups; each pair counted once)."""
    return m, m * (m - 1) / 2


def dp_scales(eps, m, size_share=0.5):
    """The Laplace noise scales (sensitivity / budget) for the group sizes and for the pair counts: the
    sizes get size_share x eps of the budget, the pairs the rest. The two budgets add up to eps."""
    assert 0 < size_share < 1, 'size_share is a share of the budget, strictly between 0 and 1'
    size_sens, pair_sens = dp_sensitivity(m)
    return size_sens / (size_share * eps), pair_sens / ((1 - size_share) * eps)


def noisy_counts(co, eps, m, size_share, rng, noise=None, return_noise=False):
    """The Laplace mechanism on co = X^T X (groups x groups; diagonal = the group sizes), for budget eps.

    Each group size gets Laplace noise of scale m / (size_share x eps); each pair of groups (counted once,
    i < j) gets its own noise of scale m(m-1)/2 / ((1 - size_share) x eps). Then post-processing, which
    reads only the noisy numbers and so keeps the guarantee: a negative count becomes 0, a pair never
    shares more members than its smaller group has, and the table is mirrored to stay symmetric.
    rng: a numpy Generator (seeded here, so the experiments can be repeated; in BOING it must draw from a
    secret source, since anyone who knows the seed can redraw the noise and subtract it).
    noise: {'sizes': n draws, 'pairs': n(n-1)/2 draws in np.triu_indices(n, 1) order} to add instead of drawing
    (the test cases give them as data; rng is then not used). return_noise: also return the draws, as that dict.
    Returns a new groups x groups array (and the draws, with return_noise=True).
    """
    co = np.asarray(co, dtype=float)
    n = co.shape[0]
    scale_size, scale_pair = dp_scales(eps, m, size_share)
    i, j = np.triu_indices(n, k=1)
    if noise is None:
        d_sizes = rng.laplace(0.0, scale_size, n)
        d_pairs = rng.laplace(0.0, scale_pair, len(i))
    else:
        d_sizes, d_pairs = np.asarray(noise['sizes'], dtype=float), np.asarray(noise['pairs'], dtype=float)
        assert d_sizes.shape == (n,) and d_pairs.shape == (len(i),), 'injected noise of the wrong size'
    sizes = np.maximum(np.diag(co) + d_sizes, 0.0)
    pairs = np.clip(co[i, j] + d_pairs, 0.0, np.minimum(sizes[i], sizes[j]))
    out = np.zeros((n, n))
    out[i, j] = pairs
    out = out + out.T
    np.fill_diagonal(out, sizes)
    return (out, {'sizes': d_sizes, 'pairs': d_pairs}) if return_noise else out


# ---------------------------------------------------------------------------------------------------
# 11. Newcomers (experiment E5) and do the rules hold? (experiment E6), notebook 10; and the test cases for
#     BOING's JavaScript port
#       newcomer_quiz()      a quiz for the members the test set leaves out (fewer than 3 groups): E5
#       check_rules()        counts every violation of the rules in a set of suggestions: E6
#       make_test_cases()    writes small cases (data, config, expected top 5) the port is checked against
#       verify_test_cases()  re-runs every case from its own files and compares with its expected.csv
# ---------------------------------------------------------------------------------------------------

def newcomer_quiz(vis, tested, seed=SEED):
    """A quiz for the members the test set leaves out (E5). The test set only hides groups of members who had 3
    or more, so it holds no brand-new member. Here every member who is not tested, not suspended, and is in at
    least one group (training data) gets one of their groups hidden, drawn with `seed` (split_memberships with
    min_groups=1: 20% rounded, at least 1, so 1 for members with 1 or 2 groups).
    tested: the ids of the test set's members (load_answers().test.user_id): scoring code passes them, since
    only the answer key says who they are. Returns (qvis, quiz): qvis is a Visible without the quiz memberships
    (and without the posts and likes that would give them away); quiz is the hidden memberships (user_id,
    group_id, joined_day). Nothing is tuned on it: it only scores."""
    leave_out = set(np.asarray(tested).tolist()) | set(vis.users.user_id[vis.users.suspended == 1].tolist())
    rows = vis.train[~vis.train.user_id.isin(leave_out)]
    _, quiz = split_memberships(rows, vis.users, vis.groups, frac=0.2, min_groups=1, seed=seed)
    hidden = set(zip(quiz.user_id, quiz.group_id))
    keep = np.array([(u, g) not in hidden for u, g in zip(vis.train.user_id, vis.train.group_id)], dtype=bool)
    posts, likes = drop_leaks(vis.posts, vis.likes, quiz)
    return replace(vis, train=vis.train[keep].reset_index(drop=True), posts=posts, likes=likes), quiz


# Every check, in the order check_rules() reports them: id -> (rule, what counts as a violation, hard rule?)
# Hard rules must have 0 violations. The last three are dials (R4, R5): a "violation" there is allowed
# when the re-ranker had to relax the rule (it says so in recs.attrs['relaxed']).
RULE_CHECKS = {
    'reason_parts':    ('R6', 'a part of the score, recomputed independently, differs from what recommend() reports', True),
    'reason_fidelity': ('R6', 'the reason is not faithful to the computed score: not the part that adds the most, nor a quota slot the list allows, nor the fallback', True),
    'reason_details':  ('R6', 'the reason names the wrong group, friend or number, or leaves its fixed template', True),
    'names_private':   ('R6, R8', 'a reason names a friend whose profile is private', True),
    'names_blocked':   ('R6, R8', 'a reason names someone the member blocked, or who blocked the member', True),
    'names_suspended': ('R6, R8', 'a reason names a suspended account', True),
    'names_other':     ('R6, R9', 'a reason names someone who is not a counted friend in that group', True),
    'hidden_by_mods':  ('R8', 'a group hidden by moderators is suggested', True),
    'closed_group':    ('R8', 'a closed group (not open to everyone) is suggested', True),
    'already_joined':  ('R7', 'a group the member is already in is suggested', True),
    'not_interested':  ('R7', 'a group the member marked "not interested" is suggested', True),
    'not_a_group':     ('R8', 'an unknown group, or the same group twice in one list', True),
    'list_length':     ('R11', 'a list does not hold exactly 5 groups (or every candidate, when there are fewer)', True),
    'empty_list':      ('R1', 'a member with at least one candidate gets no list', True),
    'allow_list':      ('R2', 'the recommender is handed a table or column outside the allow-list', True),
    'private_data':    ('R2', 'a suggestion changes when private data is added or changed (planner, chats, wallet, the answer key: as columns '
                              'handed to the recommender, and in the files it must never read: test memberships, full memberships, posts, likes)', True),
    'paid_budget':     ('R3', 'a suggestion changes when groups get a paid budget', True),
    'quota':           ('R4, dial q', 'a list holds fewer than ceil(q x 5) new or small groups', False),
    'global_cap':      ('R4, dial c', 'a group gets more than c of all slots', False),
    'topic_cap':       ('R5, dial n', 'a list holds more than n groups of one public topic cluster', False),
}

# R2's allow-list: the only columns a recommender may be handed, table by table (README, "The data files")
ALLOWED_COLUMNS = {
    'train': ['user_id', 'group_id', 'joined_day'],
    'posts': ['post_id', 'user_id', 'group_id', 'day', 'text', 'likes', 'hidden_by_mods'],
    'likes': ['post_id', 'user_id'],
    'friendships': ['user_a', 'user_b', 'since_day'],
    'blocks': ['user_id', 'blocked_id'],
    'topics': ['user_id', 'topic'],
    'not_interested': ['user_id', 'group_id', 'day'],
    'users': ['user_id', 'created_day', 'level', 'privacy', 'suspended'],
    'groups': ['group_id', 'name', 'about', 'open', 'created_day', 'hidden_by_mods'],
}


def _recount(vis, users, cfg, stats=None):
    """check_rules()'s own recomputation of every part of every served member's scores, straight from the
    tables. It calls none of group_stats(), clip_contributions(), noisy_counts(), raw_parts(), rescale(), off_parts(),
    social_scores() or recommend(), so a mistake there shows up as a difference. The counts about other members
    (co = X^T X) are recomputed too, with the clipping to m groups per member (only the hash membership_keys()
    is shared). With noise on (eps, act_eps) only the random draws themselves are taken from `stats` (the recommender's
    own statistics, default stats_for(vis, cfg); GroupStats.noise): co and the activity are rebuilt from the raw tables
    plus those draws, with this function's own post-processing. (Statistics made before the draws were kept fall
    back to the recommender's own noisy co.)"""
    from types import SimpleNamespace
    from sklearn.feature_extraction.text import TfidfVectorizer
    groups = vis.groups.sort_values('group_id').reset_index(drop=True)
    gids = groups.group_id.to_numpy()
    col = {int(g): j for j, g in enumerate(gids)}
    row = {int(u): i for i, u in enumerate(users)}
    n_u, n_g = len(users), len(gids)
    people = vis.users.set_index('user_id')
    counts = set(people.index[(people.suspended == 0) & (people.level >= cfg.L)].tolist())
    # R9 with r9_scope = 'all': an account's weight in the activity and as a friend (1, or burst_w while young)
    young_ids = set(people.index[people.created_day > TODAY - cfg.young_days].tolist())
    weight_of = (lambda v: (cfg.burst_w if v in young_ids else 1.0)) if cfg.r9_scope == 'all' else (lambda v: 1.0)
    friends_count = {v for v in counts if weight_of(v) > 0}
    if stats is None and ((cfg.eps is not None and not math.isinf(cfg.eps)) or cfg.act_eps is not None):
        stats = stats_for(vis, cfg)

    # each served member's own groups (all their visible memberships) and their candidates
    own = np.zeros((n_u, n_g))
    for u, g in zip(vis.train.user_id, vis.train.group_id):
        if u in row and g in col:
            own[row[u], col[g]] = 1.0
    on_discover = ((groups.open == 1) & (groups.hidden_by_mods == 0)).to_numpy()
    cand = on_discover[None, :] & (own == 0)
    for u, g in zip(vis.not_interested.user_id, vis.not_interested.group_id):
        if u in row and g in col:
            cand[row[u], col[g]] = False

    # members two groups share, counting only accounts that count (R8, R9), each for at most m groups (R10),
    # young ones weighted (R9)
    noisy = cfg.eps is not None and not math.isinf(cfg.eps)
    draws = stats.noise if noisy and stats is not None and stats.noise is not None and 'sizes' in stats.noise else None
    if noisy and draws is None:
        co = stats.co.reindex(index=gids, columns=gids).to_numpy(float)     # no draws kept: the recommender's own noisy co
    else:
        mem = vis.train[vis.train.user_id.isin(counts) & vis.train.group_id.isin(gids)]
        mem = mem.drop_duplicates(['user_id', 'group_id'])
        if cfg.m is not None:            # each member keeps the m groups with the smallest hash keys
            key = membership_keys(mem.user_id.to_numpy(), mem.group_id.to_numpy(),
                                  cfg.seed if cfg.noise_seed is None else cfg.noise_seed)
            mem = mem.assign(key=key).sort_values(['user_id', 'key'], kind='stable')
            mem = mem[mem.groupby('user_id').cumcount() < cfg.m]
        w = np.ones(len(mem))
        if cfg.burst_w != 1:
            young = people.created_day.reindex(mem.user_id).to_numpy() > TODAY - cfg.young_days
            w = np.where(young, math.sqrt(cfg.burst_w), 1.0)
        x = (pd.DataFrame({'u': mem.user_id.to_numpy(), 'g': mem.group_id.to_numpy(), 'w': w})
             .pivot_table(index='u', columns='g', values='w', aggfunc='sum', fill_value=0.0)
             .reindex(columns=gids, fill_value=0.0).to_numpy(float))
        co = x.T @ x
        if noisy:
            # the same Laplace draws, added and post-processed here: sizes at least 0, a pair at most its smaller group, symmetric
            iu, ju = np.triu_indices(n_g, k=1)
            sz = np.maximum(np.diag(co) + np.asarray(draws['sizes'], dtype=float), 0.0)
            pr = np.minimum(np.maximum(co[iu, ju] + np.asarray(draws['pairs'], dtype=float), 0.0), np.minimum(sz[iu], sz[ju]))
            co = np.zeros((n_g, n_g))
            co[iu, ju] = pr
            co[ju, iu] = pr
            co[np.arange(n_g), np.arange(n_g)] = sz
    # the members two groups truly share (counted accounts, each once, no weight, no clipping, no noise): the
    # number a reason must state when it does not say "About"
    real = vis.train[vis.train.user_id.isin(counts) & vis.train.group_id.isin(gids)].drop_duplicates(['user_id', 'group_id'])
    x01 = pd.crosstab(real.user_id, real.group_id).clip(upper=1).reindex(columns=gids, fill_value=0).to_numpy(float)
    members_co = x01.T @ x01
    size = np.diag(co).copy()
    union = size[:, None] + size[None, :] - co
    jac = np.zeros_like(co)
    np.divide(co, union, out=jac, where=union > 0)
    np.fill_diagonal(jac, 0.0)
    values, vectors = np.linalg.eigh((co + co.T) / 2)
    top = np.argsort(-values, kind='stable')[:cfg.k]
    links = vectors[:, top] @ vectors[:, top].T              # V V^T: the sign of each taste does not matter

    # similar descriptions: TF-IDF rows have length 1, so their dot product is the cosine
    texts = (groups.name + ' ' + groups.about).tolist()
    tfidf = TfidfVectorizer().fit(texts)
    gv = tfidf.transform(texts)
    text_sim = (gv @ gv.T).toarray()
    total, count = own @ text_sim, own.sum(axis=1)
    chosen = vis.topics.groupby('user_id').topic.apply(list).to_dict()
    if cfg.topic_weight > 0:
        query = tfidf.transform([' '.join(t.replace('_', ' ') for t in chosen.get(int(u), [])) for u in users])
        has = np.asarray(query.multiply(query).sum(axis=1)).ravel() > 0
        total = total + cfg.topic_weight * has[:, None] * (query @ gv.T).toarray()
        count = count + cfg.topic_weight * has
    content = np.divide(total, count[:, None], out=np.zeros_like(total), where=count[:, None] > 0)

    # friends who may count and be named: public, counted, and no block either way (R6, R8, R9)
    friends_of = {}
    for a, b in zip(vis.friendships.user_a, vis.friendships.user_b):
        friends_of.setdefault(int(a), set()).add(int(b))
        friends_of.setdefault(int(b), set()).add(int(a))
    blocked = {(int(a), int(b)) for a, b in zip(vis.blocks.user_id, vis.blocks.blocked_id)}
    public = set(people.index[people.privacy == 'public'].tolist())
    groups_of = vis.train.drop_duplicates(['user_id', 'group_id']).groupby('user_id').group_id.apply(list).to_dict()
    social = np.zeros((n_u, n_g))
    named = {}                                                    # (member, group) -> friends in it, by id
    for u in users:
        u = int(u)
        ok = sorted(v for v in friends_of.get(u, ()) if v in public and v in friends_count
                    and (u, v) not in blocked and (v, u) not in blocked)
        for v in ok:
            for g in groups_of.get(v, []):
                if int(g) in col:
                    social[row[u], col[int(g)]] += weight_of(v)
                    named.setdefault((u, int(g)), []).append(v)

    # each part rescaled to 0-1 over the member's candidates (rounded to 10 decimals), then weighted
    def to01(s):
        s, out = np.round(s, 10), np.zeros((n_u, n_g))
        for i in range(n_u):
            c = cand[i]
            if c.any() and s[i, c].max() > s[i, c].min():
                out[i, c] = (s[i, c] - s[i, c].min()) / (s[i, c].max() - s[i, c].min())
        return out
    weight = {'cf': cfg.alpha, 'content': cfg.beta, 'social': cfg.gamma, 'mf': cfg.delta}
    raw = {'cf': own @ jac, 'content': content, 'social': social, 'mf': own @ links}
    parts = {p: weight[p] * to01(raw[p]) for p in PARTS}
    personal = np.zeros(n_u, dtype=bool)
    if cfg.personal:
        personal = (np.where(cand, sum(parts.values()), 0.0) > 0).any(axis=1)

    # personalisation off: recent activity (posts and likes of the last 30 days, counted accounts, posts not
    # hidden by moderators) and newness
    p = vis.posts
    recent = p[(p.group_id > 0) & (p.hidden_by_mods == 0) & p.user_id.isin(counts) & (p.day > TODAY - ACTIVE_DAYS)]
    liked = vis.likes[vis.likes.user_id.isin(counts)].merge(recent[['post_id', 'group_id']], on='post_id')
    if cfg.act_eps is not None:
        # R10 for the activity: members who posted, each counted (with its R9 weight) in at most m groups (the m with the
        # smallest hash keys), plus the recommender's own draws, rounded, at least 0; no weekly count
        pairs = {}
        for u, g in zip(recent.user_id, recent.group_id):
            if weight_of(int(u)) > 0 and int(g) in col:
                pairs.setdefault(int(u), set()).add(int(g))
        seed_ = cfg.seed if cfg.noise_seed is None else cfg.noise_seed
        counted_act = np.zeros(n_g)
        for u, gs in pairs.items():
            gs = sorted(gs)
            keys = membership_keys(np.full(len(gs), u), np.array(gs), seed_)
            for k_ in np.argsort(keys, kind='stable')[:cfg.m]:
                counted_act[col[gs[k_]]] += weight_of(u)
        act_draws = stats.act_noise if stats is not None and stats.act_noise is not None else np.zeros(n_g)
        activity = np.maximum(np.round(counted_act + np.asarray(act_draws, dtype=float)), 0.0)
        posts_week = np.zeros(n_g)
    else:
        rw = np.array([weight_of(int(u)) for u in recent.user_id], dtype=float)
        lw = np.array([weight_of(int(u)) for u in liked.user_id], dtype=float)
        activity = (pd.Series(rw, index=recent.group_id.to_numpy()).groupby(level=0).sum().reindex(gids, fill_value=0.0)
                    + pd.Series(lw, index=liked.group_id.to_numpy()).groupby(level=0).sum().reindex(gids, fill_value=0.0)).to_numpy(float)
        wk = recent.day.to_numpy() > TODAY - WEEK
        posts_week = pd.Series(rw[wk], index=recent.group_id.to_numpy()[wk]).groupby(level=0).sum().reindex(gids, fill_value=0.0).to_numpy()
    act = np.log1p(activity)
    peak = act[on_discover].max() if on_discover.any() else 0.0
    created = groups.created_day.to_numpy(float)
    newness = np.clip(1 - (TODAY - created) / NEW_DAYS, 0, 1)
    off = {'active': (1 - cfg.off_new_w) * (act / peak if peak > 0 else np.zeros(n_g)), 'new': cfg.off_new_w * newness}
    for q in PARTS:
        parts[q] = np.where(personal[:, None], parts[q], 0.0)
    for q in ['active', 'new']:
        parts[q] = np.where(personal[:, None], 0.0, np.broadcast_to(off[q], (n_u, n_g)))

    new = created > TODAY - NEW_DAYS
    shown_count = vis.train[vis.train.group_id.isin(gids)].drop_duplicates(['user_id', 'group_id']).group_id.value_counts()
    if cfg.small_from == 'public':     # the member count Discover shows: every membership, no clipping, no noise
        small = shown_count.reindex(gids, fill_value=0).to_numpy() < SMALL
    elif cfg.small_from == 'r9':       # the same count, of the accounts R9 counts only (young ones weighted burst_w)
        ok = vis.train[vis.train.user_id.isin(counts) & vis.train.group_id.isin(gids)].drop_duplicates(['user_id', 'group_id'])
        w9 = np.where(people.created_day.reindex(ok.user_id).to_numpy() > TODAY - cfg.young_days, cfg.burst_w, 1.0)
        n9 = np.zeros(n_g)
        np.add.at(n9, [col[int(g)] for g in ok.group_id], w9)
        small = n9 < SMALL
    else:
        small = size < SMALL
    return SimpleNamespace(gids=gids, col=col, row=row, cand=cand, own=own, parts=parts, personal=personal,
                           co=co, members_co=members_co, jac=jac, links=links, text_sim=text_sim, named=named, new=new,
                           newcomer=new | small, activity=activity, posts_week=posts_week,
                           names=groups.name.to_numpy(), people=people, counts=counts, friends_count=friends_count, public=public,
                           friends_of=friends_of, blocked=blocked, groups_of=groups_of, chosen=chosen)


def _stated_part(code, text):
    """Which part of the score a reason says added the most ('cf', 'content', 'social', 'mf', 'active',
    'new'), read from its code and fixed template; None for 'discover'."""
    if code == 'similar_group':
        return 'mf' if text.startswith("Because you're in") else 'content'
    return {'shared_members': 'cf', 'topic': 'content', 'friend': 'social', 'active': 'active',
            'new_group': 'new'}.get(code)


def _with_private_data(vis, seed, answers=None):
    """A copy of the data where every member also has private data the recommender must never use (R2):
    planner goals and tasks, calendar, coach chats, messages, purchases, wallet balance and tokens (all made
    up), and the answer key's hidden columns, shuffled between members and groups (answers = load_answers())
    or made up (answers = None). Two seeds give two different versions."""
    rng = np.random.default_rng(seed)
    users, groups = vis.users.copy(), vis.groups.copy()
    n = len(users)
    users['planner_goal'] = rng.choice(['pass calculus', 'run a 5k', 'learn 500 Spanish words',
                                        'sleep before 11', 'finish my portfolio'], n)
    users['planner_tasks_this_week'] = rng.integers(0, 30, n)
    users['calendar_busy_hours'] = rng.integers(0, 60, n)
    users['coach_chat_topic'] = rng.choice(['exam stress', 'motivation', 'a hard week', 'a study plan'], n)
    users['messages_sent'] = rng.integers(0, 500, n)
    users['purchases'] = rng.integers(0, 10, n)
    users['wallet_balance'] = rng.gamma(1.0, 200.0, n).round(2)
    users['tokens_held'] = rng.integers(0, 10 ** 6, n)
    if answers is not None:
        users['interests'] = rng.permutation(answers.user_interests.reindex(users.user_id).to_numpy())
        users['is_fake'] = rng.permutation(answers.user_is_fake.reindex(users.user_id).to_numpy())
        groups['topic'] = rng.permutation(answers.group_topic.reindex(groups.group_id).to_numpy())
    else:
        topics = ['languages', 'coding', 'maths', 'physics', 'fitness', 'art', 'music', 'exam_prep', 'careers', 'habits']
        users['interests'] = [f'{t}:1.00' for t in rng.choice(topics, n)]
        users['is_fake'] = rng.integers(0, 2, n)
        groups['topic'] = rng.choice(topics, len(groups))
    return replace(vis, users=users, groups=groups)


# The files a recommender must never read (README, "The data files"): the test memberships, and the full memberships, posts and
# likes, which contain them; and the hidden columns of users.csv and groups.csv (the rest of those two files is allowed)
FORBIDDEN_FILES = {'test_memberships.csv': 'group_id', 'memberships.csv': 'group_id', 'posts.csv': 'group_id', 'likes.csv': 'post_id'}
FORBIDDEN_COLUMNS = {'users.csv': ['interests', 'is_fake'], 'groups.csv': ['topic']}


class _forbidden_files_altered:
    """With this active (`with _forbidden_files_altered(seed): ...`), reading a file a recommender must never read, with pandas,
    from any folder, gives an altered copy (R2): for FORBIDDEN_FILES a fifth of the rows dropped and the group of each membership
    or post (the post of each like) shuffled; for users.csv and groups.csv the hidden columns shuffled. The honest recommender
    is handed a Visible and reads no file, so its suggestions cannot change; one that peeks at the answer key on disk (for
    example through load_answers()) gets different answers, and so different suggestions."""
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.real = None

    def __enter__(self):
        self.real = real = pd.read_csv
        rng = self.rng

        def altered(path, *args, **kwargs):
            t = real(path, *args, **kwargs)
            name = Path(path).name if isinstance(path, (str, Path)) else ''
            if name in FORBIDDEN_FILES and len(t):
                t = t.iloc[np.sort(rng.choice(len(t), size=int(0.8 * len(t)), replace=False))].reset_index(drop=True)
                col = FORBIDDEN_FILES[name]
                if col in t.columns:
                    t[col] = rng.permutation(t[col].to_numpy())
            for c in FORBIDDEN_COLUMNS.get(name, []):
                if c in t.columns:
                    t[c] = rng.permutation(t[c].to_numpy())
            return t
        pd.read_csv = altered
        return self

    def __exit__(self, *exc):
        pd.read_csv = self.real
        return False


def _with_paid_budgets(vis, seed):
    """A copy of the data where about 1 group in 5 has paid for reach (tokens, a boost, ads) and members have
    spent tokens: things the ranking must never see (R3)."""
    rng = np.random.default_rng(seed)
    groups, users = vis.groups.copy(), vis.users.copy()
    paid = rng.random(len(groups)) < 0.2
    groups['paid_budget_tokens'] = np.where(paid, rng.integers(1000, 10 ** 6, len(groups)), 0)
    groups['boosted'] = paid.astype(int)
    groups['ad_spend'] = np.where(paid, rng.gamma(2.0, 500.0, len(groups)).round(2), 0.0)
    users['tokens_spent'] = rng.integers(0, 10 ** 5, len(users))
    return replace(vis, groups=groups, users=users)


def _rows_changed(a, b):
    """How many suggestions differ between two recommend() tables (by member and rank; a row on one side
    only counts too)."""
    cols = ['user_id', 'rank', 'group_id', 'score', 'reason_code', 'reason_text', 'reason_ref', 'forced', 'personal']
    m = a[cols].merge(b[cols], on=['user_id', 'rank'], how='outer', suffixes=('', '_b'), indicator=True)
    differ = np.array(m['_merge'] != 'both', dtype=bool)          # a writable copy
    both = ~differ
    for c in cols[2:]:
        if c == 'score':
            differ |= both & ~np.isclose(m.score.to_numpy(float), m.score_b.to_numpy(float), rtol=0, atol=1e-12)
        else:
            differ |= both & (m[c].astype(str) != m[c + '_b'].astype(str)).to_numpy()
    return int(differ.sum())


def check_rules(recs, data=DATA, config=None, users=None, stats=None, clusters=None, perturb=True, answers=None):
    """Count the violations of every rule in a set of suggestions (experiment E6). Nothing here trusts the
    code that made the suggestions: the scores' parts are recomputed independently (_recount) and every
    fact a reason states is checked against the data.

    recs: recommend()'s table (every check), or {user_id: [group_id, ...]} lists from any method (then only
          the checks that need no reasons: safety filters and list length);
    data: the Visible (or folder) the suggestions were made from; config: the Config they were made with;
    users: every member who was served (default: the members in recs), to catch an empty list;
    stats: the group_stats() they were made with, only needed with noise on (eps, act_eps): the checker rebuilds the
           noisy counts from the raw tables itself and takes only the random draws from it (GroupStats.noise);
    clusters: the public topic clusters they used (default: topic_clusters(data), as recommend() does);
    perturb: also run the R2 and R3 tests, which re-run recommend(users, data, config) on altered copies
             of the data, and once with the files it must never read altered (_forbidden_files_altered), and count
             the suggestions that change (needs a recs table made that way);
    answers: the answer key (load_answers()), used ONLY to hand the recommender the hidden columns
             shuffled between members in the R2 test, to show it ignores them; None = made-up values.
    Returns a table, one row per check (RULE_CHECKS): rule, check, hard, checked (how many items were
    looked at), violations, passed. table.violations.to_dict() gives the counts. Also, in table.attrs:
      'problems'  the first 20 problem rows of each check (a DataFrame), to read what went wrong;
      'fidelity'  explanation fidelity (R6): is each reason FAITHFUL TO THE COMPUTED SCORE? {kind: {'shown', 'true'}}
                  where kind is 'top part' (the reason names the part that adds the most), 'quota slot' (a slot given
                  by the newcomer quota, which says so; the list itself must show the quota could have given it, the
                  flag is not trusted) or 'fallback' (no part above 0: the reason states the fact the recommender
                  used). 'true' here means faithful, not factually true: with clipping and noise the score rests on
                  estimates, so check_facts() reads each reason against the raw data, separately.
    The quota check uses the recommender's own definition of "small" (config.small_from); check_facts() checks it on
    the real sizes.
    """
    import re
    cfg = config or Config()
    vis = data if isinstance(data, Visible) else load_visible(data)
    table = recs if isinstance(recs, pd.DataFrame) else None
    if table is not None:
        relaxed = dict(table.attrs.get('relaxed', {}))
        table = table.copy()
        table.attrs = {}                 # pandas copies attrs on every step: drop them (much faster)
    lists = lists_from(table) if table is not None else {int(u): [int(g) for g in l] for u, l in recs.items()}
    served = np.unique(np.asarray(list(lists) if users is None else list(users), dtype=int))
    rc = _recount(vis, served, cfg, stats)
    result, problems = {}, []
    fidelity = {kind: {'shown': 0, 'true': 0} for kind in ['top part', 'quota slot', 'fallback']}

    def record(check, checked, bad):
        # bad: a list of (user_id, rank, group_id, what is wrong)
        result[check] = {'checked': int(checked), 'violations': len(bad), 'passed': len(bad) == 0}
        problems.extend({'check': check, 'user_id': u, 'rank': r, 'group_id': g, 'problem': what}
                        for u, r, g, what in bad[:20])

    def skip(check):
        result[check] = {'checked': 0, 'violations': np.nan, 'passed': None}

    # --- Safety filters (R7, R8) on every suggestion
    shown = [(u, r + 1, g) for u, l in lists.items() for r, g in enumerate(l)]
    gtab = vis.groups.set_index('group_id')
    joined = set(zip(vis.train.user_id.astype(int), vis.train.group_id.astype(int)))
    dismissed = set(zip(vis.not_interested.user_id.astype(int), vis.not_interested.group_id.astype(int)))
    record('hidden_by_mods', len(shown), [(u, r, g, 'hidden by moderators') for u, r, g in shown
                                          if g in gtab.index and gtab.hidden_by_mods[g] == 1])
    record('closed_group', len(shown), [(u, r, g, 'closed') for u, r, g in shown if g in gtab.index and gtab.open[g] == 0])
    record('already_joined', len(shown), [(u, r, g, 'already a member') for u, r, g in shown if (u, g) in joined])
    record('not_interested', len(shown), [(u, r, g, 'marked not interested') for u, r, g in shown if (u, g) in dismissed])
    seen, bad = set(), []
    for u, r, g in shown:
        if g not in gtab.index or (u, g) in seen:
            bad.append((u, r, g, 'unknown group or shown twice'))
        seen.add((u, g))
    record('not_a_group', len(shown), bad)

    # --- List length (R11) and never an empty list (R1)
    n_cand = rc.cand.sum(axis=1)
    record('list_length', len(served), [(int(u), 0, 0, f'{len(lists.get(int(u), []))} groups, {min(K, n_cand[i])} expected')
                                        for i, u in enumerate(served) if len(lists.get(int(u), [])) != min(K, n_cand[i])])
    record('empty_list', int((n_cand > 0).sum()), [(int(u), 0, 0, 'no list') for i, u in enumerate(served)
                                                   if n_cand[i] > 0 and not lists.get(int(u))])

    # --- The allow-list (R2): no table or column beyond ALLOWED_COLUMNS reaches the recommender
    bad = [(0, 0, 0, f'table {t}') for t in vars(vis) if t not in ALLOWED_COLUMNS]
    bad += [(0, 0, 0, f'{t}.{c}') for t, cols in ALLOWED_COLUMNS.items() if t in vars(vis)
            for c in getattr(vis, t).columns if c not in cols]
    record('allow_list', sum(getattr(vis, t).shape[1] for t in vars(vis)), bad)

    reason_checks = ['reason_parts', 'reason_fidelity', 'reason_details', 'names_private', 'names_blocked',
                     'names_suspended', 'names_other']
    if table is None:
        for check in reason_checks + ['private_data', 'paid_budget', 'quota', 'global_cap', 'topic_cap']:
            skip(check)
    else:
        rows = table.reset_index(drop=True)
        tol = 1e-9
        about = 'About ' if cfg.m is not None or (cfg.eps is not None and not math.isinf(cfg.eps)) else ''
        # A slot marked as a quota slot (forced) is not taken on trust: the quota can only have given it if q > 0, it is
        # among the last ceil(q x 5) ranks, and the list's other slots do not already hold the new or small groups the
        # quota asks for (the re-ranker forces a slot only when the slots left are just enough for those still owed)
        need = math.ceil(cfg.q * K - 1e-9)
        flag = rows.forced.astype(bool).to_numpy()
        newc = np.array([g in rc.col and bool(rc.newcomer[rc.col[g]]) for g in rows.group_id.astype(int)], dtype=bool)
        per_list = pd.DataFrame({'u': rows.user_id.astype(int).to_numpy(), 'forced': flag, 'free_new': newc & ~flag})
        per_list = per_list.groupby('u')[['forced', 'free_new']].sum()
        quota_room = (per_list.forced + per_list.free_new <= need).to_dict()
        part_bad, fidelity_bad, detail_bad = [], [], []
        name_bad = {'names_private': [], 'names_blocked': [], 'names_suspended': [], 'names_other': []}
        naming = 0
        for t in rows.itertuples(index=False):
            u, g, r, code, text, ref = int(t.user_id), int(t.group_id), int(t.rank), t.reason_code, t.reason_text, int(t.reason_ref)
            if g not in rc.col:
                continue                                              # already counted by not_a_group
            i, j = rc.row[u], rc.col[g]
            here = {p: rc.parts[p][i, j] for p in PARTS + ['active', 'new']}
            # (1) the parts, recomputed independently
            diff = max(abs(getattr(t, f'part_{p}') - v) for p, v in here.items())
            if diff > tol or bool(t.personal) != bool(rc.personal[i]):
                part_bad.append((u, r, g, f'largest difference {diff:.2e}, personal {t.personal} vs {rc.personal[i]}'))
            # (2) fidelity: the stated reason is the largest part (or the quota, or a true fallback fact)
            keys = PARTS if rc.personal[i] else ['active', 'new']
            best = max(here[p] for p in keys)
            stated = _stated_part(code, text)
            if t.forced:
                kind = 'quota slot'
                ok = code == 'new_group' and bool(rc.newcomer[j]) and need > 0 and r > K - need and quota_room[u]
            elif best <= 1e-12:
                kind = 'fallback'
                ok = code == ('active' if rc.activity[j] > 0 else 'new_group' if rc.newcomer[j] else 'discover')
            else:
                kind, ok = 'top part', stated in keys and here[stated] >= best - tol
            fidelity[kind]['shown'] += 1
            fidelity[kind]['true'] += int(ok)
            if not ok:
                fidelity_bad.append((u, r, g, f'says {code} ({text}); parts {({p: round(here[p], 4) for p in keys})}'))
            # (3) details: the right group, friend or number, in the fixed template
            mine = np.flatnonzero(rc.own[i])
            src = rc.col.get(ref, -1)
            ref_name = rc.names[src] if src >= 0 else ''
            if code == 'shared_members':
                # without "About", the number must be the members the two groups truly share; with it (clipping or
                # noise, R10), the count the recommender learned from; with noise on and count_under_noise = False, no number
                n = int(round((rc.co if about else rc.members_co)[src, j])) if src >= 0 else -1
                no_number = cfg.eps is not None and not math.isinf(cfg.eps) and not cfg.count_under_noise
                want = (f'Members of {ref_name} also joined it' if n < 1 or no_number else
                        f'{about}{n} member{"s" if n > 1 else ""} of {ref_name} {"are" if n > 1 else "is"} in it')
                ok = src in mine and rc.jac[src, j] >= rc.jac[mine, j].max() - 1e-12 and text == want
            elif code == 'similar_group' and stated == 'mf':
                ok = (src in mine and rc.links[src, j] >= rc.links[mine, j].max() - tol
                      and text == f"Because you're in {ref_name}")
            elif code == 'similar_group':
                ok = (src in mine and rc.text_sim[src, j] >= rc.text_sim[mine, j].max() - tol
                      and text == f'Similar to {ref_name}, which you joined')
            elif code == 'topic':
                ok = ref == 0 and any(text == f'Matches a topic you picked: {c.replace("_", " ")}'
                                      for c in rc.chosen.get(u, []))
            elif code == 'friend':
                fr = rc.named.get((u, g), [])
                want = (f'Your friend user {fr[0]} is a member' if len(fr) == 1 else
                        f'Your friend user {fr[0]} and {len(fr) - 1} other friend{"s" if len(fr) > 2 else ""} are members'
                        if fr else None)
                ok = bool(fr) and ref == fr[0] and text == want
            elif code == 'new_group':
                want = ('A new group: we show new groups so they get a fair chance' if rc.new[j] else
                        'A small group: we show small groups so they get a fair chance')
                ok = ref == 0 and bool(rc.newcomer[j]) and text == want
            elif code == 'active':
                ok = ref == 0 and rc.activity[j] > 0 and text == ('Active this week' if rc.posts_week[j] > 0 else 'Active this month')
            elif code == 'discover':
                ok = ref == 0 and text == 'Open to everyone on Discover'
            else:
                ok = False
            if not ok:
                detail_bad.append((u, r, g, f'{code}: "{text}" (ref {ref})'))
            # (4) privacy of everyone a reason names
            people = {int(v) for v in re.findall(r'\buser (\d+)', text)} | ({ref} if code == 'friend' else set())
            naming += bool(people)
            for v in people:
                who = rc.people.loc[v] if v in rc.people.index else None
                if who is None or who.privacy != 'public':
                    name_bad['names_private'].append((u, r, g, f'names user {v} (private profile)'))
                if (u, v) in rc.blocked or (v, u) in rc.blocked:
                    name_bad['names_blocked'].append((u, r, g, f'names user {v} (blocked)'))
                if who is not None and who.suspended == 1:
                    name_bad['names_suspended'].append((u, r, g, f'names user {v} (suspended)'))
                if (who is None or v not in rc.friends_count or v not in rc.friends_of.get(u, ())
                        or g not in rc.groups_of.get(v, [])):
                    name_bad['names_other'].append((u, r, g, f'names user {v} (not a counted friend in the group)'))
        record('reason_parts', len(rows), part_bad)
        record('reason_fidelity', len(rows), fidelity_bad)
        record('reason_details', len(rows), detail_bad)
        for check, bad in name_bad.items():
            record(check, naming, bad)

        # --- R2 and R3: altered copies of the data must give exactly the same suggestions
        if perturb:
            again = lambda v: recommend(served, v, cfg, clusters=clusters)
            # private data handed to the recommender (two versions), then the files it must never read altered on the way in
            changed = [_rows_changed(table, again(_with_private_data(vis, seed, answers))) for seed in (1, 2)]
            with _forbidden_files_altered(4):
                changed.append(_rows_changed(table, again(vis)))
            record('private_data', 3 * len(rows), [(0, 0, 0, f'{n} suggestions changed') for n in changed for _ in range(n)])
            n = _rows_changed(table, again(_with_paid_budgets(vis, 3)))
            record('paid_budget', len(rows), [(0, 0, 0, 'a suggestion changed')] * n)
        else:
            skip('private_data')
            skip('paid_budget')

        # --- The dials (R4, R5): kept unless the re-ranker had to relax them (need: ceil(q x 5), as above)
        record('quota', len(lists), [(u, 0, 0, 'too few new or small groups') for u, l in lists.items()
                                     if len(l) >= need and sum(bool(rc.newcomer[rc.col[g]]) for g in l if g in rc.col) < need])
        cap = np.inf if cfg.c is None else max(1, math.floor(cfg.c * K * len(served) + 1e-9))
        slots = pd.Series([g for l in lists.values() for g in l], dtype='int64').value_counts()
        record('global_cap', len(slots), [(0, 0, int(g), f'{n} slots, cap {cap}') for g, n in slots.items() if n > cap])
        cl = topic_clusters(vis, cfg.clusters) if clusters is None else clusters
        limit = K if cfg.n is None else cfg.n
        record('topic_cap', len(lists), [(u, 0, 0, 'too many of one cluster') for u, l in lists.items()
                                         if l and pd.Series(cl.reindex(l).to_numpy()).value_counts().max() > limit])
        for check, rule in [('quota', 'quota'), ('global_cap', 'global cap'), ('topic_cap', 'topic cap')]:
            result[check]['passed'] = result[check]['violations'] <= relaxed.get(rule, 0)

    out = pd.DataFrame([{'id': c, 'rule': rule, 'check': what, 'hard': hard, **result[c]}
                        for c, (rule, what, hard) in RULE_CHECKS.items()]).set_index('id')
    out.attrs['problems'] = pd.DataFrame(problems, columns=['check', 'user_id', 'rank', 'group_id', 'problem'])
    out.attrs['fidelity'] = fidelity
    return out


# What check_facts() calls a true reason, kind by kind (read against the raw training data: every account, no clipping, no noise)
FACT_KINDS = {
    'shared_members': 'the two groups truly share at least one member, and a number it states is close to the true one (COUNT_CLOSE)',
    'similar_group (AI model)': 'the member is in the group the reason names',
    'similar_group (descriptions)': 'the member is in the group it names, and the two descriptions share a word',
    'friend': 'the person named is a public friend of the member, no block either way, not suspended, and truly a member',
    'topic': 'the member chose that topic',
    'new_group (new)': 'the group was created in the last 30 days',
    'new_group (small)': 'the group has fewer than 10 members (the member count Discover shows; with a config whose small_from is '
                         "'r9', the members who count under R9, the design's own definition)",
    'active (this week)': 'someone posted in the group in the last 7 days',
    'active (this month)': 'someone posted in the group in the last 30 days',
    'discover': 'the group is open and not hidden by moderators',
}


def count_close(stated, true):
    """Is a number a "shared members" reason states close to the members the two groups truly share? Close = the true number
    is at least 1, and the stated one is within a factor 2 of it or within 3 of it (the second helps small counts)."""
    stated, true = np.asarray(stated, dtype=float), np.asarray(true, dtype=float)
    return (true >= 1) & (((stated <= 2 * true) & (2 * stated >= true)) | (np.abs(stated - true) <= 3))


COUNT_CLOSE = 'within a factor 2 of the true number, or within 3 of it'


def check_facts(recs, data=DATA, q=None, config=None):
    """Is what each reason says TRUE? (experiment E6, notebook 11; scoring side.) check_rules() asks whether a reason is
    faithful to the score the recommender computed; with clipping and noise (R10) that score rests on estimates, so a
    faithful reason can still state something false ("About 3 members of X are in it" when none are). This reads every
    reason against the raw training data instead: every account, no clipping, no noise, no weights (FACT_KINDS says what
    counts as true). A number a "shared members" reason states must be close to the true one (count_close), not only the
    two groups share someone. It also checks the quota on the real sizes: does each list hold ceil(q x 5) groups that are
    truly new or small? q: the quota (default: Config().q). config: the design the suggestions were made with; with
    small_from = 'r9', "small" is judged as that design defines it (members who count under R9), and the count Discover
    shows is reported too (newcomer_groups).
    recs: recommend()'s table. Returns a table, one row per kind of reason: shown, true, share true; the same for
    personalised lists ('shown (personal)', 'true (personal)') and the default list. In table.attrs:
      'quota'   {'lists', 'lists below the quota' (by config's definition of "small"), 'lists below the quota (count Discover shows)', 'quota slots',
                 'quota slots in groups truly new or small', ...};
      'counts'  for "shared members" reasons: how many state a number, how many of those are true, how many name groups that
                share someone, how many are close (COUNT_CLOSE), and the median ratio of the stated number to the true one;
      'small'   "A small group" reasons true by the design's definition and by the count Discover shows."""
    import re
    vis = data if isinstance(data, Visible) else load_visible(data)
    q = Config().q if q is None else q
    gids = group_ids(vis)
    col = pd.Index(gids)
    x = membership_matrix(vis).to_numpy(dtype=float)
    shared = x.T @ x                                                     # members two groups truly share, every account
    members = set(zip(vis.train.user_id.astype(int), vis.train.group_id.astype(int)))
    shown_sizes = group_sizes(vis)                                       # the member count Discover shows
    r9_small = config is not None and config.small_from == 'r9'
    sizes = member_counts(vis.train, vis.users, config, gids) if r9_small else shown_sizes
    created = vis.groups.set_index('group_id').created_day
    gtab = vis.groups.set_index('group_id')
    people = vis.users.set_index('user_id')
    friends = set(zip(vis.friendships.user_a, vis.friendships.user_b)) | set(zip(vis.friendships.user_b, vis.friendships.user_a))
    blocked = set(zip(vis.blocks.user_id, vis.blocks.blocked_id)) | set(zip(vis.blocks.blocked_id, vis.blocks.user_id))
    chosen = set(zip(vis.topics.user_id, vis.topics.topic.str.replace('_', ' ')))
    p = vis.posts[(vis.posts.group_id > 0) & (vis.posts.hidden_by_mods == 0)]
    active_month = set(p.group_id[p.day > TODAY - ACTIVE_DAYS])        # (a like counts only on a post of the window)
    active_week = set(p.group_id[p.day > TODAY - WEEK])
    _, vectors = tfidf_model(vis)
    text_sim = (vectors @ vectors.T).toarray()
    nc = newcomer_groups(vis, config)                                  # the design's own definition of "small" (public count by default)
    nc_shown = newcomer_groups(vis)                                    # by the member count Discover shows
    personal = recs.personal.astype(bool).to_numpy() if 'personal' in recs.columns else np.ones(len(recs), dtype=bool)
    rows, numbers, sharing = [], [], []
    for i, t in enumerate(recs.itertuples(index=False)):
        u, g, code, text, ref = int(t.user_id), int(t.group_id), t.reason_code, t.reason_text, int(t.reason_ref)
        if code == 'shared_members':
            kind = code
            n_true = shared[col.get_loc(ref), col.get_loc(g)] if ref in col and g in col else 0
            ok = n_true >= 1
            sharing.append(bool(ok))
            stated = re.search(r'(\d+) members? of', text)
            if stated:
                close = bool(count_close(int(stated.group(1)), n_true))
                numbers.append({'stated': int(stated.group(1)), 'true': float(n_true), 'close': close})
                ok = ok and close
        elif code == 'similar_group' and text.startswith("Because you're in"):
            kind, ok = 'similar_group (AI model)', (u, ref) in members
        elif code == 'similar_group':
            kind = 'similar_group (descriptions)'
            ok = (u, ref) in members and ref in col and text_sim[col.get_loc(ref), col.get_loc(g)] > 0
        elif code == 'friend':
            kind = code
            named = {int(v) for v in re.findall(r'\buser (\d+)', text)} | {ref}
            ok = all(v in people.index and people.privacy[v] == 'public' and people.suspended[v] == 0 and (u, v) in friends
                     and (u, v) not in blocked and (v, g) in members for v in named)
        elif code == 'topic':
            kind, ok = code, any(text == f'Matches a topic you picked: {c}' for uu, c in chosen if uu == u)
        elif code == 'new_group':
            if text.startswith('A new group'):
                kind, ok = 'new_group (new)', created[g] > TODAY - NEW_DAYS
            else:
                kind, ok = 'new_group (small)', sizes[g] < SMALL
        elif code == 'active':
            kind, ok = ('active (this week)', g in active_week) if 'week' in text else ('active (this month)', g in active_month)
        else:
            kind, ok = 'discover', gtab.open[g] == 1 and gtab.hidden_by_mods[g] == 0
        rows.append({'kind': kind, 'true': bool(ok), 'personal': bool(personal[i]), 'group_id': g})
    facts = pd.DataFrame(rows, columns=['kind', 'true', 'personal', 'group_id'])
    out = facts.groupby('kind').true.agg(shown='size', true='sum').reindex(list(FACT_KINDS)).fillna(0).astype(int)
    out['share true'] = out.true / out.shown.where(out.shown > 0)
    for side, mask in [('personal', facts.personal), ('default', ~facts.personal)]:
        part = facts[mask].groupby('kind').true.agg(shown='size', true='sum').reindex(list(FACT_KINDS)).fillna(0).astype(int)
        out[f'shown ({side})'], out[f'true ({side})'] = part['shown'], part['true']
    out['a true reason'] = pd.Series(FACT_KINDS)
    need = math.ceil(q * K - 1e-9)
    lists = lists_from(recs)
    forced = recs[recs.forced.astype(bool)]
    below = lambda groups_: int(sum(len(l) >= need and sum(g in groups_ for g in l) < need for l in lists.values()))
    out.attrs['quota'] = {'lists': len(lists),
                          'lists below the quota': below(nc),
                          'lists below the quota (count Discover shows)': below(nc_shown),
                          'quota slots': int(len(forced)),
                          'quota slots in groups truly new or small': int(forced.group_id.isin(nc).sum()),
                          'quota slots in groups new or small by the count Discover shows': int(forced.group_id.isin(nc_shown).sum())}
    nums = pd.DataFrame(numbers, columns=['stated', 'true', 'close'])
    sm = facts[facts.kind == 'shared_members']
    real = nums[nums.true >= 1]
    out.attrs['counts'] = {'shared-members reasons': int(len(sm)),
                           'the two groups share someone': int(sum(sharing)),
                           'shared-members reasons with a number': int(len(nums)),
                           'of them, the two groups share someone': int((nums.true >= 1).sum()),
                           'of them, the number is close': int(nums.close.sum()),
                           'stated / true number (median)': float((real.stated / real.true).median()) if len(real) else np.nan,
                           'stated minus true, median absolute': float((nums.stated - nums.true).abs().median()) if len(nums) else np.nan}
    small_rows = facts[facts.kind == 'new_group (small)']
    out.attrs['small'] = {'"small group" reasons': int(len(small_rows)),
                          "true by the design's definition": int(small_rows.true.sum()),
                          'true by the count Discover shows': int(sum(shown_sizes[g] < SMALL for g in small_rows.group_id))}
    return out


# --- The test cases for the JavaScript port -----------------------------------------------------------

# The small world's 20 groups: (id in data/sim_v1, the community its fake members like). Their names,
# descriptions, dates and flags are copied from sim_v1's public columns; they get the ids 1 to 20 in this
# order. 17 is new (day 355), 18 small, 19 hidden by moderators, 20 closed. The communities only steer
# who joins what in the generator; they are not written anywhere.
CASE_GROUPS = [(13, 'languages'), (32, 'languages'), (42, 'languages'), (15, 'languages'),
               (67, 'coding'), (118, 'coding'), (62, 'coding'), (25, 'coding'),
               (69, 'fitness'), (53, 'fitness'), (83, 'fitness'), (98, 'fitness'),
               (4, 'exams'), (36, 'exams'), (29, 'exams'), (65, 'exams'),
               (140, 'languages'), (101, 'coding'), (134, 'fitness'), (21, 'languages')]
CASE_TOPIC = {'languages': 'languages', 'coding': 'coding', 'fitness': 'fitness', 'exams': 'exam_prep'}
CASE_USERS = 100      # members in the small world: enough that most groups have 10 or more (so the quota matters)


def case_world(n_users=CASE_USERS, seed=SEED):
    """The small community every test case starts from: n_users members, the 20 groups of CASE_GROUPS, and
    memberships, friendships, posts, likes, one block, shared topics and one "not interested", made with
    their own seeded random numbers (never with the config). Member 1, the "focus" member most cases are
    about, is ordinary: established, public, in Spanish for beginners (1), Spanish evening chat (2) and
    Python project club (5), with friends. Returns a Visible, with the same columns as data/sim_v1."""
    rng = np.random.default_rng(seed + 557)
    src = load_visible(DATA).groups.set_index('group_id')
    groups = src.loc[[s for s, _ in CASE_GROUPS], ['name', 'about', 'open', 'created_day', 'hidden_by_mods']]
    groups = groups.reset_index(drop=True).assign(group_id=np.arange(1, len(CASE_GROUPS) + 1))
    groups = groups[ALLOWED_COLUMNS['groups']]
    community = np.array([c for _, c in CASE_GROUPS])
    names = list(CASE_TOPIC)
    g_created = groups.created_day.to_numpy()

    n = n_users
    uid = np.arange(1, n + 1)
    is_new = rng.random(n) < 0.15
    created = np.where(is_new, rng.integers(TODAY - NEW_DAYS + 1, TODAY + 1, n), rng.integers(0, 331, n))
    level = np.where(is_new, rng.integers(1, 6, n), rng.integers(3, 61, n))
    privacy = np.where(rng.random(n) < 0.75, 'public', 'private')
    first = rng.integers(0, len(names), n)
    second = np.where(rng.random(n) < 0.4, (first + rng.integers(1, len(names), n)) % len(names), -1)
    is_new[0], created[0], level[0], privacy[0], first[0], second[0] = False, 0, 20, 'public', 0, 1
    users = pd.DataFrame({'user_id': uid, 'created_day': created, 'level': level, 'privacy': privacy, 'suspended': 0})

    # every group starts with its creator: a member who likes its community and existed when it was made
    size = np.zeros(len(groups))
    mem = [(1, 1, 10), (1, 2, 40), (1, 5, 200)]
    size[[0, 1, 4]] += 1
    for j in np.flatnonzero(size == 0):
        fits = (np.array(names)[first] == community[j]) & (uid > 1)
        early = fits & (created <= g_created[j])
        maker = int(rng.choice(uid[early])) if early.any() else int(uid[fits][np.argmin(created[fits])])
        mem.append((maker, j + 1, int(max(g_created[j], created[maker - 1]))))
        size[j] += 1
    # then who joins what: mostly the member's communities, bigger groups more likely (rich get richer)
    for i in np.argsort(created, kind='stable'):
        if uid[i] == 1:
            continue
        fits = (community == names[first[i]]) | ((second[i] >= 0) & (community == names[max(second[i], 0)]))
        w = np.where(fits, 1.0, 0.08) * (size + 1)
        w[[g - 1 for u, g, _ in mem if u == uid[i]]] = 0.0          # not twice (the creators)
        w[16] = w[16] if is_new[i] else 0.0                        # the new group: only new members found it
        w[17] *= 0.3                                               # a small group
        for _ in range(rng.integers(0, 3) if is_new[i] else rng.integers(2, 6)):
            if w.sum() <= 0:
                break
            j = rng.choice(len(w), p=w / w.sum())
            mem.append((int(uid[i]), j + 1, int(min(TODAY, max(created[i], g_created[j]) + rng.integers(0, 15)))))
            size[j] += 1
            w[j] = 0.0
    train = pd.DataFrame(mem, columns=ALLOWED_COLUMNS['train']).sort_values(['user_id', 'group_id']).reset_index(drop=True)

    # friendships: people who share a group are more likely to be friends; member 1 gets public friends
    # in groups they are not in (so friend reasons appear)
    groups_of = train.groupby('user_id').group_id.apply(set).to_dict()
    pairs = set()
    for a in range(1, n + 1):
        for b in range(a + 1, n + 1):
            shared = groups_of.get(a, set()) & groups_of.get(b, set())
            if rng.random() < (0.12 if shared else 0.015):
                pairs.add((a, b))
    outside = [u for u in range(2, n + 1) if privacy[u - 1] == 'public' and not is_new[u - 1]
               and groups_of.get(u, set()) - groups_of[1]]
    pairs |= {(1, u) for u in outside[:6]}
    friendships = pd.DataFrame(sorted(pairs), columns=['user_a', 'user_b'])
    friendships['since_day'] = [int(min(TODAY, max(created[a - 1], created[b - 1]) + rng.integers(0, 30)))
                                for a, b in sorted(pairs)]

    # posts and likes: only members post in a group; about a third in the last 30 days; member 1 never posts
    texts = ['Week 3 check-in: on track!', 'Any tips for staying consistent?', 'Finished my first project, feedback welcome.',
             'Who wants to practise together this weekend?', 'Sharing my notes from today.', 'Small win today.']
    posts, likes = [], []
    authors = [u for u in range(2, n + 1) if u in groups_of]
    for _ in range(80):
        u = int(rng.choice(authors))
        g = 0 if rng.random() < 0.1 else int(rng.choice(sorted(groups_of[u])))
        joined = train[(train.user_id == u) & (train.group_id == g)].joined_day.max() if g else created[u - 1]
        start = int(max(created[u - 1], joined if g else 0))
        day = int(rng.integers(max(start, TODAY - NEW_DAYS + 1), TODAY + 1)) if rng.random() < 0.35 and start < TODAY \
            else int(rng.integers(start, TODAY + 1))
        posts.append([u, g, day, str(rng.choice(texts)), int(rng.random() < 0.05)])
    posts = pd.DataFrame(posts, columns=['user_id', 'group_id', 'day', 'text', 'hidden_by_mods']).sort_values('day', kind='stable')
    posts.insert(0, 'post_id', np.arange(1, len(posts) + 1))
    for pid, u, g in zip(posts.post_id, posts.user_id, posts.group_id):
        pool = [v for v in (train.user_id[train.group_id == g].unique() if g else range(2, n + 1)) if v not in (u, 1)]
        for v in rng.choice(pool, size=min(len(pool), rng.poisson(1.5)), replace=False) if pool else []:
            likes.append((int(pid), int(v)))
    likes = pd.DataFrame(sorted(likes), columns=ALLOWED_COLUMNS['likes'])
    posts['likes'] = posts.post_id.map(likes.groupby('post_id').size()).fillna(0).astype(int)
    posts = posts[ALLOWED_COLUMNS['posts']].reset_index(drop=True)

    shared = [(u, CASE_TOPIC[names[first[u - 1]]]) for u in range(1, n + 1) if u == 1 or rng.random() < 0.3]
    biggest = int(np.argmax(np.where([g not in groups_of.get(2, set()) for g in range(1, 21)], size, -1))) + 1
    return Visible(train=train, posts=posts, likes=likes, friendships=friendships,
                   blocks=pd.DataFrame([(n - 1, n)], columns=ALLOWED_COLUMNS['blocks']),
                   topics=pd.DataFrame(shared, columns=ALLOWED_COLUMNS['topics']),
                   not_interested=pd.DataFrame([(2, biggest, 350)], columns=ALLOWED_COLUMNS['not_interested']),
                   users=users, groups=groups)


LARGE_CASE_USERS = 300   # members in the larger test world (cases 12 and 13)


def case_world_large(n_users=LARGE_CASE_USERS):
    """A larger world for the test cases where no rule has to be relaxed: the first n_users members of data/sim_v1 (by id)
    and everything a recommender may see about them (their memberships, posts and the likes on them by those members,
    friendships, blocks, topics, "not interested" among them), with all 150 groups (129 on Discover, so a 5% cap is
    never short of groups). Returns a Visible with the same columns as data/sim_v1."""
    v = load_visible(DATA)
    keep = set(v.users.user_id.sort_values().iloc[:n_users].tolist())
    posts = v.posts[v.posts.user_id.isin(keep)]
    likes = v.likes[v.likes.user_id.isin(keep) & v.likes.post_id.isin(posts.post_id)]
    posts = posts.assign(likes=posts.post_id.map(likes.groupby('post_id').size()).fillna(0).astype(int))
    f, b = v.friendships, v.blocks
    return replace(v, users=v.users[v.users.user_id.isin(keep)].reset_index(drop=True),
                   train=v.train[v.train.user_id.isin(keep)].reset_index(drop=True),
                   posts=posts.reset_index(drop=True), likes=likes.reset_index(drop=True),
                   friendships=f[f.user_a.isin(keep) & f.user_b.isin(keep)].reset_index(drop=True),
                   blocks=b[b.user_id.isin(keep) & b.blocked_id.isin(keep)].reset_index(drop=True),
                   topics=v.topics[v.topics.user_id.isin(keep)].reset_index(drop=True),
                   not_interested=v.not_interested[v.not_interested.user_id.isin(keep)].reset_index(drop=True))


def noise_table(noise, gids):
    """GroupStats.noise as a table a port can read (noise.csv): kind ('size', 'pair' or 'activity'), group_a, group_b,
    value. Pairs are listed once (group_a < group_b), in the order numpy's triu_indices gives (row by row)."""
    gids = np.asarray(gids)
    i, j = np.triu_indices(len(gids), k=1)
    parts = [pd.DataFrame({'kind': 'size', 'group_a': gids, 'group_b': gids, 'value': noise['sizes']}),
             pd.DataFrame({'kind': 'pair', 'group_a': gids[i], 'group_b': gids[j], 'value': noise['pairs']})]
    if 'activity' in noise:
        parts.append(pd.DataFrame({'kind': 'activity', 'group_a': gids, 'group_b': gids, 'value': noise['activity']}))
    return pd.concat(parts, ignore_index=True)


def noise_from_table(table, gids):
    """noise.csv (noise_table()) -> the dict group_stats(noise=...) takes, in its own order."""
    gids = np.asarray(gids)
    t = table.copy()
    out = {'sizes': t[t.kind == 'size'].set_index('group_a').value.reindex(gids).to_numpy(float)}
    i, j = np.triu_indices(len(gids), k=1)
    pairs = t[t.kind == 'pair'].set_index(['group_a', 'group_b']).value
    out['pairs'] = pairs.reindex(pd.MultiIndex.from_arrays([gids[i], gids[j]])).to_numpy(float)
    if (t.kind == 'activity').any():
        out['activity'] = t[t.kind == 'activity'].set_index('group_a').value.reindex(gids).to_numpy(float)
    assert not any(np.isnan(v).any() for v in out.values()), 'noise.csv misses a group or a pair'
    return out


def _served(vis):
    """The members a test case serves together: every account that is not suspended."""
    return sorted(int(u) for u in vis.users.user_id[vis.users.suspended == 0])


def _named(recs, user=None):
    """Everyone a set of reasons names (friend reasons), for one member or all."""
    r = recs if user is None else recs[recs.user_id == user]
    return set(r.reason_ref[r.reason_code == 'friend'].astype(int))


def _sorted_train(*tables):
    return pd.concat(tables, ignore_index=True).sort_values(['user_id', 'group_id']).reset_index(drop=True)


def _test_cases(world, cfg, clusters):
    """The cases, built from `world`: a list of dicts with name, title, data, config, what (the README line)
    and intent(recs, data) -> True if the case shows what it is meant to show. Two cases set dials
    themselves so that they test what they are about whatever the final design: case 03 keeps a newcomer
    quota (q at least 0.2, and c at least 10% with no clipping, see there) and case 08 counts only accounts at
    level 3 or more (L at least 3)."""
    base = recommend(_served(world), world, cfg, clusters=clusters)
    mine = base[base.user_id == 1].sort_values('rank')
    gname = world.groups.set_index('group_id').name
    top = int(mine.group_id.iloc[0])
    cases = []
    focus = lambda recs: recs[recs.user_id == 1]

    cases.append(dict(name='01_ordinary_member', title='An ordinary member', data=world, config=cfg,
        what='An ordinary member: user 1 (in Spanish for beginners, Spanish evening chat and Python project club, '
             'with public friends) gets 5 suggestions, each with its main true reason from a fixed template (R6).',
        intent=lambda recs, v: len(focus(recs)) == K and focus(recs).personal.all()))

    keep = world.train[(world.train.user_id != 1) | (world.train.group_id == 1)]
    lonely = world.friendships[(world.friendships.user_a != 1) & (world.friendships.user_b != 1)]
    cases.append(dict(name='02_cold_start_member', title='A cold-start member',
        data=replace(world, train=keep.reset_index(drop=True), friendships=lonely.reset_index(drop=True)), config=cfg,
        what='Cold start: user 1 is in one group only (Spanish for beginners) and has no friends; they still get 5 '
             'suggestions, and every reason that names a group names that one (R6).',
        intent=lambda recs, v: len(focus(recs)) == K and set(focus(recs).reason_ref[focus(recs).reason_code.isin(
            ['shared_members', 'similar_group'])]) <= {1}))

    # 03: group 17 becomes brand new (2 days old), about Spanish, with its creator (a new member); then, one by
    # one, members of user 1's group 1 join it, until it is the newcomer that takes user 1's quota slot.
    # The case keeps the quota as the rule that decides that slot, whatever the dials (notebook 11): q at least 0.2, the
    # cap c at least 10% (this world has only 18 groups on Discover: a 5% cap, 25 of the 500 slots each, cannot even cover
    # all the slots, so the cap would decide user 1's list first) and no clipping (clipping to m groups makes most groups
    # here look small, so the quota would already be met). With notebook 06's defaults (q 0.2, c 0.1, no m) this changes nothing.
    cfg3 = replace(cfg, q=max(cfg.q, 0.2), c=None if cfg.c is None else max(cfg.c, 0.1), m=None)
    keeps = 'q >= 0.2' + (', c >= 10% and no clipping' if (cfg3.c, cfg3.m) != (cfg.c, cfg.m) else '')
    groups = world.groups.copy()
    groups.loc[groups.group_id == 17, ['name', 'about', 'created_day']] = \
        ['Spanish for travellers', 'Speak Spanish before your trip. Weekly voice chats, all levels.', TODAY - 2]
    creator = int(world.users.user_id[(world.users.created_day > TODAY - NEW_DAYS) & (world.users.user_id > 1)].min())
    others = [int(u) for u in world.train.user_id[(world.train.group_id == 1) & (world.train.user_id > 1)] if u != creator]
    posts = world.posts[world.posts.group_id != 17].reset_index(drop=True)
    for extra in range(len(others) + 1):
        joiners = [creator] + others[:extra]
        data = replace(world, groups=groups, posts=posts, likes=world.likes[world.likes.post_id.isin(posts.post_id)],
                       train=_sorted_train(world.train[world.train.group_id != 17],
                                           pd.DataFrame({'user_id': joiners, 'group_id': 17, 'joined_day': TODAY - 2})))
        trial = focus(recommend(_served(data), data, cfg3, clusters=clusters))
        if 17 in set(trial.group_id):          # the first time it appears: as the quota slot if it can be
            break
    row = trial[trial.group_id == 17]
    how = ('it takes the newcomer slot (rank 5, forced), with the reason "A new group: ..."' if len(row) and row.forced.iloc[0]
           else 'it makes the list on its own merit' if len(row) else 'it does NOT make the list')
    cases.append(dict(name='03_brand_new_group', title='A brand-new group gets the newcomer slot', data=data, config=cfg3,
        what=f'A brand-new group: Spanish for travellers (group 17) was created 2 days ago and has {len(joiners)} '
             f'member{"s" if len(joiners) > 1 else ""}; in user 1\'s list {how} (R4; this case keeps {keeps}).',
        intent=lambda recs, v: bool((focus(recs).forced & (focus(recs).group_id == 17)
                                     & (focus(recs).reason_code == 'new_group')).any())))

    groups = world.groups.copy()
    groups.loc[groups.group_id == top, 'hidden_by_mods'] = 1
    cases.append(dict(name='04_hidden_by_moderators', title='A group hidden by moderators',
        data=replace(world, groups=groups), config=cfg,
        what=f'Hidden by moderators: {gname[top]} (group {top}), user 1\'s first suggestion when it is visible, '
             f'is hidden; it must never appear in anyone\'s list (R8).',
        intent=lambda recs, v, g=top: g not in set(recs.group_id)))

    friends = [int(f) for f in mine.reason_ref[mine.reason_code == 'friend']]
    if len(friends) < 2:          # then friends in user 1's suggested groups, then any public friend of user 1
        counted = stats_for(world, cfg).counted
        fig = friends_in_groups(world, [1], counted)
        more = list(fig.friend_id[fig.group_id.isin(mine.group_id)]) + list(public_friends(world, [1], counted).friend_id)
        friends += [int(f) for f in dict.fromkeys(more) if int(f) not in friends]
    f1, f2 = friends[:2]
    blocks = pd.concat([world.blocks, pd.DataFrame({'user_id': [1, f2], 'blocked_id': [f1, 1]})], ignore_index=True)
    cases.append(dict(name='05_blocked_friend', title='Blocked friends are never named',
        data=replace(world, blocks=blocks), config=cfg,
        what=f'Blocks: user 1 blocked user {f1}, and user {f2} blocked user 1; both are user 1\'s friends and were '
             f'named in user 1\'s reasons before; neither may be named or counted for user 1 now, in either direction (R6, R8).',
        intent=lambda recs, v: not ({f1, f2} & _named(recs, 1))))

    users = world.users.copy()
    users.loc[users.user_id == f1, 'privacy'] = 'private'
    cases.append(dict(name='06_private_friend', title='A private-profile friend is never named',
        data=replace(world, users=users), config=cfg,
        what=f'A private profile: user {f1}, user 1\'s friend named in a reason before, switches to a private profile; '
             f'no reason may name them, for anyone (R6, R8).',
        intent=lambda recs, v: f1 not in _named(recs)))

    dismissed = pd.concat([world.not_interested, pd.DataFrame({'user_id': [1], 'group_id': [top], 'day': [360]})],
                          ignore_index=True)
    cases.append(dict(name='07_not_interested', title='"Not interested" is respected',
        data=replace(world, not_interested=dismissed), config=cfg,
        what=f'Not interested: user 1 marked {gname[top]} (group {top}), their first suggestion before, "not interested"; '
             f'it must not come back for user 1 (R7).',
        intent=lambda recs, v, g=top: g not in set(focus(recs).group_id)))

    # 08: accounts that must not count (4 suspended, 4 at level 1) join user 1's group 2 and group 16 and
    # befriend user 1. The case counts only accounts at level 3 or more (L >= 3), so all 8 are ignored.
    cfg8 = replace(cfg, L=max(cfg.L, 3))
    n = len(world.users)
    bad_ids = list(range(n + 1, n + 9))
    extra = pd.DataFrame({'user_id': bad_ids, 'created_day': [200] * 4 + [TODAY - 20] * 4, 'level': [30] * 4 + [1] * 4,
                          'privacy': 'public', 'suspended': [1] * 4 + [0] * 4})
    joins = pd.DataFrame({'user_id': bad_ids * 2, 'group_id': [2] * 8 + [16] * 8, 'joined_day': 360})
    befriend = pd.DataFrame({'user_a': 1, 'user_b': bad_ids, 'since_day': 360})
    data8 = replace(world, users=pd.concat([world.users, extra], ignore_index=True),
                    train=_sorted_train(world.train, joins),
                    friendships=pd.concat([world.friendships, befriend], ignore_index=True))
    without = replace(data8, train=world.train)                    # the same, but their joins never happened

    def r9_intent(recs, v, ids=bad_ids):
        a, b = stats_for(v, cfg8), stats_for(without, cfg8)
        same_stats = (np.allclose(a.co.to_numpy(), b.co.to_numpy(), rtol=0, atol=1e-12) and a.newcomers == b.newcomers
                      and a.activity.equals(b.activity))
        return same_stats and not (_named(recs) & set(ids))
    small_note = ('or which groups count as small, ' if cfg8.small_from == 'r9' else '')
    cases.append(dict(name='08_accounts_that_do_not_count', title='Suspended and low-level accounts are ignored (R8, R9)',
        data=data8, config=cfg8,
        what=f'Accounts that must not count: 4 suspended accounts (users {bad_ids[0]}-{bad_ids[3]}) and 4 level-1 accounts '
             f'(users {bad_ids[4]}-{bad_ids[7]}) joined Spanish evening chat (user 1\'s group) and GRE study hall, and are '
             f'user 1\'s public friends. With L = {cfg8.L} (this case keeps L >= 3) none of them counts in any statistic: their '
             f'joins change no group size, "also joined" count, {small_note}or activity, and no reason names them (R8, R9). '
             f'Suspended accounts are not served. The level-1 accounts still get their own suggestions, and those take slots under '
             f'the shared cap c, so other members\' lists can still shift when they join (the cap is shared, not a statistic).',
        intent=r9_intent))

    discover = [int(g) for g in discover_groups(world.groups)]
    left = [9, 14, 17]
    rows = pd.DataFrame({'user_id': 1, 'group_id': [g for g in discover if g not in left and g not in (1, 2, 5)],
                         'joined_day': 300})
    cases.append(dict(name='09_almost_everything_joined', title='Fewer than 5 candidates',
        data=replace(world, train=_sorted_train(world.train, rows)), config=cfg,
        what='Almost everything joined: user 1 is in every Discover group but 3 (groups 9, 14 and 17); the list must hold '
             'exactly those 3, never padded with other groups (R11).',
        intent=lambda recs, v: sorted(focus(recs).group_id) == left))

    cases.append(dict(name='10_personalisation_off', title='Personalisation off', data=world,
        config=replace(cfg, personal=False),
        what='Personalisation off (the default, R1): no profile is used; every member gets the same scores (recent '
             'activity and newness), a list of 5 (or every candidate), reasons "active" or "new_group" only, never empty.',
        intent=lambda recs, v: (~recs.personal).all() and recs.reason_code.isin(['active', 'new_group', 'discover']).all()
        and recs.groupby('user_id').size().min() >= 1))

    users = world.users.copy()
    users.loc[users.user_id == 1, ['created_day', 'level']] = [TODAY - 3, 1]
    cases.append(dict(name='11_nothing_to_go_on', title='A brand-new member with nothing to go on',
        data=replace(world, users=users, train=world.train[world.train.user_id != 1].reset_index(drop=True),
                     friendships=lonely.reset_index(drop=True)), config=cfg,
        what='A brand-new member with nothing to go on: user 1 (created 3 days ago, level 1, no groups, no friends) has '
             'personalisation on but no data, so gets the default list, never an empty one (R1).',
        intent=lambda recs, v: len(focus(recs)) == K and not focus(recs).personal.any()))
    return cases


def _large_cases(config, cfg, clusters):
    """Cases 12 and 13, on the larger world (case_world_large): 12 checks the re-ranker where no rule has to be relaxed
    (the small world's 18 Discover groups make the cap bind everywhere), 13 checks the noise path number for number: the
    Laplace draws are given as data (noise.csv), so a port adds exactly the same numbers. config: the design asked for
    (its eps, or FINAL_CONFIG's if it has none, is used in case 13); cfg: the same with the noise off; clusters: the public
    topic clusters of all 150 groups."""
    world = case_world_large()
    no_relaxing = lambda recs, v: sum(recs.attrs['relaxed'].values()) == 0 and bool(recs.groupby('user_id').size().eq(K).all())
    cases = [dict(name='12_larger_world_no_relaxing', title='A larger world where no rule is relaxed', data=world, config=cfg,
                  clusters=clusters,
                  what=f'A larger world: the first {LARGE_CASE_USERS} members of the synthetic community and all 150 groups (129 on '
                       f'Discover). Every rule holds without being relaxed (quota, topic cap, global cap), so this case checks the '
                       f're-ranker in the regime BOING will run in (R4, R5).',
                  intent=no_relaxing)]
    private = config.eps is not None and not math.isinf(config.eps)
    cfg13 = replace(cfg, eps=config.eps if private else FINAL_CONFIG.eps, m=cfg.m or FINAL_CONFIG.m,
                    act_eps=config.act_eps)
    exact = recommend(_served(world), world, replace(cfg13, eps=None, act_eps=None), clusters=clusters)
    cases.append(dict(name='13_noise_on', title='Privacy noise on, with the draws given as data', data=world, config=cfg13,
                      clusters=clusters, noisy=True,
                      what=f'Privacy noise on (R10: eps = {cfg13.eps:g}, m = {cfg13.m}): the same larger world, with the Laplace draws '
                           f'given in noise.csv (one per group size and one per pair of groups), so a port adds exactly the same numbers '
                           f'and must give exactly expected.csv. The noise changes some suggestions against the same case without noise.',
                      intent=lambda recs, v: _rows_changed(recs, exact) > 0 and no_relaxing(recs, v)))
    return cases


TESTCASES = ROOT / 'testcases'

TEST_CASES_README = """# Test cases for BOING's JavaScript port of the recommender

Made by `boingrec.make_test_cases(config, outdir)` (notebook 10), with the design in `boingrec.Config`. Each folder is one small case:
the port reads its files, runs the recommender with its `config.json`, and must give exactly `expected.csv`. `index.csv` lists the cases.
To regenerate them all (for example with the final dials): `br.make_test_cases(br.Config(...))`.

## In each folder

| File | What it is |
|---|---|
| `users.csv`, `groups.csv` | the members and groups, with the columns of `data/sim_v1` minus the hidden ones |
| `train_memberships.csv`, `train_posts.csv`, `train_likes.csv` | memberships, posts and likes (in BOING: all of them; "train" only means "what the recommender may see") |
| `friendships.csv`, `blocks.csv`, `topics.csv`, `not_interested.csv` | as in `data/sim_v1` |
| `clusters.csv` | each group's public topic cluster (rule R5), given as data: in BOING they are computed once from all groups' texts |
| `config.json` | `config`: every setting (`boingrec.Config`); `constants`; `users`: who is served together; `serve_order`: the order they are served in (the cap c is shared in that order); `focus_user`: the member the case is about |
| `expected.csv` | the answer, for every served member: user_id, rank, group_id, score (6 decimals), reason_code, reason_text |
| `README.md` | what the case checks |

## To match exactly

- TF-IDF as scikit-learn's default `TfidfVectorizer` on `name + " " + about`: lowercase, tokens of 2 or more letters, digits or `_`
  (regular expression `\\b\\w\\w+\\b`; all texts here are plain ASCII), idf = ln((1 + n) / (1 + df)) + 1, each row scaled to length 1;
  similarity = dot product.
- The AI model: the k eigenvectors of co = X^T X with the largest eigenvalues (any sign: only V V^T is used). `index.csv`'s
  `taste_gap` is the gap between the k-th and (k+1)-th eigenvalues over the largest ({gap_text}): far above rounding
  error, so V V^T is well defined, but close enough that a port should use a full symmetric eigen-solver (for example Jacobi), not a few
  rounds of power iteration.
- Rescaling: round to 10 decimals, then (s - min) / (max - min) over the member's candidates (0 if max = min).
- Ties: the smaller group id first; values are rounded to 10 decimals before comparing.
- The noise is off (`eps` is null) in every case but one, so every number is exact: it draws numpy random numbers that a port
  cannot redo. Case 13 turns it on and gives the draws as data (`noise.csv`: `kind` size / pair / activity, `group_a`, `group_b`,
  `value`; pairs once, smaller id first): add each draw to its count, then a size below 0 becomes 0, a pair is clipped to between 0
  and its smaller group's noisy size, and the table is made symmetric. The clipping (`m`, when set) stays: each member keeps the m
  groups with the smallest `boingrec.membership_keys` (a splitmix64 hash of the seed, the member and the group; the seed is
  `noise_seed`, or `seed` if null), which a port can redo exactly with 64-bit integers.
- The serve order is given (`serve_order`), because it is drawn with numpy's random numbers too.
- The number in a "shared members" reason: the members the two groups share among the accounts that count. With `m` set it is the
  clipped count and the text starts with "About ". With young accounts down-weighted (`burst_w` < 1, no `m`) it is still the true
  number of members, not the weighted count the scores use. With the noise on and `count_under_noise` false (case 13 with the final
  design), the reason states no number: "Members of X also joined it".
- "Small" (`small_from`): `r9` counts a group's members among the accounts that count (not suspended, `level` at least `L`; an
  account younger than `young_days` days counts `burst_w`, so 0 with the final design), with no clipping and no noise; `public`
  counts every member; `counted` uses the recommender's own (clipped, noisy) sizes.

To check the Python side: `boingrec.verify_test_cases()` re-runs every case from its files.
"""


def _taste_gap_text(index):
    """The range of the test cases' taste gaps, in words, for the README."""
    gaps = index.taste_gap[index.taste_gap < 1]
    return (f'{gaps.min():.2%} to {gaps.max():.2%} in these cases' if len(gaps) else 'see index.csv')


def _readme_template(index):
    return TEST_CASES_README.replace('{gap_text}', _taste_gap_text(index))


def make_test_cases(config=None, outdir=None):
    """Write the test cases BOING's JavaScript port is checked against (one call regenerates them all).

    config: the design to use (default Config()); the noise is always turned off (eps = None) so the expected
    numbers are exact (the clipping, m, is a hash that a port can redo, so it stays). outdir: where to write (default ROOT/testcases); old case folders there
    (NN_name with a config.json) are replaced. Every case starts from case_world() and changes one thing
    (see _test_cases). Each folder gets the data files (load_visible's names and columns), clusters.csv,
    config.json, expected.csv and a README.md line. Also writes README.md and index.csv in outdir.
    Returns the index: one row per case with what it checks, its size, whether it shows what it is meant
    to (intent_holds) and its hard-rule violations (check_rules, which must be 0).
    """
    import json
    import re
    import shutil
    from dataclasses import asdict
    asked = config or Config()
    cfg = replace(asked, eps=None, act_eps=None)
    outdir = Path(outdir) if outdir is not None else TESTCASES
    outdir.mkdir(parents=True, exist_ok=True)
    for old in outdir.iterdir():
        if old.is_dir() and re.match(r'\d\d_', old.name) and (old / 'config.json').exists():
            shutil.rmtree(old)
    full = topic_clusters(load_visible(DATA), cfg.clusters)
    clusters = pd.Series(full.reindex([s for s, _ in CASE_GROUPS]).to_numpy(), name='cluster',
                         index=pd.Index(np.arange(1, len(CASE_GROUPS) + 1), name='group_id'))
    world = case_world()
    constants = {'K': K, 'TODAY': TODAY, 'NEW_DAYS': NEW_DAYS, 'SMALL': SMALL, 'ACTIVE_DAYS': ACTIVE_DAYS,
                 'WEEK': WEEK, 'YOUNG_DAYS': YOUNG_DAYS}
    index = []
    for case in _test_cases(world, cfg, clusters) + _large_cases(asked, cfg, full.rename('cluster')):
        folder, data, ccfg = outdir / case['name'], case['data'], case['config']
        cl = case.get('clusters', clusters)
        folder.mkdir()
        for field, fname in VISIBLE_FILES.items():
            getattr(data, field)[ALLOWED_COLUMNS[field]].to_csv(folder / fname, index=False)
        cl.reset_index().to_csv(folder / 'clusters.csv', index=False)
        users = _served(data)
        stats = None
        if case.get('noisy'):          # the draws are written as data, and the expected answer uses exactly those
            stats = stats_for(data, ccfg)
            noise_table(stats.noise, group_ids(data)).to_csv(folder / 'noise.csv', index=False, float_format='%.17g')
            stats = stats_for(data, ccfg, noise=noise_from_table(pd.read_csv(folder / 'noise.csv'), group_ids(data)))
        recs = recommend(users, data, ccfg, stats=stats, clusters=cl)
        recs[['user_id', 'rank', 'group_id', 'score', 'reason_code', 'reason_text']].to_csv(
            folder / 'expected.csv', index=False, float_format='%.6f')
        spec = {'case': case['name'], 'checks': case['what'], 'config': asdict(ccfg), 'constants': constants,
                'users': users, 'serve_order': recs.attrs['order'], 'focus_user': 1,
                'noise_file': 'noise.csv' if stats is not None else None}
        (folder / 'config.json').write_text(json.dumps(spec, indent=2), encoding='utf-8')
        (folder / 'README.md').write_text(f'# {case["title"]}\n\n{case["what"]}\n', encoding='utf-8')
        rules = check_rules(recs, data, ccfg, users=users, stats=stats, clusters=cl)
        values = np.linalg.eigvalsh((stats if stats is not None else stats_for(data, ccfg)).co.to_numpy())[::-1]
        index.append({'case': case['name'], 'checks': case['what'], 'members': len(data.users),
                      'groups': len(data.groups), 'served': len(users), 'rows': len(recs),
                      'relaxed': sum(recs.attrs['relaxed'].values()),
                      'intent_holds': bool(case['intent'](recs, data)),
                      'hard_rule_violations': int(rules.violations[rules.hard].sum()),
                      'taste_gap': float((values[ccfg.k - 1] - values[ccfg.k]) / values[0]) if len(values) > ccfg.k else 1.0})
    index = pd.DataFrame(index).set_index('case')
    index.to_csv(outdir / 'index.csv')
    (outdir / 'README.md').write_text(_readme_template(index), encoding='utf-8')
    return index


def verify_test_cases(outdir=None, rules=True):
    """Re-run every test case from its own files (load_visible on the folder, config.json, clusters.csv) and
    compare with its expected.csv: the same rows, scores within 0.0000005. With rules=True also count the
    hard-rule violations (check_rules). Returns one row per case."""
    import json
    outdir = Path(outdir) if outdir is not None else TESTCASES
    rows = []
    for folder in sorted(p for p in outdir.iterdir() if (p / 'config.json').exists()):
        spec = json.loads((folder / 'config.json').read_text(encoding='utf-8'))
        cfg = Config(**spec['config'])
        clusters = pd.read_csv(folder / 'clusters.csv', index_col='group_id').cluster
        stats = _case_stats(folder, cfg, spec)
        recs = recommend(spec['users'], folder, cfg, stats=stats, clusters=clusters)
        want = pd.read_csv(folder / 'expected.csv')
        cols = ['user_id', 'rank', 'group_id', 'reason_code', 'reason_text']
        got = recs[cols + ['score']].reset_index(drop=True)
        same = (len(got) == len(want) and (got[cols].astype(str).to_numpy() == want[cols].astype(str).to_numpy()).all()
                and np.allclose(got.score.to_numpy(), want.score.to_numpy(), rtol=0, atol=5e-7))
        row = {'case': folder.name, 'rows': len(want), 'matches_expected': bool(same),
               'same_serve_order': recs.attrs['order'] == spec['serve_order']}
        if rules:
            table = check_rules(recs, folder, cfg, users=spec['users'], stats=stats, clusters=clusters)
            row['hard_rule_violations'] = int(table.violations[table.hard].sum())
        rows.append(row)
    return pd.DataFrame(rows).set_index('case')


def _case_stats(folder, cfg, spec):
    """A test case's statistics when it gives its noise draws as data (noise.csv), else None (recommend() makes them)."""
    if not spec.get('noise_file'):
        return None
    vis = load_visible(folder)
    return stats_for(vis, cfg, noise=noise_from_table(pd.read_csv(Path(folder) / spec['noise_file']), group_ids(vis)))

# ---------------------------------------------------------------------------------------------------
# 12. The final design (notebook 11)
#       FINAL_CONFIG         every dial and weight, each chosen on the practice quiz (never on the test)
#       test_cases_readme()  the README of testcases/ for the final design: what each case checks, how a port passes
# ---------------------------------------------------------------------------------------------------

# The design BOING runs for a member who switches personalisation on. With it off (the default, rule R1), BOING serves
# replace(FINAL_CONFIG, personal=False): the same statistics and re-ranking, and no profile. Where each value comes from:
#   k 10, topic_weight 0, off_new_w 0.5                  notebooks 04 to 06 (Config's defaults, unchanged)
#   q 0.2, c 0.05, n 2, lam 0.8                          E2, notebook 07 (results/e2_recommendation.json)
#   L 3, burst_w 0, young_days 30                        E4, notebook 09 (results/e4_recommendation.json)
#   small_from 'r9'                                      notebook 11, after the two reviews: "small" is judged from a member count (not the
#                                                        recommender's clipped, noisy one), and only of the accounts R9 counts, so fake
#                                                        accounts that R9 ignores cannot push a rival small group over the line
#   r9_scope 'all'                                       E4, notebook 09 section 10: R9 also weighs posts, likes and friends
#                                                        (fake accounts that post and like change nothing)
#   alpha 0.2, beta 0.2, gamma 0.3, delta 0.3            notebook 06's protocol re-run in notebook 11 under the final (noisy) statistics:
#                                                        notebook 06's mix (0.4, 0.1, 0.3, 0.2) loses beyond the noise, so the choices
#                                                        below ran again with this mix (rounds), and it then held (results/final_rounds.csv)
#   clusters 8                                           notebook 11: the number of public topic clusters whose lists hold 3+ groups
#                                                        of one member-chosen topic least often, within E2's budget, on average over five
#                                                        practice quizzes
#   eps 1.5, m 3, size_share 0.1                         E3's rule (notebook 08), applied in notebook 11 to the design with every
#                                                        other dial on: stage 1 (notebook 08's grid) picks m and the split; stage 2
#                                                        picks the smallest eps whose 95% range over five practice quizzes (20 fresh noise
#                                                        draws on each) keeps 90% of the accuracy and of the newcomer slots
#                                                        (results/final_eps_fine.csv)
#   act_eps None                                         notebook 11: private activity counts were measured, and no budget keeps 90%
#                                                        of the default list's accuracy, so the activity stays outside the noise
#   count_under_noise False                              notebook 11: with the noise on, few stated counts are close to the truth, so a
#                                                        "shared members" reason names the group without a number
# In BOING the clipping and the noise must draw from a secret seed: noise_seed here only makes the experiments repeatable.
# Config's own defaults stay those of notebook 06, so no other notebook's results change.
FINAL_CONFIG = Config(alpha=0.2, beta=0.2, gamma=0.3, delta=0.3, c=0.05, lam=0.8, clusters=8, L=3, burst_w=0.0, eps=1.5, m=3,
                      size_share=0.1, small_from='r9', r9_scope='all', count_under_noise=False)
# The final design before the review (notebook 11's first version), kept to show what the review changed
FINAL_CONFIG_BEFORE_REVIEW = Config(c=0.05, lam=0.8, L=3, burst_w=0.0, eps=5.0, m=3, size_share=0.25)

# What each setting does, in plain words (for the test cases' README and the final config's file)
CONFIG_MEANING = {
    'alpha': 'weight of "also joined" (collaborative filtering)',
    'beta': 'weight of similar descriptions (TF-IDF)',
    'gamma': 'weight of friends (public friends who are members)',
    'delta': 'weight of hidden tastes (the AI model)',
    'k': "the AI model's number of hidden tastes",
    'topic_weight': "how much a member's chosen topics count in similar descriptions",
    'personal': 'personalisation on (False: the default list, rule R1)',
    'off_new_w': 'personalisation off: weight of newness (the rest is recent activity)',
    'q': 'R4: at least ceil(q x 5) slots of each list go to new or small groups',
    'c': 'R4: no group gets more than c of all slots (null: no cap)',
    'n': 'R5: at most n groups of one public topic cluster per list (null: no limit)',
    'lam': 'R5: MMR, lam x relevance - (1 - lam) x similarity to the groups already picked',
    'clusters': 'number of public topic clusters (KMeans on the group texts)',
    'L': 'R9: only accounts at level L or more count',
    'burst_w': 'R9: weight of the joins of accounts younger than young_days (0: they count once they are older)',
    'young_days': 'R9: an account is young for this many days',
    'eps': 'R10: differential-privacy budget epsilon (null or inf: no noise)',
    'm': 'R10: each member counts for at most m groups (null: no clipping)',
    'size_share': 'R10: share of epsilon spent on the group sizes (the rest on the pair counts)',
    'noise_seed': 'R10: seed of the clipping hash and the noise (null: use seed)',
    'seed': 'seed of the order members are served in (for the cap c), and of the clipping and noise when noise_seed is null',
    'small_from': "R4: 'r9' = a group is small if fewer than 10 of its members are accounts that count under R9 (level L or more, at least "
                  "young_days old when burst_w = 0), no clipping, no noise; 'public' = if the member count Discover shows is under 10; "
                  "'counted' = from the recommender's own (clipped, noisy) counts",
    'r9_scope': "R9: 'all' = the level bar and the young-account wait apply to posts, likes and friends too; 'joins' = to memberships only",
    'act_eps': 'R10 for the recent activity: privacy budget of the active-member counts (null: activity counts posts and likes, no noise)',
    'count_under_noise': 'R6: with the noise on, a "shared members" reason states its noisy count (true) or names the group only (false)',
}


def test_cases_readme(index, config, outdir=None):
    """The README of testcases/ for the cases make_test_cases(config, outdir) wrote (notebook 11, with FINAL_CONFIG):
    the settings, what each case checks (with the settings a case changes itself), the files, how a port passes a case,
    and how to match the numbers exactly. index: make_test_cases()'s table. Returns the text (Markdown)."""
    import json
    from dataclasses import asdict
    outdir = Path(outdir) if outdir is not None else TESTCASES
    cfg = replace(config, eps=None)
    base = asdict(cfg)
    template = _readme_template(index)
    files = template.split('## In each folder')[1].split('## To match exactly')[0].strip()
    match = template.split('## To match exactly')[1].split('To check the Python side')[0].strip()
    show = lambda v: 'null' if v is None else ('true' if v is True else 'false' if v is False else f'{v:g}' if isinstance(v, float) else str(v))
    lines = ['# Test cases for BOING\'s JavaScript port of the recommender', '',
             f'Made by notebook 11 with the final design (`boingrec.make_test_cases(boingrec.FINAL_CONFIG)`), with the privacy noise '
             f'switched off (`eps` is null) so that every number is exact, except in case 13, which gives its noise draws as data. '
             f'{len(index)} cases; each is a folder with a small community '
             f'({int(index.members.min())} to {int(index.members.max())} members, {int(index.groups.min())} to {int(index.groups.max())} groups), the settings, and '
             f'the answer: every served member\'s suggestions in `expected.csv`. The port reads a folder\'s files, runs with its '
             f'`config.json`, and must give the same answer. Notebook 10 writes the same cases with notebook 06\'s settings, so run '
             f'notebook 11 after it.', '',
             '## The settings', '', '| Setting | Value | What it does |', '|---|---|---|']
    lines += [f'| `{k}` | {show(v)} | {CONFIG_MEANING.get(k, "")} |' for k, v in base.items()]
    lines += ['', 'The noise (`eps`) draws random numbers, which a port cannot redo; so case 13 gives them as data (`noise.csv`) and the port '
              'adds exactly those. BOING turns the noise on '
              f'with the final value (`eps` = {show(config.eps)}) and a secret seed; its effect is measured in notebooks 08 and 11.', '',
              '## The cases', '',
              '"Relaxed" counts how many times the re-ranker had to drop a rule to fill a slot (quota / topic cap / global cap, as '
              '`recommend()` reports in `attrs["relaxed"]`): a port should count the same.', '',
              '| Case | What it checks | Members | Served | Rows | Settings the case changes | Relaxed |', '|---|---|---|---|---|---|---|']
    for case, row in index.iterrows():
        spec = json.loads((outdir / case / 'config.json').read_text(encoding='utf-8'))
        own = spec['config']
        changed = ', '.join(f'`{k}` = {show(v)}' for k, v in own.items() if v != base.get(k)) or 'none'
        clusters = pd.read_csv(outdir / case / 'clusters.csv', index_col='group_id').cluster
        relaxed = recommend(spec['users'], outdir / case, Config(**own), stats=_case_stats(outdir / case, Config(**own), spec),
                            clusters=clusters).attrs['relaxed']
        lines.append(f'| `{case}` | {row.checks} | {int(row.members)} | {int(row.served)} | {int(row.rows)} | {changed} | '
                     f'{relaxed["quota"]} / {relaxed["topic cap"]} / {relaxed["global cap"]} |')
    small_world = index[index.groups == len(CASE_GROUPS)]
    n_served = int(small_world.served.min())
    if cfg.c is not None:
        cap = max(1, math.floor(cfg.c * K * n_served + 1e-9))
        n_discover = len(discover_groups(load_visible(outdir / small_world.index[0]).groups))
        lines += ['', f'**The cap binds hard in the small world (cases 01 to 11).** With {n_discover} groups on Discover and {n_served} members served, '
                  f'c = {cfg.c:g} lets a group take at most {cap} of the {K * n_served} slots: {n_discover} x {cap} = {n_discover * cap} in all'
                  + (f', fewer than the slots to fill. So the re-ranker must relax the cap about {K * n_served - n_discover * cap} times per case '
                     f'(a slot that drops the global cap drops the topic cap too, so both counts rise)' if n_discover * cap < K * n_served else '')
                  + '. The order members are served in decides who still gets the capped groups: serve exactly in `serve_order`, count each '
                  'group\'s slots across members, and drop the rules in the same order (quota, then topic cap, then global cap). In BOING, '
                  'with many more groups, the cap rarely binds; it must stay above 1 / (groups on Discover). **Cases 12 and 13** use a '
                  f'larger world ({LARGE_CASE_USERS} members of the synthetic community, all 150 groups) where no rule is relaxed: the '
                  'regime BOING runs in. Case 13 also turns the privacy noise on, with its draws in `noise.csv`.']
    lines += ['', '## In each folder', '', files, '',
              '## How a port passes a case', '',
              'Run the port on the folder\'s files with its `config.json` (serve the members in `users`, in the order `serve_order`), then '
              'compare with `expected.csv`, member by member:', '',
              '1. **the same group ids in the same order**: rank 1 to 5 (fewer only when fewer groups can be shown, as in case 09);',
              '2. **the same `reason_code`** on every row;',
              '3. **every `score` within 1e-6** of the expected one (`expected.csv` keeps 6 decimals);',
              '4. the same `reason_text`, character for character: the templates are fixed. A port that shows them in another language '
              'should translate each template one to one and check the code and the group, friend or number it names.', '',
              'A case passes when every row does; the port passes when all the cases do. That match is itself a result for the report.', '',
              '## To match exactly', '', match, '',
              '## Checking the Python side', '',
              '`boingrec.verify_test_cases()` re-runs every case from its own files and compares with `expected.csv` (the same rows and '
              'texts, scores within 0.0000005), then counts the hard-rule violations with `boingrec.check_rules()` (all 0).', '']
    return '\n'.join(lines)


# ---------------------------------------------------------------------------------------------------
# 13. People suggestions (experiment E7, notebook 12)
# ---------------------------------------------------------------------------------------------------
# BOING's "People you may know" (boing-backend/recs.js: makePeople, eligible, peopleOut) on the synthetic
# community, with the owner's age bands (19 Nov 2026). The answer key is a set of hidden FRIENDSHIPS, so this
# experiment reads the full memberships as input (they are not answers here). The people recommender reads no
# posts, likes, topics or anything else.
#
# The synthetic community has no ages, no course rooms, no suggestion switch, no "takes friend requests" setting,
# no pending requests and no "not interested" for people. E7 adds them with stated assumptions (PEOPLE_ASSUME,
# AGE_SHARES, the course model); every draw is seeded. Ties between equal scores are broken by a random key per
# member, as BOING sorts by the member's random id string (user ids here follow sign-up order, so breaking ties
# by id would favour old accounts).

PEOPLE_ASSUME = {
    'unknown': 0.05,      # share with no birth year (early accounts): counted as under 18 (band 14-17), as in BOING
    'opt_in': 0.25,       # share who switched suggestions on (E3's assumption); sensitivity 10% to 100%
    'no_requests': 0.05,  # share not taking friend requests (a BOING setting): never suggested
    'test_frac': 0.2,     # share of friendships hidden for the test (and again, inside training, for the practice quiz)
    'courses': 160,       # course rooms this term: 40 at each of 4 year levels
    'per_member': 5,      # courses each student takes this term (4 at their level, 1 at any level)
    'class_friends': 1000,  # friendships formed in class, added to sim_v1's 5,374 (about 16% of all)
}
# Ages (assumption): a McGill-first network where most members are 18 to 24, first-years are often 17, and a few
# younger people are possible. BOING's minimum age at sign-up is 14; the 13-year-olds test the under-14 rule.
AGE_SHARES = {13: 0.005, 14: 0.005, 15: 0.005, 16: 0.005, 17: 0.06,
              18: 0.15, 19: 0.15, 20: 0.15, 21: 0.08, 22: 0.08, 23: 0.08, 24: 0.08,
              25: 0.02, 26: 0.02, 27: 0.02, 28: 0.02, 29: 0.02}          # sums to 0.95; the other 5% have no birth year
UNKNOWN_AGE = -1
BANDS = {0: 'under 14', 1: '14-17 or unknown', 2: '18-20', 3: '21 and over'}


def age_band(age):
    """0: under 14; 1: 14 to 17, or no birth year (counted as under 18); 2: 18 to 20; 3: 21 and over."""
    age = np.asarray(age)
    return np.where(age == UNKNOWN_AGE, 1, np.where(age < 14, 0, np.where(age < 18, 1, np.where(age <= 20, 2, 3))))


# The owner's rule (19 Nov 2026), written as a table: (viewer band, candidate band) -> the links that allow a
# suggestion ('any' = no extra condition; an empty set = never). 'tie' = a mutual friend or a shared group or
# course; 'course' = classmates (the same course this term). Under-14s get no list and are never suggested.
AGE_RULE = {
    (1, 1): {'any'}, (1, 2): {'tie'}, (1, 3): set(),
    (2, 1): {'course'}, (2, 2): {'any'}, (2, 3): {'any'},
    (3, 1): set(), (3, 2): {'any'}, (3, 3): {'any'},
}
PEOPLE_RULES = ('self', 'friend', 'pending', 'blocked', 'suspended', 'private', 'opt_in', 'requests', 'age', 'dismissed')
SAFETY = ('self', 'friend', 'pending', 'blocked', 'suspended', 'private', 'dismissed')
PEOPLE_STEPS = {                     # the cost of the rules, one step at a time (notebook 12)
    'No rules (score only)': ('self', 'friend'),
    '+ Safety filters (R8: blocked either way, suspended, private)': SAFETY,
    '+ Age bands (R8)': SAFETY + ('age',),
    '+ Consent (R1: only people who switched on and take requests)': PEOPLE_RULES,
}


@dataclass
class PeopleWorld:
    """Everything the people recommender may read, as index-aligned numpy arrays (member i = ids[i])."""
    ids: np.ndarray            # user ids
    friends: np.ndarray        # n x n 0/1, current (training) friendships, symmetric
    groups: np.ndarray         # n x g 0/1: interest groups not hidden by moderators, then this term's course rooms
    group_ids: np.ndarray      # g ids (course rooms: 10001 and up)
    is_course: np.ndarray      # g bools
    group_open: np.ndarray     # g bools: listed to everyone (open groups, and course rooms on campus): a reason may name it
    group_size: np.ndarray     # g member counts
    blocked: np.ndarray        # n x n bool: i blocked j
    pending: np.ndarray        # n x n bool: i sent j a friend request that is still pending
    dismissed: np.ndarray      # n x n bool: i pressed "Not interested" on j
    suspended: np.ndarray      # n bools
    private: np.ndarray        # n bools
    opted_in: np.ndarray       # n bools: suggestions switched on (to see people, and to be suggested)
    takes_requests: np.ndarray # n bools
    age: np.ndarray            # n ints (UNKNOWN_AGE = no birth year); read only by the age rule
    created_day: np.ndarray    # n ints
    tie_key: np.ndarray        # n floats: random order for equal scores

    @property
    def band(self):
        return age_band(self.age)


def people_attributes(users, seed=SEED, assume=None):
    """The E7 additions to the synthetic community (seeded): age, this term's courses, the suggestion switch, the
    friend-request setting and a random tie-break key. One uniform draw per member and switch, so a larger share
    always contains the smaller one. Returns (draws, courses): draws has one row per member; courses is a
    memberships table (user_id, group_id) of course rooms."""
    a = {**PEOPLE_ASSUME, **(assume or {})}
    rng = np.random.default_rng(seed)
    uids = users.sort_values('user_id').user_id.to_numpy()
    n = len(uids)
    ages, shares = np.array(list(AGE_SHARES)), np.array(list(AGE_SHARES.values()))
    age = rng.choice(ages, size=n, p=shares / shares.sum())
    unknown = rng.random(n) < a['unknown']
    draws = pd.DataFrame({'user_id': uids, 'true_age': age, 'age': np.where(unknown, UNKNOWN_AGE, age),
                          'opt_draw': rng.random(n), 'req_draw': rng.random(n), 'tie_key': rng.random(n)})
    # Courses: 4 year levels of 40 rooms; a student's level comes from their (true) age; within a level, intro
    # courses are bigger (Zipf weights). Under-14s take none.
    per_level = a['courses'] // 4
    weights = 1 / np.arange(1, per_level + 1) ** 0.8
    weights /= weights.sum()
    level_of = {17: [1], 18: [1], 19: [1, 2], 20: [2, 3], 21: [3, 4]}
    rows = []
    for uid, t in zip(uids, draws.true_age):
        if t < 14:
            continue
        levels = level_of.get(int(t), [1] if t < 17 else [4])
        lvl = levels[rng.integers(len(levels))]
        own = rng.choice(per_level, size=a['per_member'] - 1, replace=False, p=weights)
        picks = {10001 + (lvl - 1) * per_level + int(c) for c in own}
        while len(picks) < a['per_member']:                      # one elective, any level
            picks.add(10001 + int(rng.integers(4)) * per_level + int(rng.choice(per_level, p=weights)))
        rows += [(uid, g) for g in sorted(picks)]
    courses = pd.DataFrame(rows, columns=['user_id', 'group_id'])
    return draws, courses


def add_class_friendships(friendships, courses, blocks, extra, seed=SEED):
    """Add `extra` friendships formed in class: a random student befriends a random classmate (seeded)."""
    rng = np.random.default_rng(seed)
    roster = courses.groupby('group_id').user_id.apply(list).to_dict()
    mine = courses.groupby('user_id').group_id.apply(list).to_dict()
    pairs = set(zip(friendships.user_a, friendships.user_b))
    blocked = set(zip(blocks.user_id, blocks.blocked_id)) | set(zip(blocks.blocked_id, blocks.user_id))
    students = sorted(mine)
    rows = []
    while len(rows) < extra:
        u = students[rng.integers(len(students))]
        c = mine[u][rng.integers(len(mine[u]))]
        v = roster[c][rng.integers(len(roster[c]))]
        p = (min(u, v), max(u, v))
        if u == v or p in pairs or (u, v) in blocked:
            continue
        pairs.add(p)
        rows.append((*p, 365))
    return pd.concat([friendships, pd.DataFrame(rows, columns=['user_a', 'user_b', 'since_day'])], ignore_index=True)


def add_triadic_closure(friendships, users, blocks, extra, seed=SEED):
    """A sensitivity world: add `extra` friendships that each close a triangle (a friend of a friend), as real
    networks do (Kossinets & Watts, 2006) and our simulator does not. Seeded."""
    rng = np.random.default_rng(seed)
    nb = {u: set() for u in users.user_id}
    for a, b in zip(friendships.user_a, friendships.user_b):
        nb[a].add(b); nb[b].add(a)
    blocked = set(zip(blocks.user_id, blocks.blocked_id)) | set(zip(blocks.blocked_id, blocks.user_id))
    with_friends = [u for u in users.user_id if nb[u]]
    rows, tries = [], 0
    while len(rows) < extra and tries < 100 * extra:
        tries += 1
        u = with_friends[rng.integers(len(with_friends))]
        v = sorted(nb[u])[rng.integers(len(nb[u]))]
        w = sorted(nb[v])[rng.integers(len(nb[v]))]
        if w == u or w in nb[u] or (u, w) in blocked:
            continue
        nb[u].add(w); nb[w].add(u)
        rows.append((min(u, w), max(u, w), 365))
    return pd.concat([friendships, pd.DataFrame(rows, columns=['user_a', 'user_b', 'since_day'])], ignore_index=True)


def split_friendships(friendships, frac=0.2, seed=SEED):
    """Hide `frac` of the friendships at random (seeded): (kept, hidden), each a friendships table."""
    f = friendships.reset_index(drop=True)
    rng = np.random.default_rng(seed)
    hide = np.sort(rng.choice(len(f), size=int(round(frac * len(f))), replace=False))
    return f.drop(index=hide).reset_index(drop=True), f.loc[hide].reset_index(drop=True)


def people_world(users, groups, memberships, courses, friendships, blocks, draws, assume=None, pending=(), dismissed=(),
                 overrides=None):
    """Build a PeopleWorld from tables. `assume` overrides PEOPLE_ASSUME (the switch shares); pending and dismissed
    are (from, to) user-id pairs; overrides maps an attribute name to {user_id: value} (planted test cases)."""
    a = {**PEOPLE_ASSUME, **(assume or {})}
    users = users.sort_values('user_id').reset_index(drop=True)
    ids = users.user_id.to_numpy()
    pos = pd.Series(np.arange(len(ids)), index=ids)
    d = draws.set_index('user_id').loc[ids]
    n = len(ids)
    F = np.zeros((n, n), dtype=np.int32)
    ia, ib = pos[friendships.user_a].to_numpy(), pos[friendships.user_b].to_numpy()
    F[ia, ib] = 1; F[ib, ia] = 1
    visible = groups[groups.hidden_by_mods == 0].sort_values('group_id')
    course_ids = np.sort(courses.group_id.unique())
    gids = np.concatenate([visible.group_id.to_numpy(), course_ids])
    gpos = pd.Series(np.arange(len(gids)), index=gids)
    m = pd.concat([memberships[memberships.group_id.isin(visible.group_id)][['user_id', 'group_id']],
                   courses[['user_id', 'group_id']]])
    G = np.zeros((n, len(gids)), dtype=np.int32)
    G[pos[m.user_id].to_numpy(), gpos[m.group_id].to_numpy()] = 1
    size = pd.concat([memberships[['user_id', 'group_id']], courses]).groupby('group_id').size().reindex(gids, fill_value=0)

    def pairs(p):
        M = np.zeros((n, n), dtype=bool)
        p = list(p)
        if p:
            M[pos[[x for x, _ in p]].to_numpy(), pos[[y for _, y in p]].to_numpy()] = True
        return M
    w = PeopleWorld(ids=ids, friends=F, groups=G, group_ids=gids, is_course=np.isin(gids, course_ids),
                    group_open=np.concatenate([visible.open.to_numpy() == 1, np.ones(len(course_ids), dtype=bool)]),
                    group_size=size.to_numpy(), blocked=pairs(zip(blocks.user_id, blocks.blocked_id)),
                    pending=pairs(pending), dismissed=pairs(dismissed), suspended=users.suspended.to_numpy() == 1,
                    private=users.privacy.to_numpy() == 'private', opted_in=d.opt_draw.to_numpy() < a['opt_in'],
                    takes_requests=d.req_draw.to_numpy() >= a['no_requests'], age=d.age.to_numpy().copy(),
                    created_day=users.created_day.to_numpy(), tie_key=d.tie_key.to_numpy())
    for field, values in (overrides or {}).items():
        arr = getattr(w, field)
        for uid, v in values.items():
            arr[pos[uid]] = v
    return w


def people_signals(w):
    """(mutual friends, shared groups and courses, shared courses) for every pair."""
    C = w.groups[:, w.is_course]
    return w.friends @ w.friends, w.groups @ w.groups.T, C @ C.T


def age_allowed(w, signals, rule=None):
    """n x n bool: does the age rule let member i be suggested member j? rule: AGE_RULE (the owner's bands) or
    'binary' (the earlier rule: adults and under-18s never mixed, unknown = under 18)."""
    band = w.band
    if rule == 'binary':
        minor = band <= 1
        return minor[:, None] == minor[None, :]
    rule = rule or AGE_RULE
    mutual, shared, courses = signals
    tie, course = (mutual > 0) | (shared > 0), courses > 0
    ok = np.zeros(mutual.shape, dtype=bool)
    for (bi, bj), links in rule.items():
        cell = (band[:, None] == bi) & (band[None, :] == bj)
        if 'any' in links:
            ok |= cell
        elif 'tie' in links:
            ok |= cell & tie
        elif 'course' in links:
            ok |= cell & course
    return ok                                                   # band 0 (under 14) appears in no cell: never


def people_allowed(w, rules=PEOPLE_RULES, signals=None, age_rule=None):
    """n x n bool: may member i be suggested member j, under the given rules (R8 and the people rules)."""
    n = len(w.ids)
    ok = np.ones((n, n), dtype=bool)
    if 'self' in rules: np.fill_diagonal(ok, False)
    if 'friend' in rules: ok &= w.friends == 0
    if 'pending' in rules: ok &= ~w.pending & ~w.pending.T
    if 'blocked' in rules: ok &= ~w.blocked & ~w.blocked.T
    if 'suspended' in rules: ok &= ~w.suspended[None, :]
    if 'private' in rules: ok &= ~w.private[None, :]
    if 'opt_in' in rules: ok &= w.opted_in[None, :]
    if 'requests' in rules: ok &= w.takes_requests[None, :]
    if 'age' in rules: ok &= age_allowed(w, signals if signals is not None else people_signals(w), age_rule)
    if 'dismissed' in rules: ok &= ~w.dismissed
    return ok


def _shared_named(w, i, j):
    """The group a reason names for members i and j: the smallest shared group listed to everyone (then the lowest
    id), or None."""
    common = np.flatnonzero(w.groups[i] & w.groups[j])
    named = [g for g in common if w.group_open[g]]
    if not named:
        return None
    return min(named, key=lambda g: (w.group_size[g], w.group_ids[g]))


def suggest_people(w, askers, method='boing', rules=PEOPLE_RULES, signals=None, weight=1.0, variety=True, k=K,
                   seed=SEED, only_opted_in=False, age_rule=None):
    """Lists of up to k people for each asker (row index): {i: [(j, (kind, value)), ...]}.

    method 'boing': candidates are friends of friends and members of my groups and courses; score = mutual friends +
        weight x shared groups; reason = the bigger one ("N mutual friends", or "You're both in X" naming the smallest
        shared group listed to everyone, or "You're in N groups together"); at most 2 people for the same named group.
    'mutual': friends of friends only, by mutual friends.   'groups': members of my groups only, by shared groups.
    'popular': the most-connected allowed members, the same ranking for everyone.   'random': k allowed members.
    only_opted_in: members who did not switch suggestions on get no list (R1), as in BOING. With the age rule on,
    under-14s get no list either. Every method sees the same allowed set (people_allowed)."""
    signals = signals if signals is not None else people_signals(w)
    mutual, shared, _ = signals
    allowed = people_allowed(w, rules, signals, age_rule)
    degree = w.friends.sum(axis=1)
    band = w.band
    rng = np.random.default_rng(seed)
    out = {}
    for i in askers:
        if (only_opted_in and not w.opted_in[i]) or ('age' in rules and age_rule != 'binary' and band[i] == 0):
            out[i] = []
            continue
        if method == 'random':
            pool = np.flatnonzero(allowed[i])
            pick = rng.choice(pool, size=min(k, len(pool)), replace=False) if len(pool) else []
            out[i] = [(int(j), ('random', None)) for j in pick]
            continue
        if method == 'popular':
            pool = np.flatnonzero(allowed[i])
            order = pool[np.lexsort((w.tie_key[pool], -degree[pool]))][:k]
            out[i] = [(int(j), ('popular', int(degree[j]))) for j in order]
            continue
        mu, sh = mutual[i], shared[i]
        if method == 'mutual':
            cand = np.flatnonzero(allowed[i] & (mu > 0)); score = mu[cand].astype(float)
        elif method == 'groups':
            cand = np.flatnonzero(allowed[i] & (sh > 0)); score = sh[cand].astype(float)
        else:
            cand = np.flatnonzero(allowed[i] & ((mu > 0) | (sh > 0))); score = mu[cand] + weight * sh[cand]
        order = cand[np.lexsort((w.tie_key[cand], -score))]
        items, per_group = [], {}
        for j in order:
            if len(items) >= k:
                break
            m_, s_ = int(mu[j]), int(sh[j])
            if method == 'mutual':
                items.append((int(j), ('mutual', m_))); continue
            if m_ >= s_ and m_ > 0:
                reason = ('mutual', m_)
            else:
                g = _shared_named(w, i, j)
                if g is None:
                    reason = ('groups', s_)
                else:
                    if variety and method == 'boing':
                        if per_group.get(g, 0) >= 2:
                            continue
                        per_group[g] = per_group.get(g, 0) + 1
                    reason = ('group', int(w.group_ids[g]))
            items.append((int(j), reason))
        out[i] = items
    return out


def people_relevance(lists, truth, k=K):
    """Per-asker hit rate, recall@k and NDCG@k against the hidden friends (truth: {i: set of j}). The ideal ranking
    puts min(hidden, k) friends first, so a short or empty list is not excused."""
    rows = []
    for i, hidden in truth.items():
        got = [j for j, _ in lists.get(i, [])][:k]
        hits = [j in hidden for j in got]
        dcg = sum(1 / np.log2(r + 2) for r, h in enumerate(hits) if h)
        ideal = sum(1 / np.log2(r + 2) for r in range(min(len(hidden), k)))
        rows.append({'asker': i, 'hit_rate': float(any(hits)), 'recall@5': sum(hits) / len(hidden),
                     'ndcg@5': dcg / ideal, 'length': len(got)})
    return pd.DataFrame(rows).set_index('asker')


def people_exposure(lists, w, pool):
    """How evenly suggestions are spread over the people who may be suggested (pool: bool array)."""
    counts = np.zeros(len(w.ids))
    for items in lists.values():
        for j, _ in items:
            counts[j] += 1
    c = counts[pool]
    slots = counts.sum()
    top = np.sort(c)[::-1][:max(1, int(round(0.1 * len(c))))]
    new = (w.created_day > TODAY - NEW_DAYS)
    return {'slots': int(slots), 'pool': int(pool.sum()), 'gini': gini(c),
            'top10_share': float(top.sum() / slots) if slots else 0.0, 'coverage': float((c > 0).mean()),
            'new_share_of_slots': float(counts[new & pool].sum() / slots) if slots else 0.0,
            'new_share_of_pool': float((new & pool).sum() / pool.sum()), 'outside_pool': int(counts[~pool].sum())}


PEOPLE_CHECKS = ['R1 no list while switched off', 'R1 no list for under-14s', 'R11 at most 5, no repeats', 'never me',
                 'never a friend', 'never a pending request', 'R8 never blocked either way', 'R8 never suspended',
                 'R8 never private', 'only people who switched on', 'only people taking requests',
                 'R8 age bands', 'R7 never someone dismissed', 'R6 "N mutual friends" is true',
                 'R6 the reason is the bigger signal', 'R6 "both in X": both are members and X is listed',
                 'R6 "N groups together" is true', 'R5 at most 2 people per named group']


def _age_ok_spec(age_i, age_j, mutual, shared, courses):
    """The owner's age rule, restated from its text for the checker (independent of age_allowed)."""
    def band(a):
        return 'minor' if a == UNKNOWN_AGE else 'child' if a < 14 else 'minor' if a < 18 else 'young' if a <= 20 else 'adult'
    bi, bj = band(age_i), band(age_j)
    if 'child' in (bi, bj):
        return False                                             # under 14: never suggested, never shown anyone
    if bi == 'minor':
        return bj == 'minor' or (bj == 'young' and (mutual > 0 or shared > 0))
    if bi == 'young':
        return bj != 'minor' or courses > 0                      # a minor only as a classmate
    return bj != 'minor'                                         # 21 and over: never a minor


def check_people(lists, w):
    """Count every check and every violation of the people rules, recomputing everything from the world's raw
    tables (not from the recommender). lists: {i: [(j, (kind, value)), ...]} for every member asked."""
    checks = {c: [0, 0] for c in PEOPLE_CHECKS}             # rule -> [checks, violations]

    def rule(name, good):
        checks[name][0] += 1
        checks[name][1] += 0 if good else 1
    gpos = {int(g): x for x, g in enumerate(w.group_ids)}
    nb = [set(np.flatnonzero(w.friends[i])) for i in range(len(w.ids))]
    gs = [set(np.flatnonzero(w.groups[i])) for i in range(len(w.ids))]
    cs = [{g for g in s if w.is_course[g]} for s in gs]
    for i, items in lists.items():
        rule('R1 no list while switched off', w.opted_in[i] or not items)
        rule('R1 no list for under-14s', not items or w.age[i] == UNKNOWN_AGE or w.age[i] >= 14)
        rule('R11 at most 5, no repeats', len(items) <= K and len({j for j, _ in items}) == len(items))
        named = {}
        for j, (kind, value) in items:
            mutual, shared, courses = len(nb[i] & nb[j]), len(gs[i] & gs[j]), len(cs[i] & cs[j])
            rule('never me', j != i)
            rule('never a friend', j not in nb[i])
            rule('never a pending request', not (w.pending[i, j] or w.pending[j, i]))
            rule('R8 never blocked either way', not (w.blocked[i, j] or w.blocked[j, i]))
            rule('R8 never suspended', not w.suspended[j])
            rule('R8 never private', not w.private[j])
            rule('only people who switched on', bool(w.opted_in[j]))
            rule('only people taking requests', bool(w.takes_requests[j]))
            rule('R8 age bands', _age_ok_spec(int(w.age[i]), int(w.age[j]), mutual, shared, courses))
            rule('R7 never someone dismissed', not w.dismissed[i, j])
            if kind == 'mutual':
                rule('R6 "N mutual friends" is true', value == mutual and mutual > 0)
                rule('R6 the reason is the bigger signal', mutual >= shared)
            elif kind == 'group':
                g = gpos.get(value)
                rule('R6 "both in X": both are members and X is listed',
                     g is not None and g in gs[i] and g in gs[j] and bool(w.group_open[g]))
                rule('R6 the reason is the bigger signal', shared > mutual or mutual == 0)
                named[value] = named.get(value, 0) + 1
            elif kind == 'groups':
                rule('R6 "N groups together" is true', value == shared and shared > 0)
                rule('R6 the reason is the bigger signal', shared > mutual or mutual == 0)
        for g, c in named.items():
            rule('R5 at most 2 people per named group', c <= 2)
    return {c: {'checks': v[0], 'violations': v[1]} for c, v in checks.items()}


AGE_GRID = [13, 15, 17, 18, 19, 20, 21, 25, UNKNOWN_AGE]
LINKS = ['course', 'group', 'mutual']


def age_grid_world():
    """The planted age cases: one isolated pair (viewer, candidate) for every viewer age x candidate age x link in
    AGE_GRID x AGE_GRID x LINKS (9 x 9 x 3 = 243). 'course': the two share one course room and nothing else;
    'group': one open interest group and nothing else (not classmates); 'mutual': one mutual friend (aged 25) and no
    group. Everyone is public, switched on and takes requests. Returns (world, cases): cases is a table with the
    viewer and candidate row indices, their ages and the link."""
    rows, n, groups_of, friends, gid = [], 0, [], [], 0
    for va in AGE_GRID:
        for ca in AGE_GRID:
            for link in LINKS:
                v, c = n, n + 1
                n += 2
                if link == 'mutual':
                    f = n; n += 1
                    friends += [(v, f), (f, c)]
                    groups_of.append((None, v, c, f))
                else:
                    groups_of.append((gid, v, c, link)); gid += 1
                rows.append({'viewer': v, 'candidate': c, 'viewer_age': va, 'candidate_age': ca, 'link': link})
    cases = pd.DataFrame(rows)
    ages = np.full(n, 25)
    ages[cases.viewer.to_numpy()] = cases.viewer_age.to_numpy()
    ages[cases.candidate.to_numpy()] = cases.candidate_age.to_numpy()
    G = np.zeros((n, gid), dtype=np.int32)
    is_course = np.zeros(gid, dtype=bool)
    for g, v, c, link in groups_of:
        if g is not None:
            G[v, g] = G[c, g] = 1
            is_course[g] = link == 'course'
    F = np.zeros((n, n), dtype=np.int32)
    for a, b in friends:
        F[a, b] = F[b, a] = 1
    z = np.zeros((n, n), dtype=bool)
    w = PeopleWorld(ids=np.arange(1, n + 1), friends=F, groups=G, group_ids=np.arange(1, gid + 1), is_course=is_course,
                    group_open=np.ones(gid, dtype=bool), group_size=np.full(gid, 2), blocked=z, pending=z.copy(),
                    dismissed=z.copy(), suspended=np.zeros(n, dtype=bool), private=np.zeros(n, dtype=bool),
                    opted_in=np.ones(n, dtype=bool), takes_requests=np.ones(n, dtype=bool), age=ages,
                    created_day=np.zeros(n, dtype=int), tie_key=np.arange(n) / n)
    return w, cases


def age_grid_expected(cases):
    """What the owner's rule says for each planted case, read off its text (not from the code)."""
    def says(va, ca, link):
        def band(a):
            return 'minor' if a == UNKNOWN_AGE else 'under 14' if a < 14 else 'minor' if a < 18 else '18-20' if a <= 20 else '21+'
        v, c = band(va), band(ca)
        if 'under 14' in (v, c):
            return False                        # 1. under 14: no suggestions, never suggested
        if v == 'minor':
            return c == 'minor' or (c == '18-20')   # 2. minors: other minors; 18-20 only through a tie (every case has one); never 21+
        if v == '18-20':
            return c != 'minor' or link == 'course'  # 3. 18-20: a minor only if classmates
        return c != 'minor'                     # 4. 21 and over: never a minor
    return np.array([says(r.viewer_age, r.candidate_age, r.link) for r in cases.itertuples()])


# E7 v2 (19 Nov 2026): a realistic friendship model for the main E7 world, fixed before any test result was seen.
# Friendships form inside shared foci (groups and classes: sim_v1's group friendships and the classmate friendships)
# and close triangles, more readily when the two already share a group or course ("focal closure"; Kossinets & Watts,
# 2006), until the average local clustering coefficient reaches CLUSTERING_TARGET. Real friendship networks are highly
# clustered, and clustering falls as degree rises: about 0.14 for Facebook users with 100 friends (Ugander et al., 2011);
# our members have about 10 friends, so 0.15 is conservative. (0.20 was the first choice, but this generator levels off
# near 0.17, so it was lowered before any test result was seen.)
CLUSTERING_TARGET = 0.15
CLOSURE_P_NO_FOCUS = 0.3     # a friend of a friend with no shared group or course is accepted 30% of the time (100% with one)


def avg_clustering(friendships, user_ids):
    """Average local clustering coefficient (members with fewer than 2 friends count as 0, as in networkx)."""
    pos = pd.Series(np.arange(len(user_ids)), index=user_ids)
    A = np.zeros((len(user_ids), len(user_ids)), dtype=np.float32)
    a, b = pos[friendships.user_a].to_numpy(), pos[friendships.user_b].to_numpy()
    A[a, b] = 1; A[b, a] = 1
    tri = ((A @ A) * A).sum(axis=1) / 2
    k = A.sum(axis=1)
    cc = np.where(k > 1, 2 * tri / np.maximum(k * (k - 1), 1), 0.0)
    return float(cc.mean())


def add_focal_closure(friendships, users, memberships, courses, blocks, target=CLUSTERING_TARGET,
                      p_no_focus=CLOSURE_P_NO_FOCUS, seed=SEED, batch=250, max_added=20000):
    """Add friend-of-a-friend friendships until the average local clustering reaches `target` (checked every `batch`
    additions). A candidate u-w (w a friend of u's friend v) is accepted with probability 1 if u and w share a group or
    course, else p_no_focus. Seeded. Returns (friendships, added, clustering)."""
    rng = np.random.default_rng(seed)
    uids = users.sort_values('user_id').user_id.to_numpy()
    nb = {u: set() for u in uids}
    for a, b in zip(friendships.user_a, friendships.user_b):
        nb[a].add(b); nb[b].add(a)
    foci = pd.concat([memberships[['user_id', 'group_id']], courses[['user_id', 'group_id']]])
    focus_of = foci.groupby('user_id').group_id.apply(set).to_dict()
    blocked = set(zip(blocks.user_id, blocks.blocked_id)) | set(zip(blocks.blocked_id, blocks.user_id))
    rows, f = [], friendships
    cc = avg_clustering(f, uids)
    while cc < target and len(rows) < max_added:
        added = 0
        while added < batch:
            u = uids[rng.integers(len(uids))]
            if not nb[u]:
                continue
            v = sorted(nb[u])[rng.integers(len(nb[u]))]
            w = sorted(nb[v])[rng.integers(len(nb[v]))]
            if w == u or w in nb[u] or (u, w) in blocked:
                continue
            shared = focus_of.get(u, set()) & focus_of.get(w, set())
            if not shared and rng.random() >= p_no_focus:
                continue
            nb[u].add(w); nb[w].add(u)
            rows.append((min(u, w), max(u, w), 365))
            added += 1
        f = pd.concat([friendships, pd.DataFrame(rows, columns=['user_a', 'user_b', 'since_day'])], ignore_index=True)
        cc = avg_clustering(f, uids)
    return f, len(rows), cc
