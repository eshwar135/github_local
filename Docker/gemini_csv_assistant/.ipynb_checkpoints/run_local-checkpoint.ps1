# Run in Jupyter terminal (PowerShell) from project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
setx GEMINI_API_KEY ""
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload