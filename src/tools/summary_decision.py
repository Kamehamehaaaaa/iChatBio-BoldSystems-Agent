from state import BoldAgentState
from urllib.parse import quote
from schema import responseModel
from ichatbio.agent_response import IChatBioAgentProcess
from langchain.tools import tool
import requests

async def summary_decision(state: BoldAgentState):
    # async with state["context"].begin_process(summary="Summarizing query output") as process:
    #     process: IChatBioAgentProcess

    if state['session_active'] == False:
        return state
    
    state["session_active"] = False

    process = state['process']
    # await process.log("params", data=state["valid_triplets"])

    query_seq = ""
    for triplet in state["valid_triplets"]:
        query_seq += triplet

    encoded_seq = quote(query_seq)

    url = "https://portal.boldsystems.org" + "/api/summary?query=" + encoded_seq + "&fields=species,specimens,bin_uri,collection_date_start,coord,country/ocean,identified_by,inst,marker_code,sequence_run_site,sequence_upload_date"

    print(url)

    response = requests.get(url, timeout=10)

    code = response.status_code
    # code = f"{response.status_code} {http.client.responses.get(response.status_code, '')}"
    await process.log(f"summary of results generated with code: {code}")

    response_json = response.json()

    if code == 422:
        await process.log(f"Error while generating summary data.", data=response_json)
        return state

    # print(response_json)

    # print(state)

    await process.create_artifact(
            mimetype="application/json",
            description="summary generated",
            uris=[url],
            metadata={
                "data_source": "bold systems",
                "portal_url": "portal_url",
                # "retrieved_record_count": record_count,
                # "total_matching_count": matching_count
            }, 
        )

    return state

