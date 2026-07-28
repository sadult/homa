"""Long-term memory tools exposed to the agent."""
from core import memory
from tools.registry import Tool, ToolRegistry


async def remember(key: str, value: str):
    memory.remember(key, value)
    return {"remembered": key}


async def recall(key: str):
    return {"key": key, "value": memory.recall(key)}


async def search_memory(query: str):
    return {"results": memory.search_facts(query)}


async def list_memory():
    return {"facts": memory.list_facts()}


async def forget(key: str):
    return {"forgotten": memory.forget(key)}


def register(r: ToolRegistry) -> None:
    C = "memory"
    r.register(Tool("memory.remember", "Store a durable fact/preference under a key.",
        {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}},
         "required": ["key", "value"]}, remember, category=C))
    r.register(Tool("memory.recall", "Recall a stored fact by key.",
        {"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]}, recall, category=C))
    r.register(Tool("memory.search", "Search stored facts by text.",
        {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}, search_memory, category=C))
    r.register(Tool("memory.list", "List all stored facts.",
        {"type": "object", "properties": {}}, list_memory, category=C))
    r.register(Tool("memory.forget", "Delete a stored fact by key.",
        {"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]}, forget, category=C))
