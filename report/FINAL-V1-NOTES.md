# Final report, version 2 (19 Nov 2026): notes

Files: `Final report - Word.docx` (main), `Final report - Word.pdf`, `Final report - LaTeX (Overleaf).zip`.
Source: `report/src/final-nov24.md`. The build commands are at the top of that file.

## Page and word count

- 16 pages in the PDF: the cover (p. 1), the AI-use declaration (p. 2), **the body (pp. 3–12, exactly 10 pages)**, the
  references (p. 13–14) and the appendices (pp. 15–16).
- The body is about 6,000 words, counting tables and captions.
- **Page 12 is full.** The conclusion ends on its last line. When you rewrite 4.3 or fill a placeholder in the body, cut as
  much as you add. Rebuild and check that "References" still starts page 13.

## What changed in version 2 (E7's weak spot)

- **A realistic friendship world is now E7's main world.** It was fixed before any test result was seen:
  - friends of friends become friends, more readily when they share a group or course (focal closure, Kossinets & Watts, 2006);
  - this runs until the average clustering reaches 0.15, conservative next to the 0.14 that Ugander et al. (2011, new
    reference, checked) report for Facebook users with 100 friends;
  - the target was first 0.20, but this generator levels off near 0.17, so it was lowered, also before any test result.
  - The first world (clustering 0.007) is kept as a sensitivity check.
- **The people weight was tuned on the practice quiz:** w = 0.05, so mutual friends come first and shared groups break ties.
  BOING's first version used w = 1, which found half as much in E7 (7.4% against 15.8%). **BOING now uses w = 0.05** (BOING
  commit 52622d5, `SHARED_W = 0.05` in recs.js; 33,261 rule checks, 0 violations; the port still passes 13 of 13). The report
  says so, and that the doubling was measured in E7 on synthetic data, not re-measured in BOING.
- **New headline numbers (main world):**
  - the design finds a hidden friend for 15.8% of tested members, against 12.9% for mutual friends only, 3.2% for shared
    groups only, 0.9% for the most connected and 0.8% at random;
  - for members with 0–1 friends (28 tested), the design finds 17.9%, mutual friends only 14.3% while leaving 43% of them
    with an empty list, and BOING's first version (w = 1) 7.1%;
  - 0 violations in 72,440 rule checks; 243 of 243 age cases correct; 18 of 18 planted faults caught;
  - Gini of exposure 0.40 (most connected 0.98); newcomers get 5.4% of slots against 15.2% of the people who may be
    suggested;
  - all the rules together cost 63% of the unconstrained score, mostly consent (0.090 NDCG@5), with the age bands at
    0.006;
  - minors find a friend 9.0% of the time under the bands, 2.5% under the binary line and 10.9% with no age rule; no one
    over 20 is shown a minor (109 slots with no rule).
- Table 6, Figure 3, 2.3, 3.1, 3.5, Table 7, 4.1, 4.2, 4.3, 4.4, the conclusion, model card B1 and Appendix C are updated.
- The minors' result now rests on more members (201 tested), so the v1 caveat ("3 vs 2 members") no longer applies.

## What changed in version 1

- **TA feedback.** Only what we built is reported. The posts feed and the coach's privacy audit are gone, apart from one
  sentence in 1 ("Approach and scope").
- **People suggestions (new).** They are designed in 2.3 and evaluated as **E7** in 3.5, Table 6 and Figure 3. The
  evaluation is notebook 12, with results in `results/e7_*`.
- **The owner's age bands** (19 Nov) are in R8, 2.3, 3.5, 3.6 and 4.2 ("belonging against safety"). They are compared with
  the old binary line and with no age rule.
- **BOING's McGill launch.**
  - Sign-up is by McGill email, with no crypto.
  - Most members are 17 or older.
  - McGill is now an indirect stakeholder.
  - The reasoning behind R9 is revisited in 4.1.
- **Implementation (3.6, Figure 4).**
  - The port passes 13 of 13 test cases (8,488 rows).
  - BOING's rule checker made 33,261 checks with 0 violations (with w = 0.05).
  - The screens come from the local test copy, with fake members only.
- **To fit 10 pages:** the interim's plan and progress material and the coach design were cut, the before/after,
  privacy and fake-account figures were dropped (their numbers are in the text and tables), and 4.3 was folded into 4.1.
- **New for the rubric:**
  - Table 3 now says "value → design choice, and why".
  - 2.4 covers the implications and the planned results, with hypotheses H1–H4 for E7.
  - Table 7 compares the objectives with what was planned and what we found.
  - 4.3 is a reflection subsection.
  - Appendix B has short model cards for both recommenders (Mitchell et al., 2019).
- The teammate's name, Sehajpreet Kaur, is now on the cover and in Appendix A.

## Placeholders you must fill in yourselves (18, highlighted in yellow)

1. **AI-use declaration (p. 2).**
   - Any later AI use, up to submission.
   - The model versions of earlier sessions.
   - Two or three of Claude's proposals you changed or rejected.
   - Whether you opened the DSA and Ofcom texts yourselves.
   - "What we checked or changed ourselves", task by task.
   - The **Reflection**, in your own words.
2. **4.3 Reflection.** Rewrite it in your own words, and add what you would do differently. It is drafted from the
   project's record, but it speaks for you.
3. **Appendix A.**
   - How you reviewed, ran and revised Claude's work.
   - Nine "who did what" names.
4. **Appendix D.** The repository link, or "submitted as a zip".

## Claims to confirm before submitting

- **The launch date.** 3.6 and the conclusion say the design "runs in BOING since the McGill launch on November 22,
  2026". This was written on Nov 19; if the launch moves, change these sentences.
- **BOING-side numbers** (from BOING's team on Nov 19, with the age bands):
  - 33,261 rule checks, 0 violations (with the age bands and w = 0.05);
  - ages known only by birth year treated as a range;
  - "classmates" means the same course room this term;
  - under-14s can't switch suggestions on.

  Check that they still hold at submission. The count to use is 33,261, from the run with the age bands and w = 0.05.
- **BOING's minimum age of 14** is a default the owner was asked to confirm (PROJECT.md). If it changes, edit
  assumption 3.
- **Ofcom's measure ICU F1 and DSA Article 28** were checked only through search excerpts and secondary sources (both
  sites block automated reading). Open both and check the wording. Details are in `report/references.md`, part 5.
- **Quebec ss. 4.1, 8.1, 9.1 and 14** were checked word for word against the official PDF (updated to Oct 15, 2026).
  "Section 14 favours a separate switch for being suggested" (4.1) is our reading of it, not the regulator's.
- **The interim's AI pre-amble.** The submitted interim said "we authored the core algorithms" and that Claude "strictly
  remained a supporting tool". The AI log shows Claude wrote most of the code and drafts, so this final declaration
  follows the log. Make your reflection consistent with both, and say plainly what changed.
- **E7 rests on our assumptions:**
  - ages, courses, 1,000 classmate friendships, 3,000 triangle-closing friendships (clustering 0.15), and 25% switching on;
  - ages drawn independently of who is friends with whom.

  Absolute relevance depends on the friendship model: in the first world every method is weak (about 2%).
- **The 0–1-friend slice is small:** 28 members, so 5 against 4 find a friend. The clearer point is that mutual friends
  alone leave 43% of these members with an empty list.
- **One argument in 4.2 is reasoning, not data:** "classmates already meet in class".
- **Figure 4** is cropped above a "What is used" line that still reads "keep adults and under-18s apart". If BOING's
  wording changes, retake the screenshot.

## Rebuilding

From `report/build`, use `py -3.14` (it has python-docx; the default `py` doesn't):

1. Run `md2docx.py`.
2. Run `docx2pdf.ps1`.
3. Run `md2tex.py`, then `check_tex.py`.

The exact commands are at the top of the source. Notebook 12 reruns in about 5 minutes; every step is seeded.
