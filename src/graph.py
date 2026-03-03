# graph.py
from langgraph.graph import StateGraph, END
from state import BoldAgentState

# Assume these tools exist
from tools.interpret_intent import interpret_intent
from tools.preprocess_terms import preprocess_terms
from tools.query_creation import query_creation

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def create_workflow():
    builder = StateGraph(BoldAgentState)

    builder.add_node("interpret_intent", interpret_intent)
    # builder.add_node("request_clarification", request_clarification)
    builder.add_node("preprocess_terms", preprocess_terms)
    # builder.add_node("react_term_correction", react_term_correction)
    builder.add_node("query_creation", query_creation)
    # builder.add_node("summary_decision", summary_decision)
    # builder.add_node("retrieve_documents", retrieve_documents)

    builder.set_entry_point("interpret_intent")

    builder.add_edge("interpret_intent", "preprocess_terms")
    builder.add_edge("preprocess_terms", "query_creation")

    # builder.add_conditional_edges(
    #     "summary_decision",
    #     route_after_summary
    # )

    # builder.add_edge("retrieve_documents", END)
    builder.add_edge("query_creation", END)

    graph = builder.compile()

    return graph

async def run_pipeline(context, user_request: str):
    workflow = create_workflow()

    initial_state = {}

    initial_state["user_query"] = user_request
    initial_state["context"] = context
    initial_state["retry_count"] = 0
    initial_state["session_active"] = True
    initial_state["clarification_needed"] = False
    initial_state["proceed_to_retrieval"] = False
    initial_state["valid_triplets"] = []

    result = await workflow.ainvoke(initial_state)

    return result

