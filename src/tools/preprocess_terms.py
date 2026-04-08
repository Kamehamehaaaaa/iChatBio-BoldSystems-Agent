from state import BoldAgentState
import utils
from urllib.parse import quote
import requests
from utils import partial_term_resolver

async def populate_with_resolver(term):
    try:
        value = term.get('value', '')
        if len(value) == 0:
            return False, ""
        
        if len(value) < 3:
            return True, term
        
        success, resolver = await partial_term_resolver(value)

        # print("resolving")
        # print(term)
        # print(resolver)

        # print()

        if success == 0:
            return False, ""

        for i in resolver:
            if len(term.get('scope', '')) > 0 and i['scope'] == term['scope']:
                return True, i
        
        # the partial term matcher always returns something from BOLD so reliable
        return True, resolver[0]

    except Exception as e:
        print(e)


async def preprocess_terms(state: BoldAgentState):
    # async with state["context"].begin_process(summary="Query preprocessor") as process:
    #     await process.log("Preprocessing query")
    if state['session_active'] == False:
        return state
    
    process = state['process']

    extracted_terms = state["extracted_terms"]
    updated_terms = []


    # use the partial term extractor to get BOLD specific triplets 
    for term in extracted_terms:
        res, resolved = await populate_with_resolver(term)
        print(res,resolved)
        if not res:
            if len(term.get('value', '')) == 0:
                await process.log(f"Invalid value, agent encountered error")
            else:
                await process.log(f"The term {term.get('value')} not found in Bold")
            state['session_active'] = False
            return state
        updated_terms.append(resolved)

    # print(updated_terms)

    # use the updated_terms from BOLD (guaranteed) to check if everything is good
    tokens = utils.params_to_token(updated_terms)

    # print(tokens)
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
            term = s_terms["matched"].split(';')[0]
            state["valid_triplets"].append(term)
        
    failed = response_json.get('failed_terms', '')
    if len(failed) > 0:
        for f_terms in failed:
            term = f_terms["matched"].split(';')[0]
            state["valid_triplets"].append(term)


    # print(state)
    return state

    