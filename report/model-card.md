# Model card: BOING group recommender (final design)

**Model.** Suggests 5 groups to join on BOING's Groups page, each with its main reason. ECSE 557, Group 14, Oct–Nov 2026; course design
project, not deployed. Code: `notebooks/boingrec.py` (`FINAL_CONFIG`), notebook 11; settings and reasons: `results/final_config.json`,
`results/final_choices.md`. Hybrid score: "also joined" (item-to-item overlap of memberships, 0.2), public friends who are members (0.3),
hidden tastes (truncated SVD of the member × group table, 10 tastes, 0.3: the learned, "AI" part) and TF-IDF similarity of group descriptions
(0.2); the weights were chosen under the noisy statistics.
A fixed re-ranker then reserves 1 of 5 slots for new or small groups (small = fewer than 10 members who count under R9), caps any group at 5% of
all slots, allows at most 2 groups per topic cluster (8 clusters of the descriptions) and spreads similar groups (MMR, λ = 0.8). Only
accounts at level 3+ count, each once, and their joins, posts and likes only once they are 30 days old; each member counts for at most 3 groups;
group sizes and pair counts get Laplace noise for ε = 1.5. Reasons come from fixed templates (no generated text); with the noise on, they
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
| Today's BOING (biggest first) | 0.220 | 0.131 (0.117–0.146) | 0% | 1,406 | 0.95 | 10 |
| Final design, personalisation on | 0.613 | 0.488 (0.466–0.510; sd 0.008) | 19.9% | 0 | 0.53 | 127 |
| Default list, personalisation off | 0.105 | 0.058 | 44.1% | 0 | 0.84 | 23 |

"Slots" counts new or small groups by the member count Discover shows; "lists without one" counts by the members who count (the design's
definition). By the members who count, the final design gives 20.8% of the slots to new or small groups; by the count Discover shows,
55 final lists hold no group under 10 members.
New members: NDCG@5 0.343 (today 0.134); members with one group 0.40, with no group yet 0.34 (newcomer quiz). New groups get
7.2% of the slots and older small groups 12.7%; 12.5 of the 42 hidden test memberships in new or small groups are found (today 0).
**Fake accounts.** Accounts younger than 30 days or below level 3 change no statistic and no list: 100 and 200 of them joining a new group or
posting and liking in an older one, and 9, 11 or 24 of them pushing 1, 2 or 4 rival small groups over the "small" line. Accounts that
wait a month and reach level 3 still can: 100 lift a new group into 351 lists (the 5% cap is 351), 100 that post and like put an
old group into 351 default lists, and 9 push a rival small group over the line (126 lists to 17; another group
gains 9). **Hard rules** (no hidden, closed, joined or dismissed group; no private, blocked or suspended account named; private
data and paid budgets change nothing): 0 violations for all 1,983 members, and 26 planted faults show each of the 20
checks can fire. **Reasons:** all 19,830 faithful to the computed score. True to the raw data: 97.3% on personalised lists
(the false ones name two groups that share nobody: 41% of "shared members" reasons, 31% to 52%
across draws), and all 10,085 on the default list. The best possible hit rate is 95.3% (79 hidden memberships are in
closed groups no method may suggest).

**Ethical considerations.** The AI part profiles members' tastes (they largely line up with the hidden topics), so it is opt-in (R1, Quebec's Law 25).
Fairness to new and small groups costs accuracy (0.015 NDCG@5), paid most by members with one group. **Privacy (R10):** ε-differential
privacy (ε = 1.5, odds bound 4.5) covers one release of the group sizes and pair counts. ε was chosen by our rule (keep 90% of the accuracy
and of the newcomer slots, with 95% confidence) on five practice quizzes; ε = 1 failed it. It does **not** cover the friends signal (public
friends' memberships, shown on their profiles), the member counts behind "small", the recent activity behind the default list (posts and like
counts of open groups; noise on it failed our rule), or the shared cap c (one member's own list can shift other members' lists: 0.2 on
average when one of the 30 non-counted members with the most memberships leaves, at most 5). Explaining reasons helps members and, a
little, manipulators: R9 and the cap limit the damage. No paid reach; 5 suggestions, no endless list.

**Limitations.** Synthetic data: trust the trade-offs more than the absolute numbers; relevance is "rejoins a hidden group", not satisfaction.
With noise, 41% of "shared members" reasons name groups that share nobody; the noisy counts were close to the truth only
29% of the time, so reasons state none. ε holds per release: release the statistics rarely. The topic cap acts on text clusters:
without noise 68% of lists hold 3+ groups of one hidden topic. Patient fake accounts (30 days, level 3) are not stopped, and can
push a rival small group over the "small" line. "Small" can name a group that has 10 or more members on Discover (fewer than 10 who count). At
launch most accounts are young, so the 30-day wait leaves little to learn from. No user study; ages are unknown.

**The off switch.** Personalisation is off by default; one switch per member turns it on or off, and "not interested" removes a group for
good. Off means no profile at all: the default list (recent activity and newness, with the same fairness rules and filters). The operator can
serve the default list to everyone (`personal = false`), or switch the recommender off and return Discover to its old ranking, at any time.
