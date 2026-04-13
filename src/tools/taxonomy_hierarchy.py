from state import BoldAgentState
import utils
from urllib.parse import quote
from schema import responseModel
from ichatbio.agent_response import IChatBioAgentProcess
import requests

async def taxonomy_hierarchy(state: BoldAgentState):

    if state['session_active'] == False:
        return state
    
    process = state['process']

    await process.log("Fetching taxonomy hierarchy from Bold systems")

    encoded_seq = quote(state['query_id'])

    url = "https://portal.boldsystems.org" + "/api/taxonomy/" + encoded_seq

    # state['urls'].append(url)

    response = requests.get(url, timeout=10)

    code = response.status_code
    await process.log(f"Taxonomy summary fetched using url {url} with status code {code}")

    response_json = response.json()

    if code == 422:
        await process.log(f"fetching taxonomic hierarchy failed", data=response_json)
        state['session_active'] = False
        return state

    await process.create_artifact(
            mimetype="application/json",
            description="taxonomy summary for " + state["user_intent"],
            uris=[url],
            metadata={
                "data_source": "bold systems",
                "portal_url": "portal_url",
            }, 
        )

    return {'taxonomy': True}