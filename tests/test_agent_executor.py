from typing import Any

import pytest

from lexmachina_agent.agent_executor import (
    LexMachinaAPIAgent,
)


class DummyEventQueue:
    def __init__(self) -> None:
        self.events: list[Any] = []

    async def enqueue_event(self, event: Any) -> None:
        self.events.append(event)


class DummyRequestContext:
    def __init__(self, query: str) -> None:
        self.task_id = "task123"
        self.context_id = "ctx456"
        self.message = {"role": "user", "content": query}

    def get_user_input(self) -> str:
        return self.message["content"]


@pytest.mark.asyncio
async def test_process_query_success(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = LexMachinaAPIAgent("https://example.com", "tok")

    async def fake_get_suggested(query: str) -> dict[str, Any]:
        return {
            "result": [
                {"description_url": "/desc/1"},
                {"description_url": "/desc/2"},
            ]
        }

    async def fake_get_desc(url: str) -> dict[str, Any]:
        return {"url": url, "text": f"Description for {url}"}

    monkeypatch.setattr(agent, "get_suggested_searches", fake_get_suggested)
    monkeypatch.setattr(agent, "get_search_description", fake_get_desc)
    data = await agent.process_query("abc")
    assert "result" in data
    assert all("enriched_description" in s for s in data["result"])
    await agent._client.aclose()


@pytest.mark.asyncio
async def test_process_query_error_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = LexMachinaAPIAgent("https://example.com", "tok")

    async def fake_get_suggested(query: str) -> dict[str, Any]:
        return {"result": []}  # triggers error path

    monkeypatch.setattr(agent, "get_suggested_searches", fake_get_suggested)
    data = await agent.process_query("abc")
    assert data["error"] == "Failed to get initial suggestions."
    await agent._client.aclose()
