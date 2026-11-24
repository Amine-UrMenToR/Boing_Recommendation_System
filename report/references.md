# References for the final report (checked, APA 7)

> Checked on 30 Oct 2026 by Claude (Anthropic) against the sources linked under each entry: the DOI registry's
> record (Crossref) for every DOI, the publisher's or authors' copy where the record and the paper disagree, and the
> official texts for the laws and the Montréal Declaration. Log this use in `../AI-USE-LOG.md`, and give the list one
> last look before submitting. **⚠** marks something to decide or a detail we could not verify.

What is here:

1. The 25 entries, in APA order: the 15 from the interim report (all kept) and 10 new ones. Each has its APA entry,
   what we cite it for, and how it was checked.
2. The law checks: the DSA articles and Quebec's sections 8.1 and 9.1, quoted from the official texts.
3. The Montréal Declaration numbers in Table 3, checked against the official English PDF.
4. Everything flagged, in one list.

Changes from the interim list: every entry now has its DOI (when one exists) and the full proceedings title, the
Montréal Declaration gets an author (Université de Montréal) and a link, and the Quebec law gets a link. No author,
year, title or page range of the interim list was wrong (two page ranges are discussed under flags 1 and 2).

---

## 1. The entries

**Abdollahpouri, Burke & Mobasher (2017)** *(interim)*
> Abdollahpouri, H., Burke, R., & Mobasher, B. (2017). Controlling popularity bias in learning-to-rank
> recommendation. In *Proceedings of the Eleventh ACM Conference on Recommender Systems* (pp. 42–46). Association for
> Computing Machinery. https://doi.org/10.1145/3109859.3109912

- Cited for: popularity bias, where a few items take most of the attention and new ones are rarely shown (Section 1).
- Checked: Crossref record https://api.crossref.org/works/10.1145/3109859.3109912 (authors, title, RecSys '17, pp. 42–46).

**Act respecting the protection of personal information in the private sector (Quebec)** *(new)*
> Act respecting the protection of personal information in the private sector, CQLR c P-39.1, ss. 8.1, 9.1
> (consolidated to October 15, 2026). https://www.legisquebec.gouv.qc.ca/en/document/cs/P-39.1

- Cited for: s. 8.1 (people must be told, before collection, when a technology that can identify, locate or profile
  them is used, and how to switch those functions on) and s. 9.1 (privacy settings at the highest level of
  confidentiality by default), behind R1 and assumption 5. Wording quoted in Part 2.
- Checked: LegisQuebec, English consolidated text, "up to date as of 15 October 2026", sections 8.1 and 9.1 read in
  full. Both sections were added by S.Q. 2021, c. 25 (ss. 107 and 108), that is, by Law 25.
- ⚠ APA 7 has no fixed format for Canadian statutes and says to follow the jurisdiction's legal style; this follows
  the usual Canadian (McGill Guide) pattern. In the text: "s. 8.1 of the private-sector act (Act respecting…)".

**An Act to modernize legislative provisions as regards the protection of personal information (Law 25)** *(interim)*
> An Act to modernize legislative provisions as regards the protection of personal information, S.Q. 2021, c. 25
> (assented to September 22, 2021). https://www.assnat.qc.ca/en/travaux-parlementaires/projets-loi/projet-loi-64-42-1.html

- Cited for: Law 25, the 2021 reform that added ss. 8.1 and 9.1 to the private-sector act (assumption 5, R1).
- Checked: National Assembly page for Bill 64 (title, assent on September 22, 2021, chapter 25 of the 2021 statutes,
  most provisions in force September 22, 2023).
- ⚠ The interim wrote this as "Quebec. (2021). An Act to modernize … (S.Q. 2021, c. 25)." That form is also fine
  and keeps the in-text "(Quebec, 2021)"; pick one form for both Quebec entries and use it everywhere.

**Carbonell & Goldstein (1998)** *(interim)*
> Carbonell, J., & Goldstein, J. (1998). The use of MMR, diversity-based reranking for reordering documents and
> producing summaries. In *Proceedings of the 21st Annual International ACM SIGIR Conference on Research and
> Development in Information Retrieval* (pp. 335–336). Association for Computing Machinery.
> https://doi.org/10.1145/290941.291025

- Cited for: the greedy re-ranker that trades relevance against similarity to what is already picked (R5).
- Checked: Crossref record https://api.crossref.org/works/10.1145/290941.291025 (SIGIR '98, pp. 335–336).

**Chaney, Stewart & Engelhardt (2018)** *(interim)*
> Chaney, A. J. B., Stewart, B. M., & Engelhardt, B. E. (2018). How algorithmic confounding in recommendation systems
> increases homogeneity and decreases utility. In *Proceedings of the 12th ACM Conference on Recommender Systems*
> (pp. 224–232). Association for Computing Machinery. https://doi.org/10.1145/3240323.3240370

- Cited for: feedback loops that make users' behaviour more alike (Section 1).
- Checked: Crossref record https://api.crossref.org/works/10.1145/3240323.3240370 (RecSys '18, pp. 224–232).

**Douceur (2002)** *(interim)*
> Douceur, J. R. (2002). The Sybil attack. In P. Druschel, F. Kaashoek, & A. Rowstron (Eds.), *Peer-to-peer
> systems: First International Workshop, IPTPS 2002* (Lecture Notes in Computer Science, Vol. 2429, pp. 251–260).
> Springer. https://doi.org/10.1007/3-540-45748-8_24

- Cited for: the Sybil attack, one attacker running many identities (assumption 2, R9).
- Checked: Crossref records for the chapter (https://api.crossref.org/works/10.1007/3-540-45748-8_24, pp. 251–260)
  and the book (https://api.crossref.org/works/10.1007/3-540-45748-8: editors, IPTPS 2002, LNCS 2429).

**Dwork & Roth (2014)** *(interim)*
> Dwork, C., & Roth, A. (2014). The algorithmic foundations of differential privacy. *Foundations and Trends in
> Theoretical Computer Science, 9*(3–4), 211–407. https://doi.org/10.1561/0400000042

- Cited for: differential privacy, the Laplace mechanism and capping each person's contribution (R10, E3).
- Checked: the monograph's own title page (https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf) reads
  "Vol. 9, Nos. 3–4 (2014) 211–407". ⚠ The Crossref record gives 211–487; we keep the paper's own 211–407 (flag 1).

**Dwork, Talwar, Thakurta & Zhang (2014)** *(new)*
> Dwork, C., Talwar, K., Thakurta, A., & Zhang, L. (2014). Analyze Gauss: Optimal bounds for privacy-preserving
> principal component analysis. In *Proceedings of the Forty-Sixth Annual ACM Symposium on Theory of Computing*
> (pp. 11–20). Association for Computing Machinery. https://doi.org/10.1145/2591796.2591883

- Cited for: a private version of our SVD taste model: add calibrated Gaussian noise to the AᵀA (co-membership)
  matrix, then take its top eigenvectors; the noise level is near-optimal (R10).
- Checked: Crossref record https://api.crossref.org/works/10.1145/2591796.2591883 (STOC '14, pp. 11–20); Microsoft
  Research abstract page (https://www.microsoft.com/en-us/research/?p=166811). The "add Gaussian noise to AᵀA" summary
  comes from later papers describing the method; read Section 1 before describing the algorithm in the report.

**Friedman & Hendry (2019)** *(interim)*
> Friedman, B., & Hendry, D. G. (2019). *Value sensitive design: Shaping technology with moral imagination*. MIT
> Press. https://doi.org/10.7551/mitpress/7585.001.0001

- Cited for: value sensitive design: direct and indirect stakeholders, values, value tensions (Sections 1, 2.1).
- Checked: Crossref record https://api.crossref.org/works/10.7551/mitpress/7585.001.0001 (MIT Press, 2019).

**Hoang et al. (2021), Tournesol** *(new)*
> Hoang, L.-N., Faucon, L., Jungo, A., Volodin, S., Papuc, D., Liossatos, O., Crulis, B., Tighanimine, M.,
> Constantin, I., Kucherenko, A., Maurer, A., Grimberg, F., Nitu, V., Vossen, C., Rouault, S., & El-Mhamdi, E.-M.
> (2021). *Tournesol: A quest for a large, secure and trustworthy database of reliable human judgments*
> (arXiv:2107.07334). arXiv. https://doi.org/10.48550/arXiv.2107.07334

- Cited for: a real recommender built on human judgements that resists fake accounts (verified accounts from trusted
  email domains, vouching) and manipulation ("one contributor, one unit force", median-like aggregation), and is
  transparent (open code, public data). Precedent for R9 and R6.
- Checked: arXiv record and PDF (https://arxiv.org/abs/2107.07334): 16 authors in this order, one version (v1,
  29 May 2021), 27 pages. APA 7 lists up to 20 authors, so all 16 are written out.
- ⚠ A preprint, not peer-reviewed; say so if it carries weight. The current algorithm is in a later preprint, now
  titled "Solidago: A modular collaborative scoring pipeline" (arXiv:2211.01179); add it only if we describe today's
  Tournesol.

**Järvelin & Kekäläinen (2002)** *(interim)*
> Järvelin, K., & Kekäläinen, J. (2002). Cumulated gain-based evaluation of IR techniques. *ACM Transactions on
> Information Systems, 20*(4), 422–446. https://doi.org/10.1145/582415.582418

- Cited for: NDCG, the ranking metric that gives more credit to correct items near the top (Section 3.1).
- Checked: Crossref record https://api.crossref.org/works/10.1145/582415.582418 (TOIS 20(4), 422–446).

**Kleinberg, Mullainathan & Raghavan (2022)** *(interim)*
> Kleinberg, J., Mullainathan, S., & Raghavan, M. (2022). The challenge of understanding what users want:
> Inconsistent preferences and engagement optimization. In *Proceedings of the 23rd ACM Conference on Economics and
> Computation* (p. 29). Association for Computing Machinery. https://doi.org/10.1145/3490486.3538365

- Cited for: engagement is only a proxy for what people value, and the two can diverge (Section 1).
- Checked: Crossref record https://api.crossref.org/works/10.1145/3490486.3538365 (EC '22, page 29 only: a one-page
  abstract). ⚠ The full paper is in *Management Science* (published online November 7, 2023,
  https://doi.org/10.1287/mnsc.2022.03683); we could not confirm its volume, issue and pages (flag 3).

**Koren, Bell & Volinsky (2009)** *(interim)*
> Koren, Y., Bell, R., & Volinsky, C. (2009). Matrix factorization techniques for recommender systems. *Computer,
> 42*(8), 30–37. https://doi.org/10.1109/MC.2009.263

- Cited for: matrix factorisation, our "hidden tastes" AI model, and why plain SVD needs care with missing data.
- Checked: Crossref record https://api.crossref.org/works/10.1109/MC.2009.263 (IEEE *Computer* 42(8), 30–37,
  August 2009). ⚠ The widely shared PDF shows printed page numbers 42–49 (flag 2).

**Lam & Riedl (2004)** *(new)*
> Lam, S. K., & Riedl, J. (2004). Shilling recommender systems for fun and profit. In *Proceedings of the 13th
> International Conference on World Wide Web* (pp. 393–402). Association for Computing Machinery.
> https://doi.org/10.1145/988672.988726

- Cited for: fake-profile ("shilling") attacks that push an item up; their lessons: item–item methods resist much
  better than user–user, measure attacks on the top-N list rather than prediction error, and new or obscure items are
  the easiest to push. This is our E4 attack model and supports "also joined" (item–item) as a method (R9).
- Checked: Crossref record https://api.crossref.org/works/10.1145/988672.988726 (WWW '04, pp. 393–402); full text
  on the conference archive (https://archives.iw3c2.org/www2004/proceedings/docs/1p393.pdf), conclusions read.

**McSherry & Mironov (2009)** *(new)*
> McSherry, F., & Mironov, I. (2009). Differentially private recommender systems: Building privacy into the Netflix
> Prize contenders. In *Proceedings of the 15th ACM SIGKDD International Conference on Knowledge Discovery and Data
> Mining* (pp. 627–636). Association for Computing Machinery. https://doi.org/10.1145/1557019.1557090

- Cited for: evidence that leading recommender methods can be made differentially private by adding noise to the
  shared statistics they learn from, "without significantly degrading" accuracy (R10, E3).
- Checked: Crossref record https://api.crossref.org/works/10.1145/1557019.1557090 (KDD '09, pp. 627–636, with the
  subtitle); abstract wording from the Microsoft Research page (https://microsoft.com/en-us/research/?p=157447).

**Milano, Taddeo & Floridi (2020)** *(interim)*
> Milano, S., Taddeo, M., & Floridi, L. (2020). Recommender systems and their ethical challenges. *AI & Society,
> 35*(4), 957–967. https://doi.org/10.1007/s00146-020-00950-y

- Cited for: the ethical challenges of recommenders, including privacy and autonomy (Section 1).
- Checked: Crossref record https://api.crossref.org/works/10.1007/s00146-020-00950-y (35(4), 957–967; online
  February 2020, issue December 2020).

**Mitchell et al. (2019)** *(new)*
> Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru,
> T. (2019). Model cards for model reporting. In *Proceedings of the Conference on Fairness, Accountability, and
> Transparency* (pp. 220–229). Association for Computing Machinery. https://doi.org/10.1145/3287560.3287596

- Cited for: the format of our model card appendix (intended use, data, metrics, results broken down by group, e.g.
  newcomers, ethical considerations, caveats).
- Checked: Crossref record https://api.crossref.org/works/10.1145/3287560.3287596 (FAT* '19, pp. 220–229, nine
  authors in this order).

**Pariser (2011)** *(interim)*
> Pariser, E. (2011). *The filter bubble: What the Internet is hiding from you*. Penguin Press.

- Cited for: filter bubbles that narrow what people encounter (Section 1).
- Checked: library catalogue records for ISBN 978-1-59420-300-8 (Penguin Press, New York, 2011), e.g. Open Library
  https://openlibrary.org/works/OL15747216W. A book: no DOI. The 2012 paperback has a different ISBN; cite the
  edition you read.

**Regulation (EU) 2022/2065, Digital Services Act** *(new)*
> Regulation (EU) 2022/2065 of the European Parliament and of the Council of 19 October 2022 on a Single Market For
> Digital Services and amending Directive 2000/31/EC (Digital Services Act). (2022). *Official Journal of the European
> Union*, L 277, 1–102. https://eur-lex.europa.eu/eli/reg/2022/2065/oj

- Cited for: Art. 27 (online platforms must explain the main parameters of their recommender systems and let users
  change them) and Art. 38 (very large platforms must offer at least one recommender option not based on profiling),
  as benchmarks for R6, R7 and R1. Wording quoted in Part 2.
- Checked: the official text from the EU Publications Office (CELEX 32022R2065, XHTML and PDF copies): OJ L 277,
  27.10.2022, pages L 277/1 to L 277/102. EUR-Lex itself blocked automated reading; the ELI link above is the
  official address. ("For" is capitalised in the official title.)
- ⚠ No fixed APA 7 format for EU law; this uses the Official Journal pattern. In the text: (Digital Services Act, 2022).

**Sarwar, Karypis, Konstan & Riedl (2001)** *(interim)*
> Sarwar, B., Karypis, G., Konstan, J., & Riedl, J. (2001). Item-based collaborative filtering recommendation
> algorithms. In *Proceedings of the 10th International Conference on World Wide Web* (pp. 285–295). Association for
> Computing Machinery. https://doi.org/10.1145/371920.372071

- Cited for: item-to-item collaborative filtering, our "also joined" method (Section 2.4).
- Checked: Crossref record https://api.crossref.org/works/10.1145/371920.372071 (WWW '01, pp. 285–295).

**Singh & Joachims (2018)** *(new)*
> Singh, A., & Joachims, T. (2018). Fairness of exposure in rankings. In *Proceedings of the 24th ACM SIGKDD
> International Conference on Knowledge Discovery & Data Mining* (pp. 2219–2228). Association for Computing
> Machinery. https://doi.org/10.1145/3219819.3220088

- Cited for: exposure as the resource a ranking hands out, position bias, and fairness constraints on exposure
  (parity, or proportional to relevance). The basis of R4 and E2.
- Checked: Crossref record https://api.crossref.org/works/10.1145/3219819.3220088 (KDD '18, pp. 2219–2228); full text
  read from arXiv 1802.07281.

**Tintarev & Masthoff (2007)** *(new)*
> Tintarev, N., & Masthoff, J. (2007). A survey of explanations in recommender systems. In *2007 IEEE 23rd
> International Conference on Data Engineering Workshop* (pp. 801–810). IEEE.
> https://doi.org/10.1109/ICDEW.2007.4401070

- Cited for: the seven aims an explanation can serve (transparency, scrutability, trust, effectiveness,
  persuasiveness, efficiency, satisfaction). R6 aims at transparency and scrutability, never at persuasion.
- Why this one: it is where the seven aims first appear, and it is short. Also checked, if you prefer a handbook
  chapter: Tintarev, N., & Masthoff, J. (2015). Explaining recommendations: Design and evaluation. In F. Ricci,
  L. Rokach, & B. Shapira (Eds.), *Recommender systems handbook* (2nd ed., pp. 353–382). Springer.
  https://doi.org/10.1007/978-1-4899-7637-6_10. (The 2011 first-edition chapter is pp. 479–510,
  https://doi.org/10.1007/978-0-387-85820-3_15.)
- Checked: Crossref records for all three. ⚠ The 2007 abstract speaks of "seven possible advantages"; the names of
  the seven aims are confirmed from the authors' later work and from papers citing it. Check the original's table
  before quoting a definition.

**Université de Montréal (2018), Montréal Declaration** *(interim)*
> Université de Montréal. (2018). *Montréal Declaration for a responsible development of artificial intelligence*.
> https://declarationmontreal-iaresponsable.com/wp-content/uploads/2023/04/UdeM_Decl-IA-Resp_LA-Declaration-ENG_WEB_09-07-19.pdf

- Cited for: the 10 principles our rules are traced to (Table 3), and the quote on p. 5 that the principles are not
  ranked but limit one another.
- Checked: the official English PDF, linked as "Download the Declaration" on
  https://montrealdeclaration-responsibleai.com/the-declaration/ ("An initiative of Université de Montréal").
  All 10 principles and the p. 5 quote read in full (Part 3).
- ⚠ The interim used the title as author. Naming the university as author is more standard APA 7, but the in-text
  citation then becomes (Université de Montréal, 2018). Pick one form and use it everywhere.

**van de Poel (2013)** *(interim)*
> van de Poel, I. (2013). Translating values into design requirements. In D. P. Michelfelder, N. McCarthy, &
> D. E. Goldberg (Eds.), *Philosophy and engineering: Reflections on practice, principles and process* (pp. 253–266).
> Springer. https://doi.org/10.1007/978-94-007-7762-0_20

- Cited for: the values hierarchy (values → norms → design requirements), Figure 1 and Section 2.2.
- Checked: Crossref records for the chapter (pp. 253–266) and the book
  (https://api.crossref.org/works/10.1007/978-94-007-7762-0: editors, Springer, 2013).

**Zehlike et al. (2017), FA\*IR** *(new)*
> Zehlike, M., Bonchi, F., Castillo, C., Hajian, S., Megahed, M., & Baeza-Yates, R. (2017). FA\*IR: A fair top-k
> ranking algorithm. In *Proceedings of the 2017 ACM on Conference on Information and Knowledge Management*
> (pp. 1569–1578). Association for Computing Machinery. https://doi.org/10.1145/3132847.3132938

- Cited for: a re-ranker that guarantees a minimum share of a protected group in *every prefix* of a top-k list,
  using a statistical test, with little loss of utility. An alternative way to enforce R4's floor q in a short list.
- Checked: Crossref record https://api.crossref.org/works/10.1145/3132847.3132938 (CIKM '17, pp. 1569–1578, six
  authors); abstract from arXiv 1706.06368.

---

## 2. The laws: what the articles and sections actually say

**Digital Services Act**, read in the official text (CELEX 32022R2065).

- **Art. 27, "Recommender system transparency": confirmed.** (1) Online platforms that use recommender systems "shall
  set out in their terms and conditions, in plain and intelligible language, the main parameters used in their
  recommender systems, as well as any options for the recipients of the service to modify or influence those main
  parameters." (2) The main parameters "shall explain why certain information is suggested", including at least the
  most significant criteria and the reasons for their relative importance. (3) Where there are several options, users
  must be able to select and change their preferred option at any time, "directly and easily accessible" from where
  the information is ranked.
- **Art. 38, "Recommender systems": confirmed.** Very large online platforms and search engines "shall provide at
  least one option for each of their recommender systems which is not based on profiling as defined in Article 4,
  point (4), of Regulation (EU) 2016/679" (the GDPR).
- **Definition, Art. 3(s):** a recommender system is "a fully or partially automated system used by an online platform
  to suggest in its online interface specific information to recipients of the service or prioritise that
  information…". BOING's group suggestions fit this definition.
- **⚠ Scope, worth one sentence in the report.** Art. 27 is in Chapter III, Section 3, which by Art. 19(1) does not
  apply to micro or small enterprises (unless designated very large). Art. 38 applies only to very large platforms
  (45 million or more average monthly active users in the EU, Art. 33(1)). BOING is neither, so we cite the DSA as a
  standard we follow voluntarily, not as a legal duty. Also relevant to BOING's teenagers: Art. 28, "Online
  protection of minors" (same Section 3).

**Quebec, Act respecting the protection of personal information in the private sector**, read on LegisQuebec
(English, consolidated to 15 October 2026).

- **s. 8.1: confirmed, with one detail to add.** "In addition to the information that must be provided in accordance
  with section 8, any person who collects personal information from the person concerned using technology that
  includes functions allowing the person concerned to be identified, located or profiled must first inform the person
  (1) of the use of such technology; and (2) of the means available to activate the functions that allow a person to
  be identified, located or profiled." It defines profiling as "the collection and use of personal information to
  assess certain characteristics of a natural person, in particular for the purpose of analyzing that person's work
  performance, economic situation, health, personal preferences, interests or behaviour." A taste model is
  therefore profiling.
- **s. 9.1: confirmed.** "Any person carrying on an enterprise who collects personal information when offering to the
  public a technological product or service having privacy settings must ensure that those settings provide the
  highest level of confidentiality by default, without any intervention by the person concerned." Its second
  paragraph excludes browser-cookie settings.
- **What to change in the interim text (Section 2.2):** its summary of both sections is accurate. Add that s. 8.1 also
  requires telling people *how to activate* the profiling functions; read with s. 9.1, that supports R1's "off until
  the member turns it on". We did not check the privacy regulator's (Commission d'accès à l'information) guidance on
  this reading, so word it as our reading, not as settled law.

---

## 3. The Montréal Declaration numbers in Table 3

Checked against the official English PDF (2018). The Declaration has 10 principles, each with numbered items; "3.4"
means Principle 3, item 4. **Three rules need a change (R7, R8, R9); the other eight can stay as they are.**

| Rule | Interim | Verdict | Use instead |
|---|---|---|---|
| R1 Opt-in | 3.4, 3.6 | Right. 3.4: no preference profiles to influence people "without their free and informed consent". 3.6: control over personal data; access to a service must not depend on giving it up. | Keep |
| R2 Allow-list | 3.1, 3.2, 8.4 | Right. 3.1: personal spaces protected from AI intrusion and data collection. 3.2: intimacy of thoughts and emotions (coach chats, planner). 8.4: prevent misuse of user data. | Keep |
| R3 No paying for reach | 6.2 | Right. 6.2: end domination "based on differences of power, wealth, or knowledge". | Keep |
| R4 Fair exposure | 6.2, 6.3, 7.1 | Acceptable. 6.2 and 6.3 (benefits for all, fewer inequalities) fit. 7.1 (no homogenisation of behaviour and opinions) is closer to R5. Avoid 7.6: it is about a varied market of AI services, not fairness among ranked items. | 6.2, 6.3 (7.1 optional) |
| R5 Diversity | 7.1, 7.4 | Right. 7.4 (no locking people into a profile or a "filtering bubble") is the strongest. | Keep |
| R6 Honest reasons | 5.2, 5.7, 5.8 | Right. 5.2: justified in understandable language, showing the most important factors. 5.7: we can check that the system does what it was programmed for (fidelity test). 5.8: people should know when an AI made a decision about them (the label). | Keep |
| R7 Members steer | 2.1, 3.6, 9.1 | **Change 9.1.** 9.1 says only humans are *responsible* for decisions that follow AI recommendations. "The system only suggests; the member decides" is 9.2: the final decision is taken by a human and is "free and informed" (9.2 is written for weighty decisions, so cite it as the spirit). Hide, reset and "see what is used" match 3.4 (control over information about one's preferences). | 2.1, 3.4, 3.6, 9.2 |
| R8 Safety filters | 1.5, 2.5, 8.3 | **Change 2.5.** 2.5 is about not spreading "untrustworthy information, lies, or propaganda": it covers only content hidden for misinformation, not blocked, suspended or private accounts. 4.1 (reduce people's "vulnerability and isolation", foster relationships) fits suggesting people only through shared groups and friends; 3.1 covers never suggesting private accounts. 1.5 and 8.3 are right. | 1.5, 3.1, 4.1, 8.3 |
| R9 Fake accounts | 8.1 | **Weak.** 8.1 asks for ways to limit harmful "double use" of AI research and development, which is not the same as attackers gaming a ranking. 8.3 (strict reliability, security and integrity requirements, tested before release: E4 is that test) fits better, and 6.2 covers the fairness side (no one gains power by creating accounts). | 8.3, 6.2 (8.1 optional) |
| R10 Differential privacy | 3.5, 8.4 | Right. 3.5: guarantee "data confidentiality and personal profile anonymity". | Keep |
| R11 Well-being | 1.5, 2.6, 3.3 | Right. 2.6 (no dependency through "attention-capturing techniques") and 3.3 (disconnection, "without encouraging people to stay connected") fit exactly. For "never inferred topics", 7.4 or 3.4 can be added. | Keep (+7.4 optional) |

Other points from the same check:

- **Call them principles and items, not "articles"** (Table 3's caption and the AI-use statement both say
  "articles"). Suggested caption wording: "Montréal numbers are principle.item of the Declaration (2018)."
- **The p. 5 quote is exact**: "As a general rule, the limits of one principle's application are defined by another
  principle's field of application." The same page says: "Although they are presented as a list, there is no
  hierarchy."
- **Principle 8 has two names** in the PDF: "Caution principle" in the table of contents, "Prudence principle" on its
  page (p. 15). If we name it, use one name throughout.

---

## 4. Flags in one list

1. **Dwork & Roth (2014) pages.** The paper's own title page says 211–407; the Crossref record says 211–487. We keep
   211–407, as in the interim.
2. **Koren et al. (2009) pages.** The DOI record and IEEE give *Computer* 42(8), 30–37. The commonly shared PDF has
   printed page numbers 42–49. Keep 30–37, and don't give a page number for a quote without checking IEEE Xplore.
3. **Kleinberg et al.** The EC '22 entry is a one-page abstract (p. 29). The full paper is in *Management Science*
   (online November 7, 2023, DOI 10.1287/mnsc.2022.03683), but we could not confirm its volume, issue and pages.
   Citing the journal version is better if those can be found on the journal's page.
4. **Montréal Declaration author.** Group author (Université de Montréal) or title first: decide, then make the
   in-text citations match.
5. **Legal entries.** APA 7 has no fixed format for EU or Quebec law. The entries follow each jurisdiction's usual
   style; ask the TA if the course wants another one. The Law 25 page on LegisQuebec refused a second automated visit,
   so its title, chapter and assent date were checked on the National Assembly's page instead.
6. **DSA scope.** Arts. 27 and 38 do not legally bind a platform of BOING's size (Part 2); present them as a benchmark.
7. **Tournesol.** The 2021 paper is a preprint (one version). tournesol.app's pages need JavaScript and could not be
   read by our tools; what we say about today's trust scores comes from the Solidago documentation
   (https://solidago.tournesol.app/modules/trust_propagation/).
8. **Tintarev & Masthoff.** Check the 2007 paper's own table before quoting a definition of an aim.
9. **Analyze Gauss.** The one-line description of the method comes from its abstract page and later papers; read its
   Section 1 before describing the algorithm in detail.
10. **Montréal numbers.** R7, R8 and R9 need the changes in Part 3, and "articles" should become "principles/items".

---

## 5. Added for the final report (19 Nov 2026)

Checked on 19 Nov 2026 by Claude (Anthropic). Log: `../AI-USE-LOG.md`.

- **Kossinets & Watts (2006)**, Science 311(5757), 88–90, https://doi.org/10.1126/science.1116869. Cited for: in real
  networks a friend of a friend is the likeliest new friend (triadic closure), which our simulator lacks (E7's
  sensitivity world). Checked: Crossref record (authors, title, volume, issue, pages, 2006).
- **Liben-Nowell & Kleinberg (2007)**, JASIST 58(7), 1019–1031, https://doi.org/10.1002/asi.20591. Cited for: hiding
  links and predicting them, our E7 protocol. Checked: Crossref record.
- **Su, Sharma & Goel (2016)**, WWW '16, pp. 1157–1167, https://doi.org/10.1145/2872427.2883040. Cited for: "who to
  follow" recommendations made well-connected users better connected (the rich-get-richer effect behind E7's newcomer
  finding). Checked: Crossref record (authors, title, proceedings, pages).
- **Quebec's act, ss. 4.1 and 14** (added to the existing entry). s. 4.1: "The personal information concerning a minor
  under 14 years of age may not be collected from him without the consent of the person having parental authority or of
  the tutor, unless collecting the information is clearly for the minor's benefit." (2021, c. 25). s. 14: consent "must
  be clear, free and informed and be given for specific purposes. It must be requested for each such purpose, in clear
  and simple language"; a minor 14 or over consents alone or through a parent or tutor. Checked: the official PDF from
  LégisQuébec, "updated to October 15, 2026", read in full for ss. 4.1, 8.1, 9.1 and 14 (8.1 and 9.1 unchanged).
- **DSA Article 28** (existing DSA entry). Cited for: platforms accessible to minors must ensure a high level of privacy,
  safety and security of minors (28(1)); Article 19 exempts micro and small enterprises from Section 3 (Articles 19–28)
  except Article 24(3), so it does not bind BOING. ⚠ Checked only through secondary sources (law-firm and regulator
  summaries; the EUR-Lex page returned nothing to automated reading). Open the official text before submitting.
- **Ofcom (2025)**, Illegal content Codes of Practice for user-to-user services (issued 24 Feb 2025, in force 17 Mar
  2025; statement of 16 Dec 2024), measure ICU F1 (default settings for child users: children are neither recommended in
  nor shown network-expansion prompts, where a service has them). ⚠ Checked only through search-engine excerpts of the
  official PDF (Ofcom's site refused automated reading, HTTP 403). Open the PDF, check ICU F1.2's wording and the
  measure number, and adjust the reference (title, date, URL) before submitting.
