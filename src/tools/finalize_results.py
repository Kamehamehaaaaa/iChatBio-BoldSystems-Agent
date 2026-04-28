from state import BoldAgentState

async def finalize_results(state: BoldAgentState):
    if state['session_active'] == False:
        return state
    
    process = state['process']
    
    if state["documents"] and state["images"] and state["geomap"] and state["taxonomy"]:
        await process.log(f"Completion of query")
        state["session_active"] = False
    
    return state