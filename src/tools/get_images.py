from state import BoldAgentState
import utils
from urllib.parse import quote
from schema import responseModel
from ichatbio.agent_response import IChatBioAgentProcess
import requests

async def get_images(state: BoldAgentState):
    # async with state["context"].begin_process(summary="Document retrieval") as process:
    #     process: IChatBioAgentProcess

    if state['session_active'] == False:
        return state

    process = state['process']
    
    await process.log("Fetching image data from Bold systems")

    encoded_seq = quote(state['query_id'])

    url = "https://portal.boldsystems.org" + "/api/images/" + encoded_seq

    # state['urls'].append(url)

    response = requests.get(url, timeout=10)

    code = response.status_code
    # code = f"{response.status_code} {http.client.responses.get(response.status_code, '')}"
    await process.log(f"Images retrieved using {url} with status code {code}")

    response_json = response.json()

    if code == 422:
        await process.log(f"get image data failed", data=response_json)
        # state['session_active'] = False
        return state
    
    # state["images"] = True

    await process.create_artifact(
            mimetype="application/json",
            description="for user query: " + state["user_intent"],
            uris=[url],
            metadata={
                "data_source": "bold systems",
                "portal_url": "portal_url",
                # "retrieved_record_count": record_count,
                # "total_matching_count": matching_count
            }, 
        )
    
    return {"images": True}