# Notebook builders

The scripts that wrote notebooks 03 (T5 part) to 11 cell by cell, kept here so the work can be traced.
They were run from a temporary folder, so some paths inside point there. **The executed notebooks in `notebooks/`
are the source of truth**: re-run those (in order, from a clean kernel) rather than these scripts.

- `run_nb.py` runs a notebook from a clean kernel with UTF-8 output (plain `jupyter execute` garbles accents on Windows).
- `build_10.py` and `build_11.py` are the versions after the second review's fixes (1 Nov 2026).
