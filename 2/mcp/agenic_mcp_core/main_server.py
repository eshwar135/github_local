from fastapi import FastAPI
from data_agent import DataAgent

app = FastAPI()
agent = DataAgent()

@app.get("/")
def root():
    return {"status": "MCP server running"}

@app.post("/process")
def process_data(input_data: dict):
    result = agent.process(input_data)
    return {"result": result}
