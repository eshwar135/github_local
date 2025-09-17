import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# load .env (this container receives env_file from compose)
load_dotenv(dotenv_path="/app/.env" if os.path.exists("/app/.env") else None)

# Gemini / Google generative AI (example usage)
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if GENAI_AVAILABLE and GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

app = FastAPI(title="multi-service-demo")

class PromptIn(BaseModel):
    prompt: str

@app.get("/", tags=["root"])
async def root():
    return {"msg": "multi-service FastAPI running"}

@app.post("/generate", tags=["gen"])
async def generate(inp: PromptIn):
    if not GENAI_AVAILABLE or not GEMINI_KEY:
        return {"error": "Generative AI client or API key not configured inside container."}

    # Example call - adjust depending on actual genai SDK's function names in your installed version
    # This is a simple illustrative call — check your installed SDK if method names differ.
    resp = genai.generate_text(model="models/text-bison-001", input=inp.prompt)
    # resp will be an SDK object — make sure to access content field as appropriate.
    text = getattr(resp, "output", None) or getattr(resp, "content", None) or str(resp)
    return {"prompt": inp.prompt, "response": text}
