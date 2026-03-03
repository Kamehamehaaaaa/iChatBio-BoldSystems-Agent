from state import BoldAgentState
import utils
from urllib.parse import quote
import requests
import http
from langchain.tools import tool

async def preprocess_terms(state: BoldAgentState):
    async with state["context"].begin_process(summary="Query preprocessor") as process:
        await process.log("Preprocessing query")
        print(state)
        tokens = utils.params_to_token(state["extracted_terms"])
        encoded_tokens = quote(tokens)

        url = "https://portal.boldsystems.org" + "/api/query/preprocessor?query=" + encoded_tokens
        response = requests.get(url, timeout=10)

        code = response.status_code
        # code = f"{response.status_code} {http.client.responses.get(response.status_code, '')}"
        await process.log(f"Bold Systems triplets verified with code: {code}")

        response_json = response.json()

        print(response_json)

        success = response_json.get("successful_terms", "")
        if len(success) > 0:
            for s_terms in success:
                state["valid_triplets"].append(s_terms["matched"])

        print(state)
        return state

        