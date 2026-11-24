# Summary of results

Every number the final report quotes, with the file it comes from (made by notebook 11 from `results/`; the same numbers are in `results/summary.json`). Synthetic community only: 2,000 fake members and 150 groups; the test set is 1,406 members.

The final design: `br.FINAL_CONFIG` = alpha = 0.2, beta = 0.2, gamma = 0.3, delta = 0.3, k = 10, topic_weight = 0, off_new_w = 0.5, q = 0.2, c = 0.05, n = 2, lam = 0.8, small_from = r9, clusters = 8, L = 3, burst_w = 0, young_days = 30, r9_scope = all, eps = 1.5, m = 3, size_share = 0.1, act_eps = None, count_under_noise = no. Personalisation is off by default (R1). The reasoning for each dial is in `results/final_choices.md`.

**What the privacy guarantee covers:** one release of the group sizes and pair counts (X^T X), epsilon = 1.5, m = 3. **Not covered:** the friends signal (public friends' memberships, shown on their public profiles); the member counts that decide "small" (members who count under R9; Discover shows every member); the recent activity behind the default list (posts and like counts of open groups); act_eps failed the rule; the shared cap c (one member's own list can change which capped groups later members get).

Contents: the key points by step (below), then every number by step, then every figure with a suggested caption.

## Key points: The final design (test, 1,406 members; rows with noise: mean of 10 draws)

| What | Value | Key in summary.json |
|---|---|---|
| Hit rate, today's BOING (test) | 0.2205 | `final.test.popularity.hit_rate` |
| Hit rate, final design | 0.6132 | `final.test.final.hit_rate` |
| NDCG@5, today's BOING | 0.1311 | `final.test.popularity.ndcg@5` |
| NDCG@5, final design (mean of 10 noise draws) | 0.4882 | `final.test.final.ndcg@5` |
| NDCG@5, final design, 95% range (low) | 0.466 | `final.test.final.ndcg@5 low` |
| NDCG@5, final design, 95% range (high) | 0.5095 | `final.test.final.ndcg@5 high` |
| NDCG@5, the hybrid without any rule | 0.5407 | `final.test.hybrid.ndcg@5` |
| NDCG@5, the final design before the review (epsilon 5) | 0.5104 | `final.test.before.ndcg@5` |
| Share of slots for new or small groups, today's BOING | 0 | `final.test.popularity.newcomer_share` |
| Share of slots for new or small groups, final design (count Discover shows) | 0.1994 | `final.test.final.newcomer_share` |
| Share of slots for new or small groups, final design (members who count) | 0.2078 | `final.test.final.newcomer_share (members who count)` |
| Share of slots for new or small groups, before the review | 0.1581 | `final.test.before.newcomer_share` |
| Lists with no new or small group, final design, by the members who count (of 1,406) | 0 | `final.test.final.lists below the quota (members who count)` |
| The same, by the count Discover shows (mean of 10 draws) | 55.2 | `final.test.final.lists below the quota (count Discover shows)` |
| Lists with no new or small group (count Discover shows), before the first review | 470.4 | `final.test.before.lists below the quota (count Discover shows)` |
| Gini of exposure, today's BOING | 0.9534 | `final.test.popularity.gini` |
| Gini of exposure, final design | 0.5319 | `final.test.final.gini` |
| Lists with 3+ groups of one hidden topic, final design | 0.4654 | `final.test.final.lists with 3+ of one hidden topic` |
| Cost of fair exposure and variety (NDCG@5) | 0.01497 | `final.cost.step2.cost` |
| Cost of judging "small" from the count Discover shows, with the final clusters (NDCG@5) | 0.004772 | `final.cost.step3.cost` |
| Cost of the final weights without noise (NDCG@5) | 0.001976 | `final.cost.step4.cost` |
| Cost of fake-account resistance (NDCG@5) | 0.004324 | `final.cost.step5.cost` |
| Cost of privacy, epsilon = 1.5 (NDCG@5) | 0.02646 | `final.cost.step6.cost` |
| Cost of every rule together (NDCG@5) | 0.0525 | `final.cost.step7.cost` |
| Practice quizzes, epsilon = 1.5: accuracy kept (5 quizzes x 20 fresh draws) | 0.9284 | `final.quiz.eps.eps1.5.accuracy kept` |
| Practice quizzes, epsilon = 1.5: accuracy kept, 95% range over the quizzes (low) | 0.9192 | `final.quiz.eps.eps1.5.accuracy kept low` |
| Practice quizzes, epsilon = 1.5: single releases keeping less than 90% | 0.08 | `final.quiz.eps.eps1.5.single releases below 90%` |
| Practice quizzes, epsilon = 1: accuracy kept | 0.8969 | `final.quiz.eps.eps1.accuracy kept` |
| Practice quizzes, epsilon = 1: accuracy kept, 95% range (high) | 0.9067 | `final.quiz.eps.eps1.accuracy kept high` |
| Practice quizzes, epsilon = 1: quizzes where the first version's rule passes (of 5) | 0 | `final.quiz.eps.eps1.quizzes passing alone` |
| Practice quizzes, epsilon = 1: single releases keeping less than 90% | 0.59 | `final.quiz.eps.eps1.single releases below 90%` |
| Round 1 (notebook 06's weights): epsilon chosen | 2 | `final.quiz.rounds.1.eps` |
| Round 1: how much the best mix beats notebook 06's (NDCG@5, under noise) | 0.0121 | `final.quiz.rounds.1.best minus the mix` |
| NDCG@5, final design without privacy | 0.5146 | `final.test.exact.ndcg@5` |
| NDCG@5, the final design at epsilon = 2 | 0.4929 | `final.test.eps2.ndcg@5` |
| Default list (personalisation off): NDCG@5 | 0.0584 | `final.test.off.ndcg@5` |
| Reasons checked (both lists, all members) | 19830 | `final.rules.reasons_checked` |
| Reasons faithful to the computed score | 19830 | `final.rules.reasons_faithful` |
| Reasons on personalised lists (both runs) | 9745 | `final.rules.personal_shown` |
| Of them, true to the raw data | 9481 | `final.rules.personal_true` |
| Reasons on default lists (both runs) | 10085 | `final.rules.default_shown` |
| Of them, true to the raw data | 10085 | `final.rules.default_true` |
| "Shared members" reasons naming groups that share nobody, final design (mean of 10 draws) | 0.4103 | `final.reasons.final.share naming groups that share nobody` |
| The same, lowest draw | 0.307 | `final.reasons.final.share naming groups that share nobody, lowest draw` |
| The same, highest draw | 0.5185 | `final.reasons.final.share naming groups that share nobody, highest draw` |
| Noisy counts that would be close to the truth if stated (final design) | 0.2882 | `final.reasons.final.share of noisy counts that would be close` |
| Hard-rule violations, final design (all members) | 0 | `final.rules.Final design, all members.hard_violations` |
| Shared cap: other members whose list changed when one member left, mean of 30 trials | 0.1667 | `final.privacy_scope.shared cap.other members whose list changed (default + personalised), mean` |
| Lists showing the target with 100 patient fake accounts (D) | 351 | `final.sybil.D.k100.target exposure` |
| First fix ("small" from the count Discover shows): lists another group gains when new accounts (A) push one rival over the line | 11 | `final.sabotage.first fix, attacker A: largest gain of another group` |
| Final: new or low-level accounts (A to C) pushing rivals change no statistic | yes | `final.sabotage.final, attackers A to C: statistics unchanged` |
| Final: lists another group gains when patient accounts (D) push one rival over the line | 9 | `final.sabotage.final, attacker D: largest gain of another group` |
| Default lists showing an old group pushed by 100 posting fakes (B: young, levelled up) | 0 | `final.sybil_posting.B.k100.default lists showing the target` |
| Best possible hit rate (hidden groups out of reach of any method) | 0.9531 | `final.reachable.best possible hit rate` |
| Test cases for the port, all matching | 13 | `final.testcases.cases` |

## Key points: E1: which method works best (test, notebook 06)

| What | Value | Key in summary.json |
|---|---|---|
| NDCG@5, random suggestions | 0.025 | `e1.random.ndcg@5` |
| NDCG@5, today's BOING (biggest groups first) | 0.131 | `e1.popularity.ndcg@5` |
| NDCG@5, "also joined" | 0.499 | `e1.also_joined.ndcg@5` |
| NDCG@5, similar descriptions | 0.159 | `e1.descriptions.ndcg@5` |
| NDCG@5, the AI model (hidden tastes) | 0.475 | `e1.hidden_tastes.ndcg@5` |
| NDCG@5, the hybrid | 0.541 | `e1.hybrid.ndcg@5` |
| NDCG@5, hybrid + fair re-ranking (notebook 06 dials) | 0.528 | `e1.reranked.ndcg@5` |
| Share of slots for new or small groups, the hybrid | 0.02 | `e1.hybrid.newcomer_share` |
| Share of slots for new or small groups, hybrid + fair re-ranking | 0.203 | `e1.reranked.newcomer_share` |
| Price of fairness: NDCG@5 the re-ranking costs | 0.0126 | `e1.price_of_fairness.cost` |
| Price of fairness, 95% range (low) | 0.0081 | `e1.price_of_fairness.cost low` |
| Price of fairness, 95% range (high) | 0.0171 | `e1.price_of_fairness.cost high` |
| NDCG@5, personalisation off | 0.058 | `e1.off.ndcg@5` |

## Key points: E2: what fair exposure and variety cost (notebook 07)

| What | Value | Key in summary.json |
|---|---|---|
| Chosen q: share of each list for new or small groups | 0.2 | `e2.recommended.q` |
| Chosen c: most slots one group may take (share of all) | 0.05 | `e2.recommended.c` |
| Chosen n: groups of one topic cluster per list | 2 | `e2.recommended.n` |
| Chosen λ: variety weight (1 = no variety term) | 0.8 | `e2.recommended.lam` |
| Practice quiz: share of the hybrid's NDCG@5 kept (budget 95%) | 0.9714 | `e2.validation.share of the hybrid` |
| Test NDCG@5 with the chosen dials | 0.5257 | `e2.test.ndcg@5` |
| Test share of slots for new or small groups | 0.2009 | `e2.test.newcomer_share` |
| Cost against the hybrid (NDCG@5) | 0.015 | `e2.test.cost vs hybrid` |
| Cost of the quota q alone (NDCG@5) | 0.0144 | `e2.dial.q.cost` |
| Cost of the topic cap n alone (NDCG@5) | 0.0008 | `e2.dial.n.cost` |
| Cost of variety λ alone (NDCG@5) | 0.0024 | `e2.dial.lam.cost` |
| Topics per list without variety (λ = 1) | 2.402 | `e2.dial.lam.topics_per_list off` |
| Topics per list with λ = 0.8 | 2.591 | `e2.dial.lam.topics_per_list on` |
| NDCG@5 with a second newcomer slot (q = 40%) | 0.504 | `e2.table.More quota (q = 40%).ndcg@5` |
| Default list: groups shown without the cap c | 8 | `e2.dial.c.coverage off` |
| Default list: groups shown with c = 5% | 23 | `e2.dial.c.coverage on` |
| Default list: most-shown group's share of slots, no cap | 0.1999 | `e2.dial.c.largest_share off` |
| Default list: most-shown group's share of slots, c = 5% | 0.0499 | `e2.dial.c.largest_share on` |
| Rank correlation of NDCG@5, practice quiz vs test (180 settings) | 0.9685 | `e2.spearman ndcg@5 validation vs test` |

## Key points: E3: what privacy costs (test, notebook 06's design, m = 3; noise rows: mean of 10 draws)

| What | Value | Key in summary.json |
|---|---|---|
| NDCG@5, no privacy | 0.5281 | `e3.curve.no_privacy.ndcg@5` |
| NDCG@5, ε = 0.1 | 0.2599 | `e3.curve.eps0.1.m3.ndcg@5` |
| NDCG@5, ε = 0.5 | 0.4081 | `e3.curve.eps0.5.m3.ndcg@5` |
| NDCG@5, ε = 1 | 0.461 | `e3.curve.eps1.m3.ndcg@5` |
| NDCG@5, ε = 2 | 0.4951 | `e3.curve.eps2.m3.ndcg@5` |
| NDCG@5, ε = 5 | 0.5162 | `e3.curve.eps5.m3.ndcg@5` |
| NDCG@5, clipping only (ε = ∞) | 0.526 | `e3.curve.clip.m3.ndcg@5` |
| NDCG@5, no statistics about other members at all | 0.4239 | `e3.curve.no_statistics_about_others.ndcg@5` |
| E3's choice for notebook 06's design: ε | 2 | `e3.eps` |
| E3's choice: m (groups each member counts for) | 3 | `e3.m` |
| Share of memberships kept by clipping to 3 groups | 0.7441 | `e3.memberships_kept_by_clipping` |
| Test cost of ε = 2 (NDCG@5) | 0.033 | `e3.test.cost` |
| "Shared members" reasons naming groups that share nobody, ε = 2 | 0.2626 | `e3.reasons.test, chosen setting.shares nobody` |
| 25% opt in, ε = 2: NDCG@5 of those who opt in when everyone counts | 0.4895 | `e3.opt_in_25.everyone counts, epsilon = 2, m = 3.ndcg@5 (opted in)` |
| 25% opt in, ε = 2: the same when only opted-in members count | 0.2826 | `e3.opt_in_25.only opted-in members count, epsilon = 2, m = 3.ndcg@5 (opted in)` |

## Key points: E4: fake accounts (test, notebook 06's other dials; k = number of fake accounts)

| What | Value | Key in summary.json |
|---|---|---|
| Lists showing the target, no attack, R9 off | 21 | `e4.test.target_exposure.fresh.R9 off.k=0` |
| Lists showing the target, 100 fakes, R9 off | 442 | `e4.test.target_exposure.fresh.R9 off.k=100` |
| Lists showing the target, 200 fakes, R9 off | 521 | `e4.test.target_exposure.fresh.R9 off.k=200` |
| Lists showing the target, 100 new or low-level fakes (A), L = 3 and a 30-day wait | 20 | `e4.test.target_exposure.fresh.L = 3 + burst 0.k=100` |
| Lists showing the target, 100 patient fakes (D), L = 3 and a 30-day wait | 433 | `e4.test.target_exposure.both.L = 3 + burst 0.k=100` |
| Bar: lists showing the most-shown honest new group | 49 | `e4.test.bar_top_honest_new_group` |
| Places gained per fake account (A, 10 fakes, R9 off) | 1.572 | `e4.test.places_per_fake_A.R9 off.k=10` |
| Median lists gained by the 21 small new groups as targets, R9 off | 414 | `e4.targets_robustness_median_gain.R9 off` |
| The same, L = 3 and a 30-day wait | 0 | `e4.targets_robustness_median_gain.L = 3 + burst 0` |
| Default lists showing an old group, 20 posting fakes (B), R9 on joins only | 703 | `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins only.levelled.k=20` |
| The same, R9 on joins, posts, likes and friends | 0 | `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins, posts, likes and friends.levelled.k=20` |
| NDCG@5 with no attack, R9 off | 0.5281 | `e4.cost_no_attack.ndcg@5_tested_r9_off` |
| NDCG@5 with no attack, L = 3 and a 30-day wait | 0.5267 | `e4.cost_no_attack.ndcg@5_tested_chosen` |
| Honest memberships that wait 30 days before they count | 282 | `e4.cost_no_attack.honest_memberships_turned_down` |
| Honest memberships in all | 6367 | `e4.cost_no_attack.honest_memberships` |

## Key points: E5: new members and new groups (notebook 06's design)

| What | Value | Key in summary.json |
|---|---|---|
| NDCG@5, proposed design, members with 3 or more groups (test) | 0.546 | `e5.reranked.ndcg@5 3+ groups (test)` |
| NDCG@5, proposed design, members with 2 groups (test) | 0.465 | `e5.reranked.ndcg@5 2 groups (test)` |
| NDCG@5, proposed design, members with 1 group (newcomer quiz) | 0.4 | `e5.reranked.ndcg@5 1 group (quiz)` |
| NDCG@5, proposed design, members with no group yet (newcomer quiz) | 0.326 | `e5.reranked.ndcg@5 no group yet (quiz)` |
| NDCG@5, proposed design, new members (newcomer quiz) | 0.343 | `e5.reranked.ndcg@5 new members (quiz)` |
| NDCG@5, today's BOING, new members (newcomer quiz) | 0.134 | `e5.popularity.ndcg@5 new members (quiz)` |
| Cost of the re-ranking for members with 1 group (NDCG@5) | 0.031 | `e5.cost_of_reranking.1 group.cost` |
| The same, relative | 0.072 | `e5.cost_of_reranking.1 group.relative cost` |
| Share of slots for new groups, proposed design | 0.042 | `e5.reranked.share new groups` |
| Share of slots for older small groups, proposed design | 0.161 | `e5.reranked.share older small groups` |
| Hidden memberships in new or small groups found, proposed design (of 42) | 14 | `e5.reranked.found in new or small groups` |
| The same, the hybrid | 8 | `e5.hybrid.found in new or small groups` |

## Key points: E6: do the hard rules hold (notebook 10)

| What | Value | Key in summary.json |
|---|---|---|
| Hard-rule violations, proposed design, all members | 0 | `e6.runs.Proposed design, all members.hard_violations` |
| Hard-rule violations, personalisation off, all members | 0 | `e6.runs.Personalisation off, all members.hard_violations` |
| Reasons checked | 26860 | `e6.fidelity.reasons` |
| Reasons faithful to the computed score | 26860 | `e6.fidelity.true` |
| Faults planted on purpose | 26 | `e6.faults.planted` |
| Faults caught | 26 | `e6.faults.caught` |
| Checks with a planted fault of their own (of 20) | 20 | `e6.faults.checks_with_a_fault` |
| Wrong reasons the checker found before the fix (young accounts down-weighted) | 916 | `e6.found_and_fixed.wrong reasons before the fix` |
| Test cases matching their answers | 13 | `e6.test_cases.match_expected` |

## Every number: The final design: every dial

| Key | Value | Source |
|---|---|---|
| `final.config.alpha` | 0.2 | `results/final_config.json`: config > alpha |
| `final.config.beta` | 0.2 | `results/final_config.json`: config > beta |
| `final.config.gamma` | 0.3 | `results/final_config.json`: config > gamma |
| `final.config.delta` | 0.3 | `results/final_config.json`: config > delta |
| `final.config.k` | 10 | `results/final_config.json`: config > k |
| `final.config.topic_weight` | 0 | `results/final_config.json`: config > topic_weight |
| `final.config.off_new_w` | 0.5 | `results/final_config.json`: config > off_new_w |
| `final.config.q` | 0.2 | `results/final_config.json`: config > q |
| `final.config.c` | 0.05 | `results/final_config.json`: config > c |
| `final.config.n` | 2 | `results/final_config.json`: config > n |
| `final.config.lam` | 0.8 | `results/final_config.json`: config > lam |
| `final.config.small_from` | r9 | `results/final_config.json`: config > small_from |
| `final.config.clusters` | 8 | `results/final_config.json`: config > clusters |
| `final.config.L` | 3 | `results/final_config.json`: config > L |
| `final.config.burst_w` | 0 | `results/final_config.json`: config > burst_w |
| `final.config.young_days` | 30 | `results/final_config.json`: config > young_days |
| `final.config.r9_scope` | all | `results/final_config.json`: config > r9_scope |
| `final.config.eps` | 1.5 | `results/final_config.json`: config > eps |
| `final.config.m` | 3 | `results/final_config.json`: config > m |
| `final.config.size_share` | 0.1 | `results/final_config.json`: config > size_share |
| `final.config.count_under_noise` | no | `results/final_config.json`: config > count_under_noise |

## Every number: The final design (notebook 11): the checks on the practice quiz, then the test

| Key | Value | Source |
|---|---|---|
| `final.quiz.rounds.1.clusters` | 8 | `results/final_rounds.csv`: row "1", column "clusters" |
| `final.quiz.rounds.1.m` | 3 | `results/final_rounds.csv`: row "1", column "m" |
| `final.quiz.rounds.1.size_share` | 0.1 | `results/final_rounds.csv`: row "1", column "size_share" |
| `final.quiz.rounds.1.eps` | 2 | `results/final_rounds.csv`: row "1", column "eps" |
| `final.quiz.rounds.1.accuracy kept low (eps)` | 0.9083 | `results/final_rounds.csv`: row "1", column "accuracy kept low (eps)" |
| `final.quiz.rounds.1.rank of the mix` | 14 | `results/final_rounds.csv`: row "1", column "rank of the mix" |
| `final.quiz.rounds.1.best minus the mix` | 0.0121 | `results/final_rounds.csv`: row "1", column "best minus the mix" |
| `final.quiz.rounds.1.best minus the mix, low` | 0.0062 | `results/final_rounds.csv`: row "1", column "best minus the mix, low" |
| `final.quiz.rounds.1.best minus the mix, high` | 0.018 | `results/final_rounds.csv`: row "1", column "best minus the mix, high" |
| `final.quiz.rounds.2.clusters` | 8 | `results/final_rounds.csv`: row "2", column "clusters" |
| `final.quiz.rounds.2.m` | 3 | `results/final_rounds.csv`: row "2", column "m" |
| `final.quiz.rounds.2.size_share` | 0.1 | `results/final_rounds.csv`: row "2", column "size_share" |
| `final.quiz.rounds.2.eps` | 1.5 | `results/final_rounds.csv`: row "2", column "eps" |
| `final.quiz.rounds.2.accuracy kept low (eps)` | 0.9192 | `results/final_rounds.csv`: row "2", column "accuracy kept low (eps)" |
| `final.quiz.rounds.2.rank of the mix` | 1 | `results/final_rounds.csv`: row "2", column "rank of the mix" |
| `final.quiz.rounds.2.best minus the mix` | 0 | `results/final_rounds.csv`: row "2", column "best minus the mix" |
| `final.quiz.rounds.2.best minus the mix, low` | 0 | `results/final_rounds.csv`: row "2", column "best minus the mix, low" |
| `final.quiz.rounds.2.best minus the mix, high` | 0 | `results/final_rounds.csv`: row "2", column "best minus the mix, high" |
| `final.quiz.clusters.5.ndcg@5` | 0.4382 | `results/final_topic_clusters.csv`: row "5", column "ndcg@5" |
| `final.quiz.clusters.5.share of the hybrid's NDCG@5` | 0.9474 | `results/final_topic_clusters.csv`: row "5", column "share of the hybrid's NDCG@5" |
| `final.quiz.clusters.5.lists with 3+ of one chosen topic` | 0.5626 | `results/final_topic_clusters.csv`: row "5", column "lists with 3+ of one chosen topic" |
| `final.quiz.clusters.8.ndcg@5` | 0.4423 | `results/final_topic_clusters.csv`: row "8", column "ndcg@5" |
| `final.quiz.clusters.8.share of the hybrid's NDCG@5` | 0.9561 | `results/final_topic_clusters.csv`: row "8", column "share of the hybrid's NDCG@5" |
| `final.quiz.clusters.8.lists with 3+ of one chosen topic` | 0.5828 | `results/final_topic_clusters.csv`: row "8", column "lists with 3+ of one chosen topic" |
| `final.quiz.clusters.10.ndcg@5` | 0.4413 | `results/final_topic_clusters.csv`: row "10", column "ndcg@5" |
| `final.quiz.clusters.10.share of the hybrid's NDCG@5` | 0.9539 | `results/final_topic_clusters.csv`: row "10", column "share of the hybrid's NDCG@5" |
| `final.quiz.clusters.10.lists with 3+ of one chosen topic` | 0.5851 | `results/final_topic_clusters.csv`: row "10", column "lists with 3+ of one chosen topic" |
| `final.quiz.clusters.15.ndcg@5` | 0.439 | `results/final_topic_clusters.csv`: row "15", column "ndcg@5" |
| `final.quiz.clusters.15.share of the hybrid's NDCG@5` | 0.949 | `results/final_topic_clusters.csv`: row "15", column "share of the hybrid's NDCG@5" |
| `final.quiz.clusters.15.lists with 3+ of one chosen topic` | 0.547 | `results/final_topic_clusters.csv`: row "15", column "lists with 3+ of one chosen topic" |
| `final.quiz.clusters.20.ndcg@5` | 0.4422 | `results/final_topic_clusters.csv`: row "20", column "ndcg@5" |
| `final.quiz.clusters.20.share of the hybrid's NDCG@5` | 0.9558 | `results/final_topic_clusters.csv`: row "20", column "share of the hybrid's NDCG@5" |
| `final.quiz.clusters.20.lists with 3+ of one chosen topic` | 0.5939 | `results/final_topic_clusters.csv`: row "20", column "lists with 3+ of one chosen topic" |
| `final.quiz.clusters.25.ndcg@5` | 0.4423 | `results/final_topic_clusters.csv`: row "25", column "ndcg@5" |
| `final.quiz.clusters.25.share of the hybrid's NDCG@5` | 0.9562 | `results/final_topic_clusters.csv`: row "25", column "share of the hybrid's NDCG@5" |
| `final.quiz.clusters.25.lists with 3+ of one chosen topic` | 0.5938 | `results/final_topic_clusters.csv`: row "25", column "lists with 3+ of one chosen topic" |
| `final.quiz.clusters.30.ndcg@5` | 0.4429 | `results/final_topic_clusters.csv`: row "30", column "ndcg@5" |
| `final.quiz.clusters.30.share of the hybrid's NDCG@5` | 0.9575 | `results/final_topic_clusters.csv`: row "30", column "share of the hybrid's NDCG@5" |
| `final.quiz.clusters.30.lists with 3+ of one chosen topic` | 0.6004 | `results/final_topic_clusters.csv`: row "30", column "lists with 3+ of one chosen topic" |
| `final.quiz.clusters.no topic cap (n = None).ndcg@5` | 0.4449 | `results/final_topic_clusters.csv`: row "no topic cap (n = None)", column "ndcg@5" |
| `final.quiz.clusters.no topic cap (n = None).share of the hybrid's NDCG@5` | 0.9618 | `results/final_topic_clusters.csv`: row "no topic cap (n = None)", column "share of the hybrid's NDCG@5" |
| `final.quiz.clusters.no topic cap (n = None).lists with 3+ of one chosen topic` | 0.6024 | `results/final_topic_clusters.csv`: row "no topic cap (n = None)", column "lists with 3+ of one chosen topic" |
| `final.quiz.clusters.10 from the AI model's tastes.ndcg@5` | 0.4264 | `results/final_topic_clusters.csv`: row "10 from the AI model's tastes", column "ndcg@5" |
| `final.quiz.clusters.10 from the AI model's tastes.share of the hybrid's NDCG@5` | 0.9218 | `results/final_topic_clusters.csv`: row "10 from the AI model's tastes", column "share of the hybrid's NDCG@5" |
| `final.quiz.clusters.10 from the AI model's tastes.lists with 3+ of one chosen topic` | 0.2015 | `results/final_topic_clusters.csv`: row "10 from the AI model's tastes", column "lists with 3+ of one chosen topic" |
| `final.quiz.grid.eps0.1_m3.ndcg@5` | 0.3137 | `results/final_validation.csv`: row "(0.1, 0.1, 3)", column "ndcg@5" |
| `final.quiz.grid.eps0.1_m3.newcomer_share` | 0.2541 | `results/final_validation.csv`: row "(0.1, 0.1, 3)", column "newcomer_share" |
| `final.quiz.grid.eps0.1_m3.accuracy kept` | 0.6873 | `results/final_validation.csv`: row "(0.1, 0.1, 3)", column "accuracy kept" |
| `final.quiz.grid.eps0.1_m3.newcomer slots kept` | 1.251 | `results/final_validation.csv`: row "(0.1, 0.1, 3)", column "newcomer slots kept" |
| `final.quiz.grid.eps0.5_m3.ndcg@5` | 0.3736 | `results/final_validation.csv`: row "(0.1, 0.5, 3)", column "ndcg@5" |
| `final.quiz.grid.eps0.5_m3.newcomer_share` | 0.2194 | `results/final_validation.csv`: row "(0.1, 0.5, 3)", column "newcomer_share" |
| `final.quiz.grid.eps0.5_m3.accuracy kept` | 0.8185 | `results/final_validation.csv`: row "(0.1, 0.5, 3)", column "accuracy kept" |
| `final.quiz.grid.eps0.5_m3.newcomer slots kept` | 1.08 | `results/final_validation.csv`: row "(0.1, 0.5, 3)", column "newcomer slots kept" |
| `final.quiz.grid.eps1_m3.ndcg@5` | 0.4192 | `results/final_validation.csv`: row "(0.1, 1.0, 3)", column "ndcg@5" |
| `final.quiz.grid.eps1_m3.newcomer_share` | 0.2106 | `results/final_validation.csv`: row "(0.1, 1.0, 3)", column "newcomer_share" |
| `final.quiz.grid.eps1_m3.accuracy kept` | 0.9185 | `results/final_validation.csv`: row "(0.1, 1.0, 3)", column "accuracy kept" |
| `final.quiz.grid.eps1_m3.newcomer slots kept` | 1.037 | `results/final_validation.csv`: row "(0.1, 1.0, 3)", column "newcomer slots kept" |
| `final.quiz.grid.eps2_m3.ndcg@5` | 0.4352 | `results/final_validation.csv`: row "(0.1, 2.0, 3)", column "ndcg@5" |
| `final.quiz.grid.eps2_m3.newcomer_share` | 0.208 | `results/final_validation.csv`: row "(0.1, 2.0, 3)", column "newcomer_share" |
| `final.quiz.grid.eps2_m3.accuracy kept` | 0.9535 | `results/final_validation.csv`: row "(0.1, 2.0, 3)", column "accuracy kept" |
| `final.quiz.grid.eps2_m3.newcomer slots kept` | 1.024 | `results/final_validation.csv`: row "(0.1, 2.0, 3)", column "newcomer slots kept" |
| `final.quiz.grid.eps5_m3.ndcg@5` | 0.4477 | `results/final_validation.csv`: row "(0.1, 5.0, 3)", column "ndcg@5" |
| `final.quiz.grid.eps5_m3.newcomer_share` | 0.2051 | `results/final_validation.csv`: row "(0.1, 5.0, 3)", column "newcomer_share" |
| `final.quiz.grid.eps5_m3.accuracy kept` | 0.9808 | `results/final_validation.csv`: row "(0.1, 5.0, 3)", column "accuracy kept" |
| `final.quiz.grid.eps5_m3.newcomer slots kept` | 1.01 | `results/final_validation.csv`: row "(0.1, 5.0, 3)", column "newcomer slots kept" |
| `final.quiz.eps.eps0.5.ndcg@5` | 0.3584 | `results/final_eps_fine.csv`: row "0.5", column "ndcg@5" |
| `final.quiz.eps.eps0.5.accuracy kept` | 0.8103 | `results/final_eps_fine.csv`: row "0.5", column "accuracy kept" |
| `final.quiz.eps.eps0.5.accuracy kept low` | 0.7954 | `results/final_eps_fine.csv`: row "0.5", column "accuracy kept low" |
| `final.quiz.eps.eps0.5.accuracy kept high` | 0.8252 | `results/final_eps_fine.csv`: row "0.5", column "accuracy kept high" |
| `final.quiz.eps.eps0.5.newcomer slots kept` | 1.086 | `results/final_eps_fine.csv`: row "0.5", column "newcomer slots kept" |
| `final.quiz.eps.eps0.5.newcomer slots kept low` | 1.077 | `results/final_eps_fine.csv`: row "0.5", column "newcomer slots kept low" |
| `final.quiz.eps.eps0.5.quizzes passing alone` | 0 | `results/final_eps_fine.csv`: row "0.5", column "quizzes passing alone" |
| `final.quiz.eps.eps0.5.single releases below 90%` | 1 | `results/final_eps_fine.csv`: row "0.5", column "single releases below 90%" |
| `final.quiz.eps.eps0.5.accuracy kept, quiz 0` | 0.8132 | `results/final_eps_fine.csv`: row "0.5", column "accuracy kept, quiz 0" |
| `final.quiz.eps.eps0.5.accuracy kept, quiz 1` | 0.7925 | `results/final_eps_fine.csv`: row "0.5", column "accuracy kept, quiz 1" |
| `final.quiz.eps.eps0.5.accuracy kept, quiz 2` | 0.816 | `results/final_eps_fine.csv`: row "0.5", column "accuracy kept, quiz 2" |
| `final.quiz.eps.eps0.5.accuracy kept, quiz 3` | 0.8242 | `results/final_eps_fine.csv`: row "0.5", column "accuracy kept, quiz 3" |
| `final.quiz.eps.eps0.5.accuracy kept, quiz 4` | 0.8054 | `results/final_eps_fine.csv`: row "0.5", column "accuracy kept, quiz 4" |
| `final.quiz.eps.eps1.ndcg@5` | 0.3967 | `results/final_eps_fine.csv`: row "1.0", column "ndcg@5" |
| `final.quiz.eps.eps1.accuracy kept` | 0.8969 | `results/final_eps_fine.csv`: row "1.0", column "accuracy kept" |
| `final.quiz.eps.eps1.accuracy kept low` | 0.8872 | `results/final_eps_fine.csv`: row "1.0", column "accuracy kept low" |
| `final.quiz.eps.eps1.accuracy kept high` | 0.9067 | `results/final_eps_fine.csv`: row "1.0", column "accuracy kept high" |
| `final.quiz.eps.eps1.newcomer slots kept` | 1.048 | `results/final_eps_fine.csv`: row "1.0", column "newcomer slots kept" |
| `final.quiz.eps.eps1.newcomer slots kept low` | 1.044 | `results/final_eps_fine.csv`: row "1.0", column "newcomer slots kept low" |
| `final.quiz.eps.eps1.quizzes passing alone` | 0 | `results/final_eps_fine.csv`: row "1.0", column "quizzes passing alone" |
| `final.quiz.eps.eps1.single releases below 90%` | 0.59 | `results/final_eps_fine.csv`: row "1.0", column "single releases below 90%" |
| `final.quiz.eps.eps1.accuracy kept, quiz 0` | 0.8986 | `results/final_eps_fine.csv`: row "1.0", column "accuracy kept, quiz 0" |
| `final.quiz.eps.eps1.accuracy kept, quiz 1` | 0.8886 | `results/final_eps_fine.csv`: row "1.0", column "accuracy kept, quiz 1" |
| `final.quiz.eps.eps1.accuracy kept, quiz 2` | 0.9035 | `results/final_eps_fine.csv`: row "1.0", column "accuracy kept, quiz 2" |
| `final.quiz.eps.eps1.accuracy kept, quiz 3` | 0.9051 | `results/final_eps_fine.csv`: row "1.0", column "accuracy kept, quiz 3" |
| `final.quiz.eps.eps1.accuracy kept, quiz 4` | 0.8889 | `results/final_eps_fine.csv`: row "1.0", column "accuracy kept, quiz 4" |
| `final.quiz.eps.eps1.5.ndcg@5` | 0.4107 | `results/final_eps_fine.csv`: row "1.5", column "ndcg@5" |
| `final.quiz.eps.eps1.5.accuracy kept` | 0.9284 | `results/final_eps_fine.csv`: row "1.5", column "accuracy kept" |
| `final.quiz.eps.eps1.5.accuracy kept low` | 0.9192 | `results/final_eps_fine.csv`: row "1.5", column "accuracy kept low" |
| `final.quiz.eps.eps1.5.accuracy kept high` | 0.9376 | `results/final_eps_fine.csv`: row "1.5", column "accuracy kept high" |
| `final.quiz.eps.eps1.5.newcomer slots kept` | 1.029 | `results/final_eps_fine.csv`: row "1.5", column "newcomer slots kept" |
| `final.quiz.eps.eps1.5.newcomer slots kept low` | 1.028 | `results/final_eps_fine.csv`: row "1.5", column "newcomer slots kept low" |
| `final.quiz.eps.eps1.5.quizzes passing alone` | 5 | `results/final_eps_fine.csv`: row "1.5", column "quizzes passing alone" |
| `final.quiz.eps.eps1.5.single releases below 90%` | 0.08 | `results/final_eps_fine.csv`: row "1.5", column "single releases below 90%" |
| `final.quiz.eps.eps1.5.accuracy kept, quiz 0` | 0.9352 | `results/final_eps_fine.csv`: row "1.5", column "accuracy kept, quiz 0" |
| `final.quiz.eps.eps1.5.accuracy kept, quiz 1` | 0.9232 | `results/final_eps_fine.csv`: row "1.5", column "accuracy kept, quiz 1" |
| `final.quiz.eps.eps1.5.accuracy kept, quiz 2` | 0.9315 | `results/final_eps_fine.csv`: row "1.5", column "accuracy kept, quiz 2" |
| `final.quiz.eps.eps1.5.accuracy kept, quiz 3` | 0.9341 | `results/final_eps_fine.csv`: row "1.5", column "accuracy kept, quiz 3" |
| `final.quiz.eps.eps1.5.accuracy kept, quiz 4` | 0.9182 | `results/final_eps_fine.csv`: row "1.5", column "accuracy kept, quiz 4" |
| `final.quiz.eps.eps2.ndcg@5` | 0.4176 | `results/final_eps_fine.csv`: row "2.0", column "ndcg@5" |
| `final.quiz.eps.eps2.accuracy kept` | 0.944 | `results/final_eps_fine.csv`: row "2.0", column "accuracy kept" |
| `final.quiz.eps.eps2.accuracy kept low` | 0.9355 | `results/final_eps_fine.csv`: row "2.0", column "accuracy kept low" |
| `final.quiz.eps.eps2.accuracy kept high` | 0.9525 | `results/final_eps_fine.csv`: row "2.0", column "accuracy kept high" |
| `final.quiz.eps.eps2.newcomer slots kept` | 1.023 | `results/final_eps_fine.csv`: row "2.0", column "newcomer slots kept" |
| `final.quiz.eps.eps2.newcomer slots kept low` | 1.022 | `results/final_eps_fine.csv`: row "2.0", column "newcomer slots kept low" |
| `final.quiz.eps.eps2.quizzes passing alone` | 5 | `results/final_eps_fine.csv`: row "2.0", column "quizzes passing alone" |
| `final.quiz.eps.eps2.single releases below 90%` | 0 | `results/final_eps_fine.csv`: row "2.0", column "single releases below 90%" |
| `final.quiz.eps.eps2.accuracy kept, quiz 0` | 0.9516 | `results/final_eps_fine.csv`: row "2.0", column "accuracy kept, quiz 0" |
| `final.quiz.eps.eps2.accuracy kept, quiz 1` | 0.942 | `results/final_eps_fine.csv`: row "2.0", column "accuracy kept, quiz 1" |
| `final.quiz.eps.eps2.accuracy kept, quiz 2` | 0.9442 | `results/final_eps_fine.csv`: row "2.0", column "accuracy kept, quiz 2" |
| `final.quiz.eps.eps2.accuracy kept, quiz 3` | 0.9485 | `results/final_eps_fine.csv`: row "2.0", column "accuracy kept, quiz 3" |
| `final.quiz.eps.eps2.accuracy kept, quiz 4` | 0.9338 | `results/final_eps_fine.csv`: row "2.0", column "accuracy kept, quiz 4" |
| `final.quiz.eps.eps2.5.ndcg@5` | 0.4219 | `results/final_eps_fine.csv`: row "2.5", column "ndcg@5" |
| `final.quiz.eps.eps2.5.accuracy kept` | 0.9538 | `results/final_eps_fine.csv`: row "2.5", column "accuracy kept" |
| `final.quiz.eps.eps2.5.accuracy kept low` | 0.9462 | `results/final_eps_fine.csv`: row "2.5", column "accuracy kept low" |
| `final.quiz.eps.eps2.5.accuracy kept high` | 0.9614 | `results/final_eps_fine.csv`: row "2.5", column "accuracy kept high" |
| `final.quiz.eps.eps2.5.newcomer slots kept` | 1.02 | `results/final_eps_fine.csv`: row "2.5", column "newcomer slots kept" |
| `final.quiz.eps.eps2.5.newcomer slots kept low` | 1.018 | `results/final_eps_fine.csv`: row "2.5", column "newcomer slots kept low" |
| `final.quiz.eps.eps2.5.quizzes passing alone` | 5 | `results/final_eps_fine.csv`: row "2.5", column "quizzes passing alone" |
| `final.quiz.eps.eps2.5.single releases below 90%` | 0 | `results/final_eps_fine.csv`: row "2.5", column "single releases below 90%" |
| `final.quiz.eps.eps2.5.accuracy kept, quiz 0` | 0.9613 | `results/final_eps_fine.csv`: row "2.5", column "accuracy kept, quiz 0" |
| `final.quiz.eps.eps2.5.accuracy kept, quiz 1` | 0.9506 | `results/final_eps_fine.csv`: row "2.5", column "accuracy kept, quiz 1" |
| `final.quiz.eps.eps2.5.accuracy kept, quiz 2` | 0.9536 | `results/final_eps_fine.csv`: row "2.5", column "accuracy kept, quiz 2" |
| `final.quiz.eps.eps2.5.accuracy kept, quiz 3` | 0.9578 | `results/final_eps_fine.csv`: row "2.5", column "accuracy kept, quiz 3" |
| `final.quiz.eps.eps2.5.accuracy kept, quiz 4` | 0.9455 | `results/final_eps_fine.csv`: row "2.5", column "accuracy kept, quiz 4" |
| `final.quiz.eps.eps3.ndcg@5` | 0.4243 | `results/final_eps_fine.csv`: row "3.0", column "ndcg@5" |
| `final.quiz.eps.eps3.accuracy kept` | 0.9593 | `results/final_eps_fine.csv`: row "3.0", column "accuracy kept" |
| `final.quiz.eps.eps3.accuracy kept low` | 0.9507 | `results/final_eps_fine.csv`: row "3.0", column "accuracy kept low" |
| `final.quiz.eps.eps3.accuracy kept high` | 0.968 | `results/final_eps_fine.csv`: row "3.0", column "accuracy kept high" |
| `final.quiz.eps.eps3.newcomer slots kept` | 1.018 | `results/final_eps_fine.csv`: row "3.0", column "newcomer slots kept" |
| `final.quiz.eps.eps3.newcomer slots kept low` | 1.016 | `results/final_eps_fine.csv`: row "3.0", column "newcomer slots kept low" |
| `final.quiz.eps.eps3.quizzes passing alone` | 5 | `results/final_eps_fine.csv`: row "3.0", column "quizzes passing alone" |
| `final.quiz.eps.eps3.single releases below 90%` | 0 | `results/final_eps_fine.csv`: row "3.0", column "single releases below 90%" |
| `final.quiz.eps.eps3.accuracy kept, quiz 0` | 0.9686 | `results/final_eps_fine.csv`: row "3.0", column "accuracy kept, quiz 0" |
| `final.quiz.eps.eps3.accuracy kept, quiz 1` | 0.9562 | `results/final_eps_fine.csv`: row "3.0", column "accuracy kept, quiz 1" |
| `final.quiz.eps.eps3.accuracy kept, quiz 2` | 0.9559 | `results/final_eps_fine.csv`: row "3.0", column "accuracy kept, quiz 2" |
| `final.quiz.eps.eps3.accuracy kept, quiz 3` | 0.9645 | `results/final_eps_fine.csv`: row "3.0", column "accuracy kept, quiz 3" |
| `final.quiz.eps.eps3.accuracy kept, quiz 4` | 0.9515 | `results/final_eps_fine.csv`: row "3.0", column "accuracy kept, quiz 4" |
| `final.quiz.eps.eps3.5.ndcg@5` | 0.4259 | `results/final_eps_fine.csv`: row "3.5", column "ndcg@5" |
| `final.quiz.eps.eps3.5.accuracy kept` | 0.9628 | `results/final_eps_fine.csv`: row "3.5", column "accuracy kept" |
| `final.quiz.eps.eps3.5.accuracy kept low` | 0.9552 | `results/final_eps_fine.csv`: row "3.5", column "accuracy kept low" |
| `final.quiz.eps.eps3.5.accuracy kept high` | 0.9704 | `results/final_eps_fine.csv`: row "3.5", column "accuracy kept high" |
| `final.quiz.eps.eps3.5.newcomer slots kept` | 1.016 | `results/final_eps_fine.csv`: row "3.5", column "newcomer slots kept" |
| `final.quiz.eps.eps3.5.newcomer slots kept low` | 1.014 | `results/final_eps_fine.csv`: row "3.5", column "newcomer slots kept low" |
| `final.quiz.eps.eps3.5.quizzes passing alone` | 5 | `results/final_eps_fine.csv`: row "3.5", column "quizzes passing alone" |
| `final.quiz.eps.eps3.5.single releases below 90%` | 0 | `results/final_eps_fine.csv`: row "3.5", column "single releases below 90%" |
| `final.quiz.eps.eps3.5.accuracy kept, quiz 0` | 0.9703 | `results/final_eps_fine.csv`: row "3.5", column "accuracy kept, quiz 0" |
| `final.quiz.eps.eps3.5.accuracy kept, quiz 1` | 0.9583 | `results/final_eps_fine.csv`: row "3.5", column "accuracy kept, quiz 1" |
| `final.quiz.eps.eps3.5.accuracy kept, quiz 2` | 0.96 | `results/final_eps_fine.csv`: row "3.5", column "accuracy kept, quiz 2" |
| `final.quiz.eps.eps3.5.accuracy kept, quiz 3` | 0.9683 | `results/final_eps_fine.csv`: row "3.5", column "accuracy kept, quiz 3" |
| `final.quiz.eps.eps3.5.accuracy kept, quiz 4` | 0.9569 | `results/final_eps_fine.csv`: row "3.5", column "accuracy kept, quiz 4" |
| `final.quiz.eps.eps4.ndcg@5` | 0.4271 | `results/final_eps_fine.csv`: row "4.0", column "ndcg@5" |
| `final.quiz.eps.eps4.accuracy kept` | 0.9657 | `results/final_eps_fine.csv`: row "4.0", column "accuracy kept" |
| `final.quiz.eps.eps4.accuracy kept low` | 0.9588 | `results/final_eps_fine.csv`: row "4.0", column "accuracy kept low" |
| `final.quiz.eps.eps4.accuracy kept high` | 0.9727 | `results/final_eps_fine.csv`: row "4.0", column "accuracy kept high" |
| `final.quiz.eps.eps4.newcomer slots kept` | 1.016 | `results/final_eps_fine.csv`: row "4.0", column "newcomer slots kept" |
| `final.quiz.eps.eps4.newcomer slots kept low` | 1.015 | `results/final_eps_fine.csv`: row "4.0", column "newcomer slots kept low" |
| `final.quiz.eps.eps4.quizzes passing alone` | 5 | `results/final_eps_fine.csv`: row "4.0", column "quizzes passing alone" |
| `final.quiz.eps.eps4.single releases below 90%` | 0 | `results/final_eps_fine.csv`: row "4.0", column "single releases below 90%" |
| `final.quiz.eps.eps4.accuracy kept, quiz 0` | 0.9722 | `results/final_eps_fine.csv`: row "4.0", column "accuracy kept, quiz 0" |
| `final.quiz.eps.eps4.accuracy kept, quiz 1` | 0.9623 | `results/final_eps_fine.csv`: row "4.0", column "accuracy kept, quiz 1" |
| `final.quiz.eps.eps4.accuracy kept, quiz 2` | 0.9616 | `results/final_eps_fine.csv`: row "4.0", column "accuracy kept, quiz 2" |
| `final.quiz.eps.eps4.accuracy kept, quiz 3` | 0.9714 | `results/final_eps_fine.csv`: row "4.0", column "accuracy kept, quiz 3" |
| `final.quiz.eps.eps4.accuracy kept, quiz 4` | 0.9611 | `results/final_eps_fine.csv`: row "4.0", column "accuracy kept, quiz 4" |
| `final.quiz.eps.eps5.ndcg@5` | 0.4288 | `results/final_eps_fine.csv`: row "5.0", column "ndcg@5" |
| `final.quiz.eps.eps5.accuracy kept` | 0.9694 | `results/final_eps_fine.csv`: row "5.0", column "accuracy kept" |
| `final.quiz.eps.eps5.accuracy kept low` | 0.9607 | `results/final_eps_fine.csv`: row "5.0", column "accuracy kept low" |
| `final.quiz.eps.eps5.accuracy kept high` | 0.9781 | `results/final_eps_fine.csv`: row "5.0", column "accuracy kept high" |
| `final.quiz.eps.eps5.newcomer slots kept` | 1.014 | `results/final_eps_fine.csv`: row "5.0", column "newcomer slots kept" |
| `final.quiz.eps.eps5.newcomer slots kept low` | 1.013 | `results/final_eps_fine.csv`: row "5.0", column "newcomer slots kept low" |
| `final.quiz.eps.eps5.quizzes passing alone` | 5 | `results/final_eps_fine.csv`: row "5.0", column "quizzes passing alone" |
| `final.quiz.eps.eps5.single releases below 90%` | 0 | `results/final_eps_fine.csv`: row "5.0", column "single releases below 90%" |
| `final.quiz.eps.eps5.accuracy kept, quiz 0` | 0.9771 | `results/final_eps_fine.csv`: row "5.0", column "accuracy kept, quiz 0" |
| `final.quiz.eps.eps5.accuracy kept, quiz 1` | 0.9668 | `results/final_eps_fine.csv`: row "5.0", column "accuracy kept, quiz 1" |
| `final.quiz.eps.eps5.accuracy kept, quiz 2` | 0.9615 | `results/final_eps_fine.csv`: row "5.0", column "accuracy kept, quiz 2" |
| `final.quiz.eps.eps5.accuracy kept, quiz 3` | 0.9766 | `results/final_eps_fine.csv`: row "5.0", column "accuracy kept, quiz 3" |
| `final.quiz.eps.eps5.accuracy kept, quiz 4` | 0.9652 | `results/final_eps_fine.csv`: row "5.0", column "accuracy kept, quiz 4" |
| `final.quiz.activity.none (activity as before: posts and likes, no noise).ndcg@5` | 0.0619 | `results/final_activity_privacy.csv`: row "none (activity as before: posts and likes, no noise)", column "ndcg@5" |
| `final.quiz.activity.none (activity as before: posts and likes, no noise).accuracy kept` | 1 | `results/final_activity_privacy.csv`: row "none (activity as before: posts and likes, no noise)", column "accuracy kept" |
| `final.quiz.activity.none (activity as before: posts and likes, no noise).accuracy kept low` | 1 | `results/final_activity_privacy.csv`: row "none (activity as before: posts and likes, no noise)", column "accuracy kept low" |
| `final.quiz.activity.none (activity as before: posts and likes, no noise).newcomer slots kept` | 1 | `results/final_activity_privacy.csv`: row "none (activity as before: posts and likes, no noise)", column "newcomer slots kept" |
| `final.quiz.activity.the definition alone (members who posted, clipped; no noise).ndcg@5` | 0.0336 | `results/final_activity_privacy.csv`: row "the definition alone (members who posted, clipped; no noise)", column "ndcg@5" |
| `final.quiz.activity.the definition alone (members who posted, clipped; no noise).accuracy kept` | 0.5437 | `results/final_activity_privacy.csv`: row "the definition alone (members who posted, clipped; no noise)", column "accuracy kept" |
| `final.quiz.activity.the definition alone (members who posted, clipped; no noise).accuracy kept low` | 0.5437 | `results/final_activity_privacy.csv`: row "the definition alone (members who posted, clipped; no noise)", column "accuracy kept low" |
| `final.quiz.activity.the definition alone (members who posted, clipped; no noise).newcomer slots kept` | 0.9652 | `results/final_activity_privacy.csv`: row "the definition alone (members who posted, clipped; no noise)", column "newcomer slots kept" |
| `final.quiz.activity.0.5.ndcg@5` | 0.0115 | `results/final_activity_privacy.csv`: row "0.5", column "ndcg@5" |
| `final.quiz.activity.0.5.accuracy kept` | 0.1855 | `results/final_activity_privacy.csv`: row "0.5", column "accuracy kept" |
| `final.quiz.activity.0.5.accuracy kept low` | 0.147 | `results/final_activity_privacy.csv`: row "0.5", column "accuracy kept low" |
| `final.quiz.activity.0.5.newcomer slots kept` | 1.389 | `results/final_activity_privacy.csv`: row "0.5", column "newcomer slots kept" |
| `final.quiz.activity.1.ndcg@5` | 0.0125 | `results/final_activity_privacy.csv`: row "1", column "ndcg@5" |
| `final.quiz.activity.1.accuracy kept` | 0.2012 | `results/final_activity_privacy.csv`: row "1", column "accuracy kept" |
| `final.quiz.activity.1.accuracy kept low` | 0.1673 | `results/final_activity_privacy.csv`: row "1", column "accuracy kept low" |
| `final.quiz.activity.1.newcomer slots kept` | 1.36 | `results/final_activity_privacy.csv`: row "1", column "newcomer slots kept" |
| `final.quiz.activity.2.ndcg@5` | 0.0214 | `results/final_activity_privacy.csv`: row "2", column "ndcg@5" |
| `final.quiz.activity.2.accuracy kept` | 0.3451 | `results/final_activity_privacy.csv`: row "2", column "accuracy kept" |
| `final.quiz.activity.2.accuracy kept low` | 0.2965 | `results/final_activity_privacy.csv`: row "2", column "accuracy kept low" |
| `final.quiz.activity.2.newcomer slots kept` | 1.183 | `results/final_activity_privacy.csv`: row "2", column "newcomer slots kept" |
| `final.quiz.activity.5.ndcg@5` | 0.0318 | `results/final_activity_privacy.csv`: row "5", column "ndcg@5" |
| `final.quiz.activity.5.accuracy kept` | 0.5133 | `results/final_activity_privacy.csv`: row "5", column "accuracy kept" |
| `final.quiz.activity.5.accuracy kept low` | 0.4546 | `results/final_activity_privacy.csv`: row "5", column "accuracy kept low" |
| `final.quiz.activity.5.newcomer slots kept` | 1.021 | `results/final_activity_privacy.csv`: row "5", column "newcomer slots kept" |
| `final.quiz.activity.10.ndcg@5` | 0.0337 | `results/final_activity_privacy.csv`: row "10", column "ndcg@5" |
| `final.quiz.activity.10.accuracy kept` | 0.5449 | `results/final_activity_privacy.csv`: row "10", column "accuracy kept" |
| `final.quiz.activity.10.accuracy kept low` | 0.4904 | `results/final_activity_privacy.csv`: row "10", column "accuracy kept low" |
| `final.quiz.activity.10.newcomer slots kept` | 0.9819 | `results/final_activity_privacy.csv`: row "10", column "newcomer slots kept" |
| `final.quiz.budget_share` | 0.9698 | `results/final_config.json`: checks on the practice quiz > E2's budget |
| `final.quiz.r9_cost` | 0.001107 | `results/final_config.json`: checks on the practice quiz > R9's NDCG@5 cost > cost |
| `final.quiz.weights.chosen_rank` | 1 | `results/final_weights.csv`: rank of the chosen mix |
| `final.quiz.weights.best_minus_chosen` | 0 | `results/final_config.json`: checks on the practice quiz > the hybrid's weights > best minus chosen |
| `final.test.popularity.users` | 1406 | `results/final_table.csv`: row "Popularity (BOING today)", column "users" |
| `final.test.popularity.runs` | 1 | `results/final_table.csv`: row "Popularity (BOING today)", column "runs" |
| `final.test.popularity.hit_rate` | 0.2205 | `results/final_table.csv`: row "Popularity (BOING today)", column "hit_rate" |
| `final.test.popularity.precision@5` | 0.0444 | `results/final_table.csv`: row "Popularity (BOING today)", column "precision@5" |
| `final.test.popularity.recall@5` | 0.207 | `results/final_table.csv`: row "Popularity (BOING today)", column "recall@5" |
| `final.test.popularity.ndcg@5` | 0.1311 | `results/final_table.csv`: row "Popularity (BOING today)", column "ndcg@5" |
| `final.test.popularity.ndcg@5 low` | 0.1174 | `results/final_table.csv`: row "Popularity (BOING today)", column "ndcg@5 low" |
| `final.test.popularity.ndcg@5 high` | 0.1455 | `results/final_table.csv`: row "Popularity (BOING today)", column "ndcg@5 high" |
| `final.test.popularity.newcomer_share` | 0 | `results/final_table.csv`: row "Popularity (BOING today)", column "newcomer_share" |
| `final.test.popularity.newcomer_share (members who count)` | 0 | `results/final_table.csv`: row "Popularity (BOING today)", column "newcomer_share (members who count)" |
| `final.test.popularity.gini` | 0.9534 | `results/final_table.csv`: row "Popularity (BOING today)", column "gini" |
| `final.test.popularity.coverage` | 10 | `results/final_table.csv`: row "Popularity (BOING today)", column "coverage" |
| `final.test.popularity.largest_share` | 0.1743 | `results/final_table.csv`: row "Popularity (BOING today)", column "largest_share" |
| `final.test.popularity.topics_per_list` | 3.228 | `results/final_table.csv`: row "Popularity (BOING today)", column "topics_per_list" |
| `final.test.popularity.diversity` | 0.9121 | `results/final_table.csv`: row "Popularity (BOING today)", column "diversity" |
| `final.test.popularity.lists below the quota (members who count)` | 1406 | `results/final_table.csv`: row "Popularity (BOING today)", column "lists below the quota (members who count)" |
| `final.test.popularity.lists below the quota (count Discover shows)` | 1406 | `results/final_table.csv`: row "Popularity (BOING today)", column "lists below the quota (count Discover shows)" |
| `final.test.popularity.lists with 3+ of one hidden topic` | 0.1067 | `results/final_table.csv`: row "Popularity (BOING today)", column "lists with 3+ of one hidden topic" |
| `final.test.also_joined.users` | 1406 | `results/final_table.csv`: row ""Also joined" (component)", column "users" |
| `final.test.also_joined.runs` | 1 | `results/final_table.csv`: row ""Also joined" (component)", column "runs" |
| `final.test.also_joined.hit_rate` | 0.6401 | `results/final_table.csv`: row ""Also joined" (component)", column "hit_rate" |
| `final.test.also_joined.precision@5` | 0.1356 | `results/final_table.csv`: row ""Also joined" (component)", column "precision@5" |
| `final.test.also_joined.recall@5` | 0.6213 | `results/final_table.csv`: row ""Also joined" (component)", column "recall@5" |
| `final.test.also_joined.ndcg@5` | 0.4988 | `results/final_table.csv`: row ""Also joined" (component)", column "ndcg@5" |
| `final.test.also_joined.ndcg@5 low` | 0.4762 | `results/final_table.csv`: row ""Also joined" (component)", column "ndcg@5 low" |
| `final.test.also_joined.ndcg@5 high` | 0.5219 | `results/final_table.csv`: row ""Also joined" (component)", column "ndcg@5 high" |
| `final.test.also_joined.newcomer_share` | 0.027 | `results/final_table.csv`: row ""Also joined" (component)", column "newcomer_share" |
| `final.test.also_joined.newcomer_share (members who count)` | 0.0273 | `results/final_table.csv`: row ""Also joined" (component)", column "newcomer_share (members who count)" |
| `final.test.also_joined.gini` | 0.5986 | `results/final_table.csv`: row ""Also joined" (component)", column "gini" |
| `final.test.also_joined.coverage` | 94 | `results/final_table.csv`: row ""Also joined" (component)", column "coverage" |
| `final.test.also_joined.largest_share` | 0.0309 | `results/final_table.csv`: row ""Also joined" (component)", column "largest_share" |
| `final.test.also_joined.topics_per_list` | 2.037 | `results/final_table.csv`: row ""Also joined" (component)", column "topics_per_list" |
| `final.test.also_joined.diversity` | 0.8814 | `results/final_table.csv`: row ""Also joined" (component)", column "diversity" |
| `final.test.also_joined.lists below the quota (members who count)` | 1260 | `results/final_table.csv`: row ""Also joined" (component)", column "lists below the quota (members who count)" |
| `final.test.also_joined.lists below the quota (count Discover shows)` | 1262 | `results/final_table.csv`: row ""Also joined" (component)", column "lists below the quota (count Discover shows)" |
| `final.test.also_joined.lists with 3+ of one hidden topic` | 0.857 | `results/final_table.csv`: row ""Also joined" (component)", column "lists with 3+ of one hidden topic" |
| `final.test.hidden_tastes.users` | 1406 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "users" |
| `final.test.hidden_tastes.runs` | 1 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "runs" |
| `final.test.hidden_tastes.hit_rate` | 0.6102 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "hit_rate" |
| `final.test.hidden_tastes.precision@5` | 0.1293 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "precision@5" |
| `final.test.hidden_tastes.recall@5` | 0.5914 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "recall@5" |
| `final.test.hidden_tastes.ndcg@5` | 0.4748 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "ndcg@5" |
| `final.test.hidden_tastes.ndcg@5 low` | 0.4525 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "ndcg@5 low" |
| `final.test.hidden_tastes.ndcg@5 high` | 0.4964 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "ndcg@5 high" |
| `final.test.hidden_tastes.newcomer_share` | 0.0051 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "newcomer_share" |
| `final.test.hidden_tastes.newcomer_share (members who count)` | 0.0051 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "newcomer_share (members who count)" |
| `final.test.hidden_tastes.gini` | 0.6448 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "gini" |
| `final.test.hidden_tastes.coverage` | 76 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "coverage" |
| `final.test.hidden_tastes.largest_share` | 0.0373 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "largest_share" |
| `final.test.hidden_tastes.topics_per_list` | 2.251 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "topics_per_list" |
| `final.test.hidden_tastes.diversity` | 0.8939 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "diversity" |
| `final.test.hidden_tastes.lists below the quota (members who count)` | 1370 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "lists below the quota (members who count)" |
| `final.test.hidden_tastes.lists below the quota (count Discover shows)` | 1370 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "lists below the quota (count Discover shows)" |
| `final.test.hidden_tastes.lists with 3+ of one hidden topic` | 0.7539 | `results/final_table.csv`: row "Hidden tastes, the AI model (component)", column "lists with 3+ of one hidden topic" |
| `final.test.hybrid.users` | 1406 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "users" |
| `final.test.hybrid.runs` | 1 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "runs" |
| `final.test.hybrid.hit_rate` | 0.6871 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "hit_rate" |
| `final.test.hybrid.precision@5` | 0.1457 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "precision@5" |
| `final.test.hybrid.recall@5` | 0.6682 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "recall@5" |
| `final.test.hybrid.ndcg@5` | 0.5407 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "ndcg@5" |
| `final.test.hybrid.ndcg@5 low` | 0.517 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "ndcg@5 low" |
| `final.test.hybrid.ndcg@5 high` | 0.5631 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "ndcg@5 high" |
| `final.test.hybrid.newcomer_share` | 0.0201 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "newcomer_share" |
| `final.test.hybrid.newcomer_share (members who count)` | 0.0206 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "newcomer_share (members who count)" |
| `final.test.hybrid.gini` | 0.6402 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "gini" |
| `final.test.hybrid.coverage` | 106 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "coverage" |
| `final.test.hybrid.largest_share` | 0.0377 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "largest_share" |
| `final.test.hybrid.topics_per_list` | 2.555 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "topics_per_list" |
| `final.test.hybrid.diversity` | 0.9008 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "diversity" |
| `final.test.hybrid.lists below the quota (members who count)` | 1280 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "lists below the quota (members who count)" |
| `final.test.hybrid.lists below the quota (count Discover shows)` | 1284 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "lists below the quota (count Discover shows)" |
| `final.test.hybrid.lists with 3+ of one hidden topic` | 0.6671 | `results/final_table.csv`: row "Hybrid, no re-ranking (component)", column "lists with 3+ of one hidden topic" |
| `final.test.e2.users` | 1406 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "users" |
| `final.test.e2.runs` | 1 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "runs" |
| `final.test.e2.hit_rate` | 0.6536 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "hit_rate" |
| `final.test.e2.precision@5` | 0.1374 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "precision@5" |
| `final.test.e2.recall@5` | 0.6319 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "recall@5" |
| `final.test.e2.ndcg@5` | 0.5257 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "ndcg@5" |
| `final.test.e2.ndcg@5 low` | 0.5015 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "ndcg@5 low" |
| `final.test.e2.ndcg@5 high` | 0.5489 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "ndcg@5 high" |
| `final.test.e2.newcomer_share` | 0.2009 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "newcomer_share" |
| `final.test.e2.newcomer_share (members who count)` | 0.2009 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "newcomer_share (members who count)" |
| `final.test.e2.gini` | 0.5229 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "gini" |
| `final.test.e2.coverage` | 126 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "coverage" |
| `final.test.e2.largest_share` | 0.032 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "largest_share" |
| `final.test.e2.topics_per_list` | 2.591 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "topics_per_list" |
| `final.test.e2.diversity` | 0.9495 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "diversity" |
| `final.test.e2.lists below the quota (members who count)` | 0 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "lists below the quota (members who count)" |
| `final.test.e2.lists below the quota (count Discover shows)` | 0 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "lists below the quota (count Discover shows)" |
| `final.test.e2.lists with 3+ of one hidden topic` | 0.6842 | `results/final_table.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "lists with 3+ of one hidden topic" |
| `final.test.e2_public.users` | 1406 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "users" |
| `final.test.e2_public.runs` | 1 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "runs" |
| `final.test.e2_public.hit_rate` | 0.643 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "hit_rate" |
| `final.test.e2_public.precision@5` | 0.1353 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "precision@5" |
| `final.test.e2_public.recall@5` | 0.6216 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "recall@5" |
| `final.test.e2_public.ndcg@5` | 0.5209 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "ndcg@5" |
| `final.test.e2_public.ndcg@5 low` | 0.4971 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "ndcg@5 low" |
| `final.test.e2_public.ndcg@5 high` | 0.5444 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "ndcg@5 high" |
| `final.test.e2_public.newcomer_share` | 0.201 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "newcomer_share" |
| `final.test.e2_public.newcomer_share (members who count)` | 0.201 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "newcomer_share (members who count)" |
| `final.test.e2_public.gini` | 0.5285 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "gini" |
| `final.test.e2_public.coverage` | 126 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "coverage" |
| `final.test.e2_public.largest_share` | 0.0326 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "largest_share" |
| `final.test.e2_public.topics_per_list` | 2.607 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "topics_per_list" |
| `final.test.e2_public.diversity` | 0.949 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "diversity" |
| `final.test.e2_public.lists below the quota (members who count)` | 0 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "lists below the quota (members who count)" |
| `final.test.e2_public.lists below the quota (count Discover shows)` | 0 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "lists below the quota (count Discover shows)" |
| `final.test.e2_public.lists with 3+ of one hidden topic` | 0.6707 | `results/final_table.csv`: row "E2 dials, "small" from the count Discover shows, final clusters", column "lists with 3+ of one hidden topic" |
| `final.test.e2_w.users` | 1406 | `results/final_table.csv`: row "The same with the final weights", column "users" |
| `final.test.e2_w.runs` | 1 | `results/final_table.csv`: row "The same with the final weights", column "runs" |
| `final.test.e2_w.hit_rate` | 0.6444 | `results/final_table.csv`: row "The same with the final weights", column "hit_rate" |
| `final.test.e2_w.precision@5` | 0.135 | `results/final_table.csv`: row "The same with the final weights", column "precision@5" |
| `final.test.e2_w.recall@5` | 0.622 | `results/final_table.csv`: row "The same with the final weights", column "recall@5" |
| `final.test.e2_w.ndcg@5` | 0.519 | `results/final_table.csv`: row "The same with the final weights", column "ndcg@5" |
| `final.test.e2_w.ndcg@5 low` | 0.4954 | `results/final_table.csv`: row "The same with the final weights", column "ndcg@5 low" |
| `final.test.e2_w.ndcg@5 high` | 0.5422 | `results/final_table.csv`: row "The same with the final weights", column "ndcg@5 high" |
| `final.test.e2_w.newcomer_share` | 0.2034 | `results/final_table.csv`: row "The same with the final weights", column "newcomer_share" |
| `final.test.e2_w.newcomer_share (members who count)` | 0.2037 | `results/final_table.csv`: row "The same with the final weights", column "newcomer_share (members who count)" |
| `final.test.e2_w.gini` | 0.497 | `results/final_table.csv`: row "The same with the final weights", column "gini" |
| `final.test.e2_w.coverage` | 127 | `results/final_table.csv`: row "The same with the final weights", column "coverage" |
| `final.test.e2_w.largest_share` | 0.032 | `results/final_table.csv`: row "The same with the final weights", column "largest_share" |
| `final.test.e2_w.topics_per_list` | 2.639 | `results/final_table.csv`: row "The same with the final weights", column "topics_per_list" |
| `final.test.e2_w.diversity` | 0.9438 | `results/final_table.csv`: row "The same with the final weights", column "diversity" |
| `final.test.e2_w.lists below the quota (members who count)` | 0 | `results/final_table.csv`: row "The same with the final weights", column "lists below the quota (members who count)" |
| `final.test.e2_w.lists below the quota (count Discover shows)` | 0 | `results/final_table.csv`: row "The same with the final weights", column "lists below the quota (count Discover shows)" |
| `final.test.e2_w.lists with 3+ of one hidden topic` | 0.6721 | `results/final_table.csv`: row "The same with the final weights", column "lists with 3+ of one hidden topic" |
| `final.test.exact.users` | 1406 | `results/final_table.csv`: row "Final design without privacy", column "users" |
| `final.test.exact.runs` | 1 | `results/final_table.csv`: row "Final design without privacy", column "runs" |
| `final.test.exact.hit_rate` | 0.6373 | `results/final_table.csv`: row "Final design without privacy", column "hit_rate" |
| `final.test.exact.precision@5` | 0.1337 | `results/final_table.csv`: row "Final design without privacy", column "precision@5" |
| `final.test.exact.recall@5` | 0.6156 | `results/final_table.csv`: row "Final design without privacy", column "recall@5" |
| `final.test.exact.ndcg@5` | 0.5146 | `results/final_table.csv`: row "Final design without privacy", column "ndcg@5" |
| `final.test.exact.ndcg@5 low` | 0.491 | `results/final_table.csv`: row "Final design without privacy", column "ndcg@5 low" |
| `final.test.exact.ndcg@5 high` | 0.5386 | `results/final_table.csv`: row "Final design without privacy", column "ndcg@5 high" |
| `final.test.exact.newcomer_share` | 0.1974 | `results/final_table.csv`: row "Final design without privacy", column "newcomer_share" |
| `final.test.exact.newcomer_share (members who count)` | 0.2043 | `results/final_table.csv`: row "Final design without privacy", column "newcomer_share (members who count)" |
| `final.test.exact.gini` | 0.4946 | `results/final_table.csv`: row "Final design without privacy", column "gini" |
| `final.test.exact.coverage` | 127 | `results/final_table.csv`: row "Final design without privacy", column "coverage" |
| `final.test.exact.largest_share` | 0.0319 | `results/final_table.csv`: row "Final design without privacy", column "largest_share" |
| `final.test.exact.topics_per_list` | 2.635 | `results/final_table.csv`: row "Final design without privacy", column "topics_per_list" |
| `final.test.exact.diversity` | 0.942 | `results/final_table.csv`: row "Final design without privacy", column "diversity" |
| `final.test.exact.lists below the quota (members who count)` | 0 | `results/final_table.csv`: row "Final design without privacy", column "lists below the quota (members who count)" |
| `final.test.exact.lists below the quota (count Discover shows)` | 47 | `results/final_table.csv`: row "Final design without privacy", column "lists below the quota (count Discover shows)" |
| `final.test.exact.lists with 3+ of one hidden topic` | 0.6764 | `results/final_table.csv`: row "Final design without privacy", column "lists with 3+ of one hidden topic" |
| `final.test.clip.users` | 1406 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "users" |
| `final.test.clip.runs` | 1 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "runs" |
| `final.test.clip.hit_rate` | 0.6287 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "hit_rate" |
| `final.test.clip.precision@5` | 0.1317 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "precision@5" |
| `final.test.clip.recall@5` | 0.6067 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "recall@5" |
| `final.test.clip.ndcg@5` | 0.5015 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "ndcg@5" |
| `final.test.clip.ndcg@5 low` | 0.4781 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "ndcg@5 low" |
| `final.test.clip.ndcg@5 high` | 0.5241 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "ndcg@5 high" |
| `final.test.clip.newcomer_share` | 0.1979 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "newcomer_share" |
| `final.test.clip.newcomer_share (members who count)` | 0.203 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "newcomer_share (members who count)" |
| `final.test.clip.gini` | 0.5217 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "gini" |
| `final.test.clip.coverage` | 128 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "coverage" |
| `final.test.clip.largest_share` | 0.0361 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "largest_share" |
| `final.test.clip.topics_per_list` | 2.795 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "topics_per_list" |
| `final.test.clip.diversity` | 0.9463 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "diversity" |
| `final.test.clip.lists below the quota (members who count)` | 0 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "lists below the quota (members who count)" |
| `final.test.clip.lists below the quota (count Discover shows)` | 34 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "lists below the quota (count Discover shows)" |
| `final.test.clip.lists with 3+ of one hidden topic` | 0.6053 | `results/final_table.csv`: row "Final design, clipping only (test cases)", column "lists with 3+ of one hidden topic" |
| `final.test.final.users` | 1406 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "users" |
| `final.test.final.runs` | 10 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "runs" |
| `final.test.final.hit_rate` | 0.6132 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "hit_rate" |
| `final.test.final.precision@5` | 0.1278 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "precision@5" |
| `final.test.final.recall@5` | 0.591 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "recall@5" |
| `final.test.final.ndcg@5` | 0.4882 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "ndcg@5" |
| `final.test.final.ndcg@5 low` | 0.466 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "ndcg@5 low" |
| `final.test.final.ndcg@5 high` | 0.5095 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "ndcg@5 high" |
| `final.test.final.ndcg@5 sd` | 0.0084 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "ndcg@5 sd" |
| `final.test.final.newcomer_share` | 0.1994 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "newcomer_share" |
| `final.test.final.newcomer_share sd` | 0.0051 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "newcomer_share sd" |
| `final.test.final.newcomer_share (members who count)` | 0.2078 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "newcomer_share (members who count)" |
| `final.test.final.gini` | 0.5319 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "gini" |
| `final.test.final.coverage` | 127.1 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "coverage" |
| `final.test.final.largest_share` | 0.0356 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "largest_share" |
| `final.test.final.topics_per_list` | 3.135 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "topics_per_list" |
| `final.test.final.diversity` | 0.9514 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "diversity" |
| `final.test.final.lists below the quota (members who count)` | 0 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "lists below the quota (members who count)" |
| `final.test.final.lists below the quota (count Discover shows)` | 55.2 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "lists below the quota (count Discover shows)" |
| `final.test.final.lists with 3+ of one hidden topic` | 0.4654 | `results/final_table.csv`: row "Final design (ε = 1.5, m = 3)", column "lists with 3+ of one hidden topic" |
| `final.test.eps05.users` | 1406 | `results/final_table.csv`: row "Final design with ε = 0.5", column "users" |
| `final.test.eps05.runs` | 10 | `results/final_table.csv`: row "Final design with ε = 0.5", column "runs" |
| `final.test.eps05.hit_rate` | 0.5572 | `results/final_table.csv`: row "Final design with ε = 0.5", column "hit_rate" |
| `final.test.eps05.precision@5` | 0.1153 | `results/final_table.csv`: row "Final design with ε = 0.5", column "precision@5" |
| `final.test.eps05.recall@5` | 0.5351 | `results/final_table.csv`: row "Final design with ε = 0.5", column "recall@5" |
| `final.test.eps05.ndcg@5` | 0.4364 | `results/final_table.csv`: row "Final design with ε = 0.5", column "ndcg@5" |
| `final.test.eps05.ndcg@5 low` | 0.4163 | `results/final_table.csv`: row "Final design with ε = 0.5", column "ndcg@5 low" |
| `final.test.eps05.ndcg@5 high` | 0.4569 | `results/final_table.csv`: row "Final design with ε = 0.5", column "ndcg@5 high" |
| `final.test.eps05.ndcg@5 sd` | 0.0104 | `results/final_table.csv`: row "Final design with ε = 0.5", column "ndcg@5 sd" |
| `final.test.eps05.newcomer_share` | 0.2065 | `results/final_table.csv`: row "Final design with ε = 0.5", column "newcomer_share" |
| `final.test.eps05.newcomer_share sd` | 0.008 | `results/final_table.csv`: row "Final design with ε = 0.5", column "newcomer_share sd" |
| `final.test.eps05.newcomer_share (members who count)` | 0.2145 | `results/final_table.csv`: row "Final design with ε = 0.5", column "newcomer_share (members who count)" |
| `final.test.eps05.gini` | 0.5725 | `results/final_table.csv`: row "Final design with ε = 0.5", column "gini" |
| `final.test.eps05.coverage` | 125.2 | `results/final_table.csv`: row "Final design with ε = 0.5", column "coverage" |
| `final.test.eps05.largest_share` | 0.0418 | `results/final_table.csv`: row "Final design with ε = 0.5", column "largest_share" |
| `final.test.eps05.topics_per_list` | 3.47 | `results/final_table.csv`: row "Final design with ε = 0.5", column "topics_per_list" |
| `final.test.eps05.diversity` | 0.9574 | `results/final_table.csv`: row "Final design with ε = 0.5", column "diversity" |
| `final.test.eps05.lists below the quota (members who count)` | 0 | `results/final_table.csv`: row "Final design with ε = 0.5", column "lists below the quota (members who count)" |
| `final.test.eps05.lists below the quota (count Discover shows)` | 51.4 | `results/final_table.csv`: row "Final design with ε = 0.5", column "lists below the quota (count Discover shows)" |
| `final.test.eps05.lists with 3+ of one hidden topic` | 0.3231 | `results/final_table.csv`: row "Final design with ε = 0.5", column "lists with 3+ of one hidden topic" |
| `final.test.eps2.users` | 1406 | `results/final_table.csv`: row "Final design with ε = 2", column "users" |
| `final.test.eps2.runs` | 10 | `results/final_table.csv`: row "Final design with ε = 2", column "runs" |
| `final.test.eps2.hit_rate` | 0.6177 | `results/final_table.csv`: row "Final design with ε = 2", column "hit_rate" |
| `final.test.eps2.precision@5` | 0.1291 | `results/final_table.csv`: row "Final design with ε = 2", column "precision@5" |
| `final.test.eps2.recall@5` | 0.5959 | `results/final_table.csv`: row "Final design with ε = 2", column "recall@5" |
| `final.test.eps2.ndcg@5` | 0.4929 | `results/final_table.csv`: row "Final design with ε = 2", column "ndcg@5" |
| `final.test.eps2.ndcg@5 low` | 0.4709 | `results/final_table.csv`: row "Final design with ε = 2", column "ndcg@5 low" |
| `final.test.eps2.ndcg@5 high` | 0.5143 | `results/final_table.csv`: row "Final design with ε = 2", column "ndcg@5 high" |
| `final.test.eps2.ndcg@5 sd` | 0.0077 | `results/final_table.csv`: row "Final design with ε = 2", column "ndcg@5 sd" |
| `final.test.eps2.newcomer_share` | 0.1998 | `results/final_table.csv`: row "Final design with ε = 2", column "newcomer_share" |
| `final.test.eps2.newcomer_share sd` | 0.0038 | `results/final_table.csv`: row "Final design with ε = 2", column "newcomer_share sd" |
| `final.test.eps2.newcomer_share (members who count)` | 0.2077 | `results/final_table.csv`: row "Final design with ε = 2", column "newcomer_share (members who count)" |
| `final.test.eps2.gini` | 0.5255 | `results/final_table.csv`: row "Final design with ε = 2", column "gini" |
| `final.test.eps2.coverage` | 127.2 | `results/final_table.csv`: row "Final design with ε = 2", column "coverage" |
| `final.test.eps2.largest_share` | 0.0352 | `results/final_table.csv`: row "Final design with ε = 2", column "largest_share" |
| `final.test.eps2.topics_per_list` | 3.076 | `results/final_table.csv`: row "Final design with ε = 2", column "topics_per_list" |
| `final.test.eps2.diversity` | 0.9502 | `results/final_table.csv`: row "Final design with ε = 2", column "diversity" |
| `final.test.eps2.lists below the quota (members who count)` | 0 | `results/final_table.csv`: row "Final design with ε = 2", column "lists below the quota (members who count)" |
| `final.test.eps2.lists below the quota (count Discover shows)` | 52.8 | `results/final_table.csv`: row "Final design with ε = 2", column "lists below the quota (count Discover shows)" |
| `final.test.eps2.lists with 3+ of one hidden topic` | 0.4906 | `results/final_table.csv`: row "Final design with ε = 2", column "lists with 3+ of one hidden topic" |
| `final.test.eps5.users` | 1406 | `results/final_table.csv`: row "Final design with ε = 5", column "users" |
| `final.test.eps5.runs` | 10 | `results/final_table.csv`: row "Final design with ε = 5", column "runs" |
| `final.test.eps5.hit_rate` | 0.6265 | `results/final_table.csv`: row "Final design with ε = 5", column "hit_rate" |
| `final.test.eps5.precision@5` | 0.131 | `results/final_table.csv`: row "Final design with ε = 5", column "precision@5" |
| `final.test.eps5.recall@5` | 0.6043 | `results/final_table.csv`: row "Final design with ε = 5", column "recall@5" |
| `final.test.eps5.ndcg@5` | 0.4974 | `results/final_table.csv`: row "Final design with ε = 5", column "ndcg@5" |
| `final.test.eps5.ndcg@5 low` | 0.4748 | `results/final_table.csv`: row "Final design with ε = 5", column "ndcg@5 low" |
| `final.test.eps5.ndcg@5 high` | 0.5191 | `results/final_table.csv`: row "Final design with ε = 5", column "ndcg@5 high" |
| `final.test.eps5.ndcg@5 sd` | 0.0038 | `results/final_table.csv`: row "Final design with ε = 5", column "ndcg@5 sd" |
| `final.test.eps5.newcomer_share` | 0.1979 | `results/final_table.csv`: row "Final design with ε = 5", column "newcomer_share" |
| `final.test.eps5.newcomer_share sd` | 0.0038 | `results/final_table.csv`: row "Final design with ε = 5", column "newcomer_share sd" |
| `final.test.eps5.newcomer_share (members who count)` | 0.205 | `results/final_table.csv`: row "Final design with ε = 5", column "newcomer_share (members who count)" |
| `final.test.eps5.gini` | 0.5139 | `results/final_table.csv`: row "Final design with ε = 5", column "gini" |
| `final.test.eps5.coverage` | 127.9 | `results/final_table.csv`: row "Final design with ε = 5", column "coverage" |
| `final.test.eps5.largest_share` | 0.0343 | `results/final_table.csv`: row "Final design with ε = 5", column "largest_share" |
| `final.test.eps5.topics_per_list` | 2.915 | `results/final_table.csv`: row "Final design with ε = 5", column "topics_per_list" |
| `final.test.eps5.diversity` | 0.948 | `results/final_table.csv`: row "Final design with ε = 5", column "diversity" |
| `final.test.eps5.lists below the quota (members who count)` | 0 | `results/final_table.csv`: row "Final design with ε = 5", column "lists below the quota (members who count)" |
| `final.test.eps5.lists below the quota (count Discover shows)` | 48.8 | `results/final_table.csv`: row "Final design with ε = 5", column "lists below the quota (count Discover shows)" |
| `final.test.eps5.lists with 3+ of one hidden topic` | 0.5631 | `results/final_table.csv`: row "Final design with ε = 5", column "lists with 3+ of one hidden topic" |
| `final.test.before.users` | 1406 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "users" |
| `final.test.before.runs` | 10 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "runs" |
| `final.test.before.hit_rate` | 0.6399 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "hit_rate" |
| `final.test.before.precision@5` | 0.134 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "precision@5" |
| `final.test.before.recall@5` | 0.6179 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "recall@5" |
| `final.test.before.ndcg@5` | 0.5104 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "ndcg@5" |
| `final.test.before.ndcg@5 low` | 0.4877 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "ndcg@5 low" |
| `final.test.before.ndcg@5 high` | 0.5324 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "ndcg@5 high" |
| `final.test.before.ndcg@5 sd` | 0.0035 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "ndcg@5 sd" |
| `final.test.before.newcomer_share` | 0.1581 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "newcomer_share" |
| `final.test.before.newcomer_share sd` | 0.0173 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "newcomer_share sd" |
| `final.test.before.newcomer_share (members who count)` | 0.1625 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "newcomer_share (members who count)" |
| `final.test.before.gini` | 0.5141 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "gini" |
| `final.test.before.coverage` | 124.5 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "coverage" |
| `final.test.before.largest_share` | 0.033 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "largest_share" |
| `final.test.before.topics_per_list` | 3.08 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "topics_per_list" |
| `final.test.before.diversity` | 0.9542 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "diversity" |
| `final.test.before.lists below the quota (members who count)` | 443.5 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "lists below the quota (members who count)" |
| `final.test.before.lists below the quota (count Discover shows)` | 470.4 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "lists below the quota (count Discover shows)" |
| `final.test.before.lists with 3+ of one hidden topic` | 0.4814 | `results/final_table.csv`: row "Final design before the review (ε = 5)", column "lists with 3+ of one hidden topic" |
| `final.test.off.users` | 1406 | `results/final_table.csv`: row "Personalisation off (default list)", column "users" |
| `final.test.off.runs` | 10 | `results/final_table.csv`: row "Personalisation off (default list)", column "runs" |
| `final.test.off.hit_rate` | 0.1046 | `results/final_table.csv`: row "Personalisation off (default list)", column "hit_rate" |
| `final.test.off.precision@5` | 0.0211 | `results/final_table.csv`: row "Personalisation off (default list)", column "precision@5" |
| `final.test.off.recall@5` | 0.0978 | `results/final_table.csv`: row "Personalisation off (default list)", column "recall@5" |
| `final.test.off.ndcg@5` | 0.0584 | `results/final_table.csv`: row "Personalisation off (default list)", column "ndcg@5" |
| `final.test.off.ndcg@5 low` | 0.0491 | `results/final_table.csv`: row "Personalisation off (default list)", column "ndcg@5 low" |
| `final.test.off.ndcg@5 high` | 0.0681 | `results/final_table.csv`: row "Personalisation off (default list)", column "ndcg@5 high" |
| `final.test.off.ndcg@5 sd` | 0 | `results/final_table.csv`: row "Personalisation off (default list)", column "ndcg@5 sd" |
| `final.test.off.newcomer_share` | 0.4413 | `results/final_table.csv`: row "Personalisation off (default list)", column "newcomer_share" |
| `final.test.off.newcomer_share sd` | 0 | `results/final_table.csv`: row "Personalisation off (default list)", column "newcomer_share sd" |
| `final.test.off.newcomer_share (members who count)` | 0.4413 | `results/final_table.csv`: row "Personalisation off (default list)", column "newcomer_share (members who count)" |
| `final.test.off.gini` | 0.8434 | `results/final_table.csv`: row "Personalisation off (default list)", column "gini" |
| `final.test.off.coverage` | 23 | `results/final_table.csv`: row "Personalisation off (default list)", column "coverage" |
| `final.test.off.largest_share` | 0.0499 | `results/final_table.csv`: row "Personalisation off (default list)", column "largest_share" |
| `final.test.off.topics_per_list` | 4.245 | `results/final_table.csv`: row "Personalisation off (default list)", column "topics_per_list" |
| `final.test.off.diversity` | 0.9727 | `results/final_table.csv`: row "Personalisation off (default list)", column "diversity" |
| `final.test.off.lists below the quota (members who count)` | 0 | `results/final_table.csv`: row "Personalisation off (default list)", column "lists below the quota (members who count)" |
| `final.test.off.lists below the quota (count Discover shows)` | 0 | `results/final_table.csv`: row "Personalisation off (default list)", column "lists below the quota (count Discover shows)" |
| `final.test.off.lists with 3+ of one hidden topic` | 0.0071 | `results/final_table.csv`: row "Personalisation off (default list)", column "lists with 3+ of one hidden topic" |
| `final.reachable.hidden memberships` | 1531 | `results/final_reachable.json`: hidden memberships |
| `final.reachable.out of reach (closed or hidden groups)` | 79 | `results/final_reachable.json`: out of reach (closed or hidden groups) |
| `final.reachable.members` | 1406 | `results/final_reachable.json`: members |
| `final.reachable.members whose hidden groups are all out of reach` | 66 | `results/final_reachable.json`: members whose hidden groups are all out of reach |
| `final.reachable.best possible hit rate` | 0.9531 | `results/final_reachable.json`: best possible hit rate |
| `final.cost.step1.ndcg@5 before` | 0.1311 | `results/final_costs.csv`: row "Personalisation: today's BOING -> the hybrid", column "ndcg@5 before" |
| `final.cost.step1.ndcg@5 after` | 0.5407 | `results/final_costs.csv`: row "Personalisation: today's BOING -> the hybrid", column "ndcg@5 after" |
| `final.cost.step1.cost` | -0.4096 | `results/final_costs.csv`: row "Personalisation: today's BOING -> the hybrid", column "cost" |
| `final.cost.step1.cost low` | -0.4337 | `results/final_costs.csv`: row "Personalisation: today's BOING -> the hybrid", column "cost low" |
| `final.cost.step1.cost high` | -0.3848 | `results/final_costs.csv`: row "Personalisation: today's BOING -> the hybrid", column "cost high" |
| `final.cost.step1.relative cost` | -3.123 | `results/final_costs.csv`: row "Personalisation: today's BOING -> the hybrid", column "relative cost" |
| `final.cost.step2.ndcg@5 before` | 0.5407 | `results/final_costs.csv`: row "Fair exposure and variety (R4, R5: q, c, n, lambda)", column "ndcg@5 before" |
| `final.cost.step2.ndcg@5 after` | 0.5257 | `results/final_costs.csv`: row "Fair exposure and variety (R4, R5: q, c, n, lambda)", column "ndcg@5 after" |
| `final.cost.step2.cost` | 0.01497 | `results/final_costs.csv`: row "Fair exposure and variety (R4, R5: q, c, n, lambda)", column "cost" |
| `final.cost.step2.cost low` | 0.009592 | `results/final_costs.csv`: row "Fair exposure and variety (R4, R5: q, c, n, lambda)", column "cost low" |
| `final.cost.step2.cost high` | 0.02026 | `results/final_costs.csv`: row "Fair exposure and variety (R4, R5: q, c, n, lambda)", column "cost high" |
| `final.cost.step2.relative cost` | 0.02768 | `results/final_costs.csv`: row "Fair exposure and variety (R4, R5: q, c, n, lambda)", column "relative cost" |
| `final.cost.step3.ndcg@5 before` | 0.5257 | `results/final_costs.csv`: row ""Small" from the member count Discover shows (and 8 topic clusters)", column "ndcg@5 before" |
| `final.cost.step3.ndcg@5 after` | 0.5209 | `results/final_costs.csv`: row ""Small" from the member count Discover shows (and 8 topic clusters)", column "ndcg@5 after" |
| `final.cost.step3.cost` | 0.004772 | `results/final_costs.csv`: row ""Small" from the member count Discover shows (and 8 topic clusters)", column "cost" |
| `final.cost.step3.cost low` | 0.002193 | `results/final_costs.csv`: row ""Small" from the member count Discover shows (and 8 topic clusters)", column "cost low" |
| `final.cost.step3.cost high` | 0.00749 | `results/final_costs.csv`: row ""Small" from the member count Discover shows (and 8 topic clusters)", column "cost high" |
| `final.cost.step3.relative cost` | 0.009077 | `results/final_costs.csv`: row ""Small" from the member count Discover shows (and 8 topic clusters)", column "relative cost" |
| `final.cost.step4.ndcg@5 before` | 0.5209 | `results/final_costs.csv`: row "The weights re-chosen for noisy statistics (0.2, 0.2, 0.3, 0.3), here without noise", column "ndcg@5 before" |
| `final.cost.step4.ndcg@5 after` | 0.519 | `results/final_costs.csv`: row "The weights re-chosen for noisy statistics (0.2, 0.2, 0.3, 0.3), here without noise", column "ndcg@5 after" |
| `final.cost.step4.cost` | 0.001976 | `results/final_costs.csv`: row "The weights re-chosen for noisy statistics (0.2, 0.2, 0.3, 0.3), here without noise", column "cost" |
| `final.cost.step4.cost low` | -0.004393 | `results/final_costs.csv`: row "The weights re-chosen for noisy statistics (0.2, 0.2, 0.3, 0.3), here without noise", column "cost low" |
| `final.cost.step4.cost high` | 0.0082 | `results/final_costs.csv`: row "The weights re-chosen for noisy statistics (0.2, 0.2, 0.3, 0.3), here without noise", column "cost high" |
| `final.cost.step4.relative cost` | 0.003794 | `results/final_costs.csv`: row "The weights re-chosen for noisy statistics (0.2, 0.2, 0.3, 0.3), here without noise", column "relative cost" |
| `final.cost.step5.ndcg@5 before` | 0.519 | `results/final_costs.csv`: row "Fake-account resistance (R9: L = 3, young accounts wait 30 days; joins, posts, likes, friends and the "small" count)", column "ndcg@5 before" |
| `final.cost.step5.ndcg@5 after` | 0.5146 | `results/final_costs.csv`: row "Fake-account resistance (R9: L = 3, young accounts wait 30 days; joins, posts, likes, friends and the "small" count)", column "ndcg@5 after" |
| `final.cost.step5.cost` | 0.004324 | `results/final_costs.csv`: row "Fake-account resistance (R9: L = 3, young accounts wait 30 days; joins, posts, likes, friends and the "small" count)", column "cost" |
| `final.cost.step5.cost low` | -0.002642 | `results/final_costs.csv`: row "Fake-account resistance (R9: L = 3, young accounts wait 30 days; joins, posts, likes, friends and the "small" count)", column "cost low" |
| `final.cost.step5.cost high` | 0.01159 | `results/final_costs.csv`: row "Fake-account resistance (R9: L = 3, young accounts wait 30 days; joins, posts, likes, friends and the "small" count)", column "cost high" |
| `final.cost.step5.relative cost` | 0.008331 | `results/final_costs.csv`: row "Fake-account resistance (R9: L = 3, young accounts wait 30 days; joins, posts, likes, friends and the "small" count)", column "relative cost" |
| `final.cost.step6.ndcg@5 before` | 0.5146 | `results/final_costs.csv`: row "Privacy (R10: m = 3, epsilon = 1.5)", column "ndcg@5 before" |
| `final.cost.step6.ndcg@5 after` | 0.4882 | `results/final_costs.csv`: row "Privacy (R10: m = 3, epsilon = 1.5)", column "ndcg@5 after" |
| `final.cost.step6.cost` | 0.02646 | `results/final_costs.csv`: row "Privacy (R10: m = 3, epsilon = 1.5)", column "cost" |
| `final.cost.step6.cost low` | 0.01843 | `results/final_costs.csv`: row "Privacy (R10: m = 3, epsilon = 1.5)", column "cost low" |
| `final.cost.step6.cost high` | 0.03484 | `results/final_costs.csv`: row "Privacy (R10: m = 3, epsilon = 1.5)", column "cost high" |
| `final.cost.step6.relative cost` | 0.05142 | `results/final_costs.csv`: row "Privacy (R10: m = 3, epsilon = 1.5)", column "relative cost" |
| `final.cost.step7.ndcg@5 before` | 0.5407 | `results/final_costs.csv`: row "Every rule together: the hybrid -> the final design", column "ndcg@5 before" |
| `final.cost.step7.ndcg@5 after` | 0.4882 | `results/final_costs.csv`: row "Every rule together: the hybrid -> the final design", column "ndcg@5 after" |
| `final.cost.step7.cost` | 0.0525 | `results/final_costs.csv`: row "Every rule together: the hybrid -> the final design", column "cost" |
| `final.cost.step7.cost low` | 0.04336 | `results/final_costs.csv`: row "Every rule together: the hybrid -> the final design", column "cost low" |
| `final.cost.step7.cost high` | 0.06155 | `results/final_costs.csv`: row "Every rule together: the hybrid -> the final design", column "cost high" |
| `final.cost.step7.relative cost` | 0.0971 | `results/final_costs.csv`: row "Every rule together: the hybrid -> the final design", column "relative cost" |
| `final.cost.step8.ndcg@5 before` | 0.4882 | `results/final_costs.csv`: row "Stronger privacy instead: epsilon = 0.5", column "ndcg@5 before" |
| `final.cost.step8.ndcg@5 after` | 0.4364 | `results/final_costs.csv`: row "Stronger privacy instead: epsilon = 0.5", column "ndcg@5 after" |
| `final.cost.step8.cost` | 0.05174 | `results/final_costs.csv`: row "Stronger privacy instead: epsilon = 0.5", column "cost" |
| `final.cost.step8.cost low` | 0.04405 | `results/final_costs.csv`: row "Stronger privacy instead: epsilon = 0.5", column "cost low" |
| `final.cost.step8.cost high` | 0.05924 | `results/final_costs.csv`: row "Stronger privacy instead: epsilon = 0.5", column "cost high" |
| `final.cost.step8.relative cost` | 0.106 | `results/final_costs.csv`: row "Stronger privacy instead: epsilon = 0.5", column "relative cost" |
| `final.cost.step9.ndcg@5 before` | 0.4882 | `results/final_costs.csv`: row "Weaker privacy instead: epsilon = 2", column "ndcg@5 before" |
| `final.cost.step9.ndcg@5 after` | 0.4929 | `results/final_costs.csv`: row "Weaker privacy instead: epsilon = 2", column "ndcg@5 after" |
| `final.cost.step9.cost` | -0.004683 | `results/final_costs.csv`: row "Weaker privacy instead: epsilon = 2", column "cost" |
| `final.cost.step9.cost low` | -0.006792 | `results/final_costs.csv`: row "Weaker privacy instead: epsilon = 2", column "cost low" |
| `final.cost.step9.cost high` | -0.002596 | `results/final_costs.csv`: row "Weaker privacy instead: epsilon = 2", column "cost high" |
| `final.cost.step9.relative cost` | -0.009592 | `results/final_costs.csv`: row "Weaker privacy instead: epsilon = 2", column "relative cost" |
| `final.cost.step10.ndcg@5 before` | 0.4882 | `results/final_costs.csv`: row "Weaker privacy instead: epsilon = 5", column "ndcg@5 before" |
| `final.cost.step10.ndcg@5 after` | 0.4974 | `results/final_costs.csv`: row "Weaker privacy instead: epsilon = 5", column "ndcg@5 after" |
| `final.cost.step10.cost` | -0.009193 | `results/final_costs.csv`: row "Weaker privacy instead: epsilon = 5", column "cost" |
| `final.cost.step10.cost low` | -0.01337 | `results/final_costs.csv`: row "Weaker privacy instead: epsilon = 5", column "cost low" |
| `final.cost.step10.cost high` | -0.005279 | `results/final_costs.csv`: row "Weaker privacy instead: epsilon = 5", column "cost high" |
| `final.cost.step10.relative cost` | -0.01883 | `results/final_costs.csv`: row "Weaker privacy instead: epsilon = 5", column "relative cost" |
| `final.cost.step11.ndcg@5 before` | 0.4882 | `results/final_costs.csv`: row "The final design before the review, against the final design", column "ndcg@5 before" |
| `final.cost.step11.ndcg@5 after` | 0.5104 | `results/final_costs.csv`: row "The final design before the review, against the final design", column "ndcg@5 after" |
| `final.cost.step11.cost` | -0.02222 | `results/final_costs.csv`: row "The final design before the review, against the final design", column "cost" |
| `final.cost.step11.cost low` | -0.0283 | `results/final_costs.csv`: row "The final design before the review, against the final design", column "cost low" |
| `final.cost.step11.cost high` | -0.01618 | `results/final_costs.csv`: row "The final design before the review, against the final design", column "cost high" |
| `final.cost.step11.relative cost` | -0.04551 | `results/final_costs.csv`: row "The final design before the review, against the final design", column "relative cost" |
| `final.cost.step12.ndcg@5 before` | 0.1311 | `results/final_costs.csv`: row "The final design against today's BOING", column "ndcg@5 before" |
| `final.cost.step12.ndcg@5 after` | 0.4882 | `results/final_costs.csv`: row "The final design against today's BOING", column "ndcg@5 after" |
| `final.cost.step12.cost` | -0.3571 | `results/final_costs.csv`: row "The final design against today's BOING", column "cost" |
| `final.cost.step12.cost low` | -0.3807 | `results/final_costs.csv`: row "The final design against today's BOING", column "cost low" |
| `final.cost.step12.cost high` | -0.3336 | `results/final_costs.csv`: row "The final design against today's BOING", column "cost high" |
| `final.cost.step12.relative cost` | -2.723 | `results/final_costs.csv`: row "The final design against today's BOING", column "relative cost" |
| `final.reasons.e2.share shared_members` | 0.543 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "share shared_members" |
| `final.reasons.e2.share friend` | 0.2629 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "share friend" |
| `final.reasons.e2.share new_group` | 0.1846 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "share new_group" |
| `final.reasons.e2.share of reasons true` | 1 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "share of reasons true" |
| `final.reasons.e2.share true, personalised lists` | 1 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "share true, personalised lists" |
| `final.reasons.e2.share naming groups that share nobody` | 0 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "share naming groups that share nobody" |
| `final.reasons.e2.share naming groups that share nobody, lowest draw` | 0 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "share naming groups that share nobody, lowest draw" |
| `final.reasons.e2.share naming groups that share nobody, highest draw` | 0 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "share naming groups that share nobody, highest draw" |
| `final.reasons.e2.share of stated counts that are close` | 1 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "share of stated counts that are close" |
| `final.reasons.e2.quoted / true count (median)` | 1 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "quoted / true count (median)" |
| `final.reasons.e2.share of "small group" reasons true` | 1 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "share of "small group" reasons true" |
| `final.reasons.e2.share of "small group" reasons true (count Discover shows)` | 1 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "share of "small group" reasons true (count Discover shows)" |
| `final.reasons.e2.lists below the quota (members who count)` | 0 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "lists below the quota (members who count)" |
| `final.reasons.e2.lists below the quota (count Discover shows)` | 0 | `results/final_reasons.csv`: row "Hybrid + fair re-ranking (E2 dials)", column "lists below the quota (count Discover shows)" |
| `final.reasons.exact.share shared_members` | 0.0235 | `results/final_reasons.csv`: row "Final design without privacy", column "share shared_members" |
| `final.reasons.exact.share friend` | 0.4314 | `results/final_reasons.csv`: row "Final design without privacy", column "share friend" |
| `final.reasons.exact.share new_group` | 0.1687 | `results/final_reasons.csv`: row "Final design without privacy", column "share new_group" |
| `final.reasons.exact.share of reasons true` | 1 | `results/final_reasons.csv`: row "Final design without privacy", column "share of reasons true" |
| `final.reasons.exact.share true, personalised lists` | 1 | `results/final_reasons.csv`: row "Final design without privacy", column "share true, personalised lists" |
| `final.reasons.exact.share naming groups that share nobody` | 0 | `results/final_reasons.csv`: row "Final design without privacy", column "share naming groups that share nobody" |
| `final.reasons.exact.share naming groups that share nobody, lowest draw` | 0 | `results/final_reasons.csv`: row "Final design without privacy", column "share naming groups that share nobody, lowest draw" |
| `final.reasons.exact.share naming groups that share nobody, highest draw` | 0 | `results/final_reasons.csv`: row "Final design without privacy", column "share naming groups that share nobody, highest draw" |
| `final.reasons.exact.share of stated counts that are close` | 1 | `results/final_reasons.csv`: row "Final design without privacy", column "share of stated counts that are close" |
| `final.reasons.exact.quoted / true count (median)` | 1 | `results/final_reasons.csv`: row "Final design without privacy", column "quoted / true count (median)" |
| `final.reasons.exact.share of "small group" reasons true` | 1 | `results/final_reasons.csv`: row "Final design without privacy", column "share of "small group" reasons true" |
| `final.reasons.exact.share of "small group" reasons true (count Discover shows)` | 0.9459 | `results/final_reasons.csv`: row "Final design without privacy", column "share of "small group" reasons true (count Discover shows)" |
| `final.reasons.exact.lists below the quota (members who count)` | 0 | `results/final_reasons.csv`: row "Final design without privacy", column "lists below the quota (members who count)" |
| `final.reasons.exact.lists below the quota (count Discover shows)` | 47 | `results/final_reasons.csv`: row "Final design without privacy", column "lists below the quota (count Discover shows)" |
| `final.reasons.clip.share shared_members` | 0.0364 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "share shared_members" |
| `final.reasons.clip.share friend` | 0.4509 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "share friend" |
| `final.reasons.clip.share new_group` | 0.1727 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "share new_group" |
| `final.reasons.clip.share of reasons true` | 0.9794 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "share of reasons true" |
| `final.reasons.clip.share true, personalised lists` | 0.9794 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "share true, personalised lists" |
| `final.reasons.clip.share naming groups that share nobody` | 0 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "share naming groups that share nobody" |
| `final.reasons.clip.share naming groups that share nobody, lowest draw` | 0 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "share naming groups that share nobody, lowest draw" |
| `final.reasons.clip.share naming groups that share nobody, highest draw` | 0 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "share naming groups that share nobody, highest draw" |
| `final.reasons.clip.share of stated counts that are close` | 0.4336 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "share of stated counts that are close" |
| `final.reasons.clip.quoted / true count (median)` | 0.4783 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "quoted / true count (median)" |
| `final.reasons.clip.share of "small group" reasons true` | 1 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "share of "small group" reasons true" |
| `final.reasons.clip.share of "small group" reasons true (count Discover shows)` | 0.9632 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "share of "small group" reasons true (count Discover shows)" |
| `final.reasons.clip.lists below the quota (members who count)` | 0 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "lists below the quota (members who count)" |
| `final.reasons.clip.lists below the quota (count Discover shows)` | 34 | `results/final_reasons.csv`: row "Final design, clipping only (test cases)", column "lists below the quota (count Discover shows)" |
| `final.reasons.final.share shared_members` | 0.0588 | `results/final_reasons.csv`: row "Final design (ε = 1.5, m = 3)", column "share shared_members" |
| `final.reasons.final.share friend` | 0.4527 | `results/final_reasons.csv`: row "Final design (ε = 1.5, m = 3)", column "share friend" |
| `final.reasons.final.share new_group` | 0.1569 | `results/final_reasons.csv`: row "Final design (ε = 1.5, m = 3)", column "share new_group" |
| `final.reasons.final.share of reasons true` | 0.9761 | `results/final_reasons.csv`: row "Final design (ε = 1.5, m = 3)", column "share of reasons true" |
| `final.reasons.final.share true, personalised lists` | 0.9761 | `results/final_reasons.csv`: row "Final design (ε = 1.5, m = 3)", column "share true, personalised lists" |
| `final.reasons.final.share naming groups that share nobody` | 0.4103 | `results/final_reasons.csv`: row "Final design (ε = 1.5, m = 3)", column "share naming groups that share nobody" |
| `final.reasons.final.share naming groups that share nobody, lowest draw` | 0.307 | `results/final_reasons.csv`: row "Final design (ε = 1.5, m = 3)", column "share naming groups that share nobody, lowest draw" |
| `final.reasons.final.share naming groups that share nobody, highest draw` | 0.5185 | `results/final_reasons.csv`: row "Final design (ε = 1.5, m = 3)", column "share naming groups that share nobody, highest draw" |
| `final.reasons.final.share of noisy counts that would be close` | 0.2882 | `results/final_reasons.csv`: row "Final design (ε = 1.5, m = 3)", column "share of noisy counts that would be close" |
| `final.reasons.final.share of "small group" reasons true` | 1 | `results/final_reasons.csv`: row "Final design (ε = 1.5, m = 3)", column "share of "small group" reasons true" |
| `final.reasons.final.share of "small group" reasons true (count Discover shows)` | 0.9384 | `results/final_reasons.csv`: row "Final design (ε = 1.5, m = 3)", column "share of "small group" reasons true (count Discover shows)" |
| `final.reasons.final.lists below the quota (members who count)` | 0 | `results/final_reasons.csv`: row "Final design (ε = 1.5, m = 3)", column "lists below the quota (members who count)" |
| `final.reasons.final.lists below the quota (count Discover shows)` | 55.2 | `results/final_reasons.csv`: row "Final design (ε = 1.5, m = 3)", column "lists below the quota (count Discover shows)" |
| `final.reasons.eps05.share shared_members` | 0.0789 | `results/final_reasons.csv`: row "Final design with ε = 0.5", column "share shared_members" |
| `final.reasons.eps05.share friend` | 0.4517 | `results/final_reasons.csv`: row "Final design with ε = 0.5", column "share friend" |
| `final.reasons.eps05.share new_group` | 0.1328 | `results/final_reasons.csv`: row "Final design with ε = 0.5", column "share new_group" |
| `final.reasons.eps05.share of reasons true` | 0.9653 | `results/final_reasons.csv`: row "Final design with ε = 0.5", column "share of reasons true" |
| `final.reasons.eps05.share true, personalised lists` | 0.9653 | `results/final_reasons.csv`: row "Final design with ε = 0.5", column "share true, personalised lists" |
| `final.reasons.eps05.share naming groups that share nobody` | 0.4411 | `results/final_reasons.csv`: row "Final design with ε = 0.5", column "share naming groups that share nobody" |
| `final.reasons.eps05.share naming groups that share nobody, lowest draw` | 0.275 | `results/final_reasons.csv`: row "Final design with ε = 0.5", column "share naming groups that share nobody, lowest draw" |
| `final.reasons.eps05.share naming groups that share nobody, highest draw` | 0.6069 | `results/final_reasons.csv`: row "Final design with ε = 0.5", column "share naming groups that share nobody, highest draw" |
| `final.reasons.eps05.share of noisy counts that would be close` | 0.1407 | `results/final_reasons.csv`: row "Final design with ε = 0.5", column "share of noisy counts that would be close" |
| `final.reasons.eps05.share of "small group" reasons true` | 1 | `results/final_reasons.csv`: row "Final design with ε = 0.5", column "share of "small group" reasons true" |
| `final.reasons.eps05.share of "small group" reasons true (count Discover shows)` | 0.9427 | `results/final_reasons.csv`: row "Final design with ε = 0.5", column "share of "small group" reasons true (count Discover shows)" |
| `final.reasons.eps05.lists below the quota (members who count)` | 0 | `results/final_reasons.csv`: row "Final design with ε = 0.5", column "lists below the quota (members who count)" |
| `final.reasons.eps05.lists below the quota (count Discover shows)` | 51.4 | `results/final_reasons.csv`: row "Final design with ε = 0.5", column "lists below the quota (count Discover shows)" |
| `final.reasons.eps2.share shared_members` | 0.0552 | `results/final_reasons.csv`: row "Final design with ε = 2", column "share shared_members" |
| `final.reasons.eps2.share friend` | 0.4549 | `results/final_reasons.csv`: row "Final design with ε = 2", column "share friend" |
| `final.reasons.eps2.share new_group` | 0.1597 | `results/final_reasons.csv`: row "Final design with ε = 2", column "share new_group" |
| `final.reasons.eps2.share of reasons true` | 0.9789 | `results/final_reasons.csv`: row "Final design with ε = 2", column "share of reasons true" |
| `final.reasons.eps2.share true, personalised lists` | 0.9789 | `results/final_reasons.csv`: row "Final design with ε = 2", column "share true, personalised lists" |
| `final.reasons.eps2.share naming groups that share nobody` | 0.3823 | `results/final_reasons.csv`: row "Final design with ε = 2", column "share naming groups that share nobody" |
| `final.reasons.eps2.share naming groups that share nobody, lowest draw` | 0.2754 | `results/final_reasons.csv`: row "Final design with ε = 2", column "share naming groups that share nobody, lowest draw" |
| `final.reasons.eps2.share naming groups that share nobody, highest draw` | 0.4609 | `results/final_reasons.csv`: row "Final design with ε = 2", column "share naming groups that share nobody, highest draw" |
| `final.reasons.eps2.share of noisy counts that would be close` | 0.3418 | `results/final_reasons.csv`: row "Final design with ε = 2", column "share of noisy counts that would be close" |
| `final.reasons.eps2.share of "small group" reasons true` | 1 | `results/final_reasons.csv`: row "Final design with ε = 2", column "share of "small group" reasons true" |
| `final.reasons.eps2.share of "small group" reasons true (count Discover shows)` | 0.9406 | `results/final_reasons.csv`: row "Final design with ε = 2", column "share of "small group" reasons true (count Discover shows)" |
| `final.reasons.eps2.lists below the quota (members who count)` | 0 | `results/final_reasons.csv`: row "Final design with ε = 2", column "lists below the quota (members who count)" |
| `final.reasons.eps2.lists below the quota (count Discover shows)` | 52.8 | `results/final_reasons.csv`: row "Final design with ε = 2", column "lists below the quota (count Discover shows)" |
| `final.reasons.eps5.share shared_members` | 0.0443 | `results/final_reasons.csv`: row "Final design with ε = 5", column "share shared_members" |
| `final.reasons.eps5.share friend` | 0.4535 | `results/final_reasons.csv`: row "Final design with ε = 5", column "share friend" |
| `final.reasons.eps5.share new_group` | 0.1668 | `results/final_reasons.csv`: row "Final design with ε = 5", column "share new_group" |
| `final.reasons.eps5.share of reasons true` | 0.9915 | `results/final_reasons.csv`: row "Final design with ε = 5", column "share of reasons true" |
| `final.reasons.eps5.share true, personalised lists` | 0.9915 | `results/final_reasons.csv`: row "Final design with ε = 5", column "share true, personalised lists" |
| `final.reasons.eps5.share naming groups that share nobody` | 0.192 | `results/final_reasons.csv`: row "Final design with ε = 5", column "share naming groups that share nobody" |
| `final.reasons.eps5.share naming groups that share nobody, lowest draw` | 0.1145 | `results/final_reasons.csv`: row "Final design with ε = 5", column "share naming groups that share nobody, lowest draw" |
| `final.reasons.eps5.share naming groups that share nobody, highest draw` | 0.2727 | `results/final_reasons.csv`: row "Final design with ε = 5", column "share naming groups that share nobody, highest draw" |
| `final.reasons.eps5.share of noisy counts that would be close` | 0.3959 | `results/final_reasons.csv`: row "Final design with ε = 5", column "share of noisy counts that would be close" |
| `final.reasons.eps5.share of "small group" reasons true` | 1 | `results/final_reasons.csv`: row "Final design with ε = 5", column "share of "small group" reasons true" |
| `final.reasons.eps5.share of "small group" reasons true (count Discover shows)` | 0.9417 | `results/final_reasons.csv`: row "Final design with ε = 5", column "share of "small group" reasons true (count Discover shows)" |
| `final.reasons.eps5.lists below the quota (members who count)` | 0 | `results/final_reasons.csv`: row "Final design with ε = 5", column "lists below the quota (members who count)" |
| `final.reasons.eps5.lists below the quota (count Discover shows)` | 48.8 | `results/final_reasons.csv`: row "Final design with ε = 5", column "lists below the quota (count Discover shows)" |
| `final.reasons.before.share shared_members` | 0.5303 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "share shared_members" |
| `final.reasons.before.share friend` | 0.3093 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "share friend" |
| `final.reasons.before.share new_group` | 0.1375 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "share new_group" |
| `final.reasons.before.share of reasons true` | 0.6192 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "share of reasons true" |
| `final.reasons.before.share true, personalised lists` | 0.6192 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "share true, personalised lists" |
| `final.reasons.before.share naming groups that share nobody` | 0.1378 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "share naming groups that share nobody" |
| `final.reasons.before.share naming groups that share nobody, lowest draw` | 0.1269 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "share naming groups that share nobody, lowest draw" |
| `final.reasons.before.share naming groups that share nobody, highest draw` | 0.1552 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "share naming groups that share nobody, highest draw" |
| `final.reasons.before.share of stated counts that are close` | 0.3764 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "share of stated counts that are close" |
| `final.reasons.before.quoted / true count (median)` | 0.4806 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "quoted / true count (median)" |
| `final.reasons.before.share of "small group" reasons true` | 0.5688 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "share of "small group" reasons true" |
| `final.reasons.before.share of "small group" reasons true (count Discover shows)` | 0.5414 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "share of "small group" reasons true (count Discover shows)" |
| `final.reasons.before.lists below the quota (members who count)` | 443.5 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "lists below the quota (members who count)" |
| `final.reasons.before.lists below the quota (count Discover shows)` | 470.4 | `results/final_reasons.csv`: row "Final design before the review (ε = 5)", column "lists below the quota (count Discover shows)" |
| `final.reasons.off.share shared_members` | 0 | `results/final_reasons.csv`: row "Personalisation off (default list)", column "share shared_members" |
| `final.reasons.off.share friend` | 0 | `results/final_reasons.csv`: row "Personalisation off (default list)", column "share friend" |
| `final.reasons.off.share new_group` | 0.4413 | `results/final_reasons.csv`: row "Personalisation off (default list)", column "share new_group" |
| `final.reasons.off.share of reasons true` | 1 | `results/final_reasons.csv`: row "Personalisation off (default list)", column "share of reasons true" |
| `final.reasons.off.share true, default lists` | 1 | `results/final_reasons.csv`: row "Personalisation off (default list)", column "share true, default lists" |
| `final.reasons.off.lists below the quota (members who count)` | 0 | `results/final_reasons.csv`: row "Personalisation off (default list)", column "lists below the quota (members who count)" |
| `final.reasons.off.lists below the quota (count Discover shows)` | 0 | `results/final_reasons.csv`: row "Personalisation off (default list)", column "lists below the quota (count Discover shows)" |
| `final.promotion.first_fix.rivals1.A.fake accounts` | 9 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker A, column "fake accounts" |
| `final.promotion.first_fix.rivals1.A.statistics unchanged` | no | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker A, column "statistics unchanged" |
| `final.promotion.first_fix.rivals1.A.rivals: lists before` | 130 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker A, column "rivals: lists before" |
| `final.promotion.first_fix.rivals1.A.rivals: lists after` | 15 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker A, column "rivals: lists after" |
| `final.promotion.first_fix.rivals1.A.top gainer: gain` | 11 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker A, column "top gainer: gain" |
| `final.promotion.first_fix.rivals1.A.default lists changed` | 0 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker A, column "default lists changed" |
| `final.promotion.first_fix.rivals1.B.fake accounts` | 9 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker B, column "fake accounts" |
| `final.promotion.first_fix.rivals1.B.statistics unchanged` | no | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker B, column "statistics unchanged" |
| `final.promotion.first_fix.rivals1.B.rivals: lists before` | 130 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker B, column "rivals: lists before" |
| `final.promotion.first_fix.rivals1.B.rivals: lists after` | 15 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker B, column "rivals: lists after" |
| `final.promotion.first_fix.rivals1.B.top gainer: gain` | 11 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker B, column "top gainer: gain" |
| `final.promotion.first_fix.rivals1.B.default lists changed` | 0 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker B, column "default lists changed" |
| `final.promotion.first_fix.rivals1.C.fake accounts` | 9 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker C, column "fake accounts" |
| `final.promotion.first_fix.rivals1.C.statistics unchanged` | no | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker C, column "statistics unchanged" |
| `final.promotion.first_fix.rivals1.C.rivals: lists before` | 130 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker C, column "rivals: lists before" |
| `final.promotion.first_fix.rivals1.C.rivals: lists after` | 15 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker C, column "rivals: lists after" |
| `final.promotion.first_fix.rivals1.C.top gainer: gain` | 11 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker C, column "top gainer: gain" |
| `final.promotion.first_fix.rivals1.C.default lists changed` | 0 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker C, column "default lists changed" |
| `final.promotion.first_fix.rivals1.D.fake accounts` | 9 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker D, column "fake accounts" |
| `final.promotion.first_fix.rivals1.D.statistics unchanged` | no | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker D, column "statistics unchanged" |
| `final.promotion.first_fix.rivals1.D.rivals: lists before` | 130 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker D, column "rivals: lists before" |
| `final.promotion.first_fix.rivals1.D.rivals: lists after` | 17 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker D, column "rivals: lists after" |
| `final.promotion.first_fix.rivals1.D.top gainer: gain` | 9 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker D, column "top gainer: gain" |
| `final.promotion.first_fix.rivals1.D.default lists changed` | 0 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 1, attacker D, column "default lists changed" |
| `final.promotion.first_fix.rivals2.A.fake accounts` | 11 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker A, column "fake accounts" |
| `final.promotion.first_fix.rivals2.A.statistics unchanged` | no | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker A, column "statistics unchanged" |
| `final.promotion.first_fix.rivals2.A.rivals: lists before` | 246 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker A, column "rivals: lists before" |
| `final.promotion.first_fix.rivals2.A.rivals: lists after` | 46 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker A, column "rivals: lists after" |
| `final.promotion.first_fix.rivals2.A.top gainer: gain` | 22 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker A, column "top gainer: gain" |
| `final.promotion.first_fix.rivals2.A.default lists changed` | 0 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker A, column "default lists changed" |
| `final.promotion.first_fix.rivals2.B.fake accounts` | 11 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker B, column "fake accounts" |
| `final.promotion.first_fix.rivals2.B.statistics unchanged` | no | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker B, column "statistics unchanged" |
| `final.promotion.first_fix.rivals2.B.rivals: lists before` | 246 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker B, column "rivals: lists before" |
| `final.promotion.first_fix.rivals2.B.rivals: lists after` | 46 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker B, column "rivals: lists after" |
| `final.promotion.first_fix.rivals2.B.top gainer: gain` | 22 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker B, column "top gainer: gain" |
| `final.promotion.first_fix.rivals2.B.default lists changed` | 0 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker B, column "default lists changed" |
| `final.promotion.first_fix.rivals2.C.fake accounts` | 11 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker C, column "fake accounts" |
| `final.promotion.first_fix.rivals2.C.statistics unchanged` | no | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker C, column "statistics unchanged" |
| `final.promotion.first_fix.rivals2.C.rivals: lists before` | 246 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker C, column "rivals: lists before" |
| `final.promotion.first_fix.rivals2.C.rivals: lists after` | 46 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker C, column "rivals: lists after" |
| `final.promotion.first_fix.rivals2.C.top gainer: gain` | 22 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker C, column "top gainer: gain" |
| `final.promotion.first_fix.rivals2.C.default lists changed` | 0 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker C, column "default lists changed" |
| `final.promotion.first_fix.rivals2.D.fake accounts` | 11 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker D, column "fake accounts" |
| `final.promotion.first_fix.rivals2.D.statistics unchanged` | no | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker D, column "statistics unchanged" |
| `final.promotion.first_fix.rivals2.D.rivals: lists before` | 246 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker D, column "rivals: lists before" |
| `final.promotion.first_fix.rivals2.D.rivals: lists after` | 50 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker D, column "rivals: lists after" |
| `final.promotion.first_fix.rivals2.D.top gainer: gain` | 21 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker D, column "top gainer: gain" |
| `final.promotion.first_fix.rivals2.D.default lists changed` | 0 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 2, attacker D, column "default lists changed" |
| `final.promotion.first_fix.rivals4.A.fake accounts` | 24 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker A, column "fake accounts" |
| `final.promotion.first_fix.rivals4.A.statistics unchanged` | no | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker A, column "statistics unchanged" |
| `final.promotion.first_fix.rivals4.A.rivals: lists before` | 424 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker A, column "rivals: lists before" |
| `final.promotion.first_fix.rivals4.A.rivals: lists after` | 94 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker A, column "rivals: lists after" |
| `final.promotion.first_fix.rivals4.A.top gainer: gain` | 47 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker A, column "top gainer: gain" |
| `final.promotion.first_fix.rivals4.A.default lists changed` | 0 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker A, column "default lists changed" |
| `final.promotion.first_fix.rivals4.B.fake accounts` | 24 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker B, column "fake accounts" |
| `final.promotion.first_fix.rivals4.B.statistics unchanged` | no | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker B, column "statistics unchanged" |
| `final.promotion.first_fix.rivals4.B.rivals: lists before` | 424 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker B, column "rivals: lists before" |
| `final.promotion.first_fix.rivals4.B.rivals: lists after` | 94 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker B, column "rivals: lists after" |
| `final.promotion.first_fix.rivals4.B.top gainer: gain` | 47 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker B, column "top gainer: gain" |
| `final.promotion.first_fix.rivals4.B.default lists changed` | 0 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker B, column "default lists changed" |
| `final.promotion.first_fix.rivals4.C.fake accounts` | 24 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker C, column "fake accounts" |
| `final.promotion.first_fix.rivals4.C.statistics unchanged` | no | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker C, column "statistics unchanged" |
| `final.promotion.first_fix.rivals4.C.rivals: lists before` | 424 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker C, column "rivals: lists before" |
| `final.promotion.first_fix.rivals4.C.rivals: lists after` | 94 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker C, column "rivals: lists after" |
| `final.promotion.first_fix.rivals4.C.top gainer: gain` | 47 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker C, column "top gainer: gain" |
| `final.promotion.first_fix.rivals4.C.default lists changed` | 0 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker C, column "default lists changed" |
| `final.promotion.first_fix.rivals4.D.fake accounts` | 24 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker D, column "fake accounts" |
| `final.promotion.first_fix.rivals4.D.statistics unchanged` | no | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker D, column "statistics unchanged" |
| `final.promotion.first_fix.rivals4.D.rivals: lists before` | 424 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker D, column "rivals: lists before" |
| `final.promotion.first_fix.rivals4.D.rivals: lists after` | 101 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker D, column "rivals: lists after" |
| `final.promotion.first_fix.rivals4.D.top gainer: gain` | 41 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker D, column "top gainer: gain" |
| `final.promotion.first_fix.rivals4.D.default lists changed` | 0 | `results/final_promotion.csv`: rule "first fix (count Discover shows)", rivals 4, attacker D, column "default lists changed" |
| `final.promotion.final.rivals1.A.fake accounts` | 9 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker A, column "fake accounts" |
| `final.promotion.final.rivals1.A.statistics unchanged` | yes | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker A, column "statistics unchanged" |
| `final.promotion.final.rivals1.A.rivals: lists before` | 126 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker A, column "rivals: lists before" |
| `final.promotion.final.rivals1.A.rivals: lists after` | 126 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker A, column "rivals: lists after" |
| `final.promotion.final.rivals1.A.top gainer: gain` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker A, column "top gainer: gain" |
| `final.promotion.final.rivals1.A.default lists changed` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker A, column "default lists changed" |
| `final.promotion.final.rivals1.B.fake accounts` | 9 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker B, column "fake accounts" |
| `final.promotion.final.rivals1.B.statistics unchanged` | yes | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker B, column "statistics unchanged" |
| `final.promotion.final.rivals1.B.rivals: lists before` | 126 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker B, column "rivals: lists before" |
| `final.promotion.final.rivals1.B.rivals: lists after` | 126 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker B, column "rivals: lists after" |
| `final.promotion.final.rivals1.B.top gainer: gain` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker B, column "top gainer: gain" |
| `final.promotion.final.rivals1.B.default lists changed` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker B, column "default lists changed" |
| `final.promotion.final.rivals1.C.fake accounts` | 9 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker C, column "fake accounts" |
| `final.promotion.final.rivals1.C.statistics unchanged` | yes | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker C, column "statistics unchanged" |
| `final.promotion.final.rivals1.C.rivals: lists before` | 126 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker C, column "rivals: lists before" |
| `final.promotion.final.rivals1.C.rivals: lists after` | 126 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker C, column "rivals: lists after" |
| `final.promotion.final.rivals1.C.top gainer: gain` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker C, column "top gainer: gain" |
| `final.promotion.final.rivals1.C.default lists changed` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker C, column "default lists changed" |
| `final.promotion.final.rivals1.D.fake accounts` | 9 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker D, column "fake accounts" |
| `final.promotion.final.rivals1.D.statistics unchanged` | no | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker D, column "statistics unchanged" |
| `final.promotion.final.rivals1.D.rivals: lists before` | 126 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker D, column "rivals: lists before" |
| `final.promotion.final.rivals1.D.rivals: lists after` | 17 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker D, column "rivals: lists after" |
| `final.promotion.final.rivals1.D.top gainer: gain` | 9 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker D, column "top gainer: gain" |
| `final.promotion.final.rivals1.D.default lists changed` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 1, attacker D, column "default lists changed" |
| `final.promotion.final.rivals2.A.fake accounts` | 11 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker A, column "fake accounts" |
| `final.promotion.final.rivals2.A.statistics unchanged` | yes | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker A, column "statistics unchanged" |
| `final.promotion.final.rivals2.A.rivals: lists before` | 240 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker A, column "rivals: lists before" |
| `final.promotion.final.rivals2.A.rivals: lists after` | 240 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker A, column "rivals: lists after" |
| `final.promotion.final.rivals2.A.top gainer: gain` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker A, column "top gainer: gain" |
| `final.promotion.final.rivals2.A.default lists changed` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker A, column "default lists changed" |
| `final.promotion.final.rivals2.B.fake accounts` | 11 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker B, column "fake accounts" |
| `final.promotion.final.rivals2.B.statistics unchanged` | yes | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker B, column "statistics unchanged" |
| `final.promotion.final.rivals2.B.rivals: lists before` | 240 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker B, column "rivals: lists before" |
| `final.promotion.final.rivals2.B.rivals: lists after` | 240 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker B, column "rivals: lists after" |
| `final.promotion.final.rivals2.B.top gainer: gain` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker B, column "top gainer: gain" |
| `final.promotion.final.rivals2.B.default lists changed` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker B, column "default lists changed" |
| `final.promotion.final.rivals2.C.fake accounts` | 11 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker C, column "fake accounts" |
| `final.promotion.final.rivals2.C.statistics unchanged` | yes | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker C, column "statistics unchanged" |
| `final.promotion.final.rivals2.C.rivals: lists before` | 240 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker C, column "rivals: lists before" |
| `final.promotion.final.rivals2.C.rivals: lists after` | 240 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker C, column "rivals: lists after" |
| `final.promotion.final.rivals2.C.top gainer: gain` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker C, column "top gainer: gain" |
| `final.promotion.final.rivals2.C.default lists changed` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker C, column "default lists changed" |
| `final.promotion.final.rivals2.D.fake accounts` | 11 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker D, column "fake accounts" |
| `final.promotion.final.rivals2.D.statistics unchanged` | no | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker D, column "statistics unchanged" |
| `final.promotion.final.rivals2.D.rivals: lists before` | 240 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker D, column "rivals: lists before" |
| `final.promotion.final.rivals2.D.rivals: lists after` | 50 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker D, column "rivals: lists after" |
| `final.promotion.final.rivals2.D.top gainer: gain` | 20 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker D, column "top gainer: gain" |
| `final.promotion.final.rivals2.D.default lists changed` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 2, attacker D, column "default lists changed" |
| `final.promotion.final.rivals4.A.fake accounts` | 24 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker A, column "fake accounts" |
| `final.promotion.final.rivals4.A.statistics unchanged` | yes | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker A, column "statistics unchanged" |
| `final.promotion.final.rivals4.A.rivals: lists before` | 417 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker A, column "rivals: lists before" |
| `final.promotion.final.rivals4.A.rivals: lists after` | 417 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker A, column "rivals: lists after" |
| `final.promotion.final.rivals4.A.top gainer: gain` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker A, column "top gainer: gain" |
| `final.promotion.final.rivals4.A.default lists changed` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker A, column "default lists changed" |
| `final.promotion.final.rivals4.B.fake accounts` | 24 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker B, column "fake accounts" |
| `final.promotion.final.rivals4.B.statistics unchanged` | yes | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker B, column "statistics unchanged" |
| `final.promotion.final.rivals4.B.rivals: lists before` | 417 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker B, column "rivals: lists before" |
| `final.promotion.final.rivals4.B.rivals: lists after` | 417 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker B, column "rivals: lists after" |
| `final.promotion.final.rivals4.B.top gainer: gain` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker B, column "top gainer: gain" |
| `final.promotion.final.rivals4.B.default lists changed` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker B, column "default lists changed" |
| `final.promotion.final.rivals4.C.fake accounts` | 24 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker C, column "fake accounts" |
| `final.promotion.final.rivals4.C.statistics unchanged` | yes | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker C, column "statistics unchanged" |
| `final.promotion.final.rivals4.C.rivals: lists before` | 417 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker C, column "rivals: lists before" |
| `final.promotion.final.rivals4.C.rivals: lists after` | 417 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker C, column "rivals: lists after" |
| `final.promotion.final.rivals4.C.top gainer: gain` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker C, column "top gainer: gain" |
| `final.promotion.final.rivals4.C.default lists changed` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker C, column "default lists changed" |
| `final.promotion.final.rivals4.D.fake accounts` | 24 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker D, column "fake accounts" |
| `final.promotion.final.rivals4.D.statistics unchanged` | no | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker D, column "statistics unchanged" |
| `final.promotion.final.rivals4.D.rivals: lists before` | 417 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker D, column "rivals: lists before" |
| `final.promotion.final.rivals4.D.rivals: lists after` | 102 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker D, column "rivals: lists after" |
| `final.promotion.final.rivals4.D.top gainer: gain` | 40 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker D, column "top gainer: gain" |
| `final.promotion.final.rivals4.D.default lists changed` | 0 | `results/final_promotion.csv`: rule "final (members who count)", rivals 4, attacker D, column "default lists changed" |
| `final.newcomers.popularity.ndcg@5 3+ groups (test)` | 0.1325 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "ndcg@5 3+ groups (test)" |
| `final.newcomers.popularity.hit 3+ groups (test)` | 0.2248 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "hit 3+ groups (test)" |
| `final.newcomers.popularity.ndcg@5 2 groups (test)` | 0.1265 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "ndcg@5 2 groups (test)" |
| `final.newcomers.popularity.hit 2 groups (test)` | 0.2057 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "hit 2 groups (test)" |
| `final.newcomers.popularity.ndcg@5 1 group (quiz)` | 0.1601 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "ndcg@5 1 group (quiz)" |
| `final.newcomers.popularity.hit 1 group (quiz)` | 0.2745 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "hit 1 group (quiz)" |
| `final.newcomers.popularity.ndcg@5 no group yet (quiz)` | 0.1503 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "ndcg@5 no group yet (quiz)" |
| `final.newcomers.popularity.hit no group yet (quiz)` | 0.2295 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "hit no group yet (quiz)" |
| `final.newcomers.popularity.ndcg@5 new members (quiz)` | 0.1342 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "ndcg@5 new members (quiz)" |
| `final.newcomers.popularity.hit new members (quiz)` | 0.2129 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "hit new members (quiz)" |
| `final.newcomers.popularity.share new groups` | 0 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "share new groups" |
| `final.newcomers.popularity.share older small groups` | 0 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "share older small groups" |
| `final.newcomers.popularity.found in new groups` | 0 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "found in new groups" |
| `final.newcomers.popularity.hidden in new groups` | 8 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "hidden in new groups" |
| `final.newcomers.popularity.found in new or small groups` | 0 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "found in new or small groups" |
| `final.newcomers.popularity.hidden in new or small groups` | 42 | `results/final_newcomers.csv`: row "Popularity (BOING today)", column "hidden in new or small groups" |
| `final.newcomers.exact.ndcg@5 3+ groups (test)` | 0.5339 | `results/final_newcomers.csv`: row "Final design without privacy", column "ndcg@5 3+ groups (test)" |
| `final.newcomers.exact.hit 3+ groups (test)` | 0.6587 | `results/final_newcomers.csv`: row "Final design without privacy", column "hit 3+ groups (test)" |
| `final.newcomers.exact.ndcg@5 2 groups (test)` | 0.4483 | `results/final_newcomers.csv`: row "Final design without privacy", column "ndcg@5 2 groups (test)" |
| `final.newcomers.exact.hit 2 groups (test)` | 0.5633 | `results/final_newcomers.csv`: row "Final design without privacy", column "hit 2 groups (test)" |
| `final.newcomers.exact.ndcg@5 1 group (quiz)` | 0.3981 | `results/final_newcomers.csv`: row "Final design without privacy", column "ndcg@5 1 group (quiz)" |
| `final.newcomers.exact.hit 1 group (quiz)` | 0.521 | `results/final_newcomers.csv`: row "Final design without privacy", column "hit 1 group (quiz)" |
| `final.newcomers.exact.ndcg@5 no group yet (quiz)` | 0.341 | `results/final_newcomers.csv`: row "Final design without privacy", column "ndcg@5 no group yet (quiz)" |
| `final.newcomers.exact.hit no group yet (quiz)` | 0.459 | `results/final_newcomers.csv`: row "Final design without privacy", column "hit no group yet (quiz)" |
| `final.newcomers.exact.ndcg@5 new members (quiz)` | 0.348 | `results/final_newcomers.csv`: row "Final design without privacy", column "ndcg@5 new members (quiz)" |
| `final.newcomers.exact.hit new members (quiz)` | 0.4752 | `results/final_newcomers.csv`: row "Final design without privacy", column "hit new members (quiz)" |
| `final.newcomers.exact.share new groups` | 0.0578 | `results/final_newcomers.csv`: row "Final design without privacy", column "share new groups" |
| `final.newcomers.exact.share older small groups` | 0.1397 | `results/final_newcomers.csv`: row "Final design without privacy", column "share older small groups" |
| `final.newcomers.exact.found in new groups` | 1 | `results/final_newcomers.csv`: row "Final design without privacy", column "found in new groups" |
| `final.newcomers.exact.hidden in new groups` | 8 | `results/final_newcomers.csv`: row "Final design without privacy", column "hidden in new groups" |
| `final.newcomers.exact.found in new or small groups` | 14 | `results/final_newcomers.csv`: row "Final design without privacy", column "found in new or small groups" |
| `final.newcomers.exact.hidden in new or small groups` | 42 | `results/final_newcomers.csv`: row "Final design without privacy", column "hidden in new or small groups" |
| `final.newcomers.final.ndcg@5 3+ groups (test)` | 0.5018 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "ndcg@5 3+ groups (test)" |
| `final.newcomers.final.hit 3+ groups (test)` | 0.627 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "hit 3+ groups (test)" |
| `final.newcomers.final.ndcg@5 2 groups (test)` | 0.441 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "ndcg@5 2 groups (test)" |
| `final.newcomers.final.hit 2 groups (test)` | 0.5658 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "hit 2 groups (test)" |
| `final.newcomers.final.ndcg@5 1 group (quiz)` | 0.3976 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "ndcg@5 1 group (quiz)" |
| `final.newcomers.final.hit 1 group (quiz)` | 0.5345 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "hit 1 group (quiz)" |
| `final.newcomers.final.ndcg@5 no group yet (quiz)` | 0.34 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "ndcg@5 no group yet (quiz)" |
| `final.newcomers.final.hit no group yet (quiz)` | 0.4574 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "hit no group yet (quiz)" |
| `final.newcomers.final.ndcg@5 new members (quiz)` | 0.3428 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "ndcg@5 new members (quiz)" |
| `final.newcomers.final.hit new members (quiz)` | 0.4728 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "hit new members (quiz)" |
| `final.newcomers.final.share new groups` | 0.0721 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "share new groups" |
| `final.newcomers.final.share older small groups` | 0.1273 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "share older small groups" |
| `final.newcomers.final.found in new groups` | 1.3 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "found in new groups" |
| `final.newcomers.final.hidden in new groups` | 8 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "hidden in new groups" |
| `final.newcomers.final.found in new or small groups` | 12.5 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "found in new or small groups" |
| `final.newcomers.final.hidden in new or small groups` | 42 | `results/final_newcomers.csv`: row "Final design (ε = 1.5, m = 3)", column "hidden in new or small groups" |
| `final.newcomers.off.ndcg@5 3+ groups (test)` | 0.0563 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "ndcg@5 3+ groups (test)" |
| `final.newcomers.off.hit 3+ groups (test)` | 0.1028 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "hit 3+ groups (test)" |
| `final.newcomers.off.ndcg@5 2 groups (test)` | 0.0656 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "ndcg@5 2 groups (test)" |
| `final.newcomers.off.hit 2 groups (test)` | 0.1108 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "hit 2 groups (test)" |
| `final.newcomers.off.ndcg@5 1 group (quiz)` | 0.0687 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "ndcg@5 1 group (quiz)" |
| `final.newcomers.off.hit 1 group (quiz)` | 0.1092 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "hit 1 group (quiz)" |
| `final.newcomers.off.ndcg@5 no group yet (quiz)` | 0.0485 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "ndcg@5 no group yet (quiz)" |
| `final.newcomers.off.hit no group yet (quiz)` | 0.0902 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "hit no group yet (quiz)" |
| `final.newcomers.off.ndcg@5 new members (quiz)` | 0.047 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "ndcg@5 new members (quiz)" |
| `final.newcomers.off.hit new members (quiz)` | 0.0842 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "hit new members (quiz)" |
| `final.newcomers.off.share new groups` | 0.4413 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "share new groups" |
| `final.newcomers.off.share older small groups` | 0 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "share older small groups" |
| `final.newcomers.off.found in new groups` | 2 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "found in new groups" |
| `final.newcomers.off.hidden in new groups` | 8 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "hidden in new groups" |
| `final.newcomers.off.found in new or small groups` | 2 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "found in new or small groups" |
| `final.newcomers.off.hidden in new or small groups` | 42 | `results/final_newcomers.csv`: row "Personalisation off (default list)", column "hidden in new or small groups" |
| `final.sybil.A.k100.target exposure` | 9 | `results/final_sybil.csv`: attacker "A · New accounts, level 1-2", k 100, column "target exposure" |
| `final.sybil.A.k100.statistics unchanged (test)` | yes | `results/final_sybil.csv`: attacker "A · New accounts, level 1-2", k 100, column "statistics unchanged (test)" |
| `final.sybil.A.k200.target exposure` | 9 | `results/final_sybil.csv`: attacker "A · New accounts, level 1-2", k 200, column "target exposure" |
| `final.sybil.A.k200.statistics unchanged (test)` | yes | `results/final_sybil.csv`: attacker "A · New accounts, level 1-2", k 200, column "statistics unchanged (test)" |
| `final.sybil.B.k100.target exposure` | 9 | `results/final_sybil.csv`: attacker "B · New accounts, levelled up to 5-6", k 100, column "target exposure" |
| `final.sybil.B.k100.statistics unchanged (test)` | yes | `results/final_sybil.csv`: attacker "B · New accounts, levelled up to 5-6", k 100, column "statistics unchanged (test)" |
| `final.sybil.B.k200.target exposure` | 9 | `results/final_sybil.csv`: attacker "B · New accounts, levelled up to 5-6", k 200, column "target exposure" |
| `final.sybil.B.k200.statistics unchanged (test)` | yes | `results/final_sybil.csv`: attacker "B · New accounts, levelled up to 5-6", k 200, column "statistics unchanged (test)" |
| `final.sybil.C.k100.target exposure` | 9 | `results/final_sybil.csv`: attacker "C · A month old, level 1-2", k 100, column "target exposure" |
| `final.sybil.C.k100.statistics unchanged (test)` | yes | `results/final_sybil.csv`: attacker "C · A month old, level 1-2", k 100, column "statistics unchanged (test)" |
| `final.sybil.C.k200.target exposure` | 9 | `results/final_sybil.csv`: attacker "C · A month old, level 1-2", k 200, column "target exposure" |
| `final.sybil.C.k200.statistics unchanged (test)` | yes | `results/final_sybil.csv`: attacker "C · A month old, level 1-2", k 200, column "statistics unchanged (test)" |
| `final.sybil.D.k100.target exposure` | 351 | `results/final_sybil.csv`: attacker "D · A month old and levelled up", k 100, column "target exposure" |
| `final.sybil.D.k100.statistics unchanged (test)` | no | `results/final_sybil.csv`: attacker "D · A month old and levelled up", k 100, column "statistics unchanged (test)" |
| `final.sybil.D.k200.target exposure` | 351 | `results/final_sybil.csv`: attacker "D · A month old and levelled up", k 200, column "target exposure" |
| `final.sybil.D.k200.statistics unchanged (test)` | no | `results/final_sybil.csv`: attacker "D · A month old and levelled up", k 200, column "statistics unchanged (test)" |
| `final.sybil_posting.A.k100.default lists showing the target` | 0 | `results/final_sybil_posting.csv`: attacker "A · New accounts, level 1-2", k 100, column "default lists showing the target" |
| `final.sybil_posting.A.k100.statistics unchanged (test)` | yes | `results/final_sybil_posting.csv`: attacker "A · New accounts, level 1-2", k 100, column "statistics unchanged (test)" |
| `final.sybil_posting.A.k200.default lists showing the target` | 0 | `results/final_sybil_posting.csv`: attacker "A · New accounts, level 1-2", k 200, column "default lists showing the target" |
| `final.sybil_posting.A.k200.statistics unchanged (test)` | yes | `results/final_sybil_posting.csv`: attacker "A · New accounts, level 1-2", k 200, column "statistics unchanged (test)" |
| `final.sybil_posting.B.k100.default lists showing the target` | 0 | `results/final_sybil_posting.csv`: attacker "B · New accounts, levelled up to 5-6", k 100, column "default lists showing the target" |
| `final.sybil_posting.B.k100.statistics unchanged (test)` | yes | `results/final_sybil_posting.csv`: attacker "B · New accounts, levelled up to 5-6", k 100, column "statistics unchanged (test)" |
| `final.sybil_posting.B.k200.default lists showing the target` | 0 | `results/final_sybil_posting.csv`: attacker "B · New accounts, levelled up to 5-6", k 200, column "default lists showing the target" |
| `final.sybil_posting.B.k200.statistics unchanged (test)` | yes | `results/final_sybil_posting.csv`: attacker "B · New accounts, levelled up to 5-6", k 200, column "statistics unchanged (test)" |
| `final.sybil_posting.C.k100.default lists showing the target` | 0 | `results/final_sybil_posting.csv`: attacker "C · A month old, level 1-2", k 100, column "default lists showing the target" |
| `final.sybil_posting.C.k100.statistics unchanged (test)` | yes | `results/final_sybil_posting.csv`: attacker "C · A month old, level 1-2", k 100, column "statistics unchanged (test)" |
| `final.sybil_posting.C.k200.default lists showing the target` | 0 | `results/final_sybil_posting.csv`: attacker "C · A month old, level 1-2", k 200, column "default lists showing the target" |
| `final.sybil_posting.C.k200.statistics unchanged (test)` | yes | `results/final_sybil_posting.csv`: attacker "C · A month old, level 1-2", k 200, column "statistics unchanged (test)" |
| `final.sybil_posting.D.k100.default lists showing the target` | 351 | `results/final_sybil_posting.csv`: attacker "D · A month old and levelled up", k 100, column "default lists showing the target" |
| `final.sybil_posting.D.k100.statistics unchanged (test)` | no | `results/final_sybil_posting.csv`: attacker "D · A month old and levelled up", k 100, column "statistics unchanged (test)" |
| `final.sybil_posting.D.k200.default lists showing the target` | 351 | `results/final_sybil_posting.csv`: attacker "D · A month old and levelled up", k 200, column "default lists showing the target" |
| `final.sybil_posting.D.k200.statistics unchanged (test)` | no | `results/final_sybil_posting.csv`: attacker "D · A month old and levelled up", k 200, column "statistics unchanged (test)" |
| `final.sybil.bar` | 95 | `results/final_sybil.csv`: column "bar (top honest new group)" |
| `final.rules.Final design, all members.members` | 1983 | `results/final_rules.json`: Final design, all members > members |
| `final.rules.Final design, all members.suggestions` | 9915 | `results/final_rules.json`: Final design, all members > suggestions |
| `final.rules.Final design, all members.hard_violations` | 0 | `results/final_rules.json`: Final design, all members > hard_violations |
| `final.rules.Final design, all members.dial_checks_passed` | yes | `results/final_rules.json`: Final design, all members > dial_checks_passed |
| `final.rules.Personalisation off, all members.members` | 1983 | `results/final_rules.json`: Personalisation off, all members > members |
| `final.rules.Personalisation off, all members.suggestions` | 9915 | `results/final_rules.json`: Personalisation off, all members > suggestions |
| `final.rules.Personalisation off, all members.hard_violations` | 0 | `results/final_rules.json`: Personalisation off, all members > hard_violations |
| `final.rules.Personalisation off, all members.dial_checks_passed` | yes | `results/final_rules.json`: Personalisation off, all members > dial_checks_passed |
| `final.rules.reasons_checked` | 19830 | `results/final_rules.json`: sum of fidelity > shown, both runs |
| `final.rules.reasons_faithful` | 19830 | `results/final_rules.json`: sum of "faithful to the computed score" > true, both runs |
| `final.rules.reasons_true` | 19566 | `results/final_rules.json`: sum of "true to the raw data" > true, both runs |
| `final.rules.personal_shown` | 9745 | `results/final_rules.json`: sum of "true to the raw data, personalised lists" > shown, both runs |
| `final.rules.personal_true` | 9481 | `results/final_rules.json`: sum of "true to the raw data, personalised lists" > true, both runs |
| `final.rules.default_shown` | 10085 | `results/final_rules.json`: sum of "true to the raw data, default lists" > shown, both runs |
| `final.rules.default_true` | 10085 | `results/final_rules.json`: sum of "true to the raw data, default lists" > true, both runs |
| `final.privacy_scope.sensitivity.members removed one at a time` | 100 | `results/final_privacy_scope.json`: sensitivity > members removed one at a time |
| `final.privacy_scope.sensitivity.largest change, sizes` | 3 | `results/final_privacy_scope.json`: sensitivity > largest change, sizes |
| `final.privacy_scope.sensitivity.largest change, pairs` | 3 | `results/final_privacy_scope.json`: sensitivity > largest change, pairs |
| `final.privacy_scope.sensitivity.bound, sizes (m)` | 3 | `results/final_privacy_scope.json`: sensitivity > bound, sizes (m) |
| `final.privacy_scope.sensitivity.bound, pairs (m(m-1)/2)` | 3 | `results/final_privacy_scope.json`: sensitivity > bound, pairs (m(m-1)/2) |
| `final.privacy_scope.friends.public friends that count, of tested members (pairs)` | 6474 | `results/final_privacy_scope.json`: friends > public friends that count, of tested members (pairs) |
| `final.privacy_scope.friends.of them in more than m groups (counted in full)` | 3437 | `results/final_privacy_scope.json`: friends > of them in more than m groups (counted in full) |
| `final.privacy_scope.activity.member removed` | 1420 | `results/final_privacy_scope.json`: activity > member removed |
| `final.privacy_scope.activity.their recent posts` | 4 | `results/final_privacy_scope.json`: activity > their recent posts |
| `final.privacy_scope.activity.counts X^T X unchanged` | yes | `results/final_privacy_scope.json`: activity > counts X^T X unchanged |
| `final.privacy_scope.activity.other members whose default list changed` | 1768 | `results/final_privacy_scope.json`: activity > other members whose default list changed |
| `final.privacy_scope.shared cap.trials` | 30 | `results/final_privacy_scope.json`: shared cap > trials |
| `final.privacy_scope.shared cap.statistics unchanged in every trial` | yes | `results/final_privacy_scope.json`: shared cap > statistics unchanged in every trial |
| `final.privacy_scope.shared cap.other members whose list changed (default + personalised), mean` | 0.1667 | `results/final_privacy_scope.json`: shared cap > other members whose list changed (default + personalised), mean |
| `final.privacy_scope.shared cap.the same, most in one trial` | 5 | `results/final_privacy_scope.json`: shared cap > the same, most in one trial |
| `final.privacy_scope.shared cap.trials where some other list changed` | 1 | `results/final_privacy_scope.json`: shared cap > trials where some other list changed |
| `final.privacy_scope.shared cap.members served` | 1983 | `results/final_privacy_scope.json`: shared cap > members served |
| `final.sabotage.group_id` | 87 | `results/final_sabotage.json`: group_id |
| `final.sabotage.members (count Discover shows)` | 1 | `results/final_sabotage.json`: members (count Discover shows) |
| `final.sabotage.members who count` | 1 | `results/final_sabotage.json`: members who count |
| `final.sabotage.first fix, attacker A: fake accounts` | 9 | `results/final_sabotage.json`: first fix, attacker A: fake accounts |
| `final.sabotage.first fix, attacker A: lists before` | 130 | `results/final_sabotage.json`: first fix, attacker A: lists before |
| `final.sabotage.first fix, attacker A: lists after` | 15 | `results/final_sabotage.json`: first fix, attacker A: lists after |
| `final.sabotage.first fix, attacker A: largest gain of another group` | 11 | `results/final_sabotage.json`: first fix, attacker A: largest gain of another group |
| `final.sabotage.final, attackers A to C: statistics unchanged` | yes | `results/final_sabotage.json`: final, attackers A to C: statistics unchanged |
| `final.sabotage.final, attacker D: fake accounts` | 9 | `results/final_sabotage.json`: final, attacker D: fake accounts |
| `final.sabotage.final, attacker D: lists before` | 126 | `results/final_sabotage.json`: final, attacker D: lists before |
| `final.sabotage.final, attacker D: lists after` | 17 | `results/final_sabotage.json`: final, attacker D: lists after |
| `final.sabotage.final, attacker D: largest gain of another group` | 9 | `results/final_sabotage.json`: final, attacker D: largest gain of another group |
| `final.sabotage.final, attacker D, 4 rivals: fake accounts` | 24 | `results/final_sabotage.json`: final, attacker D, 4 rivals: fake accounts |
| `final.sabotage.final, attacker D, 4 rivals: lists the rivals lose` | 315 | `results/final_sabotage.json`: final, attacker D, 4 rivals: lists the rivals lose |
| `final.sabotage.final, attacker D, 4 rivals: largest gain of another group` | 40 | `results/final_sabotage.json`: final, attacker D, 4 rivals: largest gain of another group |
| `final.sabotage.default lists changed, any attack` | 0 | `results/final_sabotage.json`: default lists changed, any attack |
| `final.testcases.cases` | 13 | `testcases/index.csv`: rows |
| `final.testcases.intent_holds` | 13 | `testcases/index.csv`: column "intent_holds" (count) |
| `final.testcases.hard_rule_violations` | 0 | `testcases/index.csv`: column "hard_rule_violations" (sum) |

## Every number: Steps T4 to T9

| Key | Value | Source |
|---|---|---|
| `t9.quiz.5 tastes.ndcg@5` | 0.339 | `results/t9_validation.csv`: row "5 tastes", column "ndcg@5" |
| `t9.quiz.10 tastes.ndcg@5` | 0.393 | `results/t9_validation.csv`: row "10 tastes", column "ndcg@5" |
| `t9.quiz.20 tastes.ndcg@5` | 0.278 | `results/t9_validation.csv`: row "20 tastes", column "ndcg@5" |
| `t9.quiz.40 tastes.ndcg@5` | 0.119 | `results/t9_validation.csv`: row "40 tastes", column "ndcg@5" |
| `t9.clusters.purity` | 0.4867 | `results/topic_clusters_match.json`: purity |
| `t9.clusters.normalized_mutual_info` | 0.4263 | `results/topic_clusters_match.json`: normalized_mutual_info |
| `t9.clusters.adjusted_rand_index` | 0.1888 | `results/topic_clusters_match.json`: adjusted_rand_index |
| `t6.hybrid_quiz.ndcg@5` | 0.4777 | `results/hybrid_validation.csv`: row 1 (the chosen weights), column "ndcg@5" |

## Every number: E1: which method works best

| Key | Value | Source |
|---|---|---|
| `e1.random.hit_rate` | 0.048 | `results/e1_methods.csv`: row "Random (floor)", column "hit_rate" |
| `e1.random.precision@5` | 0.01 | `results/e1_methods.csv`: row "Random (floor)", column "precision@5" |
| `e1.random.recall@5` | 0.043 | `results/e1_methods.csv`: row "Random (floor)", column "recall@5" |
| `e1.random.ndcg@5` | 0.025 | `results/e1_methods.csv`: row "Random (floor)", column "ndcg@5" |
| `e1.random.newcomer_share` | 0.417 | `results/e1_methods.csv`: row "Random (floor)", column "newcomer_share" |
| `e1.random.gini` | 0.079 | `results/e1_methods.csv`: row "Random (floor)", column "gini" |
| `e1.random.coverage` | 129 | `results/e1_methods.csv`: row "Random (floor)", column "coverage" |
| `e1.random.largest_share` | 0.01 | `results/e1_methods.csv`: row "Random (floor)", column "largest_share" |
| `e1.random.topics_per_list` | 4.063 | `results/e1_methods.csv`: row "Random (floor)", column "topics_per_list" |
| `e1.popularity.hit_rate` | 0.22 | `results/e1_methods.csv`: row "Popularity (today)", column "hit_rate" |
| `e1.popularity.precision@5` | 0.044 | `results/e1_methods.csv`: row "Popularity (today)", column "precision@5" |
| `e1.popularity.recall@5` | 0.207 | `results/e1_methods.csv`: row "Popularity (today)", column "recall@5" |
| `e1.popularity.ndcg@5` | 0.131 | `results/e1_methods.csv`: row "Popularity (today)", column "ndcg@5" |
| `e1.popularity.newcomer_share` | 0 | `results/e1_methods.csv`: row "Popularity (today)", column "newcomer_share" |
| `e1.popularity.gini` | 0.953 | `results/e1_methods.csv`: row "Popularity (today)", column "gini" |
| `e1.popularity.coverage` | 10 | `results/e1_methods.csv`: row "Popularity (today)", column "coverage" |
| `e1.popularity.largest_share` | 0.174 | `results/e1_methods.csv`: row "Popularity (today)", column "largest_share" |
| `e1.popularity.topics_per_list` | 3.228 | `results/e1_methods.csv`: row "Popularity (today)", column "topics_per_list" |
| `e1.also_joined.hit_rate` | 0.64 | `results/e1_methods.csv`: row ""Also joined"", column "hit_rate" |
| `e1.also_joined.precision@5` | 0.136 | `results/e1_methods.csv`: row ""Also joined"", column "precision@5" |
| `e1.also_joined.recall@5` | 0.621 | `results/e1_methods.csv`: row ""Also joined"", column "recall@5" |
| `e1.also_joined.ndcg@5` | 0.499 | `results/e1_methods.csv`: row ""Also joined"", column "ndcg@5" |
| `e1.also_joined.newcomer_share` | 0.027 | `results/e1_methods.csv`: row ""Also joined"", column "newcomer_share" |
| `e1.also_joined.gini` | 0.599 | `results/e1_methods.csv`: row ""Also joined"", column "gini" |
| `e1.also_joined.coverage` | 94 | `results/e1_methods.csv`: row ""Also joined"", column "coverage" |
| `e1.also_joined.largest_share` | 0.031 | `results/e1_methods.csv`: row ""Also joined"", column "largest_share" |
| `e1.also_joined.topics_per_list` | 2.037 | `results/e1_methods.csv`: row ""Also joined"", column "topics_per_list" |
| `e1.descriptions.hit_rate` | 0.263 | `results/e1_methods.csv`: row "Similar descriptions", column "hit_rate" |
| `e1.descriptions.precision@5` | 0.054 | `results/e1_methods.csv`: row "Similar descriptions", column "precision@5" |
| `e1.descriptions.recall@5` | 0.247 | `results/e1_methods.csv`: row "Similar descriptions", column "recall@5" |
| `e1.descriptions.ndcg@5` | 0.159 | `results/e1_methods.csv`: row "Similar descriptions", column "ndcg@5" |
| `e1.descriptions.newcomer_share` | 0.416 | `results/e1_methods.csv`: row "Similar descriptions", column "newcomer_share" |
| `e1.descriptions.gini` | 0.502 | `results/e1_methods.csv`: row "Similar descriptions", column "gini" |
| `e1.descriptions.coverage` | 125 | `results/e1_methods.csv`: row "Similar descriptions", column "coverage" |
| `e1.descriptions.largest_share` | 0.038 | `results/e1_methods.csv`: row "Similar descriptions", column "largest_share" |
| `e1.descriptions.topics_per_list` | 1.976 | `results/e1_methods.csv`: row "Similar descriptions", column "topics_per_list" |
| `e1.hidden_tastes.hit_rate` | 0.61 | `results/e1_methods.csv`: row "Hidden tastes (AI model)", column "hit_rate" |
| `e1.hidden_tastes.precision@5` | 0.129 | `results/e1_methods.csv`: row "Hidden tastes (AI model)", column "precision@5" |
| `e1.hidden_tastes.recall@5` | 0.591 | `results/e1_methods.csv`: row "Hidden tastes (AI model)", column "recall@5" |
| `e1.hidden_tastes.ndcg@5` | 0.475 | `results/e1_methods.csv`: row "Hidden tastes (AI model)", column "ndcg@5" |
| `e1.hidden_tastes.newcomer_share` | 0.005 | `results/e1_methods.csv`: row "Hidden tastes (AI model)", column "newcomer_share" |
| `e1.hidden_tastes.gini` | 0.645 | `results/e1_methods.csv`: row "Hidden tastes (AI model)", column "gini" |
| `e1.hidden_tastes.coverage` | 76 | `results/e1_methods.csv`: row "Hidden tastes (AI model)", column "coverage" |
| `e1.hidden_tastes.largest_share` | 0.037 | `results/e1_methods.csv`: row "Hidden tastes (AI model)", column "largest_share" |
| `e1.hidden_tastes.topics_per_list` | 2.251 | `results/e1_methods.csv`: row "Hidden tastes (AI model)", column "topics_per_list" |
| `e1.hybrid.hit_rate` | 0.687 | `results/e1_methods.csv`: row "Hybrid", column "hit_rate" |
| `e1.hybrid.precision@5` | 0.146 | `results/e1_methods.csv`: row "Hybrid", column "precision@5" |
| `e1.hybrid.recall@5` | 0.668 | `results/e1_methods.csv`: row "Hybrid", column "recall@5" |
| `e1.hybrid.ndcg@5` | 0.541 | `results/e1_methods.csv`: row "Hybrid", column "ndcg@5" |
| `e1.hybrid.newcomer_share` | 0.02 | `results/e1_methods.csv`: row "Hybrid", column "newcomer_share" |
| `e1.hybrid.gini` | 0.64 | `results/e1_methods.csv`: row "Hybrid", column "gini" |
| `e1.hybrid.coverage` | 106 | `results/e1_methods.csv`: row "Hybrid", column "coverage" |
| `e1.hybrid.largest_share` | 0.038 | `results/e1_methods.csv`: row "Hybrid", column "largest_share" |
| `e1.hybrid.topics_per_list` | 2.555 | `results/e1_methods.csv`: row "Hybrid", column "topics_per_list" |
| `e1.reranked.hit_rate` | 0.656 | `results/e1_methods.csv`: row "Hybrid + fair re-ranking", column "hit_rate" |
| `e1.reranked.precision@5` | 0.139 | `results/e1_methods.csv`: row "Hybrid + fair re-ranking", column "precision@5" |
| `e1.reranked.recall@5` | 0.636 | `results/e1_methods.csv`: row "Hybrid + fair re-ranking", column "recall@5" |
| `e1.reranked.ndcg@5` | 0.528 | `results/e1_methods.csv`: row "Hybrid + fair re-ranking", column "ndcg@5" |
| `e1.reranked.newcomer_share` | 0.203 | `results/e1_methods.csv`: row "Hybrid + fair re-ranking", column "newcomer_share" |
| `e1.reranked.gini` | 0.511 | `results/e1_methods.csv`: row "Hybrid + fair re-ranking", column "gini" |
| `e1.reranked.coverage` | 125 | `results/e1_methods.csv`: row "Hybrid + fair re-ranking", column "coverage" |
| `e1.reranked.largest_share` | 0.033 | `results/e1_methods.csv`: row "Hybrid + fair re-ranking", column "largest_share" |
| `e1.reranked.topics_per_list` | 2.402 | `results/e1_methods.csv`: row "Hybrid + fair re-ranking", column "topics_per_list" |
| `e1.off.hit_rate` | 0.098 | `results/e1_methods.csv`: row "Personalisation off", column "hit_rate" |
| `e1.off.precision@5` | 0.02 | `results/e1_methods.csv`: row "Personalisation off", column "precision@5" |
| `e1.off.recall@5` | 0.091 | `results/e1_methods.csv`: row "Personalisation off", column "recall@5" |
| `e1.off.ndcg@5` | 0.058 | `results/e1_methods.csv`: row "Personalisation off", column "ndcg@5" |
| `e1.off.newcomer_share` | 0.547 | `results/e1_methods.csv`: row "Personalisation off", column "newcomer_share" |
| `e1.off.gini` | 0.921 | `results/e1_methods.csv`: row "Personalisation off", column "gini" |
| `e1.off.coverage` | 14 | `results/e1_methods.csv`: row "Personalisation off", column "coverage" |
| `e1.off.largest_share` | 0.1 | `results/e1_methods.csv`: row "Personalisation off", column "largest_share" |
| `e1.off.topics_per_list` | 4.374 | `results/e1_methods.csv`: row "Personalisation off", column "topics_per_list" |
| `e1_ci.random.hit_rate low` | 0.038 | `results/e1_methods_ci.csv`: row "Random (floor)", column "hit_rate low" |
| `e1_ci.random.hit_rate high` | 0.06 | `results/e1_methods_ci.csv`: row "Random (floor)", column "hit_rate high" |
| `e1_ci.random.ndcg@5 low` | 0.019 | `results/e1_methods_ci.csv`: row "Random (floor)", column "ndcg@5 low" |
| `e1_ci.random.ndcg@5 high` | 0.033 | `results/e1_methods_ci.csv`: row "Random (floor)", column "ndcg@5 high" |
| `e1_ci.popularity.hit_rate low` | 0.198 | `results/e1_methods_ci.csv`: row "Popularity (today)", column "hit_rate low" |
| `e1_ci.popularity.hit_rate high` | 0.243 | `results/e1_methods_ci.csv`: row "Popularity (today)", column "hit_rate high" |
| `e1_ci.popularity.ndcg@5 low` | 0.117 | `results/e1_methods_ci.csv`: row "Popularity (today)", column "ndcg@5 low" |
| `e1_ci.popularity.ndcg@5 high` | 0.146 | `results/e1_methods_ci.csv`: row "Popularity (today)", column "ndcg@5 high" |
| `e1_ci.also_joined.hit_rate low` | 0.616 | `results/e1_methods_ci.csv`: row ""Also joined"", column "hit_rate low" |
| `e1_ci.also_joined.hit_rate high` | 0.666 | `results/e1_methods_ci.csv`: row ""Also joined"", column "hit_rate high" |
| `e1_ci.also_joined.ndcg@5 low` | 0.476 | `results/e1_methods_ci.csv`: row ""Also joined"", column "ndcg@5 low" |
| `e1_ci.also_joined.ndcg@5 high` | 0.522 | `results/e1_methods_ci.csv`: row ""Also joined"", column "ndcg@5 high" |
| `e1_ci.descriptions.hit_rate low` | 0.24 | `results/e1_methods_ci.csv`: row "Similar descriptions", column "hit_rate low" |
| `e1_ci.descriptions.hit_rate high` | 0.287 | `results/e1_methods_ci.csv`: row "Similar descriptions", column "hit_rate high" |
| `e1_ci.descriptions.ndcg@5 low` | 0.144 | `results/e1_methods_ci.csv`: row "Similar descriptions", column "ndcg@5 low" |
| `e1_ci.descriptions.ndcg@5 high` | 0.176 | `results/e1_methods_ci.csv`: row "Similar descriptions", column "ndcg@5 high" |
| `e1_ci.hidden_tastes.hit_rate low` | 0.585 | `results/e1_methods_ci.csv`: row "Hidden tastes (AI model)", column "hit_rate low" |
| `e1_ci.hidden_tastes.hit_rate high` | 0.634 | `results/e1_methods_ci.csv`: row "Hidden tastes (AI model)", column "hit_rate high" |
| `e1_ci.hidden_tastes.ndcg@5 low` | 0.452 | `results/e1_methods_ci.csv`: row "Hidden tastes (AI model)", column "ndcg@5 low" |
| `e1_ci.hidden_tastes.ndcg@5 high` | 0.496 | `results/e1_methods_ci.csv`: row "Hidden tastes (AI model)", column "ndcg@5 high" |
| `e1_ci.hybrid.hit_rate low` | 0.661 | `results/e1_methods_ci.csv`: row "Hybrid", column "hit_rate low" |
| `e1_ci.hybrid.hit_rate high` | 0.711 | `results/e1_methods_ci.csv`: row "Hybrid", column "hit_rate high" |
| `e1_ci.hybrid.ndcg@5 low` | 0.517 | `results/e1_methods_ci.csv`: row "Hybrid", column "ndcg@5 low" |
| `e1_ci.hybrid.ndcg@5 high` | 0.563 | `results/e1_methods_ci.csv`: row "Hybrid", column "ndcg@5 high" |
| `e1_ci.reranked.hit_rate low` | 0.632 | `results/e1_methods_ci.csv`: row "Hybrid + fair re-ranking", column "hit_rate low" |
| `e1_ci.reranked.hit_rate high` | 0.68 | `results/e1_methods_ci.csv`: row "Hybrid + fair re-ranking", column "hit_rate high" |
| `e1_ci.reranked.ndcg@5 low` | 0.504 | `results/e1_methods_ci.csv`: row "Hybrid + fair re-ranking", column "ndcg@5 low" |
| `e1_ci.reranked.ndcg@5 high` | 0.551 | `results/e1_methods_ci.csv`: row "Hybrid + fair re-ranking", column "ndcg@5 high" |
| `e1_ci.off.hit_rate low` | 0.083 | `results/e1_methods_ci.csv`: row "Personalisation off", column "hit_rate low" |
| `e1_ci.off.hit_rate high` | 0.115 | `results/e1_methods_ci.csv`: row "Personalisation off", column "hit_rate high" |
| `e1_ci.off.ndcg@5 low` | 0.048 | `results/e1_methods_ci.csv`: row "Personalisation off", column "ndcg@5 low" |
| `e1_ci.off.ndcg@5 high` | 0.068 | `results/e1_methods_ci.csv`: row "Personalisation off", column "ndcg@5 high" |
| `e1.price_of_fairness.ndcg@5 hybrid` | 0.5407 | `results/e1_price_of_fairness.json`: ndcg@5 hybrid |
| `e1.price_of_fairness.ndcg@5 proposed` | 0.5281 | `results/e1_price_of_fairness.json`: ndcg@5 proposed |
| `e1.price_of_fairness.cost` | 0.0126 | `results/e1_price_of_fairness.json`: cost |
| `e1.price_of_fairness.cost low` | 0.0081 | `results/e1_price_of_fairness.json`: cost low |
| `e1.price_of_fairness.cost high` | 0.0171 | `results/e1_price_of_fairness.json`: cost high |
| `e1.price_of_fairness.relative cost` | 0.0233 | `results/e1_price_of_fairness.json`: relative cost |
| `e1.price_of_fairness.newcomer share hybrid` | 0.0201 | `results/e1_price_of_fairness.json`: newcomer share hybrid |
| `e1.price_of_fairness.newcomer share proposed` | 0.2027 | `results/e1_price_of_fairness.json`: newcomer share proposed |
| `e1.reasons.shared_members.Hybrid + fair re-ranking (share)` | 0.561 | `results/e1_reasons.csv`: row "shared_members", column "Hybrid + fair re-ranking (share)" |
| `e1.reasons.shared_members.Personalisation off (share)` | 0 | `results/e1_reasons.csv`: row "shared_members", column "Personalisation off (share)" |
| `e1.reasons.similar_group.Hybrid + fair re-ranking (share)` | 0.008 | `results/e1_reasons.csv`: row "similar_group", column "Hybrid + fair re-ranking (share)" |
| `e1.reasons.similar_group.Personalisation off (share)` | 0 | `results/e1_reasons.csv`: row "similar_group", column "Personalisation off (share)" |
| `e1.reasons.friend.Hybrid + fair re-ranking (share)` | 0.248 | `results/e1_reasons.csv`: row "friend", column "Hybrid + fair re-ranking (share)" |
| `e1.reasons.friend.Personalisation off (share)` | 0 | `results/e1_reasons.csv`: row "friend", column "Personalisation off (share)" |
| `e1.reasons.topic.Hybrid + fair re-ranking (share)` | 0 | `results/e1_reasons.csv`: row "topic", column "Hybrid + fair re-ranking (share)" |
| `e1.reasons.topic.Personalisation off (share)` | 0 | `results/e1_reasons.csv`: row "topic", column "Personalisation off (share)" |
| `e1.reasons.new_group.Hybrid + fair re-ranking (share)` | 0.183 | `results/e1_reasons.csv`: row "new_group", column "Hybrid + fair re-ranking (share)" |
| `e1.reasons.new_group.Personalisation off (share)` | 0.547 | `results/e1_reasons.csv`: row "new_group", column "Personalisation off (share)" |
| `e1.reasons.active.Hybrid + fair re-ranking (share)` | 0 | `results/e1_reasons.csv`: row "active", column "Hybrid + fair re-ranking (share)" |
| `e1.reasons.active.Personalisation off (share)` | 0.453 | `results/e1_reasons.csv`: row "active", column "Personalisation off (share)" |
| `e1.reasons.discover.Hybrid + fair re-ranking (share)` | 0 | `results/e1_reasons.csv`: row "discover", column "Hybrid + fair re-ranking (share)" |
| `e1.reasons.discover.Personalisation off (share)` | 0 | `results/e1_reasons.csv`: row "discover", column "Personalisation off (share)" |

## Every number: E2: what fair exposure and variety cost

| Key | Value | Source |
|---|---|---|
| `e2.recommended.q` | 0.2 | `results/e2_recommendation.json`: recommended > q |
| `e2.recommended.c` | 0.05 | `results/e2_recommendation.json`: recommended > c |
| `e2.recommended.n` | 2 | `results/e2_recommendation.json`: recommended > n |
| `e2.recommended.lam` | 0.8 | `results/e2_recommendation.json`: recommended > lam |
| `e2.budget` | 0.05 | `results/e2_recommendation.json`: budget |
| `e2.tolerance` | 0.01 | `results/e2_recommendation.json`: tolerance |
| `e2.validation.users` | 1090 | `results/e2_recommendation.json`: validation > users |
| `e2.validation.hybrid ndcg@5` | 0.4777 | `results/e2_recommendation.json`: validation > hybrid ndcg@5 |
| `e2.validation.ndcg@5` | 0.464 | `results/e2_recommendation.json`: validation > ndcg@5 |
| `e2.validation.share of the hybrid` | 0.9714 | `results/e2_recommendation.json`: validation > share of the hybrid |
| `e2.validation.newcomer_share` | 0.2006 | `results/e2_recommendation.json`: validation > newcomer_share |
| `e2.validation.topics_per_list` | 2.561 | `results/e2_recommendation.json`: validation > topics_per_list |
| `e2.test.users` | 1406 | `results/e2_recommendation.json`: test > users |
| `e2.test.hit_rate` | 0.6536 | `results/e2_recommendation.json`: test > hit_rate |
| `e2.test.precision@5` | 0.1374 | `results/e2_recommendation.json`: test > precision@5 |
| `e2.test.recall@5` | 0.6319 | `results/e2_recommendation.json`: test > recall@5 |
| `e2.test.ndcg@5` | 0.5257 | `results/e2_recommendation.json`: test > ndcg@5 |
| `e2.test.ndcg@5 low` | 0.5015 | `results/e2_recommendation.json`: test > ndcg@5 low |
| `e2.test.ndcg@5 high` | 0.5489 | `results/e2_recommendation.json`: test > ndcg@5 high |
| `e2.test.newcomer_share` | 0.2009 | `results/e2_recommendation.json`: test > newcomer_share |
| `e2.test.gini` | 0.5229 | `results/e2_recommendation.json`: test > gini |
| `e2.test.largest_share` | 0.032 | `results/e2_recommendation.json`: test > largest_share |
| `e2.test.topics_per_list` | 2.591 | `results/e2_recommendation.json`: test > topics_per_list |
| `e2.test.diversity` | 0.9495 | `results/e2_recommendation.json`: test > diversity |
| `e2.test.clusters_per_list` | 3.96 | `results/e2_recommendation.json`: test > clusters_per_list |
| `e2.test.quota_slots` | 0.1846 | `results/e2_recommendation.json`: test > quota_slots |
| `e2.test.coverage` | 126 | `results/e2_recommendation.json`: test > coverage |
| `e2.test.hybrid ndcg@5` | 0.5407 | `results/e2_recommendation.json`: test > hybrid ndcg@5 |
| `e2.test.hybrid newcomer_share` | 0.0201 | `results/e2_recommendation.json`: test > hybrid newcomer_share |
| `e2.test.cost vs hybrid` | 0.015 | `results/e2_recommendation.json`: test > cost vs hybrid |
| `e2.test.cost vs hybrid low` | 0.0096 | `results/e2_recommendation.json`: test > cost vs hybrid low |
| `e2.test.cost vs hybrid high` | 0.0203 | `results/e2_recommendation.json`: test > cost vs hybrid high |
| `e2.test.relative cost vs hybrid` | 0.0277 | `results/e2_recommendation.json`: test > relative cost vs hybrid |
| `e2.test.cost vs notebook 06 design` | 0.0024 | `results/e2_recommendation.json`: test > cost vs notebook 06 design |
| `e2.test.cost vs notebook 06 design low` | -0.002 | `results/e2_recommendation.json`: test > cost vs notebook 06 design low |
| `e2.test.cost vs notebook 06 design high` | 0.007 | `results/e2_recommendation.json`: test > cost vs notebook 06 design high |
| `e2.test.popularity ndcg@5` | 0.1311 | `results/e2_recommendation.json`: test > popularity ndcg@5 |
| `e2.test.popularity newcomer_share` | 0 | `results/e2_recommendation.json`: test > popularity newcomer_share |
| `e2.test.on the pareto front` | no | `results/e2_recommendation.json`: test > on the pareto front |
| `e2.spearman ndcg@5 validation vs test` | 0.9685 | `results/e2_recommendation.json`: spearman ndcg@5 validation vs test |
| `e2.c changes personalised lists (combinations of 60).validation` | 0 | `results/e2_recommendation.json`: c changes personalised lists (combinations of 60) > validation |
| `e2.c changes personalised lists (combinations of 60).test` | 0 | `results/e2_recommendation.json`: c changes personalised lists (combinations of 60) > test |
| `e2.dial.q.value` | 0.2 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > value |
| `e2.dial.q.switched off` | 0 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > switched off |
| `e2.dial.q.ndcg@5 off` | 0.5401 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > ndcg@5 off |
| `e2.dial.q.ndcg@5 on` | 0.5257 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > ndcg@5 on |
| `e2.dial.q.cost` | 0.0144 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > cost |
| `e2.dial.q.cost low` | 0.0104 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > cost low |
| `e2.dial.q.cost high` | 0.0188 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > cost high |
| `e2.dial.q.relative cost` | 0.0267 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > relative cost |
| `e2.dial.q.newcomer_share off` | 0.0162 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > newcomer_share off |
| `e2.dial.q.gini off` | 0.6556 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > gini off |
| `e2.dial.q.coverage off` | 108 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > coverage off |
| `e2.dial.q.largest_share off` | 0.0408 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > largest_share off |
| `e2.dial.q.topics_per_list off` | 2.853 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > topics_per_list off |
| `e2.dial.q.diversity off` | 0.9479 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > diversity off |
| `e2.dial.q.newcomer_share on` | 0.2009 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > newcomer_share on |
| `e2.dial.q.gini on` | 0.5229 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > gini on |
| `e2.dial.q.coverage on` | 126 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > coverage on |
| `e2.dial.q.largest_share on` | 0.032 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > largest_share on |
| `e2.dial.q.topics_per_list on` | 2.591 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > topics_per_list on |
| `e2.dial.q.diversity on` | 0.9495 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > q > diversity on |
| `e2.dial.c.value` | 0.05 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > value |
| `e2.dial.c.ndcg@5 off` | 0.0253 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > ndcg@5 off |
| `e2.dial.c.ndcg@5 on` | 0.065 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > ndcg@5 on |
| `e2.dial.c.cost` | -0.0397 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > cost |
| `e2.dial.c.cost low` | -0.0509 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > cost low |
| `e2.dial.c.cost high` | -0.0282 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > cost high |
| `e2.dial.c.relative cost` | -1.572 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > relative cost |
| `e2.dial.c.newcomer_share off` | 0.7991 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > newcomer_share off |
| `e2.dial.c.gini off` | 0.9607 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > gini off |
| `e2.dial.c.coverage off` | 8 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > coverage off |
| `e2.dial.c.largest_share off` | 0.1999 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > largest_share off |
| `e2.dial.c.topics_per_list off` | 4.159 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > topics_per_list off |
| `e2.dial.c.newcomer_share on` | 0.4908 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > newcomer_share on |
| `e2.dial.c.gini on` | 0.844 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > gini on |
| `e2.dial.c.coverage on` | 23 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > coverage on |
| `e2.dial.c.largest_share on` | 0.0499 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > largest_share on |
| `e2.dial.c.topics_per_list on` | 3.807 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > c > topics_per_list on |
| `e2.dial.n.value` | 2 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > value |
| `e2.dial.n.switched off` | 5 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > switched off |
| `e2.dial.n.ndcg@5 off` | 0.5265 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > ndcg@5 off |
| `e2.dial.n.ndcg@5 on` | 0.5257 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > ndcg@5 on |
| `e2.dial.n.cost` | 0.0008 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > cost |
| `e2.dial.n.cost low` | -0.0013 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > cost low |
| `e2.dial.n.cost high` | 0.003 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > cost high |
| `e2.dial.n.relative cost` | 0.0015 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > relative cost |
| `e2.dial.n.newcomer_share off` | 0.2009 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > newcomer_share off |
| `e2.dial.n.gini off` | 0.5209 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > gini off |
| `e2.dial.n.coverage off` | 127 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > coverage off |
| `e2.dial.n.largest_share off` | 0.0316 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > largest_share off |
| `e2.dial.n.topics_per_list off` | 2.518 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > topics_per_list off |
| `e2.dial.n.diversity off` | 0.9403 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > diversity off |
| `e2.dial.n.newcomer_share on` | 0.2009 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > newcomer_share on |
| `e2.dial.n.gini on` | 0.5229 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > gini on |
| `e2.dial.n.coverage on` | 126 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > coverage on |
| `e2.dial.n.largest_share on` | 0.032 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > largest_share on |
| `e2.dial.n.topics_per_list on` | 2.591 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > topics_per_list on |
| `e2.dial.n.diversity on` | 0.9495 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > n > diversity on |
| `e2.dial.lam.value` | 0.8 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > value |
| `e2.dial.lam.switched off` | 1 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > switched off |
| `e2.dial.lam.ndcg@5 off` | 0.5281 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > ndcg@5 off |
| `e2.dial.lam.ndcg@5 on` | 0.5257 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > ndcg@5 on |
| `e2.dial.lam.cost` | 0.0024 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > cost |
| `e2.dial.lam.cost low` | -0.002 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > cost low |
| `e2.dial.lam.cost high` | 0.007 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > cost high |
| `e2.dial.lam.relative cost` | 0.0045 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > relative cost |
| `e2.dial.lam.newcomer_share off` | 0.2027 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > newcomer_share off |
| `e2.dial.lam.gini off` | 0.5112 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > gini off |
| `e2.dial.lam.coverage off` | 125 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > coverage off |
| `e2.dial.lam.largest_share off` | 0.0331 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > largest_share off |
| `e2.dial.lam.topics_per_list off` | 2.402 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > topics_per_list off |
| `e2.dial.lam.diversity off` | 0.9216 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > diversity off |
| `e2.dial.lam.newcomer_share on` | 0.2009 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > newcomer_share on |
| `e2.dial.lam.gini on` | 0.5229 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > gini on |
| `e2.dial.lam.coverage on` | 126 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > coverage on |
| `e2.dial.lam.largest_share on` | 0.032 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > largest_share on |
| `e2.dial.lam.topics_per_list on` | 2.591 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > topics_per_list on |
| `e2.dial.lam.diversity on` | 0.9495 | `results/e2_recommendation.json`: dials (test; each against the recommended setting with only that dial switched off) > lam > diversity on |
| `e2.table.Popularity (today's BOING).ndcg@5` | 0.1311 | `results/e2_table.csv`: row "Popularity (today's BOING)", column "ndcg@5" |
| `e2.table.Popularity (today's BOING).hit_rate` | 0.2205 | `results/e2_table.csv`: row "Popularity (today's BOING)", column "hit_rate" |
| `e2.table.Popularity (today's BOING).newcomer_share` | 0 | `results/e2_table.csv`: row "Popularity (today's BOING)", column "newcomer_share" |
| `e2.table.Popularity (today's BOING).gini` | 0.9534 | `results/e2_table.csv`: row "Popularity (today's BOING)", column "gini" |
| `e2.table.Popularity (today's BOING).coverage` | 10 | `results/e2_table.csv`: row "Popularity (today's BOING)", column "coverage" |
| `e2.table.Popularity (today's BOING).topics_per_list` | 3.228 | `results/e2_table.csv`: row "Popularity (today's BOING)", column "topics_per_list" |
| `e2.table.Hybrid, no re-ranking.q` | 0 | `results/e2_table.csv`: row "Hybrid, no re-ranking", column "q" |
| `e2.table.Hybrid, no re-ranking.n` | 5 | `results/e2_table.csv`: row "Hybrid, no re-ranking", column "n" |
| `e2.table.Hybrid, no re-ranking.lam` | 1 | `results/e2_table.csv`: row "Hybrid, no re-ranking", column "lam" |
| `e2.table.Hybrid, no re-ranking.ndcg@5` | 0.5407 | `results/e2_table.csv`: row "Hybrid, no re-ranking", column "ndcg@5" |
| `e2.table.Hybrid, no re-ranking.hit_rate` | 0.6871 | `results/e2_table.csv`: row "Hybrid, no re-ranking", column "hit_rate" |
| `e2.table.Hybrid, no re-ranking.newcomer_share` | 0.0201 | `results/e2_table.csv`: row "Hybrid, no re-ranking", column "newcomer_share" |
| `e2.table.Hybrid, no re-ranking.gini` | 0.6402 | `results/e2_table.csv`: row "Hybrid, no re-ranking", column "gini" |
| `e2.table.Hybrid, no re-ranking.coverage` | 106 | `results/e2_table.csv`: row "Hybrid, no re-ranking", column "coverage" |
| `e2.table.Hybrid, no re-ranking.topics_per_list` | 2.555 | `results/e2_table.csv`: row "Hybrid, no re-ranking", column "topics_per_list" |
| `e2.table.Hybrid, no re-ranking.cost` | 0 | `results/e2_table.csv`: row "Hybrid, no re-ranking", column "cost" |
| `e2.table.Hybrid, no re-ranking.cost low` | 0 | `results/e2_table.csv`: row "Hybrid, no re-ranking", column "cost low" |
| `e2.table.Hybrid, no re-ranking.cost high` | 0 | `results/e2_table.csv`: row "Hybrid, no re-ranking", column "cost high" |
| `e2.table.Hybrid, no re-ranking.relative cost` | 0 | `results/e2_table.csv`: row "Hybrid, no re-ranking", column "relative cost" |
| `e2.table.Quota only (q = 20%).q` | 0.2 | `results/e2_table.csv`: row "Quota only (q = 20%)", column "q" |
| `e2.table.Quota only (q = 20%).n` | 5 | `results/e2_table.csv`: row "Quota only (q = 20%)", column "n" |
| `e2.table.Quota only (q = 20%).lam` | 1 | `results/e2_table.csv`: row "Quota only (q = 20%)", column "lam" |
| `e2.table.Quota only (q = 20%).ndcg@5` | 0.5284 | `results/e2_table.csv`: row "Quota only (q = 20%)", column "ndcg@5" |
| `e2.table.Quota only (q = 20%).hit_rate` | 0.6579 | `results/e2_table.csv`: row "Quota only (q = 20%)", column "hit_rate" |
| `e2.table.Quota only (q = 20%).newcomer_share` | 0.2027 | `results/e2_table.csv`: row "Quota only (q = 20%)", column "newcomer_share" |
| `e2.table.Quota only (q = 20%).gini` | 0.5209 | `results/e2_table.csv`: row "Quota only (q = 20%)", column "gini" |
| `e2.table.Quota only (q = 20%).coverage` | 124 | `results/e2_table.csv`: row "Quota only (q = 20%)", column "coverage" |
| `e2.table.Quota only (q = 20%).topics_per_list` | 2.289 | `results/e2_table.csv`: row "Quota only (q = 20%)", column "topics_per_list" |
| `e2.table.Quota only (q = 20%).cost` | 0.0123 | `results/e2_table.csv`: row "Quota only (q = 20%)", column "cost" |
| `e2.table.Quota only (q = 20%).cost low` | 0.0084 | `results/e2_table.csv`: row "Quota only (q = 20%)", column "cost low" |
| `e2.table.Quota only (q = 20%).cost high` | 0.0164 | `results/e2_table.csv`: row "Quota only (q = 20%)", column "cost high" |
| `e2.table.Quota only (q = 20%).relative cost` | 0.0228 | `results/e2_table.csv`: row "Quota only (q = 20%)", column "relative cost" |
| `e2.table.Recommended (E2).q` | 0.2 | `results/e2_table.csv`: row "Recommended (E2)", column "q" |
| `e2.table.Recommended (E2).n` | 2 | `results/e2_table.csv`: row "Recommended (E2)", column "n" |
| `e2.table.Recommended (E2).lam` | 0.8 | `results/e2_table.csv`: row "Recommended (E2)", column "lam" |
| `e2.table.Recommended (E2).ndcg@5` | 0.5257 | `results/e2_table.csv`: row "Recommended (E2)", column "ndcg@5" |
| `e2.table.Recommended (E2).hit_rate` | 0.6536 | `results/e2_table.csv`: row "Recommended (E2)", column "hit_rate" |
| `e2.table.Recommended (E2).newcomer_share` | 0.2009 | `results/e2_table.csv`: row "Recommended (E2)", column "newcomer_share" |
| `e2.table.Recommended (E2).gini` | 0.5229 | `results/e2_table.csv`: row "Recommended (E2)", column "gini" |
| `e2.table.Recommended (E2).coverage` | 126 | `results/e2_table.csv`: row "Recommended (E2)", column "coverage" |
| `e2.table.Recommended (E2).topics_per_list` | 2.591 | `results/e2_table.csv`: row "Recommended (E2)", column "topics_per_list" |
| `e2.table.Recommended (E2).cost` | 0.015 | `results/e2_table.csv`: row "Recommended (E2)", column "cost" |
| `e2.table.Recommended (E2).cost low` | 0.0096 | `results/e2_table.csv`: row "Recommended (E2)", column "cost low" |
| `e2.table.Recommended (E2).cost high` | 0.0203 | `results/e2_table.csv`: row "Recommended (E2)", column "cost high" |
| `e2.table.Recommended (E2).relative cost` | 0.0277 | `results/e2_table.csv`: row "Recommended (E2)", column "relative cost" |
| `e2.table.Design of notebook 06 (E1).q` | 0.2 | `results/e2_table.csv`: row "Design of notebook 06 (E1)", column "q" |
| `e2.table.Design of notebook 06 (E1).n` | 2 | `results/e2_table.csv`: row "Design of notebook 06 (E1)", column "n" |
| `e2.table.Design of notebook 06 (E1).lam` | 1 | `results/e2_table.csv`: row "Design of notebook 06 (E1)", column "lam" |
| `e2.table.Design of notebook 06 (E1).ndcg@5` | 0.5281 | `results/e2_table.csv`: row "Design of notebook 06 (E1)", column "ndcg@5" |
| `e2.table.Design of notebook 06 (E1).hit_rate` | 0.6565 | `results/e2_table.csv`: row "Design of notebook 06 (E1)", column "hit_rate" |
| `e2.table.Design of notebook 06 (E1).newcomer_share` | 0.2027 | `results/e2_table.csv`: row "Design of notebook 06 (E1)", column "newcomer_share" |
| `e2.table.Design of notebook 06 (E1).gini` | 0.5112 | `results/e2_table.csv`: row "Design of notebook 06 (E1)", column "gini" |
| `e2.table.Design of notebook 06 (E1).coverage` | 125 | `results/e2_table.csv`: row "Design of notebook 06 (E1)", column "coverage" |
| `e2.table.Design of notebook 06 (E1).topics_per_list` | 2.402 | `results/e2_table.csv`: row "Design of notebook 06 (E1)", column "topics_per_list" |
| `e2.table.Design of notebook 06 (E1).cost` | 0.0126 | `results/e2_table.csv`: row "Design of notebook 06 (E1)", column "cost" |
| `e2.table.Design of notebook 06 (E1).cost low` | 0.0081 | `results/e2_table.csv`: row "Design of notebook 06 (E1)", column "cost low" |
| `e2.table.Design of notebook 06 (E1).cost high` | 0.0171 | `results/e2_table.csv`: row "Design of notebook 06 (E1)", column "cost high" |
| `e2.table.Design of notebook 06 (E1).relative cost` | 0.0233 | `results/e2_table.csv`: row "Design of notebook 06 (E1)", column "relative cost" |
| `e2.table.More quota (q = 40%).q` | 0.4 | `results/e2_table.csv`: row "More quota (q = 40%)", column "q" |
| `e2.table.More quota (q = 40%).n` | 2 | `results/e2_table.csv`: row "More quota (q = 40%)", column "n" |
| `e2.table.More quota (q = 40%).lam` | 0.8 | `results/e2_table.csv`: row "More quota (q = 40%)", column "lam" |
| `e2.table.More quota (q = 40%).ndcg@5` | 0.504 | `results/e2_table.csv`: row "More quota (q = 40%)", column "ndcg@5" |
| `e2.table.More quota (q = 40%).hit_rate` | 0.6038 | `results/e2_table.csv`: row "More quota (q = 40%)", column "hit_rate" |
| `e2.table.More quota (q = 40%).newcomer_share` | 0.4 | `results/e2_table.csv`: row "More quota (q = 40%)", column "newcomer_share" |
| `e2.table.More quota (q = 40%).gini` | 0.4679 | `results/e2_table.csv`: row "More quota (q = 40%)", column "gini" |
| `e2.table.More quota (q = 40%).coverage` | 126 | `results/e2_table.csv`: row "More quota (q = 40%)", column "coverage" |
| `e2.table.More quota (q = 40%).topics_per_list` | 2.464 | `results/e2_table.csv`: row "More quota (q = 40%)", column "topics_per_list" |
| `e2.table.More quota (q = 40%).cost` | 0.0367 | `results/e2_table.csv`: row "More quota (q = 40%)", column "cost" |
| `e2.table.More quota (q = 40%).cost low` | 0.0297 | `results/e2_table.csv`: row "More quota (q = 40%)", column "cost low" |
| `e2.table.More quota (q = 40%).cost high` | 0.0436 | `results/e2_table.csv`: row "More quota (q = 40%)", column "cost high" |
| `e2.table.More quota (q = 40%).relative cost` | 0.0679 | `results/e2_table.csv`: row "More quota (q = 40%)", column "relative cost" |
| `e2.table.Most variety (λ = 0.5).q` | 0.2 | `results/e2_table.csv`: row "Most variety (λ = 0.5)", column "q" |
| `e2.table.Most variety (λ = 0.5).n` | 2 | `results/e2_table.csv`: row "Most variety (λ = 0.5)", column "n" |
| `e2.table.Most variety (λ = 0.5).lam` | 0.5 | `results/e2_table.csv`: row "Most variety (λ = 0.5)", column "lam" |
| `e2.table.Most variety (λ = 0.5).ndcg@5` | 0.5153 | `results/e2_table.csv`: row "Most variety (λ = 0.5)", column "ndcg@5" |
| `e2.table.Most variety (λ = 0.5).hit_rate` | 0.6366 | `results/e2_table.csv`: row "Most variety (λ = 0.5)", column "hit_rate" |
| `e2.table.Most variety (λ = 0.5).newcomer_share` | 0.201 | `results/e2_table.csv`: row "Most variety (λ = 0.5)", column "newcomer_share" |
| `e2.table.Most variety (λ = 0.5).gini` | 0.5248 | `results/e2_table.csv`: row "Most variety (λ = 0.5)", column "gini" |
| `e2.table.Most variety (λ = 0.5).coverage` | 128 | `results/e2_table.csv`: row "Most variety (λ = 0.5)", column "coverage" |
| `e2.table.Most variety (λ = 0.5).topics_per_list` | 2.996 | `results/e2_table.csv`: row "Most variety (λ = 0.5)", column "topics_per_list" |
| `e2.table.Most variety (λ = 0.5).cost` | 0.0254 | `results/e2_table.csv`: row "Most variety (λ = 0.5)", column "cost" |
| `e2.table.Most variety (λ = 0.5).cost low` | 0.0181 | `results/e2_table.csv`: row "Most variety (λ = 0.5)", column "cost low" |
| `e2.table.Most variety (λ = 0.5).cost high` | 0.0331 | `results/e2_table.csv`: row "Most variety (λ = 0.5)", column "cost high" |
| `e2.table.Most variety (λ = 0.5).relative cost` | 0.047 | `results/e2_table.csv`: row "Most variety (λ = 0.5)", column "relative cost" |

## Every number: E3: what privacy costs

| Key | Value | Source |
|---|---|---|
| `e3.curve.eps0.1.m3.ndcg@5` | 0.2599 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 3.0, column "ndcg@5" |
| `e3.curve.eps0.1.m3.ndcg@5 sd` | 0.0183 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 3.0, column "ndcg@5 sd" |
| `e3.curve.eps0.1.m3.newcomer_share` | 0.2369 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 3.0, column "newcomer_share" |
| `e3.curve.eps0.1.m3.hit_rate` | 0.3986 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 3.0, column "hit_rate" |
| `e3.curve.eps0.1.m3.accuracy kept` | 0.4922 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 3.0, column "accuracy kept" |
| `e3.curve.eps0.1.m3.newcomer slots kept` | 1.169 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 3.0, column "newcomer slots kept" |
| `e3.curve.eps0.1.m5.ndcg@5` | 0.2385 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 5.0, column "ndcg@5" |
| `e3.curve.eps0.1.m5.ndcg@5 sd` | 0.0208 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 5.0, column "ndcg@5 sd" |
| `e3.curve.eps0.1.m5.newcomer_share` | 0.2621 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 5.0, column "newcomer_share" |
| `e3.curve.eps0.1.m5.hit_rate` | 0.3656 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 5.0, column "hit_rate" |
| `e3.curve.eps0.1.m5.accuracy kept` | 0.4515 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 5.0, column "accuracy kept" |
| `e3.curve.eps0.1.m5.newcomer slots kept` | 1.293 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 5.0, column "newcomer slots kept" |
| `e3.curve.eps0.1.m8.ndcg@5` | 0.2169 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 8.0, column "ndcg@5" |
| `e3.curve.eps0.1.m8.ndcg@5 sd` | 0.0143 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 8.0, column "ndcg@5 sd" |
| `e3.curve.eps0.1.m8.newcomer_share` | 0.2907 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 8.0, column "newcomer_share" |
| `e3.curve.eps0.1.m8.hit_rate` | 0.332 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 8.0, column "hit_rate" |
| `e3.curve.eps0.1.m8.accuracy kept` | 0.4107 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 8.0, column "accuracy kept" |
| `e3.curve.eps0.1.m8.newcomer slots kept` | 1.434 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.1, m 8.0, column "newcomer slots kept" |
| `e3.curve.eps0.5.m3.ndcg@5` | 0.4081 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 3.0, column "ndcg@5" |
| `e3.curve.eps0.5.m3.ndcg@5 sd` | 0.0108 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 3.0, column "ndcg@5 sd" |
| `e3.curve.eps0.5.m3.newcomer_share` | 0.2194 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 3.0, column "newcomer_share" |
| `e3.curve.eps0.5.m3.hit_rate` | 0.5281 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 3.0, column "hit_rate" |
| `e3.curve.eps0.5.m3.accuracy kept` | 0.7728 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 3.0, column "accuracy kept" |
| `e3.curve.eps0.5.m3.newcomer slots kept` | 1.082 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 3.0, column "newcomer slots kept" |
| `e3.curve.eps0.5.m5.ndcg@5` | 0.3625 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 5.0, column "ndcg@5" |
| `e3.curve.eps0.5.m5.ndcg@5 sd` | 0.0139 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 5.0, column "ndcg@5 sd" |
| `e3.curve.eps0.5.m5.newcomer_share` | 0.2249 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 5.0, column "newcomer_share" |
| `e3.curve.eps0.5.m5.hit_rate` | 0.482 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 5.0, column "hit_rate" |
| `e3.curve.eps0.5.m5.accuracy kept` | 0.6864 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 5.0, column "accuracy kept" |
| `e3.curve.eps0.5.m5.newcomer slots kept` | 1.11 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 5.0, column "newcomer slots kept" |
| `e3.curve.eps0.5.m8.ndcg@5` | 0.2871 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 8.0, column "ndcg@5" |
| `e3.curve.eps0.5.m8.ndcg@5 sd` | 0.0162 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 8.0, column "ndcg@5 sd" |
| `e3.curve.eps0.5.m8.newcomer_share` | 0.2436 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 8.0, column "newcomer_share" |
| `e3.curve.eps0.5.m8.hit_rate` | 0.4063 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 8.0, column "hit_rate" |
| `e3.curve.eps0.5.m8.accuracy kept` | 0.5437 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 8.0, column "accuracy kept" |
| `e3.curve.eps0.5.m8.newcomer slots kept` | 1.202 | `results/e3_privacy.csv`: design "with privacy noise", eps 0.5, m 8.0, column "newcomer slots kept" |
| `e3.curve.eps1.m3.ndcg@5` | 0.461 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 3.0, column "ndcg@5" |
| `e3.curve.eps1.m3.ndcg@5 sd` | 0.0091 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 3.0, column "ndcg@5 sd" |
| `e3.curve.eps1.m3.newcomer_share` | 0.199 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 3.0, column "newcomer_share" |
| `e3.curve.eps1.m3.hit_rate` | 0.5829 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 3.0, column "hit_rate" |
| `e3.curve.eps1.m3.accuracy kept` | 0.8728 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 3.0, column "accuracy kept" |
| `e3.curve.eps1.m3.newcomer slots kept` | 0.9819 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 3.0, column "newcomer slots kept" |
| `e3.curve.eps1.m5.ndcg@5` | 0.4337 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 5.0, column "ndcg@5" |
| `e3.curve.eps1.m5.ndcg@5 sd` | 0.0116 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 5.0, column "ndcg@5 sd" |
| `e3.curve.eps1.m5.newcomer_share` | 0.2176 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 5.0, column "newcomer_share" |
| `e3.curve.eps1.m5.hit_rate` | 0.5509 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 5.0, column "hit_rate" |
| `e3.curve.eps1.m5.accuracy kept` | 0.8212 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 5.0, column "accuracy kept" |
| `e3.curve.eps1.m5.newcomer slots kept` | 1.074 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 5.0, column "newcomer slots kept" |
| `e3.curve.eps1.m8.ndcg@5` | 0.3508 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 8.0, column "ndcg@5" |
| `e3.curve.eps1.m8.ndcg@5 sd` | 0.0156 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 8.0, column "ndcg@5 sd" |
| `e3.curve.eps1.m8.newcomer_share` | 0.2269 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 8.0, column "newcomer_share" |
| `e3.curve.eps1.m8.hit_rate` | 0.4669 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 8.0, column "hit_rate" |
| `e3.curve.eps1.m8.accuracy kept` | 0.6643 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 8.0, column "accuracy kept" |
| `e3.curve.eps1.m8.newcomer slots kept` | 1.12 | `results/e3_privacy.csv`: design "with privacy noise", eps 1.0, m 8.0, column "newcomer slots kept" |
| `e3.curve.eps2.m3.ndcg@5` | 0.4951 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 3.0, column "ndcg@5" |
| `e3.curve.eps2.m3.ndcg@5 sd` | 0.003 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 3.0, column "ndcg@5 sd" |
| `e3.curve.eps2.m3.newcomer_share` | 0.1777 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 3.0, column "newcomer_share" |
| `e3.curve.eps2.m3.hit_rate` | 0.6213 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 3.0, column "hit_rate" |
| `e3.curve.eps2.m3.accuracy kept` | 0.9375 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 3.0, column "accuracy kept" |
| `e3.curve.eps2.m3.newcomer slots kept` | 0.8766 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 3.0, column "newcomer slots kept" |
| `e3.curve.eps2.m5.ndcg@5` | 0.4819 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 5.0, column "ndcg@5" |
| `e3.curve.eps2.m5.ndcg@5 sd` | 0.0071 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 5.0, column "ndcg@5 sd" |
| `e3.curve.eps2.m5.newcomer_share` | 0.2023 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 5.0, column "newcomer_share" |
| `e3.curve.eps2.m5.hit_rate` | 0.6004 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 5.0, column "hit_rate" |
| `e3.curve.eps2.m5.accuracy kept` | 0.9124 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 5.0, column "accuracy kept" |
| `e3.curve.eps2.m5.newcomer slots kept` | 0.9979 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 5.0, column "newcomer slots kept" |
| `e3.curve.eps2.m8.ndcg@5` | 0.4189 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 8.0, column "ndcg@5" |
| `e3.curve.eps2.m8.ndcg@5 sd` | 0.012 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 8.0, column "ndcg@5 sd" |
| `e3.curve.eps2.m8.newcomer_share` | 0.2133 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 8.0, column "newcomer_share" |
| `e3.curve.eps2.m8.hit_rate` | 0.5352 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 8.0, column "hit_rate" |
| `e3.curve.eps2.m8.accuracy kept` | 0.7932 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 8.0, column "accuracy kept" |
| `e3.curve.eps2.m8.newcomer slots kept` | 1.052 | `results/e3_privacy.csv`: design "with privacy noise", eps 2.0, m 8.0, column "newcomer slots kept" |
| `e3.curve.eps5.m3.ndcg@5` | 0.5162 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 3.0, column "ndcg@5" |
| `e3.curve.eps5.m3.ndcg@5 sd` | 0.0032 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 3.0, column "ndcg@5 sd" |
| `e3.curve.eps5.m3.newcomer_share` | 0.1595 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 3.0, column "newcomer_share" |
| `e3.curve.eps5.m3.hit_rate` | 0.6476 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 3.0, column "hit_rate" |
| `e3.curve.eps5.m3.accuracy kept` | 0.9774 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 3.0, column "accuracy kept" |
| `e3.curve.eps5.m3.newcomer slots kept` | 0.7869 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 3.0, column "newcomer slots kept" |
| `e3.curve.eps5.m5.ndcg@5` | 0.5164 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 5.0, column "ndcg@5" |
| `e3.curve.eps5.m5.ndcg@5 sd` | 0.002 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 5.0, column "ndcg@5 sd" |
| `e3.curve.eps5.m5.newcomer_share` | 0.1929 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 5.0, column "newcomer_share" |
| `e3.curve.eps5.m5.hit_rate` | 0.6408 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 5.0, column "hit_rate" |
| `e3.curve.eps5.m5.accuracy kept` | 0.9778 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 5.0, column "accuracy kept" |
| `e3.curve.eps5.m5.newcomer slots kept` | 0.9518 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 5.0, column "newcomer slots kept" |
| `e3.curve.eps5.m8.ndcg@5` | 0.4848 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 8.0, column "ndcg@5" |
| `e3.curve.eps5.m8.ndcg@5 sd` | 0.0056 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 8.0, column "ndcg@5 sd" |
| `e3.curve.eps5.m8.newcomer_share` | 0.2015 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 8.0, column "newcomer_share" |
| `e3.curve.eps5.m8.hit_rate` | 0.6033 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 8.0, column "hit_rate" |
| `e3.curve.eps5.m8.accuracy kept` | 0.918 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 8.0, column "accuracy kept" |
| `e3.curve.eps5.m8.newcomer slots kept` | 0.994 | `results/e3_privacy.csv`: design "with privacy noise", eps 5.0, m 8.0, column "newcomer slots kept" |
| `e3.curve.clip.m3.ndcg@5` | 0.526 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 3.0, column "ndcg@5" |
| `e3.curve.clip.m3.ndcg@5 sd` | 0.0031 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 3.0, column "ndcg@5 sd" |
| `e3.curve.clip.m3.newcomer_share` | 0.1322 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 3.0, column "newcomer_share" |
| `e3.curve.clip.m3.hit_rate` | 0.6599 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 3.0, column "hit_rate" |
| `e3.curve.clip.m3.accuracy kept` | 0.996 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 3.0, column "accuracy kept" |
| `e3.curve.clip.m3.newcomer slots kept` | 0.6521 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 3.0, column "newcomer slots kept" |
| `e3.curve.clip.m5.ndcg@5` | 0.5299 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 5.0, column "ndcg@5" |
| `e3.curve.clip.m5.ndcg@5 sd` | 0.0022 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 5.0, column "ndcg@5 sd" |
| `e3.curve.clip.m5.newcomer_share` | 0.1918 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 5.0, column "newcomer_share" |
| `e3.curve.clip.m5.hit_rate` | 0.6595 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 5.0, column "hit_rate" |
| `e3.curve.clip.m5.accuracy kept` | 1.004 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 5.0, column "accuracy kept" |
| `e3.curve.clip.m5.newcomer slots kept` | 0.946 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 5.0, column "newcomer slots kept" |
| `e3.curve.clip.m8.ndcg@5` | 0.5281 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 8.0, column "ndcg@5" |
| `e3.curve.clip.m8.ndcg@5 sd` | 0 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 8.0, column "ndcg@5 sd" |
| `e3.curve.clip.m8.newcomer_share` | 0.2027 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 8.0, column "newcomer_share" |
| `e3.curve.clip.m8.hit_rate` | 0.6565 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 8.0, column "hit_rate" |
| `e3.curve.clip.m8.accuracy kept` | 1 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 8.0, column "accuracy kept" |
| `e3.curve.clip.m8.newcomer slots kept` | 1 | `results/e3_privacy.csv`: design "clipping only (no noise)", eps inf, m 8.0, column "newcomer slots kept" |
| `e3.curve.no_privacy.ndcg@5` | 0.5281 | `results/e3_privacy.csv`: design "no privacy (proposed design)", eps inf, m nan, column "ndcg@5" |
| `e3.curve.no_privacy.newcomer_share` | 0.2027 | `results/e3_privacy.csv`: design "no privacy (proposed design)", eps inf, m nan, column "newcomer_share" |
| `e3.curve.no_privacy.hit_rate` | 0.6565 | `results/e3_privacy.csv`: design "no privacy (proposed design)", eps inf, m nan, column "hit_rate" |
| `e3.curve.no_privacy.accuracy kept` | 1 | `results/e3_privacy.csv`: design "no privacy (proposed design)", eps inf, m nan, column "accuracy kept" |
| `e3.curve.no_privacy.newcomer slots kept` | 1 | `results/e3_privacy.csv`: design "no privacy (proposed design)", eps inf, m nan, column "newcomer slots kept" |
| `e3.curve.no_statistics_about_others.ndcg@5` | 0.4239 | `results/e3_privacy.csv`: design "no statistics about others", eps nan, m nan, column "ndcg@5" |
| `e3.curve.no_statistics_about_others.newcomer_share` | 0.2411 | `results/e3_privacy.csv`: design "no statistics about others", eps nan, m nan, column "newcomer_share" |
| `e3.curve.no_statistics_about_others.hit_rate` | 0.542 | `results/e3_privacy.csv`: design "no statistics about others", eps nan, m nan, column "hit_rate" |
| `e3.curve.no_statistics_about_others.accuracy kept` | 0.8026 | `results/e3_privacy.csv`: design "no statistics about others", eps nan, m nan, column "accuracy kept" |
| `e3.curve.no_statistics_about_others.newcomer slots kept` | 1.19 | `results/e3_privacy.csv`: design "no statistics about others", eps nan, m nan, column "newcomer slots kept" |
| `e3.curve.popularity.ndcg@5` | 0.1311 | `results/e3_privacy.csv`: design "popularity (today)", eps nan, m nan, column "ndcg@5" |
| `e3.curve.popularity.newcomer_share` | 0 | `results/e3_privacy.csv`: design "popularity (today)", eps nan, m nan, column "newcomer_share" |
| `e3.curve.popularity.hit_rate` | 0.2205 | `results/e3_privacy.csv`: design "popularity (today)", eps nan, m nan, column "hit_rate" |
| `e3.curve.popularity.accuracy kept` | 0.2483 | `results/e3_privacy.csv`: design "popularity (today)", eps nan, m nan, column "accuracy kept" |
| `e3.curve.popularity.newcomer slots kept` | 0 | `results/e3_privacy.csv`: design "popularity (today)", eps nan, m nan, column "newcomer slots kept" |
| `e3.eps` | 2 | `results/e3_recommendation.json`: eps |
| `e3.m` | 3 | `results/e3_recommendation.json`: m |
| `e3.size_share` | 0.25 | `results/e3_recommendation.json`: size_share |
| `e3.odds_bound_e_to_eps` | 7.389 | `results/e3_recommendation.json`: odds_bound_e_to_eps |
| `e3.noise_scale_sizes` | 6 | `results/e3_recommendation.json`: noise_scale_sizes |
| `e3.noise_scale_pairs` | 2 | `results/e3_recommendation.json`: noise_scale_pairs |
| `e3.memberships_kept_by_clipping` | 0.7441 | `results/e3_recommendation.json`: memberships_kept_by_clipping |
| `e3.quiz.ndcg@5` | 0.4227 | `results/e3_recommendation.json`: quiz > ndcg@5 |
| `e3.quiz.ndcg@5 sd` | 0.0045 | `results/e3_recommendation.json`: quiz > ndcg@5 sd |
| `e3.quiz.newcomer_share` | 0.1926 | `results/e3_recommendation.json`: quiz > newcomer_share |
| `e3.quiz.accuracy kept` | 0.9092 | `results/e3_recommendation.json`: quiz > accuracy kept |
| `e3.quiz.newcomer slots kept` | 0.9544 | `results/e3_recommendation.json`: quiz > newcomer slots kept |
| `e3.quiz.ndcg@5 no privacy` | 0.465 | `results/e3_recommendation.json`: quiz > ndcg@5 no privacy |
| `e3.quiz.newcomer_share no privacy` | 0.2018 | `results/e3_recommendation.json`: quiz > newcomer_share no privacy |
| `e3.quiz.ndcg@5 no statistics about others` | 0.3767 | `results/e3_recommendation.json`: quiz > ndcg@5 no statistics about others |
| `e3.test.ndcg@5` | 0.4951 | `results/e3_recommendation.json`: test > ndcg@5 |
| `e3.test.ndcg@5 sd` | 0.003 | `results/e3_recommendation.json`: test > ndcg@5 sd |
| `e3.test.newcomer_share` | 0.1777 | `results/e3_recommendation.json`: test > newcomer_share |
| `e3.test.newcomer_share sd` | 0.0184 | `results/e3_recommendation.json`: test > newcomer_share sd |
| `e3.test.hit_rate` | 0.6213 | `results/e3_recommendation.json`: test > hit_rate |
| `e3.test.coverage` | 122.4 | `results/e3_recommendation.json`: test > coverage |
| `e3.test.gini` | 0.5045 | `results/e3_recommendation.json`: test > gini |
| `e3.test.ndcg@5 no privacy` | 0.5281 | `results/e3_recommendation.json`: test > ndcg@5 no privacy |
| `e3.test.newcomer_share no privacy` | 0.2027 | `results/e3_recommendation.json`: test > newcomer_share no privacy |
| `e3.test.cost` | 0.033 | `results/e3_recommendation.json`: test > cost |
| `e3.test.cost low` | 0.0248 | `results/e3_recommendation.json`: test > cost low |
| `e3.test.cost high` | 0.0406 | `results/e3_recommendation.json`: test > cost high |
| `e3.test.relative cost` | 0.0625 | `results/e3_recommendation.json`: test > relative cost |
| `e3.test.ndcg@5 no statistics about others` | 0.4239 | `results/e3_recommendation.json`: test > ndcg@5 no statistics about others |
| `e3.test.ndcg@5 popularity` | 0.1311 | `results/e3_recommendation.json`: test > ndcg@5 popularity |
| `e3.small_groups_found_by_noisy_sizes.truly new or small` | 53 | `results/e3_recommendation.json`: small_groups_found_by_noisy_sizes > truly new or small |
| `e3.small_groups_found_by_noisy_sizes.look new or small` | 57.4 | `results/e3_recommendation.json`: small_groups_found_by_noisy_sizes > look new or small |
| `e3.small_groups_found_by_noisy_sizes.found (of the true ones)` | 0.9094 | `results/e3_recommendation.json`: small_groups_found_by_noisy_sizes > found (of the true ones) |
| `e3.small_groups_found_by_noisy_sizes.right (of those that look it)` | 0.8411 | `results/e3_recommendation.json`: small_groups_found_by_noisy_sizes > right (of those that look it) |
| `e3.opt_in_25.everyone counts, no privacy.ndcg@5 (opted in)` | 0.5235 | `results/e3_recommendation.json`: opt_in_25% > everyone counts, no privacy > ndcg@5 (opted in) |
| `e3.opt_in_25.everyone counts, no privacy.ndcg@5 (all tested)` | 0.1706 | `results/e3_recommendation.json`: opt_in_25% > everyone counts, no privacy > ndcg@5 (all tested) |
| `e3.opt_in_25.only opted-in members count, no privacy.ndcg@5 (opted in)` | 0.475 | `results/e3_recommendation.json`: opt_in_25% > only opted-in members count, no privacy > ndcg@5 (opted in) |
| `e3.opt_in_25.only opted-in members count, no privacy.ndcg@5 (all tested)` | 0.1494 | `results/e3_recommendation.json`: opt_in_25% > only opted-in members count, no privacy > ndcg@5 (all tested) |
| `e3.opt_in_25.everyone counts, epsilon = 2, m = 3.ndcg@5 (opted in)` | 0.4895 | `results/e3_recommendation.json`: opt_in_25% > everyone counts, epsilon = 2, m = 3 > ndcg@5 (opted in) |
| `e3.opt_in_25.everyone counts, epsilon = 2, m = 3.ndcg@5 (all tested)` | 0.162 | `results/e3_recommendation.json`: opt_in_25% > everyone counts, epsilon = 2, m = 3 > ndcg@5 (all tested) |
| `e3.opt_in_25.only opted-in members count, epsilon = 2, m = 3.ndcg@5 (opted in)` | 0.2826 | `results/e3_recommendation.json`: opt_in_25% > only opted-in members count, epsilon = 2, m = 3 > ndcg@5 (opted in) |
| `e3.opt_in_25.only opted-in members count, epsilon = 2, m = 3.ndcg@5 (all tested)` | 0.1013 | `results/e3_recommendation.json`: opt_in_25% > only opted-in members count, epsilon = 2, m = 3 > ndcg@5 (all tested) |
| `e3.reasons.test, no privacy.shared-members reasons` | 0.5607 | `results/e3_recommendation.json`: reasons > test, no privacy > shared-members reasons |
| `e3.reasons.test, no privacy.shares nobody` | 0 | `results/e3_recommendation.json`: reasons > test, no privacy > shares nobody |
| `e3.reasons.test, no privacy.median error of the count` | 0 | `results/e3_recommendation.json`: reasons > test, no privacy > median error of the count |
| `e3.reasons.test, no privacy.quoted / true (median)` | 1 | `results/e3_recommendation.json`: reasons > test, no privacy > quoted / true (median) |
| `e3.reasons.test, clipping only.shared-members reasons` | 0.5155 | `results/e3_recommendation.json`: reasons > test, clipping only > shared-members reasons |
| `e3.reasons.test, clipping only.shares nobody` | 0 | `results/e3_recommendation.json`: reasons > test, clipping only > shares nobody |
| `e3.reasons.test, clipping only.median error of the count` | 27 | `results/e3_recommendation.json`: reasons > test, clipping only > median error of the count |
| `e3.reasons.test, clipping only.quoted / true (median)` | 0.4898 | `results/e3_recommendation.json`: reasons > test, clipping only > quoted / true (median) |
| `e3.reasons.test, chosen setting.shared-members reasons` | 0.5446 | `results/e3_recommendation.json`: reasons > test, chosen setting > shared-members reasons |
| `e3.reasons.test, chosen setting.shares nobody` | 0.2626 | `results/e3_recommendation.json`: reasons > test, chosen setting > shares nobody |
| `e3.reasons.test, chosen setting.median error of the count` | 12.9 | `results/e3_recommendation.json`: reasons > test, chosen setting > median error of the count |
| `e3.reasons.test, chosen setting.quoted / true (median)` | 0.5245 | `results/e3_recommendation.json`: reasons > test, chosen setting > quoted / true (median) |
| `e3.reasons.test, chosen setting.shares nobody sd` | 0.0207 | `results/e3_recommendation.json`: reasons > test, chosen setting > shares nobody sd |
| `e3.reasons.test, chosen setting.count below 3b` | 0.1679 | `results/e3_recommendation.json`: reasons > test, chosen setting > count below 3b |
| `e3.reasons.test, chosen setting.shares nobody, count 3b or more` | 0.1537 | `results/e3_recommendation.json`: reasons > test, chosen setting > shares nobody, count 3b or more |

## Every number: E4: fake accounts

| Key | Value | Source |
|---|---|---|
| `e4.L` | 3 | `results/e4_recommendation.json`: L |
| `e4.burst_w` | 0 | `results/e4_recommendation.json`: burst_w |
| `e4.young_days` | 30 | `results/e4_recommendation.json`: young_days |
| `e4.cost_no_attack.ndcg@5_tested_r9_off` | 0.5281 | `results/e4_recommendation.json`: cost_no_attack > ndcg@5_tested_r9_off |
| `e4.cost_no_attack.ndcg@5_tested_chosen` | 0.5267 | `results/e4_recommendation.json`: cost_no_attack > ndcg@5_tested_chosen |
| `e4.cost_no_attack.new_member_quiz_users` | 80 | `results/e4_recommendation.json`: cost_no_attack > new_member_quiz_users |
| `e4.cost_no_attack.ndcg@5_new_members_r9_off` | 0.3307 | `results/e4_recommendation.json`: cost_no_attack > ndcg@5_new_members_r9_off |
| `e4.cost_no_attack.ndcg@5_new_members_chosen` | 0.3415 | `results/e4_recommendation.json`: cost_no_attack > ndcg@5_new_members_chosen |
| `e4.cost_no_attack.slots_for_new_groups_r9_off` | 0.042 | `results/e4_recommendation.json`: cost_no_attack > slots_for_new_groups_r9_off |
| `e4.cost_no_attack.slots_for_new_groups_chosen` | 0.0405 | `results/e4_recommendation.json`: cost_no_attack > slots_for_new_groups_chosen |
| `e4.cost_no_attack.honest_memberships_turned_down` | 282 | `results/e4_recommendation.json`: cost_no_attack > honest_memberships_turned_down |
| `e4.cost_no_attack.honest_memberships` | 6367 | `results/e4_recommendation.json`: cost_no_attack > honest_memberships |
| `e4.young_network_183_days.no burst rule` | 0.5257 | `results/e4_recommendation.json`: young_network_183_days > no burst rule |
| `e4.young_network_183_days.burst 0.5` | 0.5301 | `results/e4_recommendation.json`: young_network_183_days > burst 0.5 |
| `e4.young_network_183_days.burst 0.25` | 0.5286 | `results/e4_recommendation.json`: young_network_183_days > burst 0.25 |
| `e4.young_network_183_days.burst 0.1` | 0.5306 | `results/e4_recommendation.json`: young_network_183_days > burst 0.1 |
| `e4.young_network_183_days.burst 0` | 0.5304 | `results/e4_recommendation.json`: young_network_183_days > burst 0 |
| `e4.targets_robustness_median_gain.L = 3 + burst 0` | 0 | `results/e4_recommendation.json`: targets_robustness_median_gain > L = 3 + burst 0 |
| `e4.targets_robustness_median_gain.R9 off` | 414 | `results/e4_recommendation.json`: targets_robustness_median_gain > R9 off |
| `e4.burst_weights_attacker_B_test.burst_w = 1.k=0` | 22 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 1 > 0 |
| `e4.burst_weights_attacker_B_test.burst_w = 1.k=50` | 267 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 1 > 50 |
| `e4.burst_weights_attacker_B_test.burst_w = 1.k=100` | 439 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 1 > 100 |
| `e4.burst_weights_attacker_B_test.burst_w = 1.k=200` | 519 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 1 > 200 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.5.k=0` | 20 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0.5 > 0 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.5.k=50` | 128 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0.5 > 50 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.5.k=100` | 265 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0.5 > 100 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.5.k=200` | 438 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0.5 > 200 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.25.k=0` | 22 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0.25 > 0 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.25.k=50` | 37 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0.25 > 50 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.25.k=100` | 131 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0.25 > 100 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.25.k=200` | 270 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0.25 > 200 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.1.k=0` | 21 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0.1 > 0 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.1.k=50` | 22 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0.1 > 50 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.1.k=100` | 32 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0.1 > 100 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.1.k=200` | 95 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0.1 > 200 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.k=0` | 20 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0 > 0 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.k=50` | 20 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0 > 50 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.k=100` | 20 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0 > 100 |
| `e4.burst_weights_attacker_B_test.burst_w = 0.k=200` | 20 | `results/e4_recommendation.json`: burst_weights_attacker_B_test > burst_w = 0 > 200 |
| `e4.target.group_id` | 149 | `results/e4_recommendation.json`: target_group > group_id |
| `e4.target.members` | 1 | `results/e4_recommendation.json`: target_group > members |
| `e4.target.days_old` | 4 | `results/e4_recommendation.json`: target_group > days_old |
| `e4.test.members_tested` | 1406 | `results/e4_recommendation.json`: test > members_tested |
| `e4.test.bar_top_honest_new_group` | 49 | `results/e4_recommendation.json`: test > bar_top_honest_new_group |
| `e4.test.target_exposure.fresh.R9 off.k=0` | 21 | `results/e4_recommendation.json`: test > target_exposure > fresh > R9 off > 0 |
| `e4.test.target_exposure.fresh.R9 off.k=10` | 31 | `results/e4_recommendation.json`: test > target_exposure > fresh > R9 off > 10 |
| `e4.test.target_exposure.fresh.R9 off.k=20` | 98 | `results/e4_recommendation.json`: test > target_exposure > fresh > R9 off > 20 |
| `e4.test.target_exposure.fresh.R9 off.k=50` | 269 | `results/e4_recommendation.json`: test > target_exposure > fresh > R9 off > 50 |
| `e4.test.target_exposure.fresh.R9 off.k=100` | 442 | `results/e4_recommendation.json`: test > target_exposure > fresh > R9 off > 100 |
| `e4.test.target_exposure.fresh.R9 off.k=200` | 521 | `results/e4_recommendation.json`: test > target_exposure > fresh > R9 off > 200 |
| `e4.test.target_exposure.fresh.L = 3 + burst 0.k=0` | 20 | `results/e4_recommendation.json`: test > target_exposure > fresh > L = 3 + burst 0 > 0 |
| `e4.test.target_exposure.fresh.L = 3 + burst 0.k=10` | 20 | `results/e4_recommendation.json`: test > target_exposure > fresh > L = 3 + burst 0 > 10 |
| `e4.test.target_exposure.fresh.L = 3 + burst 0.k=20` | 20 | `results/e4_recommendation.json`: test > target_exposure > fresh > L = 3 + burst 0 > 20 |
| `e4.test.target_exposure.fresh.L = 3 + burst 0.k=50` | 20 | `results/e4_recommendation.json`: test > target_exposure > fresh > L = 3 + burst 0 > 50 |
| `e4.test.target_exposure.fresh.L = 3 + burst 0.k=100` | 20 | `results/e4_recommendation.json`: test > target_exposure > fresh > L = 3 + burst 0 > 100 |
| `e4.test.target_exposure.fresh.L = 3 + burst 0.k=200` | 20 | `results/e4_recommendation.json`: test > target_exposure > fresh > L = 3 + burst 0 > 200 |
| `e4.test.target_exposure.levelled.R9 off.k=0` | 21 | `results/e4_recommendation.json`: test > target_exposure > levelled > R9 off > 0 |
| `e4.test.target_exposure.levelled.R9 off.k=10` | 31 | `results/e4_recommendation.json`: test > target_exposure > levelled > R9 off > 10 |
| `e4.test.target_exposure.levelled.R9 off.k=20` | 98 | `results/e4_recommendation.json`: test > target_exposure > levelled > R9 off > 20 |
| `e4.test.target_exposure.levelled.R9 off.k=50` | 269 | `results/e4_recommendation.json`: test > target_exposure > levelled > R9 off > 50 |
| `e4.test.target_exposure.levelled.R9 off.k=100` | 442 | `results/e4_recommendation.json`: test > target_exposure > levelled > R9 off > 100 |
| `e4.test.target_exposure.levelled.R9 off.k=200` | 521 | `results/e4_recommendation.json`: test > target_exposure > levelled > R9 off > 200 |
| `e4.test.target_exposure.levelled.L = 3 + burst 0.k=0` | 20 | `results/e4_recommendation.json`: test > target_exposure > levelled > L = 3 + burst 0 > 0 |
| `e4.test.target_exposure.levelled.L = 3 + burst 0.k=10` | 20 | `results/e4_recommendation.json`: test > target_exposure > levelled > L = 3 + burst 0 > 10 |
| `e4.test.target_exposure.levelled.L = 3 + burst 0.k=20` | 20 | `results/e4_recommendation.json`: test > target_exposure > levelled > L = 3 + burst 0 > 20 |
| `e4.test.target_exposure.levelled.L = 3 + burst 0.k=50` | 20 | `results/e4_recommendation.json`: test > target_exposure > levelled > L = 3 + burst 0 > 50 |
| `e4.test.target_exposure.levelled.L = 3 + burst 0.k=100` | 20 | `results/e4_recommendation.json`: test > target_exposure > levelled > L = 3 + burst 0 > 100 |
| `e4.test.target_exposure.levelled.L = 3 + burst 0.k=200` | 20 | `results/e4_recommendation.json`: test > target_exposure > levelled > L = 3 + burst 0 > 200 |
| `e4.test.target_exposure.aged.R9 off.k=0` | 21 | `results/e4_recommendation.json`: test > target_exposure > aged > R9 off > 0 |
| `e4.test.target_exposure.aged.R9 off.k=10` | 31 | `results/e4_recommendation.json`: test > target_exposure > aged > R9 off > 10 |
| `e4.test.target_exposure.aged.R9 off.k=20` | 98 | `results/e4_recommendation.json`: test > target_exposure > aged > R9 off > 20 |
| `e4.test.target_exposure.aged.R9 off.k=50` | 269 | `results/e4_recommendation.json`: test > target_exposure > aged > R9 off > 50 |
| `e4.test.target_exposure.aged.R9 off.k=100` | 442 | `results/e4_recommendation.json`: test > target_exposure > aged > R9 off > 100 |
| `e4.test.target_exposure.aged.R9 off.k=200` | 521 | `results/e4_recommendation.json`: test > target_exposure > aged > R9 off > 200 |
| `e4.test.target_exposure.aged.L = 3 + burst 0.k=0` | 20 | `results/e4_recommendation.json`: test > target_exposure > aged > L = 3 + burst 0 > 0 |
| `e4.test.target_exposure.aged.L = 3 + burst 0.k=10` | 20 | `results/e4_recommendation.json`: test > target_exposure > aged > L = 3 + burst 0 > 10 |
| `e4.test.target_exposure.aged.L = 3 + burst 0.k=20` | 20 | `results/e4_recommendation.json`: test > target_exposure > aged > L = 3 + burst 0 > 20 |
| `e4.test.target_exposure.aged.L = 3 + burst 0.k=50` | 20 | `results/e4_recommendation.json`: test > target_exposure > aged > L = 3 + burst 0 > 50 |
| `e4.test.target_exposure.aged.L = 3 + burst 0.k=100` | 20 | `results/e4_recommendation.json`: test > target_exposure > aged > L = 3 + burst 0 > 100 |
| `e4.test.target_exposure.aged.L = 3 + burst 0.k=200` | 20 | `results/e4_recommendation.json`: test > target_exposure > aged > L = 3 + burst 0 > 200 |
| `e4.test.target_exposure.both.R9 off.k=0` | 21 | `results/e4_recommendation.json`: test > target_exposure > both > R9 off > 0 |
| `e4.test.target_exposure.both.R9 off.k=10` | 31 | `results/e4_recommendation.json`: test > target_exposure > both > R9 off > 10 |
| `e4.test.target_exposure.both.R9 off.k=20` | 98 | `results/e4_recommendation.json`: test > target_exposure > both > R9 off > 20 |
| `e4.test.target_exposure.both.R9 off.k=50` | 269 | `results/e4_recommendation.json`: test > target_exposure > both > R9 off > 50 |
| `e4.test.target_exposure.both.R9 off.k=100` | 442 | `results/e4_recommendation.json`: test > target_exposure > both > R9 off > 100 |
| `e4.test.target_exposure.both.R9 off.k=200` | 521 | `results/e4_recommendation.json`: test > target_exposure > both > R9 off > 200 |
| `e4.test.target_exposure.both.L = 3 + burst 0.k=0` | 20 | `results/e4_recommendation.json`: test > target_exposure > both > L = 3 + burst 0 > 0 |
| `e4.test.target_exposure.both.L = 3 + burst 0.k=10` | 29 | `results/e4_recommendation.json`: test > target_exposure > both > L = 3 + burst 0 > 10 |
| `e4.test.target_exposure.both.L = 3 + burst 0.k=20` | 98 | `results/e4_recommendation.json`: test > target_exposure > both > L = 3 + burst 0 > 20 |
| `e4.test.target_exposure.both.L = 3 + burst 0.k=50` | 263 | `results/e4_recommendation.json`: test > target_exposure > both > L = 3 + burst 0 > 50 |
| `e4.test.target_exposure.both.L = 3 + burst 0.k=100` | 433 | `results/e4_recommendation.json`: test > target_exposure > both > L = 3 + burst 0 > 100 |
| `e4.test.target_exposure.both.L = 3 + burst 0.k=200` | 515 | `results/e4_recommendation.json`: test > target_exposure > both > L = 3 + burst 0 > 200 |
| `e4.test.places_per_fake_A.R9 off.k=10` | 1.572 | `results/e4_recommendation.json`: test > places_per_fake_A > R9 off > 10 |
| `e4.test.places_per_fake_A.R9 off.k=20` | 1.033 | `results/e4_recommendation.json`: test > places_per_fake_A > R9 off > 20 |
| `e4.test.places_per_fake_A.R9 off.k=50` | 0.46 | `results/e4_recommendation.json`: test > places_per_fake_A > R9 off > 50 |
| `e4.test.places_per_fake_A.R9 off.k=100` | 0.24 | `results/e4_recommendation.json`: test > places_per_fake_A > R9 off > 100 |
| `e4.test.places_per_fake_A.R9 off.k=200` | 0.126 | `results/e4_recommendation.json`: test > places_per_fake_A > R9 off > 200 |
| `e4.test.places_per_fake_A.L = 3 + burst 0.k=10` | 0 | `results/e4_recommendation.json`: test > places_per_fake_A > L = 3 + burst 0 > 10 |
| `e4.test.places_per_fake_A.L = 3 + burst 0.k=20` | 0 | `results/e4_recommendation.json`: test > places_per_fake_A > L = 3 + burst 0 > 20 |
| `e4.test.places_per_fake_A.L = 3 + burst 0.k=50` | 0 | `results/e4_recommendation.json`: test > places_per_fake_A > L = 3 + burst 0 > 50 |
| `e4.test.places_per_fake_A.L = 3 + burst 0.k=100` | 0 | `results/e4_recommendation.json`: test > places_per_fake_A > L = 3 + burst 0 > 100 |
| `e4.test.places_per_fake_A.L = 3 + burst 0.k=200` | 0 | `results/e4_recommendation.json`: test > places_per_fake_A > L = 3 + burst 0 > 200 |
| `e4.quiz.ndcg@5_r9_off` | 0.465 | `results/e4_recommendation.json`: practice_quiz > ndcg@5_r9_off |
| `e4.quiz.ndcg@5_chosen` | 0.4607 | `results/e4_recommendation.json`: practice_quiz > ndcg@5_chosen |
| `e4.quiz.ndcg@5_cost` | 0.0043 | `results/e4_recommendation.json`: practice_quiz > ndcg@5_cost |
| `e4.posting.default_lists_showing_target.R9 off.fresh.k=20` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > R9 off > fresh > 20 |
| `e4.posting.default_lists_showing_target.R9 off.fresh.k=100` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > R9 off > fresh > 100 |
| `e4.posting.default_lists_showing_target.R9 off.levelled.k=20` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > R9 off > levelled > 20 |
| `e4.posting.default_lists_showing_target.R9 off.levelled.k=100` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > R9 off > levelled > 100 |
| `e4.posting.default_lists_showing_target.R9 off.aged.k=20` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > R9 off > aged > 20 |
| `e4.posting.default_lists_showing_target.R9 off.aged.k=100` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > R9 off > aged > 100 |
| `e4.posting.default_lists_showing_target.R9 off.both.k=20` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > R9 off > both > 20 |
| `e4.posting.default_lists_showing_target.R9 off.both.k=100` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > R9 off > both > 100 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins only.fresh.k=20` | 0 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins only > fresh > 20 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins only.fresh.k=100` | 0 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins only > fresh > 100 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins only.levelled.k=20` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins only > levelled > 20 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins only.levelled.k=100` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins only > levelled > 100 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins only.aged.k=20` | 0 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins only > aged > 20 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins only.aged.k=100` | 0 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins only > aged > 100 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins only.both.k=20` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins only > both > 20 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins only.both.k=100` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins only > both > 100 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins, posts, likes and friends.fresh.k=20` | 0 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins, posts, likes and friends > fresh > 20 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins, posts, likes and friends.fresh.k=100` | 0 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins, posts, likes and friends > fresh > 100 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins, posts, likes and friends.levelled.k=20` | 0 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins, posts, likes and friends > levelled > 20 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins, posts, likes and friends.levelled.k=100` | 0 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins, posts, likes and friends > levelled > 100 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins, posts, likes and friends.aged.k=20` | 0 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins, posts, likes and friends > aged > 20 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins, posts, likes and friends.aged.k=100` | 0 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins, posts, likes and friends > aged > 100 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins, posts, likes and friends.both.k=20` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins, posts, likes and friends > both > 20 |
| `e4.posting.default_lists_showing_target.L = 3 + burst 0, joins, posts, likes and friends.both.k=100` | 703 | `results/e4_recommendation.json`: activity_attack > default_lists_showing_target > L = 3 + burst 0, joins, posts, likes and friends > both > 100 |
| `e4.posting.no_attack_default_lists.R9 off` | 0 | `results/e4_recommendation.json`: activity_attack > no_attack_default_lists > R9 off |
| `e4.posting.no_attack_default_lists.L = 3 + burst 0, joins only` | 0 | `results/e4_recommendation.json`: activity_attack > no_attack_default_lists > L = 3 + burst 0, joins only |
| `e4.posting.no_attack_default_lists.L = 3 + burst 0, joins, posts, likes and friends` | 0 | `results/e4_recommendation.json`: activity_attack > no_attack_default_lists > L = 3 + burst 0, joins, posts, likes and friends |

## Every number: E5: new members and new groups

| Key | Value | Source |
|---|---|---|
| `e5.popularity.ndcg@5 3+ groups (test)` | 0.132 | `results/e5_newcomers.csv`: row "Popularity (today)", column "ndcg@5 3+ groups (test)" |
| `e5.popularity.hit 3+ groups (test)` | 0.225 | `results/e5_newcomers.csv`: row "Popularity (today)", column "hit 3+ groups (test)" |
| `e5.popularity.ndcg@5 2 groups (test)` | 0.127 | `results/e5_newcomers.csv`: row "Popularity (today)", column "ndcg@5 2 groups (test)" |
| `e5.popularity.hit 2 groups (test)` | 0.206 | `results/e5_newcomers.csv`: row "Popularity (today)", column "hit 2 groups (test)" |
| `e5.popularity.ndcg@5 1 group (quiz)` | 0.16 | `results/e5_newcomers.csv`: row "Popularity (today)", column "ndcg@5 1 group (quiz)" |
| `e5.popularity.hit 1 group (quiz)` | 0.275 | `results/e5_newcomers.csv`: row "Popularity (today)", column "hit 1 group (quiz)" |
| `e5.popularity.ndcg@5 no group yet (quiz)` | 0.15 | `results/e5_newcomers.csv`: row "Popularity (today)", column "ndcg@5 no group yet (quiz)" |
| `e5.popularity.hit no group yet (quiz)` | 0.23 | `results/e5_newcomers.csv`: row "Popularity (today)", column "hit no group yet (quiz)" |
| `e5.popularity.ndcg@5 new members (quiz)` | 0.134 | `results/e5_newcomers.csv`: row "Popularity (today)", column "ndcg@5 new members (quiz)" |
| `e5.popularity.hit new members (quiz)` | 0.213 | `results/e5_newcomers.csv`: row "Popularity (today)", column "hit new members (quiz)" |
| `e5.popularity.ndcg@5 all tested` | 0.131 | `results/e5_newcomers.csv`: row "Popularity (today)", column "ndcg@5 all tested" |
| `e5.popularity.hit all tested` | 0.22 | `results/e5_newcomers.csv`: row "Popularity (today)", column "hit all tested" |
| `e5.popularity.share new groups` | 0 | `results/e5_newcomers.csv`: row "Popularity (today)", column "share new groups" |
| `e5.popularity.share older small groups` | 0 | `results/e5_newcomers.csv`: row "Popularity (today)", column "share older small groups" |
| `e5.popularity.newcomer share` | 0 | `results/e5_newcomers.csv`: row "Popularity (today)", column "newcomer share" |
| `e5.popularity.found in new groups` | 0 | `results/e5_newcomers.csv`: row "Popularity (today)", column "found in new groups" |
| `e5.popularity.hidden in new groups` | 8 | `results/e5_newcomers.csv`: row "Popularity (today)", column "hidden in new groups" |
| `e5.popularity.found in new or small groups` | 0 | `results/e5_newcomers.csv`: row "Popularity (today)", column "found in new or small groups" |
| `e5.popularity.hidden in new or small groups` | 42 | `results/e5_newcomers.csv`: row "Popularity (today)", column "hidden in new or small groups" |
| `e5.popularity.recall new groups` | 0 | `results/e5_newcomers.csv`: row "Popularity (today)", column "recall new groups" |
| `e5.popularity.recall new or small groups` | 0 | `results/e5_newcomers.csv`: row "Popularity (today)", column "recall new or small groups" |
| `e5.hybrid.ndcg@5 3+ groups (test)` | 0.562 | `results/e5_newcomers.csv`: row "Hybrid", column "ndcg@5 3+ groups (test)" |
| `e5.hybrid.hit 3+ groups (test)` | 0.709 | `results/e5_newcomers.csv`: row "Hybrid", column "hit 3+ groups (test)" |
| `e5.hybrid.ndcg@5 2 groups (test)` | 0.468 | `results/e5_newcomers.csv`: row "Hybrid", column "ndcg@5 2 groups (test)" |
| `e5.hybrid.hit 2 groups (test)` | 0.611 | `results/e5_newcomers.csv`: row "Hybrid", column "hit 2 groups (test)" |
| `e5.hybrid.ndcg@5 1 group (quiz)` | 0.431 | `results/e5_newcomers.csv`: row "Hybrid", column "ndcg@5 1 group (quiz)" |
| `e5.hybrid.hit 1 group (quiz)` | 0.608 | `results/e5_newcomers.csv`: row "Hybrid", column "hit 1 group (quiz)" |
| `e5.hybrid.ndcg@5 no group yet (quiz)` | 0.332 | `results/e5_newcomers.csv`: row "Hybrid", column "ndcg@5 no group yet (quiz)" |
| `e5.hybrid.hit no group yet (quiz)` | 0.443 | `results/e5_newcomers.csv`: row "Hybrid", column "hit no group yet (quiz)" |
| `e5.hybrid.ndcg@5 new members (quiz)` | 0.353 | `results/e5_newcomers.csv`: row "Hybrid", column "ndcg@5 new members (quiz)" |
| `e5.hybrid.hit new members (quiz)` | 0.505 | `results/e5_newcomers.csv`: row "Hybrid", column "hit new members (quiz)" |
| `e5.hybrid.ndcg@5 all tested` | 0.541 | `results/e5_newcomers.csv`: row "Hybrid", column "ndcg@5 all tested" |
| `e5.hybrid.hit all tested` | 0.687 | `results/e5_newcomers.csv`: row "Hybrid", column "hit all tested" |
| `e5.hybrid.share new groups` | 0.004 | `results/e5_newcomers.csv`: row "Hybrid", column "share new groups" |
| `e5.hybrid.share older small groups` | 0.016 | `results/e5_newcomers.csv`: row "Hybrid", column "share older small groups" |
| `e5.hybrid.newcomer share` | 0.02 | `results/e5_newcomers.csv`: row "Hybrid", column "newcomer share" |
| `e5.hybrid.found in new groups` | 1 | `results/e5_newcomers.csv`: row "Hybrid", column "found in new groups" |
| `e5.hybrid.hidden in new groups` | 8 | `results/e5_newcomers.csv`: row "Hybrid", column "hidden in new groups" |
| `e5.hybrid.found in new or small groups` | 8 | `results/e5_newcomers.csv`: row "Hybrid", column "found in new or small groups" |
| `e5.hybrid.hidden in new or small groups` | 42 | `results/e5_newcomers.csv`: row "Hybrid", column "hidden in new or small groups" |
| `e5.hybrid.recall new groups` | 0.125 | `results/e5_newcomers.csv`: row "Hybrid", column "recall new groups" |
| `e5.hybrid.recall new or small groups` | 0.19 | `results/e5_newcomers.csv`: row "Hybrid", column "recall new or small groups" |
| `e5.reranked.ndcg@5 3+ groups (test)` | 0.546 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "ndcg@5 3+ groups (test)" |
| `e5.reranked.hit 3+ groups (test)` | 0.672 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "hit 3+ groups (test)" |
| `e5.reranked.ndcg@5 2 groups (test)` | 0.465 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "ndcg@5 2 groups (test)" |
| `e5.reranked.hit 2 groups (test)` | 0.601 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "hit 2 groups (test)" |
| `e5.reranked.ndcg@5 1 group (quiz)` | 0.4 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "ndcg@5 1 group (quiz)" |
| `e5.reranked.hit 1 group (quiz)` | 0.529 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "hit 1 group (quiz)" |
| `e5.reranked.ndcg@5 no group yet (quiz)` | 0.326 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "ndcg@5 no group yet (quiz)" |
| `e5.reranked.hit no group yet (quiz)` | 0.426 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "hit no group yet (quiz)" |
| `e5.reranked.ndcg@5 new members (quiz)` | 0.343 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "ndcg@5 new members (quiz)" |
| `e5.reranked.hit new members (quiz)` | 0.48 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "hit new members (quiz)" |
| `e5.reranked.ndcg@5 all tested` | 0.528 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "ndcg@5 all tested" |
| `e5.reranked.hit all tested` | 0.656 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "hit all tested" |
| `e5.reranked.share new groups` | 0.042 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "share new groups" |
| `e5.reranked.share older small groups` | 0.161 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "share older small groups" |
| `e5.reranked.newcomer share` | 0.203 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "newcomer share" |
| `e5.reranked.found in new groups` | 1 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "found in new groups" |
| `e5.reranked.hidden in new groups` | 8 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "hidden in new groups" |
| `e5.reranked.found in new or small groups` | 14 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "found in new or small groups" |
| `e5.reranked.hidden in new or small groups` | 42 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "hidden in new or small groups" |
| `e5.reranked.recall new groups` | 0.125 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "recall new groups" |
| `e5.reranked.recall new or small groups` | 0.333 | `results/e5_newcomers.csv`: row "Hybrid + fair re-ranking", column "recall new or small groups" |
| `e5.off.ndcg@5 3+ groups (test)` | 0.057 | `results/e5_newcomers.csv`: row "Personalisation off", column "ndcg@5 3+ groups (test)" |
| `e5.off.hit 3+ groups (test)` | 0.098 | `results/e5_newcomers.csv`: row "Personalisation off", column "hit 3+ groups (test)" |
| `e5.off.ndcg@5 2 groups (test)` | 0.059 | `results/e5_newcomers.csv`: row "Personalisation off", column "ndcg@5 2 groups (test)" |
| `e5.off.hit 2 groups (test)` | 0.098 | `results/e5_newcomers.csv`: row "Personalisation off", column "hit 2 groups (test)" |
| `e5.off.ndcg@5 1 group (quiz)` | 0.076 | `results/e5_newcomers.csv`: row "Personalisation off", column "ndcg@5 1 group (quiz)" |
| `e5.off.hit 1 group (quiz)` | 0.123 | `results/e5_newcomers.csv`: row "Personalisation off", column "hit 1 group (quiz)" |
| `e5.off.ndcg@5 no group yet (quiz)` | 0.07 | `results/e5_newcomers.csv`: row "Personalisation off", column "ndcg@5 no group yet (quiz)" |
| `e5.off.hit no group yet (quiz)` | 0.123 | `results/e5_newcomers.csv`: row "Personalisation off", column "hit no group yet (quiz)" |
| `e5.off.ndcg@5 new members (quiz)` | 0.063 | `results/e5_newcomers.csv`: row "Personalisation off", column "ndcg@5 new members (quiz)" |
| `e5.off.hit new members (quiz)` | 0.109 | `results/e5_newcomers.csv`: row "Personalisation off", column "hit new members (quiz)" |
| `e5.off.ndcg@5 all tested` | 0.058 | `results/e5_newcomers.csv`: row "Personalisation off", column "ndcg@5 all tested" |
| `e5.off.hit all tested` | 0.098 | `results/e5_newcomers.csv`: row "Personalisation off", column "hit all tested" |
| `e5.off.share new groups` | 0.547 | `results/e5_newcomers.csv`: row "Personalisation off", column "share new groups" |
| `e5.off.share older small groups` | 0 | `results/e5_newcomers.csv`: row "Personalisation off", column "share older small groups" |
| `e5.off.newcomer share` | 0.547 | `results/e5_newcomers.csv`: row "Personalisation off", column "newcomer share" |
| `e5.off.found in new groups` | 1 | `results/e5_newcomers.csv`: row "Personalisation off", column "found in new groups" |
| `e5.off.hidden in new groups` | 8 | `results/e5_newcomers.csv`: row "Personalisation off", column "hidden in new groups" |
| `e5.off.found in new or small groups` | 1 | `results/e5_newcomers.csv`: row "Personalisation off", column "found in new or small groups" |
| `e5.off.hidden in new or small groups` | 42 | `results/e5_newcomers.csv`: row "Personalisation off", column "hidden in new or small groups" |
| `e5.off.recall new groups` | 0.125 | `results/e5_newcomers.csv`: row "Personalisation off", column "recall new groups" |
| `e5.off.recall new or small groups` | 0.024 | `results/e5_newcomers.csv`: row "Personalisation off", column "recall new or small groups" |
| `e5.members.3 or more groups` | 1090 | `results/e5_newcomers.json`: members > 3 or more groups |
| `e5.members.2 groups` | 316 | `results/e5_newcomers.json`: members > 2 groups |
| `e5.members.1 group` | 357 | `results/e5_newcomers.json`: members > 1 group |
| `e5.members.No group yet` | 122 | `results/e5_newcomers.json`: members > No group yet |
| `e5.members.New members` | 202 | `results/e5_newcomers.json`: members > New members |
| `e5.cost_of_reranking.3 or more groups.members` | 1090 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 3 or more groups > members |
| `e5.cost_of_reranking.3 or more groups.hybrid` | 0.5617 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 3 or more groups > hybrid |
| `e5.cost_of_reranking.3 or more groups.proposed` | 0.5464 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 3 or more groups > proposed |
| `e5.cost_of_reranking.3 or more groups.cost` | 0.0153 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 3 or more groups > cost |
| `e5.cost_of_reranking.3 or more groups.cost low` | 0.0101 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 3 or more groups > cost low |
| `e5.cost_of_reranking.3 or more groups.cost high` | 0.0206 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 3 or more groups > cost high |
| `e5.cost_of_reranking.3 or more groups.relative cost` | 0.0272 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 3 or more groups > relative cost |
| `e5.cost_of_reranking.2 groups.members` | 316 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 2 groups > members |
| `e5.cost_of_reranking.2 groups.hybrid` | 0.4682 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 2 groups > hybrid |
| `e5.cost_of_reranking.2 groups.proposed` | 0.4649 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 2 groups > proposed |
| `e5.cost_of_reranking.2 groups.cost` | 0.0033 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 2 groups > cost |
| `e5.cost_of_reranking.2 groups.cost low` | -0.0065 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 2 groups > cost low |
| `e5.cost_of_reranking.2 groups.cost high` | 0.0132 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 2 groups > cost high |
| `e5.cost_of_reranking.2 groups.relative cost` | 0.007 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 2 groups > relative cost |
| `e5.cost_of_reranking.1 group.members` | 357 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 1 group > members |
| `e5.cost_of_reranking.1 group.hybrid` | 0.4307 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 1 group > hybrid |
| `e5.cost_of_reranking.1 group.proposed` | 0.3997 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 1 group > proposed |
| `e5.cost_of_reranking.1 group.cost` | 0.031 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 1 group > cost |
| `e5.cost_of_reranking.1 group.cost low` | 0.0185 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 1 group > cost low |
| `e5.cost_of_reranking.1 group.cost high` | 0.0448 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 1 group > cost high |
| `e5.cost_of_reranking.1 group.relative cost` | 0.072 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > 1 group > relative cost |
| `e5.cost_of_reranking.No group yet.members` | 122 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > No group yet > members |
| `e5.cost_of_reranking.No group yet.hybrid` | 0.3323 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > No group yet > hybrid |
| `e5.cost_of_reranking.No group yet.proposed` | 0.3256 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > No group yet > proposed |
| `e5.cost_of_reranking.No group yet.cost` | 0.0067 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > No group yet > cost |
| `e5.cost_of_reranking.No group yet.cost low` | 0 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > No group yet > cost low |
| `e5.cost_of_reranking.No group yet.cost high` | 0.0169 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > No group yet > cost high |
| `e5.cost_of_reranking.No group yet.relative cost` | 0.0202 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > No group yet > relative cost |
| `e5.cost_of_reranking.New members.members` | 202 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > New members > members |
| `e5.cost_of_reranking.New members.hybrid` | 0.353 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > New members > hybrid |
| `e5.cost_of_reranking.New members.proposed` | 0.343 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > New members > proposed |
| `e5.cost_of_reranking.New members.cost` | 0.01 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > New members > cost |
| `e5.cost_of_reranking.New members.cost low` | -0.0015 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > New members > cost low |
| `e5.cost_of_reranking.New members.cost high` | 0.0224 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > New members > cost high |
| `e5.cost_of_reranking.New members.relative cost` | 0.0284 | `results/e5_newcomers.json`: cost of re-ranking per kind of member (hybrid minus proposed, NDCG@5) > New members > relative cost |
| `e5.r9.Proposed design (R9 off: L = 1).ndcg@5 all tested` | 0.528 | `results/e5_r9.csv`: row "Proposed design (R9 off: L = 1)", column "ndcg@5 all tested" |
| `e5.r9.Proposed design (R9 off: L = 1).ndcg@5 2 groups (test)` | 0.465 | `results/e5_r9.csv`: row "Proposed design (R9 off: L = 1)", column "ndcg@5 2 groups (test)" |
| `e5.r9.Proposed design (R9 off: L = 1).ndcg@5 new members (quiz)` | 0.343 | `results/e5_r9.csv`: row "Proposed design (R9 off: L = 1)", column "ndcg@5 new members (quiz)" |
| `e5.r9.Proposed design (R9 off: L = 1).ndcg@5 no group yet (quiz)` | 0.326 | `results/e5_r9.csv`: row "Proposed design (R9 off: L = 1)", column "ndcg@5 no group yet (quiz)" |
| `e5.r9.Proposed design (R9 off: L = 1).share new groups` | 0.042 | `results/e5_r9.csv`: row "Proposed design (R9 off: L = 1)", column "share new groups" |
| `e5.r9.Proposed design (R9 off: L = 1).newcomer share` | 0.203 | `results/e5_r9.csv`: row "Proposed design (R9 off: L = 1)", column "newcomer share" |
| `e5.r9.Proposed design (R9 off: L = 1).found in new or small groups` | 14 | `results/e5_r9.csv`: row "Proposed design (R9 off: L = 1)", column "found in new or small groups" |
| `e5.r9.Only level 3 or more counts (L = 3).ndcg@5 all tested` | 0.526 | `results/e5_r9.csv`: row "Only level 3 or more counts (L = 3)", column "ndcg@5 all tested" |
| `e5.r9.Only level 3 or more counts (L = 3).ndcg@5 2 groups (test)` | 0.464 | `results/e5_r9.csv`: row "Only level 3 or more counts (L = 3)", column "ndcg@5 2 groups (test)" |
| `e5.r9.Only level 3 or more counts (L = 3).ndcg@5 new members (quiz)` | 0.336 | `results/e5_r9.csv`: row "Only level 3 or more counts (L = 3)", column "ndcg@5 new members (quiz)" |
| `e5.r9.Only level 3 or more counts (L = 3).ndcg@5 no group yet (quiz)` | 0.314 | `results/e5_r9.csv`: row "Only level 3 or more counts (L = 3)", column "ndcg@5 no group yet (quiz)" |
| `e5.r9.Only level 3 or more counts (L = 3).share new groups` | 0.042 | `results/e5_r9.csv`: row "Only level 3 or more counts (L = 3)", column "share new groups" |
| `e5.r9.Only level 3 or more counts (L = 3).newcomer share` | 0.203 | `results/e5_r9.csv`: row "Only level 3 or more counts (L = 3)", column "newcomer share" |
| `e5.r9.Only level 3 or more counts (L = 3).found in new or small groups` | 14 | `results/e5_r9.csv`: row "Only level 3 or more counts (L = 3)", column "found in new or small groups" |
| `e5.r9.Young accounts count half (burst_w = 0.5).ndcg@5 all tested` | 0.529 | `results/e5_r9.csv`: row "Young accounts count half (burst_w = 0.5)", column "ndcg@5 all tested" |
| `e5.r9.Young accounts count half (burst_w = 0.5).ndcg@5 2 groups (test)` | 0.467 | `results/e5_r9.csv`: row "Young accounts count half (burst_w = 0.5)", column "ndcg@5 2 groups (test)" |
| `e5.r9.Young accounts count half (burst_w = 0.5).ndcg@5 new members (quiz)` | 0.343 | `results/e5_r9.csv`: row "Young accounts count half (burst_w = 0.5)", column "ndcg@5 new members (quiz)" |
| `e5.r9.Young accounts count half (burst_w = 0.5).ndcg@5 no group yet (quiz)` | 0.326 | `results/e5_r9.csv`: row "Young accounts count half (burst_w = 0.5)", column "ndcg@5 no group yet (quiz)" |
| `e5.r9.Young accounts count half (burst_w = 0.5).share new groups` | 0.042 | `results/e5_r9.csv`: row "Young accounts count half (burst_w = 0.5)", column "share new groups" |
| `e5.r9.Young accounts count half (burst_w = 0.5).newcomer share` | 0.203 | `results/e5_r9.csv`: row "Young accounts count half (burst_w = 0.5)", column "newcomer share" |
| `e5.r9.Young accounts count half (burst_w = 0.5).found in new or small groups` | 14 | `results/e5_r9.csv`: row "Young accounts count half (burst_w = 0.5)", column "found in new or small groups" |

## Every number: E6: do the hard rules hold

| Key | Value | Source |
|---|---|---|
| `e6.fidelity.reasons` | 26860 | `results/e6_rules.json`: explanation_fidelity > reasons |
| `e6.fidelity.true` | 26860 | `results/e6_rules.json`: explanation_fidelity > true |
| `e6.fidelity.share` | 1 | `results/e6_rules.json`: explanation_fidelity > share |
| `e6.fidelity.name the largest part` | 23729 | `results/e6_rules.json`: explanation_fidelity > name the largest part |
| `e6.fidelity.name a part` | 23729 | `results/e6_rules.json`: explanation_fidelity > name a part |
| `e6.runs.Proposed design, all members.members` | 1983 | `results/e6_rules.json`: runs > Proposed design, all members > members |
| `e6.runs.Proposed design, all members.suggestions` | 9915 | `results/e6_rules.json`: runs > Proposed design, all members > suggestions |
| `e6.runs.Proposed design, all members.hard_violations` | 0 | `results/e6_rules.json`: runs > Proposed design, all members > hard_violations |
| `e6.runs.Personalisation off, all members.members` | 1983 | `results/e6_rules.json`: runs > Personalisation off, all members > members |
| `e6.runs.Personalisation off, all members.suggestions` | 9915 | `results/e6_rules.json`: runs > Personalisation off, all members > suggestions |
| `e6.runs.Personalisation off, all members.hard_violations` | 0 | `results/e6_rules.json`: runs > Personalisation off, all members > hard_violations |
| `e6.runs.Proposed design, tested members (E1).members` | 1406 | `results/e6_rules.json`: runs > Proposed design, tested members (E1) > members |
| `e6.runs.Proposed design, tested members (E1).suggestions` | 7030 | `results/e6_rules.json`: runs > Proposed design, tested members (E1) > suggestions |
| `e6.runs.Proposed design, tested members (E1).hard_violations` | 0 | `results/e6_rules.json`: runs > Proposed design, tested members (E1) > hard_violations |
| `e6.faults.planted` | 26 | `results/e6_rules.json`: checker_catches_faults (count) |
| `e6.faults.caught` | 26 | `results/e6_rules.json`: checker_catches_faults > caught (count) |
| `e6.faults.checks_with_a_fault` | 20 | `results/e6_rules.json`: checker_catches_faults > check (distinct) |
| `e6.found_and_fixed.wrong reasons before the fix` | 916 | `results/e6_rules.json`: found_and_fixed > wrong reasons before the fix |
| `e6.found_and_fixed.flagged by the checker` | 916 | `results/e6_rules.json`: found_and_fixed > flagged by the checker |
| `e6.found_and_fixed.flagged after the fix` | 0 | `results/e6_rules.json`: found_and_fixed > flagged after the fix |
| `e6.test_cases.cases` | 13 | `results/e6_rules.json`: test_cases > cases |
| `e6.test_cases.match_expected` | 13 | `results/e6_rules.json`: test_cases > match_expected |
| `e6.test_cases.intent_holds` | 13 | `results/e6_rules.json`: test_cases > intent_holds |
| `e6.test_cases.hard_rule_violations` | 0 | `results/e6_rules.json`: test_cases > hard_rule_violations |
| `e6.all_hard_rules_hold` | yes | `results/e6_rules.json`: all_hard_rules_hold |

## Figures

All in `figures/`, 200 dpi PNG, 6.5 in wide. The same colour means the same method in every figure.

| File | Made by | What it shows | Suggested caption |
|---|---|---|---|
| `group_sizes.png` | notebook 01 | Group sizes in the synthetic community (training data). | Group sizes in the synthetic community: a few large groups and a long tail of small ones, as on real platforms. |
| `t4_hit_rate.png` | notebook 03 | How often today's BOING (biggest groups first) puts a hidden group among a member's 5 suggestions, against random suggestions (T4). | Today's ranking finds a hidden group for 22% of members, against 5% for random suggestions. |
| `t5_exposure.png` | notebook 03 | Where today's slots go (times each Discover group is shown) and the Lorenz curve of exposure (T5). | Today's ranking shows only 10 groups and never a new or small one (Gini 0.95; random suggestions: 0.08). |
| `t7_comparison.png` | notebook 04 | NDCG@5 and newcomer share for random, popularity, "also joined" and similar descriptions (first E1 table, T7). | "Also joined" is four times as accurate as today's ranking (NDCG@5 0.499 vs 0.131), but almost never shows a new or small group. |
| `t9_tastes.png` | notebook 05 | For each learned taste of the AI model (both ends), the hidden topics of its 10 top groups (T9). | The AI model, never told the topics, learns tastes that each pick out a hidden topic: it profiles members by itself. |
| `e1_methods.png` | notebook 06 | NDCG@5 and newcomer share for every method on the test (E1), with the quota q = 20% marked. | Every method on the test set: the hybrid is the most accurate (NDCG@5 0.541); fair re-ranking raises the newcomer share from 2.0% to 20% for 0.013 NDCG@5. |
| `e2_tradeoff.png` | notebook 07 | NDCG@5 against newcomer share for the 180 re-ranker settings, the Pareto front and the recommended setting (E2, test). | What fair exposure costs: each extra newcomer slot costs more accuracy. The recommended setting (q = 20%, c = 5%, n = 2, λ = 0.8) costs 0.015 NDCG@5 against the hybrid. |
| `e2_diversity.png` | notebook 07 | NDCG@5 and topics per list against the variety weight λ, for each topic cap n (E2, test). | Variety is nearly free down to λ = 0.8: topics per list rise from 2.40 to 2.59 for 0.002 NDCG@5. |
| `e3_privacy.png` | notebook 08 | NDCG@5 and newcomer share against the privacy budget ε, for caps m = 3, 5, 8 (E3, test, notebook 06's design). | The privacy-utility curve: below ε = 1 noisy statistics do worse than none; m = 3 is the best cap at every ε. (The final design, with every rule on, uses ε = 1.5: notebook 11.) |
| `e4_sybil.png` | notebook 09 | Members shown the target group against the number of fake accounts, for four attackers and six R9 settings (E4, test). | With R9 off, 100 fake accounts push a new group into 442 of 1,406 lists; with L = 3 and a 30-day wait, attackers A to C gain nothing, while accounts that wait a month and level up (D) still do. |
| `e5_newcomers.png` | notebook 10 | NDCG@5 by kind of member, and how often new and older small groups are shown and found (E5). | New members get far better suggestions than today's ranking at every level of history; the fair re-ranking gives new groups 4.2% and older small groups 16.1% of the slots. |
| `final_before_after.png` | notebook 11 | Hit rate and NDCG@5 (left), newcomer share and Gini of exposure (right): today's BOING against the final design (test). | Before and after on the test set: the final design (ε = 1.5) finds a hidden group for 61% of members (today 22%) and gives 20% of the slots to new or small groups (today 0%); its Gini of exposure falls from 0.95 to 0.53. Dashed: the 20% quota, met by the members who count. |
| `values_hierarchy.png` | report/figures.py | The values hierarchy: values, norms, design rules (report Figure 1; no data). | Values hierarchy of the recommender (after van de Poel, 2013): each value is specified as norms, and each norm becomes a testable design rule. |
| `pipeline.png` | report/figures.py | How a suggestion is made, and the rule each step enforces (report Figure 2; no data). | How a suggestion is made, and the rules each step enforces. Only the scoring step is learned. |
| `groups_screen_sketch.png` | report/figures.py | Sketch of the new Groups page for user 1 (report Figure 3). | Sketch of the new Groups page: the default list (left) and the personalised list with reasons (right). |
