# BOING — Ethical Recommender System

**McGill University | ECSE 557: Intro to Ethics of Intelligent Systems**  
Fall 2026 · Group 14 · November 24, 2026  
**Authors:** Amine Houari and Sehajpreet Kaur  
**Instructor:** Prof. Ajung Moon

## Overview

This design project develops and evaluates value-sensitive group and people recommenders for BOING, an existing, independent student social platform. The design translates ethical values into eleven rules (R1–R11), comprising seven hard rules and four tunable design choices. Experiments E1–E7 evaluate relevance, fair exposure, privacy, autonomy, transparency, resistance to fake accounts and safety.

The submission contains the course-specific implementation, synthetic data, experiments and validation artifacts, not the full BOING website. BOING is independent of McGill University. No real member data or production credentials are required to run these experiments.

## Repository structure

| Path | Contents |
| --- | --- |
| `notebooks/01–12` | Executed Jupyter notebooks: simulation, data splits, methods, experiments and final evaluation. |
| `notebooks/boingrec.py` | Shared Python implementation, evaluation functions and rule checkers. |
| `data/sim_v1/` | Synthetic community and group recommendation data splits. |
| `results/` | CSV and JSON results; `SUMMARY.md` indexes the group results and `final_config.json` records the final group design. E7 results are stored in the `e7_*` files. |
| `figures/` | Experimental plots, design diagrams and screenshots from a synthetic test environment. |
| `testcases/` | Thirteen group-recommender test cases, configurations and expected outputs. |
| `production/recs-core.js` | Standalone JavaScript port of the group recommender. |
| `production/port.js` | Node.js validation script comparing the port with the Python test cases. |
| `report/` | Report source, model card, references and build scripts. Some development notes and drafts are retained for traceability. |

The submitted final PDF and executed notebooks are authoritative over earlier drafts and notebook-builder scripts.

## Running the Python experiments

Use Python 3 (the archive includes Python 3.12 cache files) and a Jupyter environment. From the extracted archive's root directory, install the required libraries in a clean environment:

```sh
python -m pip install numpy pandas matplotlib scipy scikit-learn joblib jupyter ipykernel nbformat nbclient
```

Open the notebooks in Jupyter and execute them in numerical order from 01 through 12, each from a clean kernel and with its working directory set to `notebooks/`. Keep the repository directory structure intact. Alternatively, the included `notebooks/builders/run_nb.py` executes notebooks in place with UTF-8 output. From the root, pass notebook paths in numerical order; for example:

```sh
python notebooks/builders/run_nb.py notebooks/01_fake_community.ipynb notebooks/02_split.ipynb
```

Continue with notebooks 03–12 in order. Notebook 11 regenerates the final group test cases, so it should be run after notebook 10. Notebook 12 evaluates people recommendations (E7). The builder scripts are historical development artifacts and are not needed to reproduce the experiments.

Saved notebook outputs and CSV/JSON files are included for inspection without rerunning the experiments. Random seeds are fixed for the synthetic experiments; numerical results may vary slightly across library versions or numerical backends.

## Validating the JavaScript group recommender

Use Node.js 22 (the version used for the submission-package validation). No npm dependencies, database, network connection or live BOING account are needed. The two JavaScript files must be together in `production/`, and `testcases/` must be at the archive root.

From the root directory, run:

```sh
node production/port.js
```

The script uses the supplied synthetic cases and compares the recommended groups, ranking order, reason codes, scores (tolerance 1e-6) and reason text. Equivalent numerical ties in AI-model explanations are counted separately. Constraint-relaxation count discrepancies are reported as warnings rather than test failures.

Expected summary:

```text
13 passed, 0 failed; 8488 rows, 75 of them numerical ties (the group an AI-model reason names)
```

The 75 ties account for the difference between ranking/score agreement on all cases and exact reason-text agreement on 8,413 of 8,488 rows (99.1%). The JavaScript validator covers the group recommender, not the entire production website or the people recommender.

## Selected findings

- Group recommendation NDCG@5: 0.488 versus 0.131 for the popularity baseline.
- New or small groups receive 20.8% of recommendation slots.
- People recommendation hit rate: 15.8% versus 0.8% for random recommendations in the synthetic evaluation.
- The report describes the ethical trade-offs, limitations and scope of the privacy guarantee. The synthetic results are not evidence of real-world user satisfaction or proof of universal safety.

For the complete methodology, ethical rationale, limitations and AI-use declaration, consult the submitted final report.

Repository: https://github.com/Amine-UrMenToR/Boing_Recommendation_System
