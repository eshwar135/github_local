from backend.agents.ingest_agent.agent import IngestAgent
from backend.agents.query_agent.agent import QueryAgent
from backend.agents.extract_agent.agent import ExtractAgent
from backend.agents.process_agent.agent import ProcessAgent

class AgentRegistry:
    def __init__(self):
        self.agents = {
            "ingest": IngestAgent(),
            "query": QueryAgent(),
            "extract": ExtractAgent(),
            "process": ProcessAgent(),
        }
    def get_agent(self, name):
        return self.agents.get(name)
