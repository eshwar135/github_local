# app/app.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI (multi-service)!"}

@app.get("/ping")
def ping():
    return {"status":"ok"}
