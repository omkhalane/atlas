import asyncio
import uuid
import logging
from typing import Optional, Any
from fastapi import FastAPI, BackgroundTasks, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, HTMLResponse, RedirectResponse
from fastapi import Form
from pydantic import BaseModel
import websockets
import json
import urllib.request
import uvicorn

from runtime.kernel.atlas_kernel import AtlasKernel
from runtime.server.execution_registry import ExecutionRegistry
from runtime.integration.capability_registry import registry as capability_registry
from runtime.integration.plugin_manager import manager as plugin_manager
from runtime.integration.mcp_manager import manager as mcp_manager
from runtime.integration.permission_manager import manager as permission_manager

logger = logging.getLogger("atlas.ipc")

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="ATLAS IPC Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global kernel instance for the IPC server
kernel: Optional[AtlasKernel] = None

class ExecuteGoalRequest(BaseModel):
    goal: str
    exec_id: Optional[str] = None
    conversation_id: Optional[str] = None
    workspace_root: Optional[str] = None

class CancelRequest(BaseModel):
    exec_id: str

class ApproveRequest(BaseModel):
    exec_id: str
    approved: bool

class AuthGrantRequest(BaseModel):
    request_id: str
    code: str

@app.on_event("startup")
async def startup_event():
    global kernel
    logger.info("Initializing ATLAS Kernel for IPC Bridge...")
    kernel = AtlasKernel()
    await kernel.start()
    app.state.kernel = kernel
    
    # Load integrations
    plugin_manager.load_all()
    mcp_manager.load_catalog()

@app.on_event("shutdown")
def shutdown_event():
    if kernel:
        kernel.stop()

@app.post("/execute")
async def execute_goal(req: ExecuteGoalRequest, background_tasks: BackgroundTasks):
    if not kernel:
        raise HTTPException(status_code=500, detail="Kernel not initialized")
    
    exec_id = req.exec_id or str(uuid.uuid4())
    
    # Store workspace context if provided
    # (Phase 8.4 will formally bind this to FilesystemPort)
    if req.workspace_root:
        kernel.state.set(f"{exec_id}_workspace_root", req.workspace_root)

    # Dispatch to background task so the HTTP response returns immediately
    background_tasks.add_task(kernel.execute_goal, req.goal, exec_id, req.conversation_id)
    
    return {"status": "started", "exec_id": exec_id}

@app.post("/cancel")
async def cancel_execution(req: CancelRequest):
    if not kernel:
        raise HTTPException(status_code=500, detail="Kernel not initialized")
    
    success = kernel.execution_registry.cancel(req.exec_id)
    if success:
        return {"status": "cancelled", "exec_id": req.exec_id}
    else:
        raise HTTPException(status_code=404, detail="Execution ID not found or already completed")

@app.post("/approve")
async def approve_tool(req: ApproveRequest):
    if not kernel:
        raise HTTPException(status_code=500, detail="Kernel not initialized")
    
    # We resolve the future stored in state for this execution/tool
    future = kernel.state.get(f"{req.exec_id}_approval_future")
    if future and not future.done():
        future.set_result(req.approved)
        return {"status": "resolved", "approved": req.approved}
    raise HTTPException(status_code=404, detail="No pending approval found")

# --- Integrations API ---

@app.get("/integrations/capabilities")
async def get_capabilities():
    return [cap.dict() for cap in capability_registry.get_all()]

@app.get("/integrations/plugins")
async def get_plugins():
    return [p.dict() for p in plugin_manager.get_all()]

@app.get("/integrations/mcp")
async def get_mcps():
    return {
        "installed": [m.dict() for m in mcp_manager.get_installed()],
        "available": [m.dict() for m in mcp_manager.get_available()]
    }

class InstallMcpRequest(BaseModel):
    mcp_id: str

@app.post("/integrations/mcp/install")
async def install_mcp(req: InstallMcpRequest):
    try:
        mcp_manager.install(req.mcp_id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

class PermissionUpdateRequest(BaseModel):
    provider_id: str
    permission_id: str
    grant: bool

@app.post("/integrations/permissions")
async def update_permission(req: PermissionUpdateRequest):
    if req.grant:
        permission_manager.grant(req.provider_id, req.permission_id)
    else:
        permission_manager.revoke(req.provider_id, req.permission_id)
    return {"status": "success"}

@app.get("/auth/authorize", response_class=HTMLResponse)
async def auth_authorize_get(request_id: str):
    html = f"""
    <html>
      <head><title>Authorize ATLAS Browser</title></head>
      <body style="font-family: sans-serif; padding: 40px; text-align: center;">
        <h1>ATLAS requires browser access</h1>
        <p>The ATLAS agent wants to control your browser via CDP.</p>
        <form method="POST" action="/auth/authorize">
          <input type="hidden" name="request_id" value="{request_id}" />
          <button type="submit" name="action" value="allow" style="padding: 10px 20px; background: #007acc; color: white; border: none; cursor: pointer; border-radius: 4px;">Allow</button>
          <button type="submit" name="action" value="deny" style="padding: 10px 20px; background: #cc0000; color: white; border: none; cursor: pointer; border-radius: 4px; margin-left: 10px;">Deny</button>
        </form>
      </body>
    </html>
    """
    return html

@app.post("/auth/authorize")
async def auth_authorize_post(request_id: str = Form(...), action: str = Form(...)):
    if not kernel:
        raise HTTPException(status_code=500, detail="Kernel not initialized")
    
    if action == "allow":
        # Look up the one-time code for this request_id
        code = None
        for cap, (req_id, expected_code) in kernel.browser_auth._requests.items():
            if req_id == request_id:
                code = expected_code
                break
        
        if code:
            redirect_uri = f"atlas://auth?request_id={request_id}&code={code}"
            return RedirectResponse(url=redirect_uri, status_code=303)
        else:
            return HTMLResponse("<h1>Invalid or expired request</h1>")
    else:
        # Deny capability
        for cap, (req_id, expected_code) in kernel.browser_auth._requests.items():
            if req_id == request_id:
                kernel.browser_auth.revoke(cap)
                break
        return HTMLResponse("<h1>Authorization Denied</h1><p>You can close this tab.</p>")

@app.post("/auth/grant")
async def auth_grant(req: AuthGrantRequest):
    if not kernel:
        raise HTTPException(status_code=500, detail="Kernel not initialized")
    
    success = kernel.browser_auth.validate_and_grant(req.request_id, req.code)
    if success:
        return {"status": "granted"}
    else:
        raise HTTPException(status_code=403, detail="Invalid auth code")

@app.get("/events/{exec_id}")
async def stream_events(exec_id: str, request: Request):
    """
    Server-Sent Events (SSE) endpoint for Phase 8.3.
    VS Code will connect to this to receive progress and reasoning.
    """
    if not kernel:
        raise HTTPException(status_code=500, detail="Kernel not initialized")

    # A queue to hold events for the SSE stream
    queue = asyncio.Queue()

    async def event_handler(event_data: Any):
        # Only yield events matching this execution ID
        event_exec_id = event_data.get("task_id") or event_data.get("exec_id")
        if event_exec_id == exec_id:
            await queue.put(event_data)

    # Subscribe to THOUGHT, message, finish, error, and tool_approval
    kernel.bus.subscribe("THOUGHT", event_handler)
    kernel.bus.subscribe("message", event_handler)
    kernel.bus.subscribe("tool_approval", event_handler)
    kernel.bus.subscribe("cdp_auth_request", event_handler)
    kernel.bus.subscribe("finish", event_handler)
    kernel.bus.subscribe("error", event_handler)

    # Replay historical events to prevent race conditions
    for evt in kernel.bus.history:
        evt_exec_id = evt.get("task_id") or evt.get("exec_id")
        if evt_exec_id == exec_id:
            queue.put_nowait(evt)

    async def event_generator():
        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                
                # Wait for an event
                event_data = await queue.get()
                
                # Format as SSE
                import json
                data_str = json.dumps(event_data)
                yield f"data: {data_str}\n\n"
                
                # Close stream if finished
                if "status" in event_data and event_data.get("status") in ["completed", "error"]:
                    # Give it a moment to flush
                    await asyncio.sleep(0.1)
                    break
        finally:
            kernel.bus.unsubscribe("THOUGHT", event_handler)
            kernel.bus.unsubscribe("message", event_handler)
            kernel.bus.unsubscribe("tool_approval", event_handler)
            kernel.bus.unsubscribe("cdp_auth_request", event_handler)
            kernel.bus.unsubscribe("finish", event_handler)
            kernel.bus.unsubscribe("error", event_handler)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.websocket("/screencast/{exec_id}")
async def websocket_screencast(websocket: WebSocket, exec_id: str):
    await websocket.accept()
    
    # 1. Discover Chrome WebSocket URL
    ws_url = None
    try:
        req = urllib.request.Request("http://127.0.0.1:9222/json/version")
        with urllib.request.urlopen(req, timeout=1) as response:
            data = response.read()
        info = json.loads(data)
        ws_url = info.get("webSocketDebuggerUrl")
    except Exception as e:
        logger.error(f"Failed to discover Chrome WS: {e}")
        
    if not ws_url:
        await websocket.close()
        return

    # 2. Connect to Chrome CDP
    try:
        async with websockets.connect(ws_url) as cdp_ws:
            # Start screencast
            await cdp_ws.send(json.dumps({
                "id": 1,
                "method": "Page.startScreencast",
                "params": {
                    "format": "jpeg",
                    "quality": 80,
                    "everyNthFrame": 1
                }
            }))

            async def forward_cdp_to_ide():
                try:
                    async for msg in cdp_ws:
                        data = json.loads(msg)
                        if data.get("method") == "Page.screencastFrame":
                            # Ack the frame
                            frame_session = data["params"]["sessionId"]
                            ack = {
                                "id": 2,
                                "method": "Page.screencastFrameAck",
                                "params": {"sessionId": frame_session}
                            }
                            await cdp_ws.send(json.dumps(ack))
                            
                            # Forward frame to IDE
                            await websocket.send_json({
                                "type": "screencastFrame",
                                "data": data["params"]["data"],
                                "metadata": data["params"]["metadata"]
                            })
                except Exception as e:
                    logger.error(f"CDP to IDE error: {e}")

            async def forward_ide_to_cdp():
                try:
                    while True:
                        msg = await websocket.receive_json()
                        # Forward Input events to CDP
                        if "method" in msg and msg["method"].startswith("Input."):
                            await cdp_ws.send(json.dumps(msg))
                except WebSocketDisconnect:
                    pass
                except Exception as e:
                    logger.error(f"IDE to CDP error: {e}")

            await asyncio.gather(forward_cdp_to_ide(), forward_ide_to_cdp())
    except Exception as e:
        logger.error(f"WebSocket bridging error: {e}")
        await websocket.close()

def run_server(port: int = 50051):
    uvicorn.run(app, host="127.0.0.1", port=port)

if __name__ == "__main__":
    run_server()
