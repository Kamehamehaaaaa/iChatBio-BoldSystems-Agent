from state import BoldAgentState
import utils
from schema import responseModel
from ichatbio.agent_response import IChatBioAgentProcess
from langchain.tools import tool
from urllib.parse import quote
import requests

async def get_possible_matches(partial_term):
    try:
        print("getting matches", partial_term)
        encoded_term = quote(partial_term)
        url = "https://portal.boldsystems.org" + "/api/terms?partial_term=" + encoded_term

        # print(url)

        response = requests.get(url, timeout=10)
        
        return {str(ind): match for ind, match in enumerate(response.json())}

    except Exception as e:
        print("Failed in term resolution")
        print(e)
        return {"message": "no partital matches found in Bold"}

async def interpret_intent(state: BoldAgentState):
    # async with state["context"].begin_process(summary="Interpreting User Intent") as process:
    #     process: IChatBioAgentProcess
    if state['session_active'] == False:
        return state
    
    process = state['process']
    prompt = utils.generate_prompt("intent.md", None)
    instructor_client = state["context"].instructor_client

    if instructor_client == None:
        instructor_client = utils.add_client(state)

    req = await instructor_client.chat.completions.create(
            model="gpt-4o-mini",
            response_model=responseModel,
            messages=[
                {"role": "system",
                    "content": prompt},
                {"role": "user", "content": state["user_query"]}],
            temperature=0,
        )
    
    params = req.model_dump(exclude_none=True, by_alias=True)

    await process.log("params generated", data=params)

    terms = params.get('terms', {})

    for term in terms:
        if term.get('scope','') == 'unresolved':
            possible_matches = await get_possible_matches(term.get('value', ''))
            await process.log(f"The query term {term.get('value', '')} has no exact match in Bold")
            # print(possible_matches)
            await process.log(f"Possible matches", data=possible_matches)
            state['session_active'] = False
            return state

    state["clarification_needed"] = params.get("clarification_needed", False)
    state["user_intent"] = params.get('user_intent', '')
    state["extracted_terms"] = params.get('terms', [])

    state["query_needs"] = params.get('query_needs', [])

    # print(state)

    return state

