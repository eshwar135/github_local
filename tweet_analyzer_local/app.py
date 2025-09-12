# app.py
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Tweet Analyzer Local")

RESULTS_PATH = os.environ.get("RESULTS_PATH", "./results.csv")

@app.get("/")
def root():
    return {"message": "Tweet Analyzer Local - ready"}

@app.post("/run_agents")
def run_agents(run_summaries: bool = Query(False, description="Set true to call Gemini for summaries")):
    try:
        from agent_manager import run_full_pipeline
        df = run_full_pipeline(save_results=True, run_summaries=run_summaries)
        return {"rows": len(df), "message": "Pipeline finished", "saved_to": RESULTS_PATH}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results")
def get_results():
    if not os.path.exists(RESULTS_PATH):
        raise HTTPException(status_code=404, detail="Results not found. Run POST /run_agents first.")
    import pandas as pd
    df = pd.read_csv(RESULTS_PATH)
    return df.to_dict(orient="records")

@app.get("/results_html", response_class=HTMLResponse)
def results_html():
    if not os.path.exists(RESULTS_PATH):
        return HTMLResponse("<pre>No results yet. POST /run_agents to run agents.</pre>", status_code=404)
    import pandas as pd
    df = pd.read_csv(RESULTS_PATH)
    return HTMLResponse(df.to_html(index=False, escape=True))

@app.get("/test_gemini")
def test_gemini(prompt: str = Query("Say hi in one sentence.", description="Prompt to send to Gemini"),
                 max_tokens: int = Query(64, description="Max output tokens (best-effort)")):
    """
    Quick test endpoint to call the configured model and return its text or an error string.
    Uses agent_manager.robust_call_gemini if available (so it will try ALT_GEMINI_MODEL on 404).
    """
    try:
        from agent_manager import robust_call_gemini
        out = robust_call_gemini(prompt, max_output_tokens=max_tokens)
        return {"result": out}
    except Exception:
        # Fallback: call gemini_wrapper directly
        try:
            from gemini_wrapper import call_gemini
            out = call_gemini(prompt, max_output_tokens=max_tokens)
            return {"result": out}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
