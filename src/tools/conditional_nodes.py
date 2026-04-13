from state import BoldAgentState

def should_summarize(state: BoldAgentState):
    if "summary" in state["query_needs"]:
        return "summary"
    return "query"

def route_after_query(state):
    routes = []
    for need in state["query_needs"]:
        state[need] = False
        routes.append(need)

    if len(routes) == 0:
        routes.append('finalize')
    return routes