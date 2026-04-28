from state import BoldAgentState
import utils
from urllib.parse import quote
from schema import responseModel
from ichatbio.agent_response import IChatBioAgentProcess
import requests
import json

async def post_processing(state: BoldAgentState):

    if state['session_active'] == False:
        return state

    post_filters = state['post_filters']

    if post_filters == None:
        return state
    
    process = state['process']
    
    await process.log("Post processing of records required", data=post_filters)

    return state
    
    # records = state['records']

    # for filter in post_filters:
    #     update_records = []
    #     for record in records:
    #         val = record.get(filter['field'], None)
    #         if val == None or val == "null":
    #             continue
    #         match filter['operator']:
    #             case "equals":
    #                 if val == filter['value']:
    #                     update_records.append(record)
    #             case "contains":
    #                 if filter['value'] in val:
    #                     update_records.append(record)
    #             case _:
    #                 update_records.append(record)
    #     records = update_records

    # data = {"data": records}

    # await process.log(f"data after applying post filters", data=data)

    # await process.create_artifact(
    #         mimetype="application/json",
    #         description="filtered response",
    #         uris=[],
    #         metadata={
    #             "data_source": "bold systems",
    #             "portal_url": "portal_url",
    #         }, 
    #         content=json.dumps(data).encode('utf-8') 
    #     )
    
    # return {"records": records}