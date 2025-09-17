# Gemini CSV Assistant (Jupyter Lab scaffold)


## Quick run (Windows, Jupyter Lab terminal)
1. Open Jupyter Lab and start a terminal.
2. Create a python venv and activate it (optional but recommended):
python -m venv .venv
.\.venv\Scripts\activate
3. Install dependencies:
pip install -r backend/requirements.txt
4. Copy `.env.example` to `.env` and add your `GEMINI_API_KEY` if you will replace the stub.
5. Start backend:
set PORT=8000
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
6. In Jupyter Lab open `demo/demo_notebook.py` or create a notebook and run the cells. The notebook uploads `demo/sample_data/sales_sample.csv` and queries the backend.


Notes:
- Replace `gemini_client.ask_gemini_for_code` with your real Gemini API call.
- The runner restricts execution to Pandas and returns DataFrame heads only to keep things safe.