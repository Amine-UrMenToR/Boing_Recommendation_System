# The final design: what we chose, and why

Written for the report's Discussion (section 4). Every number comes from `results/` (notebook 11 unless another is named; all of them are also
in `summary.json` with their source). This file is rebuilt from `report/build/templates/final_choices.md` by `report/build/fill_docs.py`, which
notebook 11 runs: no number here is typed by hand. Everything is measured on the **synthetic** community: 2,000 fake members, 150 groups.
"Practice quiz" is a validation split of the training data (1,090 members), where every choice was made; "test" is the 1,406 tested members,
used only to report.

**Updated 1 November, after two independent reviews** of the first final design. What changed, and why, is in the last two sections. The
first design (`br.FINAL_CONFIG_BEFORE_REVIEW`, ε = 5) stays as a row of every table in notebook 11.

## The design in one paragraph

For a member who switches personalisation on, BOING scores every group they may join with four signals: how many members of their groups also
joined it ("also joined", weight {w_a}), their public friends who are in it ({w_g}), the AI model's hidden tastes ({w_d}) and similar
descriptions ({w_b}). It then re-ranks the list of 5: at least one slot for a new or small group, no group above 5% of all slots, at most two
groups of one **topic cluster** ({clusters} clusters of the group descriptions), and similar groups spread out. "Small" means fewer than 10
members **who count**: only accounts at level 3 or more count, and an account's joins, posts and likes count only once it is 30 days old. Each
member counts for at most 3 groups, and the group sizes and pair counts get differential-privacy noise for ε = {eps} ({share_pct} of it on the
sizes). Every suggestion shows its main reason; with the noise on, a "shared members" reason names the group but not a count. With
personalisation off, which is the default, every member gets the same fair list with no profile. In code: `boingrec.FINAL_CONFIG`; as data:
`results/final_config.json`.

## How the dials were chosen

- **Each dial was chosen on the practice quiz, by a rule written down before looking**, never on the test. The rules allow a stated price:
  fair re-ranking may cost at most 5% of the hybrid's accuracy (E2), privacy at most 10% of the accuracy and of the newcomer slots (E3), and the
  fake-account rule must stop attackers A to C without a cost beyond noise (E4).
- **Hard rules are never traded** (R1, R2, R3, R6, R7, R8, R11). The checker found 0 violations for all {members_all} members, with
  personalisation on and off (notebook 11, section 7), and each of its {checks} checks caught a fault planted on purpose ({faults} faults,
  notebook 10).
- **The dials were then checked together** on the practice quiz (notebook 11, section 2), because each experiment had set its own dials with the
  others at notebook 06's values. After the second review, the choices that rest on small differences (ε and the topic clusters) are made on
  **five** practice quizzes (five random splits of the training data), so that luck in one split cannot decide them.

## Dial by dial

| Dial | Value | What it buys | What it costs (test, NDCG@5 unless said) | Value served |
|---|---|---|---|---|
| Weights α, β, γ, δ | {w_a}, {w_b}, {w_g}, {w_d} | the most accurate mix under the final, noisy statistics (rank {w_rank} of 286); notebook 06's 0.4, 0.1, 0.3, 0.2 is the most accurate without noise (hybrid {hybrid_ndcg}) | {cost_weights} without noise; with noise it is the more accurate | usefulness, privacy (R10) |
| k (AI model) | 10 tastes | the best of 5, 10, 20, 40 on the quiz | — | usefulness |
| topic_weight | 0 | — | chosen topics never changed accuracy on the quiz, so they do not count | — |
| q (quota) | 20% (1 of 5 slots) | every list holds a new or small group: {final_newc_r9} of the slots by the members who count ({final_newc} by the count Discover shows) instead of 2% | {cost_rerank} for q, c, n and λ together | equity, inclusion (R4) |
| "small" | fewer than 10 members who count | the quota holds without noise ({final_below} lists without a new or small group by that count; {before_below} before the first review); fake accounts that R9 ignores cannot push a group over the line | {cost_public} for "small" from the count Discover shows (with the change to {clusters} clusters); by that count, {final_below_shown} lists hold no group under 10 members | equity (R4), trust (R9), honest reasons (R6) |
| c (cap) | 5% of all slots | the default list shows {off_cov} groups instead of 8; no group takes everyone's attention | nothing on personalised lists (no group reaches 5% there) | equity (R4) |
| n (topic cap) | 2 per topic cluster | more variety in each list | within noise | diversity, autonomy (R5) |
| clusters | {clusters} | the fewest lists with 3 or more groups of one member-chosen topic, on average over five quizzes, within E2's budget ({pile_chosen}) | within E2's budget | diversity (R5) |
| λ (variety) | 0.8 | lists of less alike groups | within noise | diversity (R5) |
| L (level bar) | 3 | accounts at level 1 or 2 never count | with the 30-day wait: {cost_r9} (95% range {cost_r9_low} to {cost_r9_high}) | trust, fairness to group owners (R9) |
| burst_w, r9_scope | 0 (30 days), on joins, posts, likes, friends and "small" | accounts younger than 30 days or below level 3 change no count, no activity, no friends signal and no "small" line (tested with {sybil_ks} of them joining or posting, and {promo_fakes} pushing {promo_rivals} rival small groups over the line) | {honest_wait} of honest memberships wait 30 days before they count for others (E4) | trust (R9) |
| ε, m, split | {eps}, 3 groups, {share_pct} on the sizes | the group sizes and pair counts: one member changes the odds of any result by at most e^{eps} ≈ {odds} (one release) | {cost_r10} | privacy of everyone whose memberships feed others (R10) |
| act_eps | none | (noise on the recent activity was tried and failed the rule) | — | — |
| count_under_noise | false | with the noise on, a "shared members" reason names the group without a count: only {would_close} of those noisy counts were close to the truth | the reason is less precise | honest reasons (R6) |
| Default | personalisation off | no profiling unless a member asks for it | the default list scores only {off_ndcg} (today's BOING: {pop_ndcg}) | privacy, autonomy (R1, Law 25) |
| off_new_w (default list) | 0.5 | new or small groups get about the share random suggestions would give them ({off_quiz_newc} on the quiz) | on the quiz, NDCG@5 {off_quiz_ndcg} against {off_quiz_ndcg0} with a newness weight of 0 or 0.25, for a newcomer share of {off_quiz_newc} instead of {off_quiz_newc0} | equity (R4), autonomy (R1) |

### The weights and the AI model (notebooks 04 to 06, re-chosen in notebook 11)

Notebook 06 chose the weights for accuracy alone, on the practice quiz, with no clipping and no noise: the hybrid beats each of its parts.
Notebook 11 ran all 286 mixes again under the final, noisy statistics (5 noise draws), as the first review asked. There notebook 06's mix
(0.4, 0.1, 0.3, 0.2) loses: ({w_best}) beats it by {w_gap} NDCG@5 (95% range {w_gap_lo} to {w_gap_hi}). "Also joined" divides each overlap by
two noisy group sizes, so it suffers most from the noise, and the new mix leans on it less. By the rule written before the run, the mix
changed, and the other choices (clusters, ε) ran again with it; the mix then held. Without noise the new mix costs {cost_weights} NDCG@5; with
noise it is the more accurate one. The AI model learns 10 hidden tastes, which largely line up with the hidden topics it never sees
(notebook 05): exactly the profiling the opt-in (R1) is for. Chosen topics (`topic_weight`) did not help on the quiz, so they are off: a member's "topics I
like" choice changes nothing in this design.

### Fair exposure: q = 20%, c = 5%, n = 2, λ = 0.8 (E2, notebook 07), with "small" from the members who count (notebook 11)

- **q buys the most:** today's BOING never shows a new or small group; the quota gives every list one. A second newcomer slot (q = 40%) would
  cost 0.022 NDCG@5 more and a third 0.038 more: fairness gets dearer with each slot, so we stop at one. The budget (95% of the hybrid's
  accuracy) is our judgement; with a 10% budget the rule would pick q = 40%.
- **What "small" counts, in three steps.** (1) The first version judged "small" from the recommender's own counts. With clipping (each member
  counted for at most 3 groups) and R9, mid-sized groups looked small: on the test, {before_below} of 1,406 lists held no group that is new or
  small by the count Discover shows, and the newcomer share was {before_newc}. (2) The first review's fix used the member count Discover shows.
  But that count includes every account, so cheap fake accounts could push a *rival* small group over 10 members: {sab_fakes} brand-new accounts at level 1
  or 2 took *{sab_group}* from {sab_before_first} lists to {sab_after_first}, and another small group gained {promo_first_gain} lists.
  (3) Now "small" counts only the members who count under R9 (level 3 or more, at least 30 days old). Those cheap accounts change nothing
  (section "Fake accounts" below). The cost: by the count Discover shows, {final_below_shown} of the 1,406 lists hold no group under 10 members
  (on average over the noise draws): their newcomer slot went to a group with 10 or more members on Discover but fewer than 10 who count. And
  {small_true_shown} of the "A small group" reasons name a group that has fewer than 10 members on Discover (all of them have fewer than 10 who
  count).
- **Who pays:** members with one group pay most (E5): the newcomer slot replaces one of their few good suggestions.
- **c changes nothing for personalised lists** and helps the default list, where everyone sees nearly the same groups. It also caps the worst
  fake-account attack (below).
- **n and λ are almost free.** But the topic cap is weak: it caps clusters of the group *texts*, which match the real topics poorly. Without
  privacy noise, {hidden_pile_exact} of the lists hold 3 or more groups of one hidden topic (the hybrid, with no re-ranking at all:
  {hidden_pile_hybrid}); with it, {hidden_pile_final}, because the noise scatters the lists, not because of the cap. The number of clusters is a
  close call: on average over five quizzes {clusters} clusters give {pile_chosen}; 15 clusters (the choice on one quiz before the second review)
  give {pile_15} but keep only {budget_15} of the hybrid's accuracy, under E2's budget; and on each quiz alone the rule picks {clusters_each}.
  Clusters learned from the AI model's tastes would do much better ({pile_tastes} of quiz lists), but keep only {tastes_budget} of the hybrid's
  accuracy, below the 95% budget. So we say "at most two groups of one topic cluster", not "of one topic".

### Fake accounts: L = 3 and a 30-day wait, on joins, posts, likes, friends and "small" (E4, notebook 09; notebook 11)

What they **cannot** do. Accounts younger than 30 days or below level 3 (attackers A, B and C) change no statistic and no list, noise included.
We checked with {sybil_ks} of them that join a new group or that also post and like in an older group, and with {promo_fakes} of them
that push {promo_rivals} rival small groups over the "small" line.

What they **can** do. Accounts that wait a month and level up (attacker D) are not stopped. 100 of them push a new group into {d100} lists;
the 5% cap stops them at {cap_slots} of the {all_slots} slots. {sab_fakes_d} of them push *{sab_group}* (members on Discover: {sab_members}; members who
count: {sab_counted}) over the line: it falls from {sab_before_final} lists to {sab_after_d}, and another small group gains
{promo_d_gain}. {promo_d4_fakes} of them on 4 rivals take {promo_d4_lost} lists from the rivals, and one other group gains {promo_d4_gain}.
The default list moves too: 100 of them that post and like put an old group into {d100_post_default} default lists (without the attack:
{post_default_before}), again stopped by the 5% cap. Pushing rivals over the "small" line changes no default list. (Default lists were not
counted in the attack that joins a new group.)

Why a weight of 0 and not 0.25: any weight above 0 only means the attacker needs more cheap accounts. Before R9 covered posts and likes, 20
young levelled-up fake accounts that post once and like a few posts put an old group that no default list showed into 703 lists (notebook 09,
section 10, with notebook 09's 10% cap). The price is small for accuracy and real for newcomers: {honest_wait} of honest memberships wait 30
days before they count for others. At launch, when nearly every account is young, the 30-day wait leaves little to learn from: switch it on
once enough accounts are older.

### Privacy: ε = {eps}, m = 3, {share_pct} of ε on the sizes (E3, notebook 08, re-chosen in notebook 11)

- **What it covers, exactly.** Differential privacy for **one release of the group sizes and pair counts** (X^T X), from which "also joined"
  and the AI model are computed: adding or removing one member, with all their memberships, changes the odds of any of these by at most
  e^{eps} ≈ {odds}. This holds for every member, including those who never opt in. Checked: removing any one of 100 members changed the
  clipped counts by at most {sens_sizes} (sizes) and {sens_pairs} (pairs), within the bounds the noise assumes (3 and 3).
- **What it does not cover** (notebook 11, section 8): (1) the friends signal, which counts a public friend's memberships in full
  ({friends_over} of the {friends_pairs} public friendships of tested members involve a friend in more than 3 groups): it rests on public
  profiles; (2) the member counts that decide "small" (no noise; Discover shows every group's count anyway); (3) the recent activity behind the
  default list: removing one active member's posts changed {act_changed} other members' default lists. Noise on the activity was tried
  (counting the members who posted, each in at most 3 groups): the definition alone keeps {act_def_kept} of the default list's accuracy and no
  budget keeps more than {act_best_kept}, so it failed the 90% rule; in BOING an open group's posts and like counts are shown to anyone who
  opens it; (4) the shared cap c: members are served in turn, so one member's own list can change which capped groups later members get.
  Removing the memberships of one of the 30 members who do not count and hold the most memberships (no statistic changed) changed {cap_mean}
  other members' lists on average, at most {cap_max}.
- **What it costs:** {cost_r10} NDCG@5 ({exact_ndcg} to {final_ndcg}), and {shared_false_final} of "shared members" reasons name two groups
  that truly share no member (below). The newcomer share does not fall: "small" does not depend on the noise.
- **Why ε = {eps}.** The rule, written before the run, is unchanged since the first review: stage 1 (notebook 08's grid) picks m and the split
  ({share_pct} of the budget on the sizes); stage 2 tries ε from 0.5 to 5, and **a setting passes only if the lower end of its 95% range keeps
  at least 90% of the accuracy and of the newcomer slots; the smallest passing ε is chosen**. What changed after the second review is the
  evidence. The first time, stage 2 used one practice quiz and 20 noise draws, the same quiz and draws that had picked the weights, and the
  range covered only the noise; there ε = 1 passed by a thin margin. Now stage 2 uses **five practice quizzes with 20 fresh draws on each**,
  and the range covers which members are on the quiz as well as the noise. With notebook 06's weights the rule picks ε = {r1_eps}; with the
  weights re-chosen for noisy statistics it picks **ε = {eps}**, which keeps {epsc_acc} of the accuracy (95% range {epsc_lo} to {epsc_hi}).
  ε = {eps_below} keeps {eps_below_acc} (range {eps_below_lo} to {eps_below_hi}) and fails: it passes the first rule on {eps_below_alone} of
  the 5 quizzes, and {eps_below_single} of single releases keep less than 90% of the accuracy. At ε = {eps}, {epsc_single} of single releases
  do. On the test, ε = 0.5 would cost {cost_eps05} more NDCG@5; ε = 2 would give back {gain_eps2} and ε = 5 {gain_eps5}.
- **Why m = 3.** Counting each member for at most 3 groups bounds what one member can change, so less noise is needed (the noise on a pair count
  grows with m(m−1)/2). On the practice quiz, m = 3 is the most accurate cap at every ε, in E3 and again in notebook 11.
- **Releases add up.** ε holds for one release of the statistics. If BOING recomputed them every night, the guarantees would add up (basic
  composition), so the noisy statistics should be released rarely (for example once a week) or the budget split across releases. The noise seed
  must be secret.

## Faithful reasons and true reasons

Every reason is **faithful to the computed score** ({reasons_faithful} of {reasons_checked}): it names the part that adds the most, a quota slot,
or the fact used. That is what the checker (`check_rules`) measures; with the noise on it rebuilds the noisy counts itself from the raw tables
plus the recommender's random draws. Faithful is not the same as true. Read against the raw data (`check_facts`), and judged strictly (a
number a reason states must be within a factor 2 of the truth, or within 3):

- **Personalised lists:** {personal_true} of {personal_shown} reasons are true ({true_personal}). The false ones are "shared members" reasons
  whose noisy overlaps point at groups that share nobody: {shared_false_final} of those reasons at ε = {eps} ({shared_false_lo} to
  {shared_false_hi} across the 10 noise draws; {shared_false_eps5} at ε = 5; none without noise).
- **Default lists:** {default_true} of {default_shown} reasons are true. They state only facts read directly ("Active this week", "A new group").
- **The numbers.** Before the first review a "shared members" reason stated the noisy count ("About 17 members of X are in it"). Only
  {before_close} of those counts were close to the truth, and at ε = {eps} only {would_close} would be. So, with the noise on, the reason now
  says "Members of X also joined it", with no number. Without noise, numbers stay; with clipping only (the test cases), the "About" counts are
  close {clip_close} of the time.

So "How suggestions work" must say that "also joined" rests on estimates.

## Where the rules pull against each other

1. **Privacy (R10) against honest reasons (R6).** The stronger the privacy, the more "shared members" reasons point at a link that does not
   exist, and the less a stated count can be trusted (so none is stated).
2. **Fake-account resistance (R9) against newcomers.** New accounts' joins, posts and likes count only after 30 days, for the statistics and for
   "small"; new members' own suggestions are not hurt, but their activity helps others later.
3. **Fake-account resistance (R9) against the count members see (R4, R6).** Counting only the members who count stops cheap fakes from pushing
   rivals over the "small" line, but a group with 10 or more members on Discover can still be called small.
4. **Fairness (c) as a defence, and as a privacy leak.** The 5% cap, chosen for fair exposure, also caps the strongest attack at {cap_slots} of
   {all_slots} slots; but because it is shared, one member's own list can shift a few other members' lists, outside the privacy guarantee.
5. **Diversity (R5) against accuracy.** A topic cap that really follows the topics (clusters of the AI model's tastes) would cost more accuracy
   than E2's budget allows; the text clusters cost little but do little.

## What it means for each stakeholder

| Stakeholder | What the final design means for them |
|---|---|
| Members looking for groups | A useful list when they opt in: a hidden group among the 5 for {final_hit} of members (today {pop_hit}), each with its reason. |
| New members, members with few groups | Far better than today (NDCG@5 {no_group} to {one_group} against 0.13 to 0.16, on the newcomer quiz); members with one group pay most for the quota. |
| New and small groups | Shown in every list ({final_newc_r9} of the slots by the members who count, {final_newc} by the count Discover shows; today none); {found_nc} of the {hidden_nc} hidden test memberships in them found, on average over the noise draws (today 0). |
| Large groups | Fewer slots: no group takes more than 5% of them; the Gini of exposure falls from {pop_gini} to {final_gini}. |
| Group owners | New or low-level fake accounts cannot push a group up, by joining, posting or pushing rivals over the "small" line; patient ones (a month old, level 3+) can, up to the 5% cap, and can push a rival small group over the line. |
| Members whose data feeds others | Their memberships are counted for at most 3 groups, under noise (ε = {eps}). Not under noise: their posts (recent activity); their groups, if their profile is public (friends signal); their memberships in the counts that decide "small" (once they count under R9); and their own list, which takes slots under the shared cap and so can shift a few other lists. Never named unless a public friend; never profiled unless they opt in. |
| Teenage members | No people suggestions; blocked, private and suspended accounts never named; hidden and closed groups never shown. |
| Moderators | Hidden groups never appear; nothing new to moderate, except bursts of new accounts joining one small group. |
| The platform | 5 suggestions, no endless list, no paid reach; one switch turns personalisation off for a member, one setting for everyone. |

## How to read the absolute numbers

The synthetic community decides the absolute numbers; we trust the trade-offs (what each value costs relative to the others) more than the
levels. Also, {unreach} of the 1,531 hidden test memberships are in closed groups that no method may suggest, and {unreach_members} tested members
have only such hidden groups: no method can find a hidden group for them, so the best possible hit rate is {best_hit}. Comparisons between
methods are not affected.

## What we would revisit with real, consenting members

First, whether members read "also joined" reasons as estimates, whether "A small group" confuses them when Discover shows 10 or more members,
and whether the "off" switch is found. Then ε and the release schedule; the 30-day wait at launch; a topic cap that follows real topics; and
whether the default list's activity should be protected too (if BOING kept open groups' posts to members only).

## What the first review changed (1 November)

| Issue | What we did |
|---|---|
| The privacy claim was broader than the code | Narrowed everywhere to "one release of the group sizes and pair counts"; measured what lies outside (friends, member counts, activity, the shared cap); tried noise on the activity (failed the rule). |
| R9 covered joins only | R9 now covers posts, likes and friends (`r9_scope = 'all'`); notebook 09 added fake accounts that post and like. |
| The quota held only on the recommender's own counts | "Small" came from the member count Discover shows (`small_from = 'public'`); the second review changed this again (below). |
| "100% fidelity" read as "all reasons true" | Renamed "faithful to the computed score"; the checker rebuilds the noisy counts itself; a separate check of truth (`check_facts`). |
| The topic cap was claimed per topic | Claims say "topic cluster"; the hidden-topic rate is reported; the number of clusters is chosen on the quiz. |
| ε moved on a coarse grid inside the noise | Finer grid, more draws, a rule written before the run. |
| Weights tuned without clipping or noise | Re-checked under the final statistics: they changed to {w_a}, {w_b}, {w_g}, {w_d}, and the other choices ran again with them (rounds) until the weights held. |
| off_new_w's trade-off was not stated | Stated above. |
| Hidden groups no method can reach | Reported as a ceiling (best possible hit rate {best_hit}); the split is unchanged, so earlier numbers stay comparable. |
| Faults covered few checks | Planted faults for every check, including faulty recommenders for R2 and R3 (notebook 10). |
| Test cases only in a relaxed regime, noise untested | Case 12: a larger world where no rule is relaxed; case 13: the noise on, with its draws as data (`noise.csv`). |

## What the second review changed (1 November)

| Issue | What we did |
|---|---|
| "Small" from the count Discover shows let cheap fake accounts push rival small groups over the line and lift another group (a way around R9) | "Small" counts only the members who count under R9 (`small_from = 'r9'`); notebook 11 tests pushing 1, 2 or 4 rivals: attackers A to C change nothing; D can, and the numbers are above. Claims that new or low-level accounts "change nothing" now say exactly what they cannot and can do. |
| ε = 1 passed the rule only on one practice quiz, with the draws that had picked the weights | The same rule on five practice quizzes with fresh noise draws, the range covering both: ε = {eps}. The topic clusters are chosen on the same five quizzes: {clusters}. Everything after them was run again. |
| "98% of reasons true" mixed in the default list (true by construction) and accepted any stated count | Personalised and default lists reported apart; a stated count must be close to the truth; the per-draw range is given; with the noise on, reasons state no count. |
| The shared cap: accounts that do not count still take slots | Said in test case 08 and in the stakeholder table (members whose data feeds others), with the measured effect ({cap_mean} lists on average). |
| The documents were filled by a script outside the repository; one cell ran 17 minutes | `report/build/fill_docs.py` and its templates are in the repository and notebook 11 runs it; section 2 is split into one cell per half-round and runs 6 processes at once. |
| The private-data check (R2) never altered the test file, and no planted fault used the final design | R2 now also reruns the recommender while the files it must never read are altered; {faults} planted faults, including a recommender that reads the test file and three faults in the final design (wrong noise draw, young friends counted, "small" from the noisy counts). The young-friend fault showed a gap: the "names someone who does not count" check now also knows about the 30-day wait. |
| Small slips in the text | Corrected: the 10% cap of notebook 09 (703 lists), the cap relaxed about 50 times per test case, 9 fake accounts, the taste gap, what "small" is computed from, and what the model card's ranges are. |
