from agent import BoldSystemsAgent
from ichatbio.server import run_agent_server

agent = BoldSystemsAgent()
run_agent_server(agent, "localhost", 8991)
