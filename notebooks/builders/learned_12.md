## What we learned (version 2)

**The main world.** sim_v1's 5,374 friendships, 1,000 made in class, and 3,000 that close a triangle (focal closure), for 9,374 in
all. The average clustering is 0.153, against 0.007 in the first world, and 73% of friendships share a friend. The test hides
1,875 of them; 1,617 members are tested.

**The weight (practice quiz only).** w = 0.05 has the best NDCG@5 (0.041, tied with 0.1), against 0.019 for w = 1, BOING's
built-in weight. That means mutual friends first, with shared groups breaking ties and filling the list. Weighting groups by
1/log(size) did slightly better (0.043): a lead, not tuned.

**Relevance (H1: holds).**
- The design (w = 0.05) finds a hidden friend for **15.8%** of tested members (95% range 14.0–17.6%; NDCG@5 0.071).
- Mutual friends alone find 12.9% (11.4–14.6%); the ranges barely overlap.
- Shared groups alone find 3.2%, the most-connected people 0.9%, and random 0.8%.
- BOING as built (w = 1) finds 7.4%: shared groups swamp mutual friends, because courses are large.
- **Members with 0 or 1 friends** (28): the design finds a friend for 17.9%, mutual friends alone for 14.3%, and BOING as built
  for 7.1%. Mutual friends alone leave 43% of these members with an empty list; the design leaves none. The slice is small (5 and 4
  members).
- In the first world (no triangle closure), every method is weak: the design 1.7%, shared groups alone 2.0%, mutual friends
  alone 0.6%.

**The rules hold (H2: holds).**
- 0 violations in **72,440** rule checks: every list (36,733), the 243-case age grid (2,480; 138 allowed, 105 refused, all as
  the rule says) and the community with 191 planted cases (33,227).
- No planted case comes back; with the matching rule removed, 166 of them do.
- The checker caught all 18 planted faults.

**Exposure (H3: holds).**
- The design spreads exposure more evenly than any other method that uses the network: Gini 0.40, the top 10% take 25% of the
  slots and 96% of the pool is shown. Mutual friends only: Gini 0.48. Most connected: Gini 0.98, the top 10% take everything.
- Newcomers are still under-exposed: 5.4% of slots for 15.2% of the pool.

**Cost of the rules (H4: holds).**
- Every rule together: 0.120 NDCG@5 (95% range 0.105–0.135), 63% of the unconstrained score.
- Consent costs the most: 0.090 (0.076–0.103). With 25% switched on, the best possible hit rate is 32% (83% with everyone on), and
  the hit rate goes from 8.5% (10% on) to 32.6% (everyone on).
- The safety filters cost 0.024 (private profiles are 22% of the community). The age bands cost 0.006 (0.002–0.011).
- Variety costs nothing.

**The age bands.**
- Minors (14 to 17, or no birth year; 201 tested) find a hidden friend: 10.9% with no age rule, **9.0%** under the bands, 2.5%
  under the binary line.
- Under the bands, no one over 20 is shown a minor (109 slots with no age rule). 18- to 20-year-olds are shown minors only as
  classmates: 58 slots, against 55 classmate and 62 non-classmate slots with no rule.
- Under-14s are never shown and get no list.

**Limits.**
- The closure model, ages, courses and switch shares are assumptions.
- The target clustering (0.15) was lowered from 0.20 because this generator levels off near 0.17, before any test result.
- Ages are drawn independently of the network.

Files: `results/e7_methods.csv`, `e7_few_friends.csv`, `e7_costs.csv`, `e7_age_rules.csv`, `e7_opt_in.csv`, `e7_closure.csv` (the
first world), `e7_validation.csv`, `e7_age_grid.csv`, `e7_rules.json`, `e7_people.json`, `figures/e7_people.png`.
