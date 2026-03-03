from typing import Optional

from pydantic import BaseModel

from ichatbio.agent import IChatBioAgent
from ichatbio.types import AgentCard, AgentEntrypoint
import get_params 

from ichatbio.agent_response import ResponseContext
import graph
from openai import AsyncOpenAI
import instructor

import utils

class BoldSystemsAgent(IChatBioAgent):
    def __init__(self):
        super().__init__()
        self.entrypoint = AgentEntrypoint(id="processRequest", description="Process user's request to fetch information from Bold systems", parameters=None)

    def get_agent_card(self) -> AgentCard:
        return AgentCard(
            name="Bold systems org",
            description="Retieves data related to biological sequences of species from Bold Systems",
            icon=None,
            entrypoints=[
                self.entrypoint,
            ]
        )
    
    async def run(self, context: ResponseContext, request: str, entrypoint: str, params: Optional[BaseModel]):
        # match entrypoint:
        #     case "generate_query_params":
        #         await get_params.run(request=request, context=context)
        #     case _:
        #         raise ValueError()
        client = AsyncOpenAI(api_key=utils.getValue("OPEN_API_KEY"), base_url=utils.getValue("OPENAI_BASE_URL"))
        instructor_client = instructor.patch(client)
        context.instructor_client = instructor_client
        await graph.run_pipeline(context, request)
        await context.reply("Bold Systems query completed")