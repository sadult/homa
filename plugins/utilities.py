"""Misc utility tools: clipboard, desktop notifications, datetime."""
import datetime as dt
import platform
import subprocess

from tools.registry import Tool, ToolRegistry


async def clipboard_get():
    try:
        import pyperclip
        return {"text": pyperclip.paste()}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"clipboard unavailable: {exc}"}


async def clipboard_set(text: str):
    try:
        import pyperclip
        pyperclip.copy(text)
        return {"copied": True}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"clipboard unavailable: {exc}"}


async def notify(title: str, message: str):
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["osascript", "-e",
                f'display notification "{message}" with title "{title}"'], check=False)
        elif system == "Linux":
            subprocess.run(["notify-send", title, message], check=False)
        elif system == "Windows":
            ps = (f'powershell -c "[reflection.assembly]::loadwithpartialname('
                  f"'System.Windows.Forms');"
                  f"[System.Windows.Forms.MessageBox]::Show('{message}','{title}')\"")
            subprocess.run(ps, shell=True, check=False)
        return {"notified": True}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


async def now(timezone: str = ""):
    return {"now": dt.datetime.now().isoformat(timespec="seconds"),
            "utc": dt.datetime.utcnow().isoformat(timespec="seconds")}


def register(r: ToolRegistry) -> None:
    C = "utility"
    r.register(Tool("clipboard.get", "Read the system clipboard.",
        {"type": "object", "properties": {}}, clipboard_get, category=C))
    r.register(Tool("clipboard.set", "Write text to the system clipboard.",
        {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}, clipboard_set, category=C))
    r.register(Tool("notify.desktop", "Show a desktop notification.",
        {"type": "object", "properties": {"title": {"type": "string"}, "message": {"type": "string"}},
         "required": ["title", "message"]}, notify, category=C))
    r.register(Tool("time.now", "Get the current local and UTC datetime.",
        {"type": "object", "properties": {"timezone": {"type": "string"}}}, now, category=C))
