from pydantic import BaseModel, Field
from typing import Optional, Annotated, Literal, List

class queryPhrase(BaseModel):
    scope: Optional[
        Annotated[
            Literal["tax", "geo", "recordsetcode", "bin", "inst", "ids", "unresolved"],
            Field(
                description=(
                    "Decide which scope to be used to resolve the user request." \
                    "Chose one of the following " \
                    "- 'tax': when user wants to query by taxonomic ranks" \
                    "- 'geo' : when user wants to query by geopolitical locations" \
                    "- 'recordsetcode' : when user wants to query by dataset code" \
                    "- 'bin' : when query by Barcode Index Numbers (BINs), these are unique "
                                "identifiers that cluster animal DNA barcode sequences into operational taxonomic units, "
                                "often acting as proxies for species. Often of the from 'BOLD:*" \
                    "- 'inst' : when user wants to query by institution" \
                    "- 'ids' : when user wants to query by ID"
                    "- 'unresolved' : use this as a fallback. when the user term doesnt match any of the above scopes use this."
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
                    "- for 'geo' : 'country/ocean','province/state','region'" \
                    "- for 'recordsetcode' : 'code'" \
                    "- for 'bin' : 'uri'" \
                    "- for 'inst' : 'name','seqsite'" \
                    "- for 'ids' : 'processid','sampleid','insdcacs'" \
                )
            )
        ]
    ]

    value: Annotated[
            str,
            Field(
                description=(
                    "Value for the 'scope' or 'scope:field' combination from user request." \
                    "Ex: 'DNA barcode records from South Africa' would have value as South Africa"
                )
            )
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


class responseModel(BaseModel):
    user_intent: str = Field(description="Interpretation of User's intent from the request. " \
                        "Helps in decoding the responses and understanding query phrase choices. Limit to 100 words.")
    
    # query_id: str = Field(description="If user request has a already generated query_id, populated here, else an empty string")
    
    terms: List[queryPhrase] = Field(description="List of query phrases to resolve the user request.")

    query_needs: Optional[
        List[Literal["summary", "documents", "images", "geomap", "taxonomy"]]
    ] = Field(
        None,
        description=(
            "Specifies the type of data the user needs in response to the query. "
            "Possible values include:\n"
            "- 'summary': when the user requires a textual summary count of the data and not actual data.\n"
            "- 'documents': when the user needs detailed records or data entries.\n"
            "- 'images': when the user requests visual content or images.\n"
            "- 'geomap': when the user wants geographical mapping or spatial data of the query.\n"
            "- 'taxonomy': when the user wants taxonomy summary of the data of the query.\n"
        )
    )


    # summary: Optional[bool] = Field(default=False, description="If user asks for summary counts and not actual records set to True.")

    # map: Optional[bool] = Field(default=False, description="If user asks for a geographic map of record occurrences.")

    # images: Optional[bool] = Field(default=False, description="If user asks for images of species related to query.")

    assumptions: List[str] = Field(description="List all the assumptions made while generating the candidate_terms " \
                        "for resolving the user request.")
    
    uncertainities: List[str] = Field(description="List all the uncertainities you have with the user request. " \
                        "Use this field liberally, any small uncertainity report it here.")
    
    clarification_needed: bool = Field(description="If user clarification is needed regarding the request, populated the clarification " \
                        " question in the uncertainity and set this falg as true. " \
                        "Having a uncertainity doesn't always mean that clarification is required.")
