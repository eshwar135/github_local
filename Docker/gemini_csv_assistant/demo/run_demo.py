import requests
from pathlib import Path

csv_path = Path("demo/sample_data/sales_sample.csv")
if not csv_path.exists():
    raise SystemExit("demo/sample_data/sales_sample.csv not found - create it first")

# 1) upload
files = {"file": open(str(csv_path), "rb")}
r = requests.post("http://127.0.0.1:8000/upload", files=files)
print("upload ->", r.json())

# 2) ask
payload = {"csv_filename": csv_path.name, "user_query": "Show top 5 numeric columns by sum"}
r = requests.post("http://127.0.0.1:8000/ask", json=payload)
print("ask ->", r.json())
