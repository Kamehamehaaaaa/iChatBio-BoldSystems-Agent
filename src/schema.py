from pydantic import BaseModel, Field
from typing import Optional, Annotated, Literal, List

class queryPhrase(BaseModel):
    scope: Optional[
        Annotated[
            Literal["tax", "geo"],
            Field(
                description=(
                    "Decide which scope to be used to resolve the user request." \
                    "Chose one of the following " \
                    "- 'tax': when user wants to query by taxonomic ranks"
                    "- 'geo' : when user wants to query by location"
                )
            )
        ]
    ]

    field: Optional[
        Annotated[
            str,
            Field(
                description=(
                    "Fields or subs-scopes for the query. Chose the field based on the scope selection."
                    "If none of the fields match the user request you can skip it." \
                    "Available values for fields for each scope:" \
                    "- for 'tax' : 'kingdom','phylum','class','order','family','subfamily','tribe','genus','species','subspecies'" \
                    "- for 'geo' : 'country/ocean','province/state','region'"
                )
            )
        ]
    ]

    value: Optional[
        Annotated[
            str,
            Field(
                description=(
                    "Value for the 'scope' or 'scope:field' combination from user request." \
                    "Ex: 'DNA barcode records from South Africa' would have value as South Africa"
                )
            )
        ]
    ]

    justification: Optional[
        Annotated[
            str,
            Field(
                description=(
                    "Justify your choice for the scope, field and value here. " \
                    "Give a clean and understandable justification."
                )
            )
        ]
    ]


class candidateTerms(BaseModel):
    query_phrases: List[queryPhrase] = Field(description="List of query phrases to resolve the user request.")

class responseModel(BaseModel):
    user_intent: str = Field(description="Interpretation of User's intent from the request. " \
                        "Helps in decoding the responses and understanding query phrase choices.")
    
    terms: List[queryPhrase] = Field(description="List of query phrases to resolve the user request.")

    assumptions: List[str] = Field(description="List all the assumptions made while generating the candidate_terms " \
                        "for resolving the user request.")
    
    uncertainities: List[str] = Field(description="List all the uncertainities you have with the user request. " \
                        "Use this field liberally, any small uncertainity report it here.")
    
    clarification_needed: bool = Field(description="If user clarification is needed regarding the request, populated the clarification " \
                        " question in the uncertainity and set this falg as true. " \
                        "Having a uncertainity doesn't always mean that clarification is required.")
