"""Auto-discovers every plugin under plugins/ and builds the tool registry.

To add hundreds of new capabilities you never touch the core: drop a file in
plugins/ that defines `register(registry)` and it is wired in automatically.
"""
import importlib
import logging
import pkgutil

import plugins
from tools.registry import ToolRegistry

log = logging.getLogger("homa.plugins")


def load_plugins() -> ToolRegistry:
    registry = ToolRegistry()
    for mod in pkgutil.iter_modules(plugins.__path__):
        if mod.name.startswith("_"):
            continue
        try:
            module = importlib.import_module(f"plugins.{mod.name}")
        except Exception as exc:  # noqa: BLE001
            log.warning("Failed to import plugin %s: %s", mod.name, exc)
            continue
        register = getattr(module, "register", None)
        if callable(register):
            try:
                register(registry)
            except Exception as exc:  # noqa: BLE001
                log.warning("Plugin %s register() failed: %s", mod.name, exc)
    log.info("Loaded %d tools: %s", len(registry.all()), registry.categories())
    return registry
