"""Smoke tests for the tool registry — the contract every plugin depends on."""

import pytest

from tools.registry import Tool, ToolRegistry


async def _echo(text: str) -> dict:
    return {"echo": text}


def _tool(name: str = "demo.echo", *, dangerous: bool = False, category: str = "demo") -> Tool:
    return Tool(
        name=name,
        description="Echo the given text back. Used only in tests.",
        parameters={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
        handler=_echo,
        dangerous=dangerous,
        category=category,
    )


def test_register_and_lookup():
    registry = ToolRegistry()
    registry.register(_tool())

    assert registry.get("demo.echo") is not None
    assert registry.get("demo.echo").name == "demo.echo"
    assert any(t.name == "demo.echo" for t in registry.all())


def test_openai_schema_shape():
    registry = ToolRegistry()
    registry.register(_tool())

    schema = registry.openai_schema()
    assert isinstance(schema, list) and schema

    entry = next(s for s in schema if s["function"]["name"] == "demo.echo")
    assert entry["type"] == "function"
    fn = entry["function"]
    assert fn["description"]
    assert fn["parameters"]["type"] == "object"
    assert "text" in fn["parameters"]["properties"]


def test_categories_group_tools():
    registry = ToolRegistry()
    registry.register(_tool("demo.echo"))
    registry.register(_tool("other.echo", category="other"))

    categories = registry.categories()
    assert "demo" in categories
    assert "other" in categories


def test_dangerous_flag_is_preserved():
    registry = ToolRegistry()
    registry.register(_tool("demo.wipe", dangerous=True))

    assert registry.get("demo.wipe").dangerous is True
    assert registry.get("demo.wipe").name.startswith("demo.")


def test_tool_names_are_dotted_and_lowercase():
    registry = ToolRegistry()
    registry.register(_tool())

    for tool in registry.all():
        assert tool.name == tool.name.lower()
        assert "." in tool.name, f"{tool.name} should follow the area.verb convention"
        assert tool.description.strip(), f"{tool.name} needs a description for the model"
        assert tool.parameters.get("type") == "object"


@pytest.mark.asyncio
async def test_handler_is_awaitable():
    registry = ToolRegistry()
    registry.register(_tool())

    result = await registry.get("demo.echo").handler(text="homa")
    assert result == {"echo": "homa"}
