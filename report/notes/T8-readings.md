# T8: Notes on the key readings

> Drafted with Claude (Anthropic) on 30 Oct 2026 from the original texts listed under each reading. Read the
> originals yourselves, rewrite in your own words before anything goes into the report, and log this use in
> `../../AI-USE-LOG.md`. Full references are in `../references.md`.

---

## (a) Singh & Joachims (2018), "Fairness of Exposure in Rankings" (KDD '18)

Read: Sections 1, 3 and 4 (the framework and the three fairness constraints); proofs and experiments skimmed.
Source: arXiv 1802.07281, same text as the KDD paper (https://doi.org/10.1145/3219819.3220088).

- **Exposure is what a ranking hands out.** A ranking does not only serve the person searching. It also shares
  out attention among the items ranked, and attention is scarce. The paper calls an item's share of attention its
  *exposure* and asks whether that share is fair to the items (people, sellers, groups), not only useful to the user.
- **Position bias makes small gaps big.** People look at the top far more than the bottom. The paper models the
  attention at position *j* with a weight that falls with rank, for example 1/log(1 + *j*) as in DCG. Its job-seeker
  example: three men with relevance 0.80, 0.79, 0.78 and three women with 0.77, 0.76, 0.75. Ranking purely by
  relevance gives the women about 30% less exposure, although they are only 0.03 less relevant on average. They call
  this a "winner-take-all" allocation.
- **The method: a ranking chosen by chance, within limits.** Instead of one fixed list, the system picks a
  *probabilistic* ranking: a table P (a doubly stochastic matrix) of how often each item appears at each position.
  An item's exposure is then the sum over positions of P(item at *j*) × weight of *j*. Expected usefulness and the
  fairness rules are both linear in P, so a linear program finds the most useful table that obeys the rules. Real
  lists are then drawn from it (Birkhoff–von Neumann decomposition), so fairness holds on average over many showings.
- **Three fairness constraints between two groups.** (1) *Demographic parity*: both groups get the same average
  exposure, whatever their relevance. (2) *Disparate treatment*: each group's exposure is proportional to its average
  relevance ("merit"). (3) *Disparate impact*: each group's expected clicks are proportional to its relevance. Parity
  is the simplest but can cost a lot of usefulness when the groups really differ; the merit-based rules cost less.
- **Fairness has a measurable price, often small, and it is not the same as diversity.** In the job example, the
  fair ranking's DCG drops only from 3.8193 to 3.8031 under parity. The authors also stress that diversifying a list
  serves only the *user*, while fair exposure balances the needs of users *and* items, so the two are separate goals.

**For our design (R4 fair exposure):** our newcomer share q is a parity-style floor for the group "new or small"; we
should also report a merit-based check (do new groups get exposure in proportion to their relevance?), weight slots by
position rather than only counting them, and keep R4 (fairness to groups) apart from R5 (diversity for the member),
as the paper does. E2's accuracy-against-newcomer-share curve is exactly its price-of-fairness question.

---

## (b) Tournesol (tournesol.app) and Hoang et al. (2021)

Read: the paper's Sections 1–3 (arXiv 2107.07334, v1 of 29 May 2021) and the current documentation of Tournesol's
scoring library, Solidago (https://solidago.tournesol.app/modules/trust_propagation/). The platform's own pages load
with JavaScript and could not be read by our tools, so the notes rely on the paper and the documentation.

- **What it is and why.** Tournesol is an open-source platform where volunteers judge which YouTube videos should be
  recommended widely. Its starting point is that "any algorithm trained on uncontrolled data must not be trusted",
  because anyone can poison that data. So it builds a large, secure public database of human judgements, then
  computes recommendations from it.
- **How it collects judgements: comparisons, not stars.** A contributor picks two videos and moves a slider from 0 to
  100 to say which one should be recommended more, and by how much. Optional sliders cover quality criteria such as
  "reliable and not misleading" or "important and actionable". Comparisons avoid two problems with rating scales:
  people who always give extreme scores, and people who use the same scale to mean different things.
- **Resisting fake accounts: trusted, verified accounts.** In the 2021 version, only *verified* accounts shape the
  global scores (unverified ones get personal scores only). An account is verified with an email from a *trusted
  domain*: one where creating many fake accounts seems unlikely (for example @epfl.ch or @who.int, not @gmail.com).
  Verified accounts can also *vouch* that another account is a real person with only one account. The paper admits
  this is imperfect: it does not rule out fakes, and it leaves most would-be contributors out. Today, pre-trust from
  email domains and vouches are combined into a trust score between 0 and 1 by a PageRank-like method (LipschiTrust)
  built so that no account gains outsized influence.
- **Resisting manipulation: robust aggregation.** Comparisons are turned into scores with a Bradley–Terry-style model
  inside the "Licchavi" framework, which follows the rule "one contributor, one unit force": each person can pull a
  video's global score only by a bounded amount. With many contributors the global score tends to the *median* of
  their scores. The goals are Byzantine resilience (a minority of malicious accounts cannot move the result much) and
  approximate strategyproofness (lying does not pay). The authors say openly that their theorems only partly cover the
  deployed version.
- **Transparency.** The code is open source, most design discussions are public, the public judgements can be
  downloaded (CC BY-SA), and the paper explains the scoring formulas and settings. Contributors choose to rate each
  video publicly or privately (private ratings still count), and users can re-weight the quality criteria with
  sliders to change their own recommendations.

**For our design (R9 fake accounts, R6 explanations):** R9's "only established accounts count, once each" is our
version of Tournesol's trusted accounts plus "one contributor, one unit force", and their admitted cost (honest
newcomers count less) is the same R9-against-newcomers tension that E4 and E5 measure; capping each account's pull, as
R10 already does, is the robust-aggregation idea. For R6, Tournesol suggests going beyond per-suggestion reasons:
publish how the ranking works and let members see and adjust what it uses.

---

## (c) Koren, Bell & Volinsky (2009), "Matrix Factorization Techniques for Recommender Systems" (first pages)

Read: the first four pages (from the introduction to "Learning algorithms"), plus a glance at "Inputs with varying
confidence levels". Source: https://doi.org/10.1109/MC.2009.263.

- **Two strategies.** *Content filtering* describes users or items by attributes (Pandora's Music Genome Project
  scores songs on hundreds of traits). *Collaborative filtering* uses only past behaviour and needs no profiles. It is
  usually more accurate but has a *cold start* problem: it cannot handle new products or new users, where content
  filtering does better.
- **Two kinds of collaborative filtering.** *Neighbourhood methods* score an item by similar items the user already
  rated (item–item) or by similar users. *Latent factor models* explain behaviour with, say, 20 to 100 hidden factors
  learned from the data. The factors can be meaningful (comedy against drama) or "completely uninterpretable".
- **Matrix factorisation.** Each user and each item get a vector in the same hidden-factor space, and the predicted
  rating is their dot product. The Netflix Prize showed it beats classic nearest-neighbour methods, and it easily
  takes extra information: user and item biases, time, implicit feedback, confidence.
- **Why not plain SVD on ratings.** SVD is close to this, but conventional SVD is undefined when most of the matrix
  is missing. Filling the gaps is costly and can distort the data, so the authors fit only the known entries and add
  regularisation (a penalty on large vectors, its strength set by cross-validation) to avoid overfitting. They train it
  with stochastic gradient descent or alternating least squares.
- **Implicit feedback and gaming.** When people do not rate, the system can learn from behaviour (purchases,
  browsing). Such *implicit feedback* records whether an event happened, so its matrix is dense (every cell is a yes
  or a no). Later, under "Inputs with varying confidence levels", they note that "a system might face adversarial
  users that try to tilt the ratings of certain items" and suggest attaching confidence weights to observations.

**For our design (the AI taste model):** joins are implicit feedback, so taking a truncated SVD of the full 0/1
member × group matrix is defensible as a simple first model, but we should say so (and, if time allows, compare it
with the paper's regularised version). Cold start is why the "similar descriptions" method and the R4 re-ranker must
cover new groups. Uninterpretable factors are why R6 reasons come from "also joined" or a template, never from a
hidden factor. On join data the item-bias term mostly measures popularity, so the model can bring back the popularity
bias that R4 has to correct.
