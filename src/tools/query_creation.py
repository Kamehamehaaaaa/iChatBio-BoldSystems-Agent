from state import BoldAgentState
from urllib.parse import quote
import requests
from langchain.tools import tool

async def query_creation(state: BoldAgentState):
    async with state["context"].begin_process(summary="Query preprocessor") as process:
        await process.log("Preprocessing query")

        query_seq = ""
        for triplet in state["valid_triplets"]:
            query_seq += triplet

        encoded_seq = quote(query_seq)

        url = "https://portal.boldsystems.org" + "/api/query?query=" + encoded_seq

        print(url)

        response = requests.get(url, timeout=10)

        code = response.status_code
        # code = f"{response.status_code} {http.client.responses.get(response.status_code, '')}"
        await process.log(f"Bold Systems triplets verified with code: {code}")

        response_json = response.json()

        print(response_json)

        await process.create_artifact(
                mimetype="application/json",
                description="query generated",
                uris=[url],
                metadata={
                    "data_source": "bold systems",
                    "portal_url": "portal_url",
                    # "retrieved_record_count": record_count,
                    # "total_matching_count": matching_count
                }, 
            )

        return state
