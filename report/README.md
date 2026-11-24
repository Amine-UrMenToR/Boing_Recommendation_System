# The report

The course's structure for a design project, with a maximum of 10 pages: **1 Design Context → 2 Design → 3 Results → 4 Discussion → 5 Conclusion.**
Ask the TA whether the references and the AI-use preamble count toward the 10 pages. If they do, take the space from Results.

## Sections, pages and who writes what

| Section | Pages | Who | In the interim report (Nov 3)? |
|---|---|---|---|
| Title, names, Group 14, and the **AI-use preamble** (from `../AI-USE-LOG.md`) | short | Both | Yes |
| **1. Design Context**: why it matters, BOING, what we design and for whom, deployment assumptions, approach | 1 | You | Yes: draft in `01-design-context.md` |
| **2. Design** | 3.5 | | |
| 2.1 Stakeholders and values, and the value tensions | | You | Yes |
| 2.2 From values to rules: values hierarchy, rules table R1–R13, short Montréal check | | Teammate | Yes |
| 2.3 The system: pipeline diagram; data used and never used | | You | Yes |
| 2.4 The algorithms: popularity, "also joined", similar descriptions, hidden tastes, re-ranking, privacy noise, explanations | | Teammate | First version |
| 2.5 The coach's privacy layer (only if kept) | | You | Design only |
| **3. Results** | 3.5 | | |
| 3.1 Evaluation setup: the fake community, the test set (T3), the metrics | | Teammate | Yes, with the first numbers |
| 3.2–3.7 Experiments E1–E6 | | Teammate | Only the first E1 table |
| 3.8 The prototype in BOING: "before" and "after" screens side by side | | You | A sketch |
| **4. Discussion**: the dial settings chosen and why, what it means for each stakeholder, limitations | 1.5 | Both | No: a "Plan to Nov 24" instead |
| **5. Conclusion** | 0.5 | Both | No |
| References and appendices (who did what, full Montréal table, simulator details, model card, code link) | not counted? | Both | References |

The interim report is about 5 pages: preamble, section 1, section 2, section 3.1 with the first numbers, and the plan to Nov 24.

## Figures (the ones we already have, and the ones to make)

| Figure | Section | Status |
|---|---|---|
| Group sizes in the fake community | 3.1 | ✓ `../figures/group_sizes.png` |
| Values hierarchy (values → norms → rules) | 2.2 | to redraw (start from part 3) |
| The pipeline (nightly job and `/recs/groups`) | 2.3 | to redraw (start from part 4) |
| Comparison table and fairness–accuracy curve (E1, E2) | 3.2, 3.3 | after T7 and E2 |
| "Before" and "after" Groups screens, from the test copy | 3.8 | after the BOING prototype |

## Tips

- Use tables instead of paragraphs for the stakeholders and the rules: they save space.
- Every figure gets a caption and is referenced in the text.
- Rewrite every AI-drafted part in your own words, and log it in `../AI-USE-LOG.md`.
- Check every reference, article number and law against its source before submitting.
