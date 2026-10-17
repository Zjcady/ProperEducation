import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))


def pytest_configure(config):
    # starlette's TestClient trips an anyio deprecation on import; not yours to fix.
    config.addinivalue_line("filterwarnings", "ignore:The anyio.abc.BlockingPortal alias:DeprecationWarning")
