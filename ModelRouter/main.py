from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import os

from config import app_config
from router_engine import RouterEngine

app = FastAPI(title="Model Router")

# Initialize Router Engine
router = RouterEngine(app_config)

# Mount static files
# Mount static files
import os
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class QueryRequest(BaseModel):
    text: str

class KnowledgeRequest(BaseModel):
    text: str
    metadata: Dict[str, Any] = {}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return f.read()

@app.post("/api/chat")
async def chat(request: QueryRequest):
    try:
        response = router.process_query(request.text)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/knowledge")
async def add_knowledge(request: KnowledgeRequest):
    try:
        router.add_knowledge(request.text, request.metadata)
        return {"status": "success", "message": "Knowledge added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config():
    return {
        "llms": [llm.dict(exclude={"api_key"}) for llm in app_config.llms]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
