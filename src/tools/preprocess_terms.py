from state import BoldAgentState
import utils
from urllib.parse import quote
import requests
import http

async def preprocess_terms(state: BoldAgentState):
    # async with state["context"].begin_process(summary="Query preprocessor") as process:
    #     await process.log("Preprocessing query")
    if state['session_active'] == False:
        return state
    
    process = state['process']
    print(state)
    tokens = utils.params_to_token(state["extracted_terms"])
    encoded_tokens = quote(tokens)

    url = "https://portal.boldsystems.org" + "/api/query/preprocessor?query=" + encoded_tokens
    response = requests.get(url, timeout=10)

    code = response.status_code
    # code = f"{response.status_code} {http.client.responses.get(response.status_code, '')}"
    # await process.log(f"Bold Systems triplets verified with code: {code}")

    response_json = response.json()

    print(response_json)

    if code == 200:
        await process.log("Bold Systems Triplets successfully matched", data=response_json)
    elif code == 400:
        await process.log("Bold Systems returned partial matches for generated triplets. Verification required.", data=response_json)
    elif code == 422:
        await process.log("Invalid triplets generated", data=response_json)
        state['session_active'] = False
        return state

    success = response_json.get("successful_terms", "")
    if len(success) > 0:
        for s_terms in success:
            state["valid_triplets"].append(s_terms["matched"].split(';')[0])

    failed = response_json.get('failed_terms', '')
    if len(failed) > 0:
        for s_terms in failed:
            state["valid_triplets"].append(s_terms["matched"].split(';')[0])


    # print(state)
    return state

    