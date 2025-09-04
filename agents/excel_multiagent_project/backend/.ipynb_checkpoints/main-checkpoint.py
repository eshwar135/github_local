from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.router.langgraph_router import router

app = FastAPI(title="Excel Multi-Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Excel Multi-Agent Backend is running"}
