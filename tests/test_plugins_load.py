"""Every shipped plugin must expose register() and produce a valid tool schema."""

import importlib
import pkgutil

import pytest

from tools.registry import ToolRegistry

PLUGIN_PACKAGE = "plugins"


def _plugin_modules() -> list[str]:
    package = importlib.import_module(PLUGIN_PACKAGE)
    return [
        f"{PLUGIN_PACKAGE}.{m.name}"
        for m in pkgutil.iter_modules(package.__path__)
        if not m.name.startswith("_")
    ]


def test_at_least_one_plugin_exists():
    assert _plugin_modules(), "no plugins found in plugins/"


@pytest.mark.parametrize("module_name", _plugin_modules())
def test_plugin_registers_valid_tools(module_name: str):
    module = importlib.import_module(module_name)
    assert hasattr(module, "register"), f"{module_name} must define register(registry)"

    registry = ToolRegistry()
    module.register(registry)

    for tool in registry.all():
        assert tool.name and "." in tool.name
        assert tool.description.strip()
        assert tool.parameters.get("type") == "object"
        assert callable(tool.handler)


def test_all_plugins_together_have_unique_names():
    registry = ToolRegistry()
    for module_name in _plugin_modules():
        importlib.import_module(module_name).register(registry)

    names = [t.name for t in registry.all()]
    assert len(names) == len(set(names)), "duplicate tool names across plugins"
