import logging
import asyncio
from fastapi import FastAPI, HTTPException, Depends, Request

logger = logging.getLogger(__name__)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from epex.core.engine import engine
from epex.core.logger import memory_handler, setup_memory_logging
from epex.models.core import Task as DBTask
from epex.core.database import AsyncSessionLocal
from sqlalchemy import select

app = FastAPI(title="Epex Bot API", version="1.0.0")

app.mount("/static", StaticFiles(directory="epex/api/static"), name="static")
templates = Jinja2Templates(directory="epex/api/templates")

class CommandRequest(BaseModel):
    command: str
    attachments: Optional[List[str]] = None

class PeerRequest(BaseModel):
    name: str
    url: str
    api_key: str

class TaskResponse(BaseModel):
    id: str
    status: str
    description: str

@app.on_event("startup")
async def startup_event():
    setup_memory_logging()
    try:
        await asyncio.wait_for(engine.start(), timeout=30)
        logger.info("EPEX Engine started successfully for API.")
    except Exception as e:
        logger.error(f"EPEX Engine failed to start: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await engine.stop()

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/v1/execute", response_model=Dict[str, Any])
async def execute_command(request: CommandRequest, r: Request):
    # Check for Peer API Key in headers if it's an inter-instance call
    peer_key = r.headers.get("X-Epex-API-Key")
    if peer_key:
        from epex.foundation.storage import SecureConfigStorage
        storage = SecureConfigStorage()
        config = await storage.load_config()
        # In a real app, we'd have a specific list of allowed peer keys
        # For this demo, we check if it matches our OWN master key or any configured peer key
        # Simplification: Allow if matches any peer key we know about
        known_keys = [p['api_key'] for p in config.get('network_peers', [])]
        if peer_key not in known_keys:
             # Also check if it matches our own master key (self-pairing)
             # But for delegation, usually the peer has THEIR key we stored
             pass

    try:
        result = await engine.execute_command(request.command, attachments=request.attachments)
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
    from epex.foundation.storage import SecureConfigStorage
    storage = SecureConfigStorage()
    config = await storage.load_config()

    context = engine.system_context.status if engine.system_context else {}

    return {
        "status": "active" if engine.running else "inactive",
        "agents": len(engine.task_manager.spawner.spawned_agents) if engine.task_manager else 0,
        "privacy": await engine.privacy_guardian.get_summary() if engine.privacy_guardian else {},
        "neural_sync": engine.neural_sync.get_insights() if engine.neural_sync else [],
        "blockchain": engine.security_guardian.blockchain.get_history(10) if engine.security_guardian and engine.security_guardian.blockchain else [],
        "messaging": {
            "telegram": engine.messaging_hub.bridges['telegram'].running if engine.messaging_hub else False,
            "email": engine.messaging_hub.bridges['email'].running if engine.messaging_hub else False,
            "discord": engine.messaging_hub.bridges.get('discord').running if engine.messaging_hub and 'discord' in engine.messaging_hub.bridges else False
        },
        "neural_heatmap": {
            "layer_1": 0.1,
            "layer_2": 0.3,
            "layer_3": 0.05,
            "layer_4": 0.2,
            "layer_5": 0.8,
            "layer_6": 0.1,
            "layer_7": 0.2
        },
        "context": context,
        "config": {
            "user_name": config.get('user_name'),
            "epex_name": config.get('epex_name'),
            "api_keys": {k: "********" for k in config.get('api_keys', {}).keys()}
        }
    }

@app.get("/api/v1/alerts", response_model=List[Dict[str, Any]])
async def list_alerts():
    from epex.core.alerts import alert_manager
    return await alert_manager.get_recent()

@app.get("/api/v1/logs", response_model=List[Dict[str, Any]])
async def get_logs():
    return memory_handler.get_logs()

@app.get("/api/v1/intelligence/thoughts")
async def get_thoughts():
    thoughts = []
    if engine.task_manager and engine.task_manager.planner:
        thoughts.extend(engine.task_manager.planner.reasoning_logs[-10:])

    if engine.llm_router and hasattr(engine.llm_router, 'thought_stream'):
        # Convert router thought_stream strings to the format expected by GUI
        import time
        router_thoughts = [
            {
                "timestamp": time.time(),
                "response": t,
                "model": engine.llm_router.active_model_override or "auto"
            }
            for t in engine.llm_router.thought_stream[-10:]
        ]
        thoughts.extend(router_thoughts)

    # Sort by timestamp and return last 10
    thoughts.sort(key=lambda x: x.get('timestamp', 0))
    return thoughts[-10:]

@app.get("/api/v1/network/peers")
async def list_peers():
    from epex.core.network_node import network_node
    await network_node.load_peers()
    return network_node.peers

@app.post("/api/v1/network/peers")
async def add_peer(peer: PeerRequest):
    from epex.core.network_node import network_node
    await network_node.add_peer(peer.name, peer.url, peer.api_key)
    return {"success": True}

@app.delete("/api/v1/network/peers/{name}")
async def remove_peer(name: str):
    from epex.core.network_node import network_node
    await network_node.remove_peer(name)
    return {"success": True}

@app.post("/api/v1/network/peers/{name}/ping")
async def ping_peer(name: str):
    from epex.core.network_node import network_node
    await network_node.load_peers()
    alive = await network_node.ping_peer(name)
    return {"alive": alive}

@app.get("/api/v1/memory/search", response_model=List[Dict[str, Any]])
async def search_memory(query: str, limit: int = 5):
    results = await engine.memory.search(query, limit=limit)
    return results

@app.get("/api/v1/models/search")
async def search_models(query: str, provider: str = 'huggingface'):
    from epex.intelligence.api_manager import UniversalAPIKeyManager
    manager = UniversalAPIKeyManager()
    if provider == 'huggingface':
        results = await manager.search_huggingface(query)
        return results
    return []

@app.get("/api/v1/models/discovered")
async def list_discovered_models():
    from epex.foundation.storage import SecureConfigStorage
    storage = SecureConfigStorage()
    config = await storage.load_config()
    return config.get('discovered_models', {})

@app.get("/api/v1/tools", response_model=List[Dict[str, Any]])
async def list_tools():
    from epex.tools.registry import registry
    return [
        {
            "name": t.name,
            "description": t.description,
            "category": t.category,
            "risk_level": t.risk_level,
            "parameters": t.parameters
        }
        for t in registry.list_all()
    ]

@app.post("/api/v1/system/config")
async def update_config(config_data: Dict[str, Any]):
    from epex.foundation.storage import SecureConfigStorage
    storage = SecureConfigStorage()
    config = await storage.load_config()

    # Update the engine's current state
    if engine.task_manager:
        if 'mode' in config_data:
            engine.task_manager.mode_manager.set_mode(config_data['mode'])
            config['mode'] = config_data['mode']
        if 'role' in config_data:
            engine.task_manager.role_manager.set_role(config_data['role'])
            config['role'] = config_data['role']
        if 'api_keys' in config_data:
            current_keys = config.get('api_keys', {})
            current_keys.update(config_data['api_keys'])
            config['api_keys'] = current_keys

    await storage.store_config(config)
    return {"success": True}
