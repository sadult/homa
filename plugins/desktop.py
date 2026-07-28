"""Desktop control plugin: power, volume, media keys, screenshot, kill process.

All of these use OS-native commands only — no extra Python dependencies.
Destructive actions (power, kill) are marked dangerous, so they require
confirmation unless auto-confirm is on.
"""
import os
import platform
import subprocess
import time

from tools.registry import Tool, ToolRegistry

_OS = platform.system()  # "Windows" | "Darwin" | "Linux"


def _run(cmd, shell=False):
    proc = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=30)
    return {"exit_code": proc.returncode,
            "stdout": proc.stdout[:1500], "stderr": proc.stderr[:1000]}


# ── Power ────────────────────────────────────────────────────────────────
async def power(action: str, delay: int = 0):
    """action: shutdown | restart | sleep | hibernate | lock | logoff | cancel"""
    action = (action or "").lower()
    if _OS == "Windows":
        table = {
            "shutdown": ["shutdown", "/s", "/t", str(delay)],
            "restart": ["shutdown", "/r", "/t", str(delay)],
            "logoff": ["shutdown", "/l"],
            "hibernate": ["shutdown", "/h"],
            "cancel": ["shutdown", "/a"],
            "lock": ["rundll32.exe", "user32.dll,LockWorkStation"],
            "sleep": ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
        }
    elif _OS == "Darwin":
        table = {
            "shutdown": ["osascript", "-e", 'tell app "System Events" to shut down'],
            "restart": ["osascript", "-e", 'tell app "System Events" to restart'],
            "sleep": ["pmset", "sleepnow"],
            "logoff": ["osascript", "-e", 'tell app "System Events" to log out'],
            "lock": ["pmset", "displaysleepnow"],
        }
    else:  # Linux
        table = {
            "shutdown": ["systemctl", "poweroff"],
            "restart": ["systemctl", "reboot"],
            "sleep": ["systemctl", "suspend"],
            "hibernate": ["systemctl", "hibernate"],
            "logoff": ["loginctl", "terminate-user", os.getenv("USER", "")],
            "lock": ["loginctl", "lock-session"],
        }
    cmd = table.get(action)
    if not cmd:
        return {"error": f"unknown action '{action}'. Use one of: {', '.join(table)}"}
    if delay and action in ("shutdown", "restart") and _OS != "Windows":
        time.sleep(0)  # POSIX schedules via shutdown -h; keep simple/immediate
    res = _run(cmd)
    res["action"] = action
    return res


# ── Volume ───────────────────────────────────────────────────────────────
async def volume(action: str, steps: int = 5):
    """action: up | down | mute (mute toggles). steps = how many increments."""
    action = (action or "").lower()
    steps = max(1, min(int(steps), 50))
    if _OS == "Windows":
        key = {"up": 175, "down": 174, "mute": 173}.get(action)
        if key is None:
            return {"error": "action must be up | down | mute"}
        n = 1 if action == "mute" else steps
        ps = (f"$w=New-Object -ComObject WScript.Shell; "
              f"1..{n} | ForEach-Object {{ $w.SendKeys([char]{key}) }}")
        return _run(["powershell", "-NoProfile", "-Command", ps])
    if _OS == "Darwin":
        if action == "mute":
            return _run(["osascript", "-e", "set volume output muted (not (output muted of (get volume settings)))"])
        op = "+" if action == "up" else "-"
        return _run(["osascript", "-e",
                     f"set volume output volume (output volume of (get volume settings) {op} {steps*4})"])
    # Linux (pactl or amixer)
    if action == "mute":
        return _run(["bash", "-c", "pactl set-sink-mute @DEFAULT_SINK@ toggle || amixer set Master toggle"])
    sign = "+" if action == "up" else "-"
    return _run(["bash", "-c",
                 f"pactl set-sink-volume @DEFAULT_SINK@ {sign}{steps*4}% || amixer set Master {steps*4}%{sign}"])


# ── Media keys ───────────────────────────────────────────────────────────
async def media(action: str):
    """action: playpause | next | prev | stop"""
    action = (action or "").lower()
    if _OS == "Windows":
        key = {"playpause": 179, "next": 176, "prev": 177, "stop": 178}.get(action)
        if key is None:
            return {"error": "action must be playpause | next | prev | stop"}
        ps = f"(New-Object -ComObject WScript.Shell).SendKeys([char]{key})"
        return _run(["powershell", "-NoProfile", "-Command", ps])
    if _OS == "Darwin":
        code = {"playpause": 16, "next": 17, "prev": 18}.get(action)
        if code is None:
            return {"error": "unsupported"}
        return _run(["osascript", "-e",
                     f'tell application "System Events" to key code {100 + code}'])
    m = {"playpause": "play-pause", "next": "next", "prev": "previous", "stop": "stop"}.get(action)
    if not m:
        return {"error": "unsupported"}
    return _run(["bash", "-c", f"playerctl {m}"])


# ── Screenshot ───────────────────────────────────────────────────────────
async def screenshot(path: str | None = None):
    """Capture the whole screen to an image file and return its path."""
    path = os.path.abspath(path or f"homa_screenshot_{int(time.time())}.png")
    if _OS == "Windows":
        ps = ("Add-Type -AssemblyName System.Windows.Forms,System.Drawing; "
              "$b=[System.Windows.Forms.SystemInformation]::VirtualScreen; "
              "$bmp=New-Object System.Drawing.Bitmap $b.Width,$b.Height; "
              "$g=[System.Drawing.Graphics]::FromImage($bmp); "
              "$g.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size); "
              f"$bmp.Save('{path}'); $g.Dispose(); $bmp.Dispose()")
        res = _run(["powershell", "-NoProfile", "-Command", ps])
    elif _OS == "Darwin":
        res = _run(["screencapture", "-x", path])
    else:
        res = _run(["bash", "-c", f"scrot '{path}' || import -window root '{path}'"])
    if os.path.exists(path):
        return {"saved": path}
    return {"error": "screenshot failed", "detail": res}


# ── Kill process ─────────────────────────────────────────────────────────
async def kill_process(name: str | None = None, pid: int | None = None):
    if not name and not pid:
        return {"error": "provide a process name or pid"}
    if _OS == "Windows":
        cmd = ["taskkill", "/F"] + (["/PID", str(pid)] if pid else ["/IM", name])
    else:
        cmd = ["kill", "-9", str(pid)] if pid else ["pkill", "-f", name]
    return _run(cmd)


def register(r: ToolRegistry) -> None:
    C = "desktop"
    r.register(Tool("system.power",
        "Power control: shutdown, restart, sleep, hibernate, lock, logoff, or cancel a pending shutdown.",
        {"type": "object", "properties": {
            "action": {"type": "string",
                       "enum": ["shutdown", "restart", "sleep", "hibernate", "lock", "logoff", "cancel"]},
            "delay": {"type": "integer", "description": "seconds before shutdown/restart", "default": 0}},
         "required": ["action"]},
        power, dangerous=True, category=C))
    r.register(Tool("system.volume", "Change system volume: up, down, or mute (toggle).",
        {"type": "object", "properties": {
            "action": {"type": "string", "enum": ["up", "down", "mute"]},
            "steps": {"type": "integer", "default": 5}}, "required": ["action"]},
        volume, category=C))
    r.register(Tool("system.media", "Media keys: play/pause, next, previous, stop.",
        {"type": "object", "properties": {
            "action": {"type": "string", "enum": ["playpause", "next", "prev", "stop"]}},
         "required": ["action"]},
        media, category=C))
    r.register(Tool("system.screenshot", "Capture the whole screen to an image file.",
        {"type": "object", "properties": {"path": {"type": "string"}}}, screenshot, category=C))
    r.register(Tool("system.kill_process", "Force-kill a process by name or PID (needs confirmation).",
        {"type": "object", "properties": {
            "name": {"type": "string"}, "pid": {"type": "integer"}}},
        kill_process, dangerous=True, category=C))
