from typing import TypedDict, List, Optional, Dict, Any
from openai import AsyncOpenAI
from ichatbio.agent_response import ResponseContext
from schema import queryPhrase

class BoldAgentState(TypedDict, total=False):
    # user input
    user_query: str
    user_intent: str
    
    # structured interpretation
    extracted_terms: List[queryPhrase]
    missing_fields: List[str]
    
    # validation
    valid_triplets: List[str]
    validation_errors: List[str]
    retry_count: int
    
    # query execution
    query_token: Optional[str]
    summary_stats: Optional[Dict[str, Any]]
    
    # retrieval
    documents: List[Dict[str, Any]]
    offset: int
    
    # conversation control
    clarification_needed: bool
    proceed_to_retrieval: bool
    session_active: bool

    # OpenAI client
    instructor_client: AsyncOpenAI

    # ichatbio context
    context: ResponseContext