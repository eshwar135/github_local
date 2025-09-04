from backend.agents.ingest_agent.agent import IngestAgent

class ExtractAgent:
    def __init__(self):
        self.ingest_agent = IngestAgent()  # Note: in real implementation, share instance properly

    async def extract(self, query: str):
        df = self.ingest_agent.df
        if df is None:
            return None
        # Placeholder: return full DataFrame
        return df
