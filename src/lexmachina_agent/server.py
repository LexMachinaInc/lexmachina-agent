# SPDX-License-Identifier: Apache-2.0

"""Server application for the Lex Machina A2A agent proxy"""

import logging

import click
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from dotenv import load_dotenv
from starlette.applications import Starlette

from .agent_executor import APIAgentConfiguration, LexmachinaAgentExecutor

load_dotenv()  # Load environment variables from a .env file if present

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=10011)
def main(host: str, port: int) -> None:
    """Run the Lex Machina agent server"""
    try:
        url = f"http://{host}:{port}/"
        server = app(url)

        import uvicorn

        uvicorn.run(server, host=host, port=port)

    except Exception:
        logger.exception("An error occurred during server startup")
        exit(1)


def app(base_url: str = "http://localhost:10011/") -> Starlette:
    """Create the Starlette ASGI application with the Lex Machina agent."""
    config = APIAgentConfiguration()
    capabilities = AgentCapabilities(streaming=False)
    skill = AgentSkill(
        id="search_suggestions",
        name="Search Suggestions",
        description="Provide search suggestions based on user input.",
        tags=["search", "suggestions", "analytics"],
        examples=[
            "What is the average time to resolution for contracts cases in SDNY in the last 3 months?",
            "Time to trial in a Los Angeles County case before Judge Randy Rhodes?",
            "Reversal rate for employment cases in the 5th circuit?",
        ],
    )
    agent_card = AgentCard(
        name="Search Suggestions Agent",
        description="Provide search suggestions based on user input.",
        url=base_url,
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["application/json"],
        capabilities=capabilities,
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=LexmachinaAgentExecutor(config=config),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(agent_card=agent_card, http_handler=request_handler)
    return server.build()
