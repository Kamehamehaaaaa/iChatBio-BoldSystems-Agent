from pydantic import BaseModel, Field
from typing import Optional, Annotated, Literal, List

class queryPhrase(BaseModel):
    scope: Optional[
        Annotated[
            Literal["tax", "geo", "recordsetcode", "bin", "inst", "ids"],
            Field(
                description=(
                    "Decide which scope to be used to resolve the user request." \
                    "IMPORTANT:\n" \
                    "- Only assign scope if you are confident it maps to a valid BOLD query.\n" \
                    "- If the term does NOT clearly match any scope, leave scope as null.\n" \
                    "- DO NOT force-fit values into ids/processid.\n" \
                    "- Marker codes (e.g., ND3, COI-5P) are NOT IDs and must NOT be placed in ids scope.\n" \
                    "- 'tax': when user wants to query by taxonomic ranks" \
                    "- 'geo' : when user wants to query by geopolitical locations" \
                    "- 'recordsetcode' : when user wants to query by dataset code" \
                    "- 'bin' : when query by Barcode Index Numbers (BINs), these are unique "
                                "identifiers that cluster animal DNA barcode sequences into operational taxonomic units, "
                                "often acting as proxies for species. Often of the from 'BOLD:*" \
                    "- 'inst' : institution submitting the sequence (sequence_run_site, inst) NOT collectors. Collector names must use post_filters." \
                    "- 'ids' : when user wants to query by ID"
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

class postFilter(BaseModel):
    field: Literal[
        "marker_code",
        "identified_by",
        "collection_date_start",
        "collection_date_end",
        "country/ocean",
        "province/state",
        "region",
        "genus",
        "species",
        "family",
        "order",
        "class",
        "kingdom",
        "bin_uri",
        "sequence_run_site",
        "sequence_upload_date",
        "inst",
        "collectors",
        "habitat",
        "life_stage",
        "sex",
        "depth",
        "elev",
        "nuc_basecount"
    ] = Field(
            description=(
                "Field that cannot be queried directly via BOLD API "
                "and must be filtered after retrieval. "
                "Examples: marker_code, collection_date, sequence_length"
            )
        )

    operator: Annotated[
        Literal["equals", "contains", "gt", "lt"],
        Field(
            description="Operator used for filtering"
        )
    ] = "equals"

    value: Annotated[
        str,
        Field(description="Value for post filtering")
    ]

    justification: Optional[str]


class responseModel(BaseModel):
    user_intent: str = Field(description="Interpretation of User's intent from the request. " \
                        "Helps in decoding the responses and understanding query phrase choices. Limit to 100 words.")
    
    # query_id: str = Field(description="If user request has a already generated query_id, populated here, else an empty string")
    
    terms: List[queryPhrase] = Field(description="List of query phrases to resolve the user request.")

    post_filters: Optional[List[postFilter]] = Field(
        default=None,
        description="Filters applied after retrieving records"
    )

    start: int = Field(default=0, description="Start offset for the records to be fetched")
    length: int = Field(default=1000, description="Number of records to be fetched")

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
    
    # uncertainties: List[str] = Field(description="List all the uncertainties you have with the user request. " \
    #                     "Use this field liberally, any small uncertainity report it here as list of Strings")
    
    clarification_needed: bool = Field(description="If user clarification is needed regarding the request, populated the clarification " \
                        " question in the uncertainity and set this falg as true. " \
                        "Having a uncertainity doesn't always mean that clarification is required.")
