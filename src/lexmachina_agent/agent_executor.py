# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
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

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Base class for configuration-related errors."""

    def __init__(self) -> None:
        self.args = ("Invalid configuration",)


class RequiredConfigurationError(ConfigurationError):
    """Raised when a required configuration field is missing."""

    def __init__(self, field_name: str) -> None:
        self.args = (f"Missing required configuration value: {field_name}",)


class MissingConfigurationError(ConfigurationError):
    """Raised when all configuration fields are missing."""

    def __init__(self, missing_fields: list[str]) -> None:
        self.args = (f"Missing configuration values: {', '.join(missing_fields)}",)


class APIAgentConfiguration:
    """Configuration for the Lex Machina API Agent.
    It supports authentication via API token, OAuth2 client credentials, or delegation URL."""

    def __init__(self) -> None:
        # Load configuration from environment variables
        api_base_url = os.environ.get("API_BASE_URL", "https://law-api-poc.stage.lexmachina.com")
        token = os.environ.get("API_TOKEN")
        client_id = os.environ.get("CLIENT_ID")
        client_secret = os.environ.get("CLIENT_SECRET")
        delegation_url = os.environ.get("DELEGATION_URL")

        if all(v is None for v in [token, client_id, client_secret, delegation_url]):
            raise MissingConfigurationError(["API_TOKEN", "CLIENT_ID", "CLIENT_SECRET", "DELEGATION_URL"])

        if token:
            logger.warning(
                "Using API_TOKEN for authentication. Consider using CLIENT_ID / CLIENT_SECRET, or DELEGATION_URL for better security."
            )
        if client_id is not None and client_secret is None:
            raise RequiredConfigurationError("CLIENT_SECRET")
        if client_secret is not None and client_id is None:
            raise RequiredConfigurationError("CLIENT_ID")

        self.api_base_url = api_base_url
        self.token = token
        self.client_id = client_id
        self.client_secret = client_secret
        self.delegation_url = delegation_url

    @property
    def is_using_delegation(self) -> bool:
        return self.delegation_url is not None

    def build_agent(self) -> "LexMachinaAPIAgent":
        """Constructs and returns a LexMachinaAPIAgent instance based on the configuration."""
        if self.token:
            return LexMachinaAPIAgent(
                api_base_url=self.api_base_url,
                token=self.token,
            )
        elif self.client_id and self.client_secret:
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            token_url = f"{self.api_base_url}/api/token"
            try:
                resp = httpx.post(token_url, data=data, headers={"Accept": "application/json"})
                resp.raise_for_status()
                access_token = resp.json().get("access_token")
                if not access_token:
                    logger.error("Token endpoint did not return access_token.")
                    raise ConfigurationError()
                return LexMachinaAPIAgent(
                    api_base_url=self.api_base_url,
                    token=typing.cast(str, access_token),
                )
            except httpx.HTTPError:
                logger.exception("OAuth2 token request failed.")
                raise
        elif self.delegation_url:
            # Implement delegation URL based authentication
            raise NotImplementedError("Delegation URL authentication not implemented yet.")
        else:
            raise ConfigurationError()  # This should not happen


class LexMachinaAPIAgent:
    """
    A stateful agent that manages communication with the external Protégé in Lex Machina Agent API.
    It holds the HTTP client and authentication token.
    """

    def __init__(self, api_base_url: str, token: str):
        self._api_base_url = api_base_url
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        self._client = httpx.AsyncClient(base_url=self._api_base_url, headers=self._headers)
        logger.info("LexMachinaAPIAgent initialized.")

    async def get_suggested_searches(self, query: str) -> dict:
        """Calls the /search/ai_suggested endpoint."""
        try:
            logger.info(f"Fetching suggested searches for: '{query}'")
            response = await self._client.get("/search/ai_suggested", params={"q": query})
            response.raise_for_status()
            return typing.cast(dict, response.json())
        except httpx.HTTPStatusError as e:
            logger.exception("API Error")
            return {"error": str(e)}

    async def get_search_description(self, description_url: str) -> dict:
        """Fetches the description for a single suggested search."""
        try:
            logger.debug(f"Fetching description from: {description_url}")
            response = await self._client.get(description_url)
            response.raise_for_status()
            return typing.cast(dict, response.json())
        except httpx.HTTPStatusError as e:
            logger.exception("API Error")
            return {"error": str(e)}

    async def process_query(self, query: str) -> dict:
        """
        Main method to process a query, fetch suggestions, and enrich them in parallel.
        """
        # 1. Get initial suggestions from the API agent
        suggestions_response = await self.get_suggested_searches(query)

        if "error" in suggestions_response or not suggestions_response.get("result"):
            logger.error("Failed to get initial suggestions.")
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

        logger.debug(f"Fetching {len(enrichment_tasks)} descriptions in parallel...")

        # 3. Execute all enrichment tasks concurrently and gather results
        descriptions = await asyncio.gather(*enrichment_tasks)

        # 4. Combine the original suggestions with their fetched descriptions
        for suggestion, description_data in zip(suggestions, descriptions):
            suggestion["enriched_description"] = description_data

        logger.debug("Query processing complete")
        return suggestions_response


class LexmachinaAgentExecutor(AgentExecutor):
    """AgentExecutor implementation for the Lex Machina agent."""

    def __init__(self, config: APIAgentConfiguration) -> None:
        self.config = config

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        api = self.config.build_agent()
        if context.task_id is None or context.context_id is None or context.message is None:
            raise ServerError(error=InvalidParamsError(message="Missing task_id or context_id or message"))
        query = context.get_user_input()

        results = await api.process_query(query)
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
        """Cancellation is not supported."""
        raise ServerError(error=UnsupportedOperationError())
