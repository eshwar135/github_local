class ProcessAgent:
    async def process(self, df):
        if df is None:
            return "No data to process"
        return df.describe().to_dict()
