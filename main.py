import os
import json
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app_logic import ScribeAgent

app = FastAPI(title="Data Scribe AI Agent | High-Reliability Version")

# Global state for Live Agent Console
agent_logs = []

class ScribeRequest(BaseModel):
    url: str
    filename: str = None

# Ensure template directory exists
os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/scribe")
async def start_scribe(req: ScribeRequest, background_tasks: BackgroundTasks):
    global agent_logs
    agent_logs = ["[SYSTEM] Scribe initialized. Processing URL..."]
    
    def log_msg(msg):
        agent_logs.append(msg)
        print(msg)

    async def run_task():
        try:
            agent = ScribeAgent(log_callback=log_msg)
            result = agent.scrape(req.url, custom_filename=req.filename)
            log_msg(f"Task completed with status: {result['status']}")
        except Exception as e:
            log_msg(f"CRITICAL ERROR: {str(e)}")

    background_tasks.add_task(run_task)
    return {"status": "started", "message": "Scribe agent is now processing the URL in high-reliability mode."}

@app.get("/logs")
async def get_logs():
    return {"logs": agent_logs}

@app.get("/data")
async def get_data():
    log_file = "data/scribe_log.json"
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                logs = json.load(f)
        except:
            logs = []
    else:
        logs = []
    
    return {"history": logs}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
