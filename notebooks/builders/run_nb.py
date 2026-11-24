"""Execute notebooks in place, reading and writing them as UTF-8.

(`jupyter execute` from nbclient 0.11 opens the file with Windows' default cp1252 encoding and garbles
every non-ASCII character, so we call nbclient directly.)
Usage: python run_nb.py notebooks/03_baseline.ipynb notebooks/04_methods.ipynb
"""
import sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient

for name in sys.argv[1:]:
    path = Path(name).resolve()
    nb = nbformat.read(path, as_version=4)                 # nbformat opens paths as UTF-8
    NotebookClient(nb, timeout=900, kernel_name='python3', resources={'metadata': {'path': str(path.parent)}}).execute()
    nbformat.write(nb, path)
    print('executed', path.name)
