from openai import OpenAI, AsyncOpenAI

import instructor
from instructor.core import InstructorRetryException

from schema import responseModel
from tenacity import AsyncRetrying

import requests
import http

from ichatbio.agent import IChatBioAgent
from ichatbio.agent_response import ResponseContext, IChatBioAgentProcess
from ichatbio.types import AgentCard, AgentEntrypoint

import utils
from urllib.parse import urlencode, quote


description = """
generate query params from user request. 
"""

entrypoint= AgentEntrypoint(
    id="generate_query_params",
    description=description,
    parameters=None
)

async def run(request: str, context: ResponseContext):
    async with context.begin_process(summary="Generating query params") as process:
        process: IChatBioAgentProcess

        await process.log("user request:" + request)

        system_prompt = "You are an expert at generating query params from user request in the specific format for Bold Systems API." \
                        "You are **responsible** for parsing user's natural language request into the params format and populate candidate_terms"

        
        client = AsyncOpenAI(api_key=utils.getValue("OPEN_API_KEY"), base_url=utils.getValue("OPENAI_BASE_URL"))
    
        instructor_client = instructor.patch(client)

        req = await instructor_client.chat.completions.create(
            model="gpt-4o-mini",
            response_model=responseModel,
            messages=[
                {"role": "system",
                    "content": system_prompt},
                {"role": "user", "content": request}],
            temperature=0,
        )

        params = req.model_dump(exclude_none=True, by_alias=True)

        print(params)

        await process.log("params generated", data=params)

        # try:
        tokens = utils.params_to_token(params)
        print(tokens)
        encoded_tokens = quote(tokens)
        url = "https://portal.boldsystems.org" + "/api/query/preprocessor?query=" + encoded_tokens

        print(url)

        response = requests.get(url, timeout=10)

        code = f"{response.status_code} {http.client.responses.get(response.status_code, '')}"

        await process.log(f"Bold Systems data retrived successfully: {code}")

        print(response.json())

        await process.create_artifact(
                mimetype="application/json",
                description="generated params",
                uris=[url],
                metadata={
                    "data_source": "Bold Systems",
                    "portal_url": "portal_url",
                    "retrieved_record_count": 0,
                    "total_matching_count": 0
                }, 
            )
        
        # except Exception as e:
        #     print(e)
        #     await process.log("Error Encountered")
