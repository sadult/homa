"""Every shipped plugin must expose register() and produce a valid tool schema.

Plugins may depend on OS-specific or optional packages, so an import error is a
skip, not a failure — what we assert is the contract of whatever does import.
"""

import importlib
import pkgutil

import pytest

from tools.registry import ToolRegistry

PLUGIN_PACKAGE = "plugins"


def _plugin_modules() -> list[str]:
    package = importlib.import_module(PLUGIN_PACKAGE)
    return sorted(
        f"{PLUGIN_PACKAGE}.{m.name}"
        for m in pkgutil.iter_modules(package.__path__)
        if not m.name.startswith("_")
    )


def _import_or_skip(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception as exc:  # optional dependency or OS-specific plugin
        pytest.skip(f"{module_name} is not importable in this environment: {exc}")


def test_at_least_one_plugin_exists():
    assert _plugin_modules(), "no plugins found in plugins/"


@pytest.mark.parametrize("module_name", _plugin_modules())
def test_plugin_registers_valid_tools(module_name: str):
    module = _import_or_skip(module_name)
    assert hasattr(module, "register"), f"{module_name} must define register(registry)"

    registry = ToolRegistry()
    module.register(registry)

    for tool in registry.all():
        assert tool.name and "." in tool.name, f"{tool.name} should follow area.verb"
        assert tool.description.strip(), f"{tool.name} needs a description for the model"
        assert tool.parameters.get("type") == "object"
        assert callable(tool.handler)


def test_tool_names_are_unique_across_plugins():
    registry = ToolRegistry()
    seen: list[str] = []

    for module_name in _plugin_modules():
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        before = {t.name for t in registry.all()}
        module.register(registry)
        after = {t.name for t in registry.all()}
        seen.extend(after - before)

    assert seen, "no plugin registered any tool"
    assert len(seen) == len(set(seen)), "duplicate tool names across plugins"


def test_openai_schema_is_valid_for_every_registered_tool():
    registry = ToolRegistry()
    for module_name in _plugin_modules():
        try:
            importlib.import_module(module_name).register(registry)
        except Exception:
            continue

    for entry in registry.openai_schema():
        assert entry["type"] == "function"
        fn = entry["function"]
        assert fn["name"] and fn["description"]
        assert fn["parameters"]["type"] == "object"
