"""Macht den Projektordner importierbar (src.*), egal von wo pytest laeuft."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
