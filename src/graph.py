# graph.py
from langgraph.graph import StateGraph, END
from state import BoldAgentState

# Assume these tools exist
from tools.interpret_intent import interpret_intent
from tools.preprocess_terms import preprocess_terms
from tools.query_creation import query_creation
from tools.summary_decision import summary_decision
from tools.document_retrieval import document_retrieval
from tools.get_images import get_images
from tools.finalize_results import finalize_results
from tools.generate_map import generate_map

from tools.conditional_nodes import should_summarize, route_after_query

from ichatbio.agent_response import IChatBioAgentProcess

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def create_workflow():
    builder = StateGraph(BoldAgentState)

    builder.add_node("interpret_intent", interpret_intent)
    # builder.add_node("request_clarification", request_clarification)
    builder.add_node("preprocess_terms", preprocess_terms)
    # builder.add_node("react_term_correction", react_term_correction)
    builder.add_node("query_creation", query_creation)
    builder.add_node("summary_decision", summary_decision)
    builder.add_node("document_retrieval", document_retrieval)

    builder.add_node("get_images", get_images)
    builder.add_node("generate_map", generate_map)
    # builder.add_node("generate_geomap", generate_geomap)

    builder.add_node("finalize", finalize_results)

    builder.set_entry_point("interpret_intent")

    builder.add_edge("interpret_intent", "preprocess_terms")

    builder.add_conditional_edges(
        "preprocess_terms",
        should_summarize,
        {
            "summary": "summary_decision",
            "query": "query_creation"
        }
    )

    builder.add_edge("summary_decision", END)
    # builder.add_edge("query_creation", "document_retrieval")

    builder.add_conditional_edges(
        "query_creation",
        route_after_query,
        {
            "documents": "document_retrieval",
            "images": "get_images",
            "geomap": "generate_map",
            "finalize": "finalize"
        }
    )

    builder.add_edge("document_retrieval", "finalize")
    builder.add_edge("get_images", "finalize")
    builder.add_edge("generate_map", "finalize")


    builder.add_edge("finalize", END)
    # builder.add_conditional_edges(
    #     "document_retrieval",
        
    # )


    # builder.add_edge("preprocess_terms", "query_creation")
    # builder.add_edge("query_creation", "summary_decision")
    # builder.add_edge("summary_decision", "document_retrieval")

    # builder.add_conditional_edges(
    #     "summary",
    #     route_after_summary
    # )

    # builder.add_edge("retrieve_documents", END)
    # builder.add_edge("document_retrieval", END)

    graph = builder.compile()

    return graph

def view_graph(graph):
    png = graph.get_graph().draw_mermaid_png()

    with open("graph_image.png", "wb") as f:
        f.write(png)

    print("Image saved as graph_image.png")

async def run_pipeline(context, user_request: str):
    workflow = create_workflow()

    # view_graph(workflow)

    initial_state = BoldAgentState()

    initial_state["user_query"] = user_request
    initial_state["context"] = context
    initial_state["retry_count"] = 0
    initial_state["session_active"] = True
    initial_state["clarification_needed"] = False
    initial_state["proceed_to_retrieval"] = False
    initial_state["valid_triplets"] = []
    initial_state['query_id'] = ''
    initial_state['process'] = None
    initial_state['query_needs'] = []
    initial_state['documents'] = True
    initial_state['images'] = True
    initial_state['geomap'] = True

    async with context.begin_process(summary="Interpreting User Intent") as process:
        process: IChatBioAgentProcess
        initial_state['process'] = process
        await process.log(f"Original request: {user_request}")
        result = await workflow.ainvoke(initial_state)

    return result

