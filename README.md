# iChatBio-BoldSystems-Agent
Implementation of Bold Systems (https://id.boldsystems.org) data source as an AI Agent for iChatBio (https://ichatbio.org)

# Current Agentic workflow

graph TD

    __start__ --> interpret_intent
    interpret_intent --> preprocess_terms

    preprocess_terms -->|query| query_creation
    preprocess_terms -->|summary| summary_decision

    query_creation -->|documents| document_retrieval
    query_creation -->|geomap| generate_map
    query_creation -->|images| get_images
    query_creation -->|none| finalize

    document_retrieval --> finalize
    generate_map --> finalize
    get_images --> finalize

    finalize --> __end__
    summary_decision --> __end__

