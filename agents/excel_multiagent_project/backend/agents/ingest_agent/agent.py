import pandas as pd
import io

class IngestAgent:
    def __init__(self):
        self.df = None

    async def ingest(self, file_bytes: bytes) -> pd.DataFrame:
        df = pd.read_excel(io.BytesIO(file_bytes))
        self.df = df
        return df
