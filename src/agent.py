import os
from typing import Optional

from pydantic import BaseModel

from ichatbio.agent import IChatBioAgent
from ichatbio.types import AgentCard, AgentEntrypoint, Artifact
import get_params 

from ichatbio.agent_response import ResponseContext
from ichatbio.server import build_agent_app

import graph
from openai import AsyncOpenAI
import instructor

import utils

from starlette.applications import Starlette

class BoldSystemsAgent(IChatBioAgent):
    def __init__(self):
        super().__init__()
        self.entrypoint = AgentEntrypoint(id="processRequest", description="Process user's request to fetch information from Bold systems", parameters=None)

    def get_agent_card(self) -> AgentCard:
        return AgentCard(
            name="Bold systems org",
            description="Retieves data related to biological sequences of species from Bold Systems",
            icon_url="http://abc.com",
            entrypoints=[
                self.entrypoint,
            ]
        )
    
    async def run(
            self, 
            context: ResponseContext, 
            request: str, 
            entrypoint: str, 
            params: Optional[BaseModel],
            metadata: Optional[dict] = None
        ):
        if os.environ.get("LLM_PROXY", False):
            if metadata is None:
                raise ValueError("Metadata is required to set agent configuration.")

            llm_proxy = metadata.get("https://ichatbio.org/a2a/v1", {})

            if not llm_proxy or "temporary_llm_key" not in llm_proxy or "ichatbio_base_url" not in llm_proxy:
                raise ValueError("Metadata does not contain the required 'https://ichatbio.org/a2a/v1' key.")

            api_key = llm_proxy["temporary_llm_key"]
            base_url = llm_proxy["ichatbio_base_url"]

            client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        else:
            client = AsyncOpenAI(api_key=utils.getValue("OPEN_API_KEY"), base_url=utils.getValue("OPENAI_BASE_URL"))
        instructor_client = instructor.patch(client)
        context.instructor_client = instructor_client
        await graph.run_pipeline(context, request)
        await context.reply("Bold Systems query completed")


def create_app() -> Starlette:
    agent = BoldSystemsAgent()
    app = build_agent_app(agent)
    return app
