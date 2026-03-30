from state import BoldAgentState

async def finalize_results(state: BoldAgentState):
    if state['session_active'] == False:
        return state
    
    process = state['process']
    
    if state["documents"] and state["images"]:
        await process.log(f"Completion of query")
        return state