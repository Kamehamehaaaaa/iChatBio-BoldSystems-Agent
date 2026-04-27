from state import BoldAgentState
import utils
from schema import responseModel
from ichatbio.agent_response import IChatBioAgentProcess
from urllib.parse import quote
from utils import partial_term_resolver

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

    # for term in terms:
    #     if term.get('scope','') == 'unresolved':
    #         success, possible_matches, url = await partial_term_resolver(term.get('value', ''))
    #         await process.log(f"Failed to infer the scope of the search term '{term.get('value', '')}'")
    #         if success == 0:
    #             # await process.log(f"The query term {term.get('value', '')} has no exact match in Bold")
    #             state['session_active'] = False
    #             await process.log(f"Attempted to resolve the term '{term.get('value', '')} using url {url}")
    #             return state
    #         # print(possible_matches)
    #         await process.log(f"Possible matches for search term: {term.get('value', '')}", data=possible_matches)
    #         state['session_active'] = False
    #         return state

    state["clarification_needed"] = params.get("clarification_needed", False)
    state["user_intent"] = params.get('user_intent', '')
    state["extracted_terms"] = params.get('terms', [])
    state["post_filters"] = params.get('post_filters')
    
    state["start"] = params.get('start', 0)
    state["length"] = params.get('length', 1000)

    state["query_needs"] = params.get('query_needs', [])

    # print(state)

    return state

