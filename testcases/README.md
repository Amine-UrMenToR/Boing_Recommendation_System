# Test cases for BOING's JavaScript port of the recommender

Made by notebook 11 with the final design (`boingrec.make_test_cases(boingrec.FINAL_CONFIG)`), with the privacy noise switched off (`eps` is null) so that every number is exact, except in case 13, which gives its noise draws as data. 13 cases; each is a folder with a small community (100 to 300 members, 20 to 150 groups), the settings, and the answer: every served member's suggestions in `expected.csv`. The port reads a folder's files, runs with its `config.json`, and must give the same answer. Notebook 10 writes the same cases with notebook 06's settings, so run notebook 11 after it.

## The settings

| Setting | Value | What it does |
|---|---|---|
| `alpha` | 0.2 | weight of "also joined" (collaborative filtering) |
| `beta` | 0.2 | weight of similar descriptions (TF-IDF) |
| `gamma` | 0.3 | weight of friends (public friends who are members) |
| `delta` | 0.3 | weight of hidden tastes (the AI model) |
| `k` | 10 | the AI model's number of hidden tastes |
| `topic_weight` | 0 | how much a member's chosen topics count in similar descriptions |
| `personal` | true | personalisation on (False: the default list, rule R1) |
| `off_new_w` | 0.5 | personalisation off: weight of newness (the rest is recent activity) |
| `q` | 0.2 | R4: at least ceil(q x 5) slots of each list go to new or small groups |
| `c` | 0.05 | R4: no group gets more than c of all slots (null: no cap) |
| `n` | 2 | R5: at most n groups of one public topic cluster per list (null: no limit) |
| `lam` | 0.8 | R5: MMR, lam x relevance - (1 - lam) x similarity to the groups already picked |
| `clusters` | 8 | number of public topic clusters (KMeans on the group texts) |
| `L` | 3 | R9: only accounts at level L or more count |
| `burst_w` | 0 | R9: weight of the joins of accounts younger than young_days (0: they count once they are older) |
| `young_days` | 30 | R9: an account is young for this many days |
| `eps` | null | R10: differential-privacy budget epsilon (null or inf: no noise) |
| `m` | 3 | R10: each member counts for at most m groups (null: no clipping) |
| `size_share` | 0.1 | R10: share of epsilon spent on the group sizes (the rest on the pair counts) |
| `noise_seed` | null | R10: seed of the clipping hash and the noise (null: use seed) |
| `seed` | 0 | seed of the order members are served in (for the cap c), and of the clipping and noise when noise_seed is null |
| `small_from` | r9 | R4: 'r9' = a group is small if fewer than 10 of its members are accounts that count under R9 (level L or more, at least young_days old when burst_w = 0), no clipping, no noise; 'public' = if the member count Discover shows is under 10; 'counted' = from the recommender's own (clipped, noisy) counts |
| `r9_scope` | all | R9: 'all' = the level bar and the young-account wait apply to posts, likes and friends too; 'joins' = to memberships only |
| `act_eps` | null | R10 for the recent activity: privacy budget of the active-member counts (null: activity counts posts and likes, no noise) |
| `count_under_noise` | false | R6: with the noise on, a "shared members" reason states its noisy count (true) or names the group only (false) |

The noise (`eps`) draws random numbers, which a port cannot redo; so case 13 gives them as data (`noise.csv`) and the port adds exactly those. BOING turns the noise on with the final value (`eps` = 1.5) and a secret seed; its effect is measured in notebooks 08 and 11.

## The cases

"Relaxed" counts how many times the re-ranker had to drop a rule to fill a slot (quota / topic cap / global cap, as `recommend()` reports in `attrs["relaxed"]`): a port should count the same.

| Case | What it checks | Members | Served | Rows | Settings the case changes | Relaxed |
|---|---|---|---|---|---|---|
| `01_ordinary_member` | An ordinary member: user 1 (in Spanish for beginners, Spanish evening chat and Python project club, with public friends) gets 5 suggestions, each with its main true reason from a fixed template (R6). | 100 | 100 | 500 | none | 8 / 50 / 50 |
| `02_cold_start_member` | Cold start: user 1 is in one group only (Spanish for beginners) and has no friends; they still get 5 suggestions, and every reason that names a group names that one (R6). | 100 | 100 | 500 | none | 6 / 50 / 50 |
| `03_brand_new_group` | A brand-new group: Spanish for travellers (group 17) was created 2 days ago and has 2 members; in user 1's list it takes the newcomer slot (rank 5, forced), with the reason "A new group: ..." (R4; this case keeps q >= 0.2, c >= 10% and no clipping). | 100 | 100 | 500 | `c` = 0.1, `m` = null | 0 / 0 / 0 |
| `04_hidden_by_moderators` | Hidden by moderators: French evening chat (group 3), user 1's first suggestion when it is visible, is hidden; it must never appear in anyone's list (R8). | 100 | 100 | 500 | none | 9 / 75 / 75 |
| `05_blocked_friend` | Blocks: user 1 blocked user 6, and user 4 blocked user 1; both are user 1's friends and were named in user 1's reasons before; neither may be named or counted for user 1 now, in either direction (R6, R8). | 100 | 100 | 500 | none | 7 / 50 / 50 |
| `06_private_friend` | A private profile: user 6, user 1's friend named in a reason before, switches to a private profile; no reason may name them, for anyone (R6, R8). | 100 | 100 | 500 | none | 7 / 50 / 50 |
| `07_not_interested` | Not interested: user 1 marked French evening chat (group 3), their first suggestion before, "not interested"; it must not come back for user 1 (R7). | 100 | 100 | 500 | none | 8 / 50 / 50 |
| `08_accounts_that_do_not_count` | Accounts that must not count: 4 suspended accounts (users 101-104) and 4 level-1 accounts (users 105-108) joined Spanish evening chat (user 1's group) and GRE study hall, and are user 1's public friends. With L = 3 (this case keeps L >= 3) none of them counts in any statistic: their joins change no group size, "also joined" count, or which groups count as small, or activity, and no reason names them (R8, R9). Suspended accounts are not served. The level-1 accounts still get their own suggestions, and those take slots under the shared cap c, so other members' lists can still shift when they join (the cap is shared, not a statistic). | 108 | 104 | 520 | none | 10 / 52 / 52 |
| `09_almost_everything_joined` | Almost everything joined: user 1 is in every Discover group but 3 (groups 9, 14 and 17); the list must hold exactly those 3, never padded with other groups (R11). | 100 | 100 | 498 | none | 6 / 48 / 48 |
| `10_personalisation_off` | Personalisation off (the default, R1): no profile is used; every member gets the same scores (recent activity and newness), a list of 5 (or every candidate), reasons "active" or "new_group" only, never empty. | 100 | 100 | 500 | `personal` = false | 8 / 52 / 52 |
| `11_nothing_to_go_on` | A brand-new member with nothing to go on: user 1 (created 3 days ago, level 1, no groups, no friends) has personalisation on but no data, so gets the default list, never an empty one (R1). | 100 | 100 | 500 | none | 5 / 50 / 50 |
| `12_larger_world_no_relaxing` | A larger world: the first 300 members of the synthetic community and all 150 groups (129 on Discover). Every rule holds without being relaxed (quota, topic cap, global cap), so this case checks the re-ranker in the regime BOING will run in (R4, R5). | 300 | 297 | 1485 | none | 0 / 0 / 0 |
| `13_noise_on` | Privacy noise on (R10: eps = 1.5, m = 3): the same larger world, with the Laplace draws given in noise.csv (one per group size and one per pair of groups), so a port adds exactly the same numbers and must give exactly expected.csv. The noise changes some suggestions against the same case without noise. | 300 | 297 | 1485 | `eps` = 1.5 | 0 / 0 / 0 |

**The cap binds hard in the small world (cases 01 to 11).** With 18 groups on Discover and 100 members served, c = 0.05 lets a group take at most 25 of the 500 slots: 18 x 25 = 450 in all, fewer than the slots to fill. So the re-ranker must relax the cap about 50 times per case (a slot that drops the global cap drops the topic cap too, so both counts rise). The order members are served in decides who still gets the capped groups: serve exactly in `serve_order`, count each group's slots across members, and drop the rules in the same order (quota, then topic cap, then global cap). In BOING, with many more groups, the cap rarely binds; it must stay above 1 / (groups on Discover). **Cases 12 and 13** use a larger world (300 members of the synthetic community, all 150 groups) where no rule is relaxed: the regime BOING runs in. Case 13 also turns the privacy noise on, with its draws in `noise.csv`.

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

## How a port passes a case

Run the port on the folder's files with its `config.json` (serve the members in `users`, in the order `serve_order`), then compare with `expected.csv`, member by member:

1. **the same group ids in the same order**: rank 1 to 5 (fewer only when fewer groups can be shown, as in case 09);
2. **the same `reason_code`** on every row;
3. **every `score` within 1e-6** of the expected one (`expected.csv` keeps 6 decimals);
4. the same `reason_text`, character for character: the templates are fixed. A port that shows them in another language should translate each template one to one and check the code and the group, friend or number it names.

A case passes when every row does; the port passes when all the cases do. That match is itself a result for the report.

## To match exactly

- TF-IDF as scikit-learn's default `TfidfVectorizer` on `name + " " + about`: lowercase, tokens of 2 or more letters, digits or `_`
  (regular expression `\b\w\w+\b`; all texts here are plain ASCII), idf = ln((1 + n) / (1 + df)) + 1, each row scaled to length 1;
  similarity = dot product.
- The AI model: the k eigenvectors of co = X^T X with the largest eigenvalues (any sign: only V V^T is used). `index.csv`'s
  `taste_gap` is the gap between the k-th and (k+1)-th eigenvalues over the largest (0.73% to 1.96% in these cases): far above rounding
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

## Checking the Python side

`boingrec.verify_test_cases()` re-runs every case from its own files and compares with `expected.csv` (the same rows and texts, scores within 0.0000005), then counts the hard-rule violations with `boingrec.check_rules()` (all 0).
