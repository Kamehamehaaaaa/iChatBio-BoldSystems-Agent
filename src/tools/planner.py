from state import BoldAgentState

async def planner(state: BoldAgentState):
    prompt = '''
You are an planning expert for retrieving information from Bold Systems database (DNA barcodes database for species). 
You plan execution steps that should be taken to complete user request given the avaiable tools.

Available tools:
- "interpret_intent": used to extract parameters for Bold systems API. 
- "preprocess_terms": a validation tool for the parameters generated. Should be used whenever parameters are generated.
- "query_creation": sends request to Bold systems using parameters generated and verified.
- "summary_decision": gets summary counts of records available and not actual records.
'''