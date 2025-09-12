from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, requests

app = FastAPI(title="Gemini AI Agent")

API_KEY = os.environ.get("GEMINI_API_KEY")

class Prompt(BaseModel):
    prompt: str
    max_tokens: int = 500

@app.post("/ask")
def ask(prompt: Prompt):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": API_KEY}
    body = {
        "contents": [{"parts": [{"text": prompt.prompt}]}],
        "generationConfig": {"maxOutputTokens": prompt.max_tokens, "temperature": 0.2}
    }

    resp = requests.post(url, headers=headers, params=params, json=body, timeout=30)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=resp.text)

    data = resp.json()
    try:
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise HTTPException(status_code=502, detail="Bad Gemini response")
    return {"reply": reply, "raw": data}
