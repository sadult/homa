import logging
import sys
import time


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


class StatusReporter:
    """Collects human-readable step logs to stream/send back to the user."""

    def __init__(self, on_log=None):
        self.steps: list[dict] = []
        self.t0 = time.time()
        self.on_log = on_log  # callback(entry) for live streaming

    def log(self, message: str, level: str = "info") -> dict:
        entry = {"t": round(time.time() - self.t0, 2), "level": level, "msg": message}
        self.steps.append(entry)
        logging.getLogger("homa").info(message)
        if self.on_log:
            try:
                self.on_log(entry)
            except Exception:  # noqa: BLE001
                pass
        return entry

    def summary(self) -> str:
        dur = round(time.time() - self.t0, 1)
        lines = [f"⏱ total: {dur}s", ""]
        for s in self.steps:
            icon = {"info": "•", "error": "⚠️", "ok": "✅"}.get(s["level"], "•")
            lines.append(f"{icon} [{s['t']}s] {s['msg']}")
        return "\n".join(lines)
