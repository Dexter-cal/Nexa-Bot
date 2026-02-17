from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from nexa.core.engine import engine
from nexa.core.logger import memory_handler, setup_memory_logging
from nexa.models.core import Task as DBTask
from nexa.core.database import AsyncSessionLocal
from sqlalchemy import select

app = FastAPI(title="Nexa Bot API", version="1.0.0")

app.mount("/static", StaticFiles(directory="nexa/api/static"), name="static")
templates = Jinja2Templates(directory="nexa/api/templates")

class CommandRequest(BaseModel):
    command: str

class TaskResponse(BaseModel):
    id: str
    status: str
    description: str

@app.on_event("startup")
async def startup_event():
    setup_memory_logging()
    await engine.start()

@app.on_event("shutdown")
async def shutdown_event():
    await engine.stop()

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/v1/execute", response_model=Dict[str, Any])
async def execute_command(request: CommandRequest):
    try:
        result = await engine.execute_command(request.command)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tasks", response_model=List[Dict[str, Any]])
async def list_tasks():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(DBTask))
        tasks = result.scalars().all()
        return [{"id": t.id, "status": t.status, "description": t.description} for t in tasks]

@app.get("/api/v1/system/status")
async def get_status():
    from nexa.core.alerts import alert_manager
    return {
        "status": "active" if engine.running else "inactive",
        "agents": len(engine.task_manager.spawner.spawned_agents),
        "privacy": await engine.privacy_guardian.get_summary(),
        "messaging": {
            "telegram": engine.messaging_hub.telegram.running,
            "email": engine.messaging_hub.email.running
        }
    }

@app.get("/api/v1/alerts", response_model=List[Dict[str, Any]])
async def list_alerts():
    from nexa.core.alerts import alert_manager
    return await alert_manager.get_recent()

@app.get("/api/v1/logs", response_model=List[Dict[str, Any]])
async def get_logs():
    return memory_handler.get_logs()
