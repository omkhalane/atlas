import os
import json
import logging
import asyncio
from typing import Optional, Dict, List, Any
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
    format='%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("atlas.main")

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

    # Fast path: detect simple intents synchronously so the response
    # is available before the client opens the SSE stream
    conv_id = req.conversation_id or exec_id
    conv_context = kernel.conversations.get_context(conv_id, limit=4)
    intent_result = kernel.intent_detector.detect(req.goal, conv_context)

    direct_answer = intent_result.get("direct_answer")
    if direct_answer and intent_result.get("difficulty") == "easy":
        # Store in conversation and return immediately — no background task needed
        kernel.conversations.add_user_message(conv_id, req.goal)
        kernel.conversations.add_assistant_message(conv_id, direct_answer)
        return {
            "exec_id": exec_id,
            "direct_answer": direct_answer,
            "done": True
        }

    background_tasks.add_task(kernel.execute_goal, req.goal, exec_id, req.conversation_id)
    return {"exec_id": exec_id, "direct_answer": None, "done": False}

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

@app.get("/api/llm/status")
async def get_llm_status():
    """Returns the current local LLM detection status."""
    llm = kernel.local_llm
    return {
        "ollama_available": llm.ollama_available,
        "selected_model": llm.selected_model,
        "embed_model": llm.embed_model,
        "model_source": llm.model_source,
    }

class ProfileRequest(BaseModel):
    id: str
    name: str
    provider_type: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    organization: Optional[str] = None
    default_model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096
    context_length: int = 128000
    timeout_seconds: int = 60
    max_retries: int = 3
    enable_streaming: bool = True
    enable_prompt_cache: bool = True
    enable_tool_calling: bool = True
    is_default: bool = False

@app.get("/api/llm/providers")
async def list_providers():
    from runtime.llm.contracts import ProviderProfile
    profs = kernel.ai_runtime.llm.providers.list_profiles()
    return {"profiles": [p.__dict__ for p in profs]}

@app.post("/api/llm/providers")
async def add_provider(req: ProfileRequest):
    from runtime.llm.contracts import ProviderProfile
    prof = ProviderProfile(**req.model_dump())
    kernel.ai_runtime.llm.providers.add_profile(prof)
    return {"status": "success", "profile": prof.__dict__}

@app.post("/api/llm/providers/{provider_id}/test")
async def test_provider_connection(provider_id: str):
    res = await kernel.ai_runtime.health.check_provider_health(provider_id)
    return res

@app.post("/api/llm/providers/default")
async def set_default_provider(req: dict):
    pid = req.get("profile_id")
    if pid:
        kernel.ai_runtime.llm.providers.set_default_profile(pid)
        return {"status": "success", "default_profile_id": pid}
    return JSONResponse(status_code=400, content={"error": "profile_id required"})

@app.get("/api/llm/models")
async def list_models():
    providers = kernel.ai_runtime.llm.providers.list_profiles()
    all_models = {}
    for p in providers:
        m_list = kernel.ai_runtime.llm.models.get_models_for_provider(p.id, p.provider_type)
        all_models[p.id] = m_list
    return {"models": all_models}

@app.get("/api/ai/metrics")
async def get_ai_metrics():
    return kernel.ai_runtime.observability.get_metrics_summary()

@app.get("/api/ai/health")
async def get_ai_health():
    return kernel.ai_runtime.health.get_all_health()

@app.post("/api/llm/reset")
async def reset_llm_detection():
    """Clears the cached LLM config — triggers a full re-scan on next boot."""
    kernel.local_llm.reset_config()
    return {"status": "success", "message": "LLM config cleared. Re-scan will run on next Atlas start."}

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

    # Replay any events already published for this exec_id (fixes race condition
    # where task completes before SSE stream is opened by the client)
    replayed_finish = False
    for past_event in kernel.bus.history:
        if past_event.get("task_id") == exec_id:
            await q.put(past_event)
            if past_event.get("type") in ["finish", "error"]:
                replayed_finish = True

    async def handler(event: dict):
        if event.get("task_id") == exec_id:
            await q.put(event)

    # Only subscribe for live events if task isn't already done
    if not replayed_finish:
        kernel.bus.subscribe("*", handler)
    
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            try:
                msg = await asyncio.wait_for(q.get(), timeout=30.0)
            except asyncio.TimeoutError:
                break

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

import httpx
@app.get("/api/browser/cdp-version")
async def get_browser_cdp_version():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://127.0.0.1:9222/json/version")
            return r.json()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

from fastapi import WebSocket, WebSocketDisconnect
import websockets

@app.websocket("/api/browser/cdp-proxy")
async def cdp_proxy(websocket: WebSocket):
    await websocket.accept()
    # First message from client must be the target ws url
    target_url = await websocket.receive_text()
    try:
        async with websockets.connect(target_url) as remote_ws:
            async def forward_to_remote():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await remote_ws.send(data)
                except Exception:
                    pass

            async def forward_to_client():
                try:
                    while True:
                        data = await remote_ws.recv()
                        await websocket.send_text(data)
                except Exception:
                    pass

            import asyncio
            await asyncio.gather(
                forward_to_remote(),
                forward_to_client(),
                return_exceptions=True
            )
    except Exception as e:
        await websocket.send_text(f'{{"error": "{str(e)}"}}')
    finally:
        try:
            await websocket.close()
        except:
            pass
