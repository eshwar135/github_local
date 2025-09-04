from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.agent_registry import AgentRegistry

router = APIRouter()
agent_registry = AgentRegistry()

@router.post("/upload_excel")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith((".xls", ".xlsx")):
        raise HTTPException(status_code=400, detail="Invalid file type")
    data = await file.read()
    df = await agent_registry.get_agent("ingest").ingest(data)
    return {"message": "File ingested", "rows": len(df)}

@router.post("/query")
async def query_excel(query: str = Form(...)):
    parsed_query = await agent_registry.get_agent("query").parse(query)
    filtered_data = await agent_registry.get_agent("extract").extract(parsed_query)
    result = await agent_registry.get_agent("process").process(filtered_data)
    return {"result": result}
