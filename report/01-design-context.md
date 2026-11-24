# 1. Design Context (draft, about one page)

> Draft written with an AI assistant (Claude), logged in `../AI-USE-LOG.md`. Rewrite it in your own words before submitting.
> For the **interim report**: change "We evaluate" to "We will evaluate" and delete the bracket with the headline result.

Recommender systems shape what people see online, and most are optimised for engagement because clicks and time spent are easy to measure. Yet engagement is only a proxy for what people value (Kleinberg et al., 2022). Optimising for it has been linked to filter bubbles (Pariser, 2011), to popularity bias that hides new and niche content (Abdollahpouri et al., 2017), and to profiling that threatens privacy and autonomy (Milano et al., 2020). Platforms usually add a recommender once they are large and their incentives are set. A new platform can instead decide what its recommender is for before building it.

**BOING.** BOING (boingfrog.com) is a free social network, developed and run by one of the authors, where a member's identity is a character rather than a photograph. Members join groups around personal goals such as languages, coding or exam preparation, plan their week with an AI coach and play games. They sign in with a crypto wallet and a username, without an email address or real name, and the audience includes teenagers. BOING already enforces privacy and safety rules (private profiles, blocking, reports, human moderators), but it has no recommender. Its Discover page ranks groups by member count, so large groups keep growing while new ones stay invisible.

**What we design.** We design a recommender that suggests groups to join, with people and an optional personalised feed as extensions. Its objective and constraints come from its stakeholders' values rather than from engagement. It serves BOING's members, including newcomers and teenagers, and it also affects the groups it ranks and the members whose activity feeds it. [*Optional:* As a smaller second part, we design a privacy layer for BOING's AI coach.]

**Deployment assumptions.** Our design rests on six assumptions:

1. The network is small and young, so most members and groups have little history, and popularity bias would lock in early winners.
2. Sign-up is pseudonymous, so fake ("Sybil") accounts are cheap and could manipulate rankings.
3. Members' ages are unknown, so suggesting people must be conservative.
4. BOING's mission is reaching goals, not time on site, so success means a short list of useful suggestions, not clicks.
5. BOING is subject to Quebec's Law 25, which requires privacy-protective defaults and notice of profiling (Quebec, 2021).
6. No real-user data is used: we evaluate on a synthetic community and demonstrate the design on a local copy of BOING with fake members.

**Approach.** Following value sensitive design (Friedman & Hendry, 2019), we identify the stakeholders, their values and the tensions between them. We then use the Montréal Declaration (2018) to turn these values into thirteen testable design rules. Some are hard limits that are never traded: personalisation is opt-in, private data is never used, and money cannot buy visibility. Others are adjustable and tuned in experiments: fair exposure for new groups, diversity, resistance to fake accounts and differential privacy. We evaluate the design on a synthetic community of 2,000 users and 150 groups against BOING's current ranking, and measure what each value costs in accuracy. [*Final report only: the headline result.*] Section 2 presents the design, Section 3 the results, and Section 4 the trade-offs and limitations.

## References

- Abdollahpouri, H., Burke, R., & Mobasher, B. (2017). Controlling popularity bias in learning-to-rank recommendation. *Proc. RecSys '17*, 42–46.
- Friedman, B., & Hendry, D. G. (2019). *Value sensitive design: Shaping technology with moral imagination.* MIT Press.
- Kleinberg, J., Mullainathan, S., & Raghavan, M. (2022). The challenge of understanding what users want: Inconsistent preferences and engagement optimization. *Proc. EC '22.*
- Milano, S., Taddeo, M., & Floridi, L. (2020). Recommender systems and their ethical challenges. *AI & Society*, 35(4), 957–967.
- Montréal Declaration for a Responsible Development of Artificial Intelligence. (2018). Université de Montréal.
- Pariser, E. (2011). *The filter bubble: What the Internet is hiding from you.* Penguin Press.
- Quebec. (2021). *An Act to modernize legislative provisions as regards the protection of personal information* (S.Q. 2021, c. 25).

For section 2, next to the rules they support: Chaney et al. (2018, feedback loops), Calandrino et al. (2011, privacy risks of collaborative filtering), Douceur (2002, the Sybil attack), Dwork & Roth (2014, differential privacy) and the EU Digital Services Act (Regulation 2022/2065, Arts. 27 and 38).

**Before submitting:** check every reference, and confirm the Law 25 provisions (sections 8.1 and 9.1 of Quebec's private-sector privacy act) against the official text.
