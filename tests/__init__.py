"""Unit tests for the university record system.

Run from the repository root:

    python3 -m unittest -v      (macOS / Linux)
    py -m unittest -v           (Windows)

Importing this package puts ``src/`` (and this directory) on
``sys.path`` so the application modules and shared test helpers can
be imported directly, mirroring how the scripts are run.
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _path in (_HERE.parent / "src", _HERE):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
