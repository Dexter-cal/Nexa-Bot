from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from nexa.core.engine import engine
from nexa.models.core import Task as DBTask
from nexa.core.database import AsyncSessionLocal
from sqlalchemy import select

app = FastAPI(title="Nexa Bot API", version="1.0.0")

class CommandRequest(BaseModel):
    command: str

class TaskResponse(BaseModel):
    id: str
    status: str
    description: str

@app.on_event("startup")
async def startup_event():
    await engine.start()

@app.on_event("shutdown")
async def shutdown_event():
    await engine.stop()

@app.get("/")
async def root():
    return {"message": "Welcome to Nexa Bot API"}

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
    return {
        "status": "active" if engine.running else "inactive",
        "agents": len(engine.task_manager.spawner.spawned_agents),
        "privacy": await engine.privacy_guardian.get_summary()
    }
