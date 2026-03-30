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
    # if "records" in state["query_needs"]:
    #     state["documents"] = False
    #     routes.append("document_retrieval")
    # if "images" in state["query_needs"]:
    #     state["images"] = False
    #     routes.append("get_images")
    # if "geomap" in state["query_needs"]:
    #     state["geomap"] = False
    #     routes.append("maps")
    # print(routes, state["query_needs"], state)
    if len(routes) == 0:
        routes.append('finalize')
    return routes

# def fetch_raw_data(state: BoldAgentState):
#     if "records" in state["query_needs"]:
#         return "data"
#     return "no_data"

# def fetch_images(state: BoldAgentState):
#     if "images" in state["query_needs"]:
#         return "images"
#     return "no_images"