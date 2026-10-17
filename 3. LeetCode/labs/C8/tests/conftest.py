import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
for sub in ("C1", "C6", "_common"):
    sys.path.insert(0, str(LAB.parent / sub))
