"""Local file plugin: search, read, and (guarded) write text files."""
import fnmatch
import os

from security.guard import check_file_write
from tools.registry import Tool, ToolRegistry


async def search_files(root: str, pattern: str = "*", limit: int = 100):
    matches = []
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                matches.append(os.path.join(dirpath, name))
                if len(matches) >= limit:
                    return {"root": root, "pattern": pattern, "matches": matches}
    return {"root": root, "pattern": pattern, "matches": matches}


async def read_file(path: str, max_chars: int = 6000):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read(max_chars)
    return {"path": os.path.abspath(path), "content": content}


async def write_file(path: str, content: str, append: bool = False):
    guard = check_file_write()
    if not guard.allowed:
        return {"error": guard.reason}
    mode = "a" if append else "w"
    with open(path, mode, encoding="utf-8") as f:
        f.write(content)
    return {"saved": os.path.abspath(path), "bytes": len(content)}


def register(r: ToolRegistry) -> None:
    C = "files"
    r.register(Tool("files.search", "Search files under a folder by glob pattern.",
        {"type": "object", "properties": {"root": {"type": "string"},
         "pattern": {"type": "string", "default": "*"}, "limit": {"type": "integer", "default": 100}},
         "required": ["root"]}, search_files, category=C))
    r.register(Tool("files.read", "Read a text file.",
        {"type": "object", "properties": {"path": {"type": "string"},
         "max_chars": {"type": "integer", "default": 6000}}, "required": ["path"]}, read_file, category=C))
    r.register(Tool("files.write", "Write/append a text file (needs confirmation + ENABLE_FILE_WRITE).",
        {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"},
         "append": {"type": "boolean", "default": False}}, "required": ["path", "content"]},
        write_file, dangerous=True, category=C))
