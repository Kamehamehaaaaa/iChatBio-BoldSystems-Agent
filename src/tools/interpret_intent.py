from state import BoldAgentState
import utils
from schema import responseModel
from ichatbio.agent_response import IChatBioAgentProcess
from langchain.tools import tool

async def interpret_intent(state: BoldAgentState):
    async with state["context"].begin_process(summary="Interpreting User Intent") as process:
        process: IChatBioAgentProcess
        prompt = utils.generate_prompt("intent.md", None)
        instructor_client = state["context"].instructor_client

        if instructor_client == None:
            instructor_client = utils.add_client(state)

        req = await instructor_client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=responseModel,
                messages=[
                    {"role": "system",
                        "content": prompt},
                    {"role": "user", "content": state["user_query"]}],
                temperature=0,
            )
        
        params = req.model_dump(exclude_none=True, by_alias=True)

        await process.log("params generated", data=params)

        state["clarification_needed"] = params.get("clarification_needed", False)
        state["user_intent"] = params.get('user_intent', '')
        state["extracted_terms"] = params.get('terms', [])

        print(state)

        return state

