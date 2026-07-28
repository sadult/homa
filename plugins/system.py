"""System automation plugin: disk, files listing, processes, open apps, shell."""
import os
import platform
import shutil
import subprocess
import webbrowser

from security.guard import check_command
from tools.registry import Tool, ToolRegistry


def _gb(b: int) -> float:
    return round(b / (1024 ** 3), 2)


async def disk_usage(path: str | None = None):
    if path is None:
        path = "C:\\" if platform.system() == "Windows" else "/"
    total, used, free = shutil.disk_usage(path)
    return {"path": path, "total_gb": _gb(total), "used_gb": _gb(used),
            "free_gb": _gb(free), "percent_used": round(used / total * 100, 1)}


async def list_dir(path: str = "."):
    entries = []
    for name in sorted(os.listdir(path)):
        full = os.path.join(path, name)
        entries.append({"name": name, "is_dir": os.path.isdir(full),
                        "size": os.path.getsize(full) if os.path.isfile(full) else None})
    return {"path": os.path.abspath(path), "entries": entries[:300]}


async def system_info():
    return {"os": platform.system(), "release": platform.release(),
            "machine": platform.machine(), "python": platform.python_version(),
            "cpu_count": os.cpu_count()}


async def list_processes(limit: int = 20):
    system = platform.system()
    cmd = "tasklist" if system == "Windows" else "ps -eo pid,comm,%cpu,%mem --sort=-%cpu"
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    lines = proc.stdout.splitlines()[: limit + 1]
    return {"processes": lines}


async def open_path(target: str):
    """Open a file, folder, app, or URL with the OS default handler."""
    if target.startswith(("http://", "https://")):
        webbrowser.open(target)
        return {"opened": target}
    system = platform.system()
    if system == "Windows":
        os.startfile(target)  # type: ignore[attr-defined]
    elif system == "Darwin":
        subprocess.run(["open", target], check=False)
    else:
        subprocess.run(["xdg-open", target], check=False)
    return {"opened": target}


async def run_command(command: str):
    guard = check_command(command)
    if not guard.allowed:
        return {"error": guard.reason}
    try:
        proc = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return {"error": "timeout (60s)"}
    return {"exit_code": proc.returncode, "stdout": proc.stdout[:4000],
            "stderr": proc.stderr[:2000]}


def register(r: ToolRegistry) -> None:
    C = "system"
    r.register(Tool("system.disk_usage", "Free/used space of a drive or path (e.g. C).",
        {"type": "object", "properties": {"path": {"type": "string"}}}, disk_usage, category=C))
    r.register(Tool("system.list_dir", "List files and folders in a path.",
        {"type": "object", "properties": {"path": {"type": "string", "default": "."}}}, list_dir, category=C))
    r.register(Tool("system.info", "OS, machine, CPU and Python info.",
        {"type": "object", "properties": {}}, system_info, category=C))
    r.register(Tool("system.processes", "List running processes (top by CPU).",
        {"type": "object", "properties": {"limit": {"type": "integer", "default": 20}}}, list_processes, category=C))
    r.register(Tool("system.open", "Open a file, folder, application, or URL with the OS default.",
        {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}, open_path, category=C))
    r.register(Tool("system.run_command", "Run a shell command (needs confirmation + ENABLE_SHELL).",
        {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
        run_command, dangerous=True, category=C))
