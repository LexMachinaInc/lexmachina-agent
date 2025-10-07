"""Main entry point for the Lex Machina agent."""

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

from .agent_executor import LexmachinaAgentExecutor

load_dotenv()  # Load environment variables from a .env file if present

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=10011)
def main(host: str, port: int) -> None:
    """Main entry point for the Lex Machina agent."""
    try:
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
            url=f"http://{host}:{port}/",
            version="1.0.0",
            default_input_modes=["text"],
            default_output_modes=["application/json"],
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=LexmachinaAgentExecutor(),
            task_store=InMemoryTaskStore(),
        )

        server = A2AStarletteApplication(agent_card=agent_card, http_handler=request_handler)

        import uvicorn

        uvicorn.run(server.build(), host=host, port=port)

    except Exception:
        logger.exception("An error occurred during server startup")
        exit(1)
