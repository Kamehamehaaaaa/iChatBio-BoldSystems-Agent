from agent import BoldSystemsAgent
from ichatbio.server import run_agent_server

from graph import create_workflow


create_workflow()
agent = BoldSystemsAgent()
run_agent_server(agent, "localhost", 8991)


