import os
import json
import logging
import asyncio
from fastapi import FastAPI, BackgroundTasks, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager

from runtime.kernel.atlas_kernel import AtlasKernel
from plugins.mcp_client import MCPClient
from runtime.managers.mcp_manager import MCPManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] ATLAS ENGINE: %(message)s'
)
logger = logging.getLogger("atlas")

# Global kernel instance
kernel = AtlasKernel()
mcp_manager = MCPManager(kernel.registry)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Kernel
    await kernel.start()
    
    # Load MCP plugins
    await mcp_manager.start_all()
        
    yield
    
    # Shutdown
    kernel.stop()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExecuteRequest(BaseModel):
    goal: str
    conversation_id: str = None
    folder_id: str = None

@app.post("/api/execute")
async def start_execution(req: ExecuteRequest, background_tasks: BackgroundTasks):
    import uuid
    exec_id = req.conversation_id if req.conversation_id else str(uuid.uuid4())
    background_tasks.add_task(kernel.execute_goal, req.goal, exec_id, req.conversation_id)
    return {"exec_id": exec_id}

@app.get("/api/conversations")
async def list_conversations():
    return {"conversations": kernel.conversations.list_conversations()}

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    conv = kernel.conversations.get(conversation_id)
    if not conv:
        return JSONResponse(status_code=404, content={"error": "Conversation not found"})
    return {
        "id": conv.id,
        "messages": [
            {"role": m.role, "content": m.content, "timestamp": m.timestamp}
            for m in conv.messages
        ],
        "artifacts": conv.artifacts,
        "created_at": conv.created_at,
        "updated_at": conv.updated_at
    }

@app.get("/api/stream/global")
async def stream_global(request: Request):
    q = asyncio.Queue()
    
    async def handler(event: dict):
        if event.get("type") == "NOTIFICATION":
            await q.put(event)
            
    kernel.bus.subscribe("NOTIFICATION", handler)
    
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            msg = await q.get()
            yield {"data": json.dumps(msg)}
            
    return EventSourceResponse(event_generator())

@app.get("/api/stream/{exec_id}")
async def stream_execution(exec_id: str, request: Request):
    q = asyncio.Queue()
    
    async def handler(event: dict):
        if event.get("task_id") == exec_id:
            await q.put(event)
            
    # Subscribe to ALL events. In a real production system, we'd unsubscribe on disconnect.
    kernel.bus.subscribe("*", handler)
    
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            
            msg = await q.get()
            # Clean up internal bus data before sending to UI if necessary
            yield {"data": json.dumps(msg)}
            
            if msg.get("type") in ["finish", "error"]:
                break
                
    return EventSourceResponse(event_generator())

@app.post("/api/approve/{exec_id}")
async def approve_action(exec_id: str):
    # Auto-approve is enabled in PolicyEngine, so this endpoint is currently a no-op 
    # but left for backward compatibility.
    return {"status": "approved"}

from runtime.managers.transfer import TransferManager
from plugins.marketplace import MarketplaceManager
from pydantic import BaseModel

transfer_manager = TransferManager(kernel.bus)
marketplace_manager = MarketplaceManager()

class PluginInstallRequest(BaseModel):
    url: str

class MCPAddRequest(BaseModel):
    name: str
    command: str
    args: list = []
    env: dict = {}

@app.get("/api/mcp")
async def list_mcp_servers():
    return mcp_manager.get_status()

@app.post("/api/mcp")
async def add_mcp_server(req: MCPAddRequest):
    success = await mcp_manager.add_server(req.name, req.command, req.args, req.env)
    if success:
        return {"status": "success", "message": f"Added and started MCP server {req.name}"}
    return JSONResponse(status_code=400, content={"error": f"Failed to start MCP server {req.name}"})

@app.get("/api/plugins")
async def list_plugins():
    plugins_data = []
    for pid, p in kernel.plugins.plugins.items():
        manifest = p.get_manifest()
        plugins_data.append({
            "id": manifest.id,
            "name": manifest.name,
            "version": manifest.version,
            "description": manifest.description
        })
    return {"plugins": plugins_data}

@app.post("/api/plugins/install")
async def install_plugin(req: PluginInstallRequest):
    path = marketplace_manager.install_from_url(req.url)
    if not path:
        return JSONResponse(status_code=400, content={"error": "Failed to install plugin from URL"})
        
    # Reload plugins
    kernel.plugins.auto_load_plugins()
    return {"status": "success", "message": "Plugin installed successfully."}

@app.post("/api/upload")
async def upload_file(file: UploadFile):
    content = await file.read()
    path = await transfer_manager.process_upload(file.filename, content)
    if path:
        return {"status": "success", "path": path}
    return JSONResponse(status_code=500, content={"error": "Failed to upload"})

@app.get("/api/history")
async def get_history(limit: int = 50):
    tasks = kernel.history.load_history(limit)
    return {"history": [json.loads(t.model_dump_json()) for t in tasks]}

@app.post("/api/undo/{exec_id}")
async def undo_task(exec_id: str):
    success = kernel.rollback.undo(exec_id)
    if success:
        return {"status": "success", "message": f"Successfully rolled back task {exec_id}"}
    else:
        return JSONResponse(status_code=400, content={"error": "Failed to rollback or no rollback data found"})

@app.get("/api/browser_screenshot")
async def get_browser_screenshot():
    try:
        import mss
        import io
        from fastapi.responses import Response
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            import cv2
            import numpy as np
            img = np.array(sct_img)
            _, buffer = cv2.imencode('.jpg', img)
            return Response(content=buffer.tobytes(), media_type="image/jpeg")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/file")
async def get_file(path: str):
    try:
        if os.path.exists(path) and os.path.isfile(path):
            from fastapi.responses import FileResponse
            return FileResponse(path)
        return JSONResponse(status_code=404, content={"error": "File not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
