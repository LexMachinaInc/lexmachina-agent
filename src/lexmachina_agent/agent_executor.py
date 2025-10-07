import asyncio
import os
import typing

import httpx
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    InvalidParamsError,
    Part,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    completed_task,
    new_artifact,
)
from a2a.utils.errors import ServerError


class LexMachinaAPIAgent:
    """
    A stateful agent that manages communication with the external Lex Machina API.
    It holds the HTTP client and authentication token.
    """

    def __init__(self, api_base_url: str, token: str):
        self._api_base_url = api_base_url
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        self._client = httpx.AsyncClient(base_url=self._api_base_url, headers=self._headers)
        print("LexMachinaAPIAgent initialized.")

    async def get_suggested_searches(self, query: str) -> dict:
        """Calls the /search/ai_suggested endpoint."""
        try:
            print(f"Fetching suggested searches for: '{query}'")
            response = await self._client.get("/search/ai_suggested", params={"q": query})
            response.raise_for_status()
            return typing.cast(dict, response.json())
        except httpx.HTTPStatusError as e:
            print(f"API Error: {e}")
            return {"error": str(e)}

    async def get_search_description(self, description_url: str) -> dict:
        """Fetches the description for a single suggested search."""
        try:
            print(f"Fetching description from: {description_url}")
            response = await self._client.get(description_url)
            response.raise_for_status()
            return typing.cast(dict, response.json())
        except httpx.HTTPStatusError as e:
            print(f"API Error fetching description: {e}")
            return {"error": str(e)}

    async def process_query(self, query: str) -> dict:
        """
        Main method to process a query, fetch suggestions, and enrich them in parallel.
        """
        print(f"\n--- Processing query: '{query}' ---")

        # 1. Get initial suggestions from the API agent
        suggestions_response = await self.get_suggested_searches(query)

        if "error" in suggestions_response or not suggestions_response.get("result"):
            return {
                "error": "Failed to get initial suggestions.",
                "details": suggestions_response,
            }

        # 2. Prepare for parallel enrichment
        suggestions = suggestions_response["result"]
        enrichment_tasks = []
        for suggestion in suggestions:
            # For each suggestion, create a remote call to fetch its description
            task = self.get_search_description(suggestion["description_url"])
            enrichment_tasks.append(task)

        print(f"Fetching {len(enrichment_tasks)} descriptions in parallel...")

        # 3. Execute all enrichment tasks concurrently and gather results
        descriptions = await asyncio.gather(*enrichment_tasks)

        # 4. Combine the original suggestions with their fetched descriptions
        for suggestion, description_data in zip(suggestions, descriptions):
            suggestion["enriched_description"] = description_data

        print("--- Query processing complete ---")
        return suggestions_response


class LexmachinaAgentExecutor(AgentExecutor):
    def __init__(self) -> None:
        token = os.environ["API_TOKEN"]
        self.api = LexMachinaAPIAgent(
            api_base_url="https://law-api-poc.stage.lexmachina.com/api/v1/",
            token=token,
        )

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        if context.task_id is None or context.context_id is None or context.message is None:
            raise ServerError(error=InvalidParamsError(message="Missing task_id or context_id or message"))
        query = context.get_user_input()

        results = await self.api.process_query(query)
        parts = [Part(root=TextPart(text=str(results)))]
        await event_queue.enqueue_event(
            completed_task(
                context.task_id,
                context.context_id,
                [new_artifact(parts, f"suggestion_{context.task_id}")],
                [context.message],
            )
        )

    async def cancel(self, request: RequestContext, event_queue: EventQueue) -> None:
        raise ServerError(error=UnsupportedOperationError())
