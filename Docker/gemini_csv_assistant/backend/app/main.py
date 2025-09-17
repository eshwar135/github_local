from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path
from .csv_runner import run_pandas_snippet
from .gemini_client import ask_gemini_for_code

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Gemini CSV Assistant Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    csv_filename: str
    user_query: str

@app.post('/upload')
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail='Only CSV allowed')
    dest = UPLOAD_DIR / file.filename
    with open(dest, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    return {"filename": file.filename, "path": str(dest)}

@app.post('/ask')
async def ask(req: QueryRequest):
    csv_path = UPLOAD_DIR / req.csv_filename
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail='CSV not found')

    # 1) Ask Gemini for Pandas snippet and explanation
    code_prompt = {
        'filename': str(csv_path),
        'user_query': req.user_query
    }
    gemini_response = ask_gemini_for_code(code_prompt)
    pandas_code = gemini_response.get('pandas_code')
    explanation = gemini_response.get('explanation')

    # 2) Run snippet safely
    result = run_pandas_snippet(csv_path, pandas_code)

    return {
        'explanation': explanation,
        'pandas_code': pandas_code,
        'result': result
    }
