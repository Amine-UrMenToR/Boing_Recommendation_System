# Model card: BOING group recommender (final design)

**Model.** Suggests 5 groups to join on BOING's Groups page, each with its main reason. ECSE 557, Group 14, Oct–Nov 2026; course design
project, not deployed. Code: `notebooks/boingrec.py` (`FINAL_CONFIG`), notebook 11; settings and reasons: `results/final_config.json`,
`results/final_choices.md`. Hybrid score: "also joined" (item-to-item overlap of memberships, {w_a}), public friends who are members ({w_g}),
hidden tastes (truncated SVD of the member × group table, 10 tastes, {w_d}: the learned, "AI" part) and TF-IDF similarity of group descriptions
({w_b}); the weights were chosen under the noisy statistics.
A fixed re-ranker then reserves 1 of 5 slots for new or small groups (small = fewer than 10 members who count under R9), caps any group at 5% of
all slots, allows at most 2 groups per topic cluster ({clusters} clusters of the descriptions) and spreads similar groups (MMR, λ = 0.8). Only
accounts at level 3+ count, each once, and their joins, posts and likes only once they are 30 days old; each member counts for at most 3 groups;
group sizes and pair counts get Laplace noise for ε = {eps}. Reasons come from fixed templates (no generated text); with the noise on, they
state no noisy count. This card is rebuilt from the results by `report/build/fill_docs.py`.

**Intended use.** Members of BOING (students, including teenagers) who switch personalisation **on**; everyone else sees the same design with
no profile (the default list). **Not for:** ranking posts or a feed, suggesting people, ads or paid placement, inferring anyone's traits,
decisions about a member (moderation, access, rewards), other platforms without re-tuning, or live use before it is checked on real,
consenting data.

**Data.** Built and evaluated only on a synthetic community (2,000 fake members, 150 groups, 10 hidden topics, seed 0; 1,406 members tested,
20% of their memberships hidden). **Uses only:** memberships, public posts and likes, friendships, blocks, topics members chose, "not
interested", account age, level, privacy and suspension, and group name, description, openness, age and moderation. **Never:** messages,
planner, coach chats, purchases, wallets or tokens, the answer key (hidden interests and topics, fake-account labels), real BOING data.

**Results (synthetic test set, 5 suggestions each).** With the noise on, every number is the mean of 10 noise draws. The range after NDCG@5 is
a 95% bootstrap range over members (each member's score averaged over the draws); "sd" is the spread of NDCG@5 across the 10 draws.

| | Hit rate | NDCG@5 | Slots for new or small groups | Lists without one | Gini of exposure | Groups shown |
|---|---|---|---|---|---|---|
| Today's BOING (biggest first) | {pop_hit_f} | {pop_ndcg} ({pop_lo}–{pop_hi}) | 0% | {pop_below} | {pop_gini} | {pop_cov} |
| Final design, personalisation on | {final_hit_f} | {final_ndcg} ({final_lo}–{final_hi}; sd {final_sd}) | {final_newc} | {final_below} | {final_gini} | {final_cov} |
| Default list, personalisation off | {off_hit_f} | {off_ndcg} | {off_newc} | {off_below} | {off_gini} | {off_cov} |

"Slots" counts new or small groups by the member count Discover shows; "lists without one" counts by the members who count (the design's
definition). By the members who count, the final design gives {final_newc_r9} of the slots to new or small groups; by the count Discover shows,
{final_below_shown} final lists hold no group under 10 members.
New members: NDCG@5 {new_members} (today {pop_new_members}); members with one group {one_group}, with no group yet {no_group} (newcomer quiz). New groups get
{share_new} of the slots and older small groups {share_small}; {found_nc} of the {hidden_nc} hidden test memberships in new or small groups are found (today 0).
**Fake accounts.** Accounts younger than 30 days or below level 3 change no statistic and no list: {sybil_ks} of them joining a new group or
posting and liking in an older one, and {promo_fakes} of them pushing {promo_rivals} rival small groups over the "small" line. Accounts that
wait a month and reach level 3 still can: 100 lift a new group into {d100} lists (the 5% cap is {cap_slots}), 100 that post and like put an
old group into {d100_post_default} default lists, and {sab_fakes_d} push a rival small group over the line ({sab_before_final} lists to {sab_after_d}; another group
gains {promo_d_gain}). **Hard rules** (no hidden, closed, joined or dismissed group; no private, blocked or suspended account named; private
data and paid budgets change nothing): 0 violations for all {members_all} members, and {faults} planted faults show each of the {checks}
checks can fire. **Reasons:** all {reasons_checked} faithful to the computed score. True to the raw data: {true_personal} on personalised lists
(the false ones name two groups that share nobody: {shared_false_final} of "shared members" reasons, {shared_false_lo} to {shared_false_hi}
across draws), and all {default_shown} on the default list. The best possible hit rate is {best_hit} ({unreach} hidden memberships are in
closed groups no method may suggest).

**Ethical considerations.** The AI part profiles members' tastes (they largely line up with the hidden topics), so it is opt-in (R1, Quebec's Law 25).
Fairness to new and small groups costs accuracy ({cost_rerank} NDCG@5), paid most by members with one group. **Privacy (R10):** ε-differential
privacy (ε = {eps}, odds bound {odds}) covers one release of the group sizes and pair counts. ε was chosen by our rule (keep 90% of the accuracy
and of the newcomer slots, with 95% confidence) on five practice quizzes; ε = 1 failed it. It does **not** cover the friends signal (public
friends' memberships, shown on their profiles), the member counts behind "small", the recent activity behind the default list (posts and like
counts of open groups; noise on it failed our rule), or the shared cap c (one member's own list can shift other members' lists: {cap_mean} on
average when one of the 30 non-counted members with the most memberships leaves, at most {cap_max}). Explaining reasons helps members and, a
little, manipulators: R9 and the cap limit the damage. No paid reach; 5 suggestions, no endless list.

**Limitations.** Synthetic data: trust the trade-offs more than the absolute numbers; relevance is "rejoins a hidden group", not satisfaction.
With noise, {shared_false_final} of "shared members" reasons name groups that share nobody; the noisy counts were close to the truth only
{would_close} of the time, so reasons state none. ε holds per release: release the statistics rarely. The topic cap acts on text clusters:
without noise {hidden_pile_exact} of lists hold 3+ groups of one hidden topic. Patient fake accounts (30 days, level 3) are not stopped, and can
push a rival small group over the "small" line. "Small" can name a group that has 10 or more members on Discover (fewer than 10 who count). At
launch most accounts are young, so the 30-day wait leaves little to learn from. No user study; ages are unknown.

**The off switch.** Personalisation is off by default; one switch per member turns it on or off, and "not interested" removes a group for
good. Off means no profile at all: the default list (recent activity and newness, with the same fairness rules and filters). The operator can
serve the default list to everyone (`personal = false`), or switch the recommender off and return Discover to its old ranking, at any time.
