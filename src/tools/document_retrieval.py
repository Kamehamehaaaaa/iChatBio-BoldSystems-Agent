from state import BoldAgentState
import utils
from urllib.parse import quote
from schema import responseModel
from ichatbio.agent_response import IChatBioAgentProcess
import requests
import json

async def document_retrieval(state: BoldAgentState):
    # async with state["context"].begin_process(summary="Document retrieval") as process:
    #     process: IChatBioAgentProcess

    if state['session_active'] == False:
        return state

    process = state['process']
    
    await process.log("Fetching data from Bold systems")

    encoded_seq = quote(state['query_id'])

    url = f"https://portal.boldsystems.org/api/documents/{encoded_seq}/download?start={state['start']}&length={state['length']}"

    response = requests.get(url, timeout=100)

    code = response.status_code
    # code = f"{response.status_code} {http.client.responses.get(response.status_code, '')}"
    await process.log(f"Bold Systems data retrieved using url {url} with status code {code}")


    # response_json = response.json()
    response_json = []
    for line in response.iter_lines():
        response_json.append(json.loads(line))

    if code == 422:
        await process.log(f"fetching records failed", data=response_json)
        state['session_active'] = False
        return state
    
    # state["documents"] = True

    await process.create_artifact(
            mimetype="application/json",
            description="for user query " + state["user_intent"],
            uris=[url],
            metadata={
                "data_source": "bold systems",
                "portal_url": "portal_url",
            }, 
        )
    
    return {"documents": True, "records": response_json}