import re

from config import settings

# Commands that are never allowed, even when the shell is enabled.
BLOCKED_PATTERNS = [
    r"\brm\s+-rf\b",
    r"\bmkfs\b",
    r"\bdd\s+if=",
    r":\(\)\s*\{",              # fork bomb
    r"\bformat\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r">\s*/dev/sd",
    r"\bdel\s+/s\b",
    r"\bdiskpart\b",
    r"Remove-Item.*-Recurse.*-Force",
]


class GuardResult:
    def __init__(self, allowed: bool, reason: str = ""):
        self.allowed = allowed
        self.reason = reason


def check_command(cmd: str) -> GuardResult:
    if not settings.ENABLE_SHELL:
        return GuardResult(False, "Shell execution disabled (ENABLE_SHELL=false).")
    for pat in BLOCKED_PATTERNS:
        if re.search(pat, cmd, re.IGNORECASE):
            return GuardResult(False, f"Blocked dangerous command: {pat}")
    return GuardResult(True)


def check_file_write() -> GuardResult:
    if not settings.ENABLE_FILE_WRITE:
        return GuardResult(False, "File writing disabled (ENABLE_FILE_WRITE=false).")
    return GuardResult(True)
