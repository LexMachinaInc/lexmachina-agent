# SPDX-License-Identifier: Apache-2.0

"""Server application for the Lex Machina A2A agent proxy"""

import logging
import os

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


def app() -> Starlette:
    """Create the Starlette ASGI application with the Lex Machina agent."""
    base_url = os.environ.get("BASE_URL", "http://localhost:10011")
    config = APIAgentConfiguration()
    capabilities = AgentCapabilities(streaming=False)
    skill = AgentSkill(
        id="search_suggestions",
        name="Search Suggestions",
        description="""This takes a natural language question or prompt and suggests options for searches.
          You can ask for assistance in building searches and finding the analytics in Lex Machina you care about.""",
        tags=["search", "suggestions", "analytics", "legal"],
        examples=[
            "What is the average time to resolution for contracts cases in SDNY in the last 3 months?",
            "Time to trial in a Los Angeles County case before Judge Randy Rhodes?",
            "Reversal rate for employment cases in the 5th circuit?",
            "Patent cases that went to trial in the last 90 days",
            "Cases before Judge Schofield that mention tortious interference",
            "Has Warby Parker been sued in Texas?",
            "Complaints in Torts cases that mention section 552",
            "Pleadings that mention jurisprudence",
            "Jury Verdicts filed in California in the last 5 years",
            "How long do LA contracts cases before Judge Katherine Chilton take to get to trial?",
            "What is Judge Lemelle's grant rate for transfer motions?",
            "Which firms have the most experience arguing employment cases in N.D.Ill?",
        ],
    )
    agent_card = AgentCard(
        name="Protégé in Lex Machina Agent",
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
