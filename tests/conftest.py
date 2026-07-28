"""Make the project root importable so tests can `import tools`, `plugins`, etc.

Without this, pytest only puts `tests/` on sys.path and every import fails with
ModuleNotFoundError in CI.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Tests must never touch a real config, a real database, or a real inbox.
os.environ.setdefault("DB_PATH", ":memory:")
os.environ.setdefault("WEB_AUTH_TOKEN", "test-token")
os.environ.setdefault("ENABLE_SHELL", "false")
os.environ.setdefault("ENABLE_FILE_WRITE", "false")
