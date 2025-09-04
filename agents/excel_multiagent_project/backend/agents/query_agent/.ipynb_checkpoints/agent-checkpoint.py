class QueryAgent:
    def __init__(self):
        self.query = None

    async def parse(self, query: str):
        self.query = query
        return query
