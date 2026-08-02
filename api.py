import os
import time
import uuid
import asyncio
import json
import logging
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from atlas.core.runtime.openrouter import OpenRouterClient
from atlas.integrations.media.port import MediaPort
from atlas.integrations.filesystem.port import FilesystemPort
from atlas.integrations.command.port import CommandPort
from atlas.integrations.browser.port import BrowserPort
from atlas.core.contracts import CapabilityRequest

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] ATLAS ENGINE: %(message)s'
)
logger = logging.getLogger("atlas")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = OpenRouterClient()
media_port = MediaPort()
fs_port = FilesystemPort()
cmd_port = CommandPort()
browser_port = BrowserPort()

executions = {}
event_queues = {}
approval_events = {}

class ExecuteRequest(BaseModel):
    goal: str

@app.post("/api/execute")
async def start_execution(req: ExecuteRequest, background_tasks: BackgroundTasks):
    exec_id = str(uuid.uuid4())
    event_queues[exec_id] = asyncio.Queue()
    approval_events[exec_id] = asyncio.Event()
    
    background_tasks.add_task(run_atlas_engine, exec_id, req.goal)
    return {"exec_id": exec_id}

@app.get("/api/stream/{exec_id}")
async def stream_execution(exec_id: str, request: Request):
    async def event_generator():
        q = event_queues.get(exec_id)
        if not q:
            yield {"event": "error", "data": "Execution not found"}
            return
            
        while True:
            if await request.is_disconnected():
                break
            
            msg = await q.get()
            yield {"data": msg}
            if '"Execution Complete"' in msg or '"status": "failed"' in msg or '"status": "completed"' in msg:
                break
                
    return EventSourceResponse(event_generator())

@app.post("/api/approve/{exec_id}")
async def approve_action(exec_id: str):
    if exec_id in approval_events:
        executions[exec_id]["approved"] = True
        approval_events[exec_id].set()
        return {"status": "approved"}
    return {"status": "error"}

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

async def execute_capability(q, exec_id, cid, params, artifacts):
    req = CapabilityRequest(id=cid, parameters=params)
    
    if cid == "media":
        res = media_port.execute(req)
        if res.data and "video_path" in res.data:
            artifacts.append(res.data["video_path"])
    elif cid == "command":
        res = cmd_port.execute(req)
    elif cid == "browser":
        res = browser_port.execute(req)
    elif cid == "filesystem":
        res = fs_port.execute(req)
        if getattr(res, 'requires_human', False):
            await q.put(json.dumps({
                "type": "security_halt",
                "requires_human": True, 
                "detail": res.error,
                "data": res.data
            }))
            await approval_events[exec_id].wait()
            if executions[exec_id]["approved"]:
                await q.put(json.dumps({"type": "thought", "content": "Action Approved by User"}))
                req.parameters["approved"] = True
                res = fs_port.execute(req)
            else:
                raise Exception("Action Denied by User")
        if getattr(res, 'success', False):
            action_type = params.get("action")
            if action_type in ["write_file", "append_file"] and "path" in res.data:
                await q.put(json.dumps({
                    "type": "file_written",
                    "path": res.data["path"],
                    "name": os.path.basename(res.data["path"])
                }))
    else:
        raise ValueError(f"Unknown action: {cid}")
        
    return res

async def run_atlas_engine(exec_id: str, goal: str):
    logger.info(f"Starting Execution ID: {exec_id} | Goal: {goal}")
    q = event_queues[exec_id]
    executions[exec_id] = {"approved": False}
    
    available = [
        {"id": "media", "actions": ["start_recording", "stop_recording", "take_screenshot"]},
        {"id": "filesystem", "actions": ["write_file", "append_file", "delete_file", "list_files"], "params": ["path", "content"]},
        {"id": "command", "actions": ["run"], "params": ["command"], "description": "Execute a bash command in the workspace."},
        {"id": "browser", "actions": ["run"], "params": ["script"], "description": "Control the browser. Pass Python script controlling browser-harness."}
    ]
    
    try:
        start_time = time.time()
        artifacts = []
        
        await q.put(json.dumps({"type": "thought", "content": "Classifying Intent..."}))
        intent_data = await asyncio.to_thread(llm.classify_intent, goal)
        intent = intent_data.get("intent", "complex")
        logger.info(f"Classified intent as: {intent}")
        await q.put(json.dumps({"type": "thought", "content": f"Intent Classified: {intent.upper()}"}))

        if intent == "simple":
            step = await asyncio.to_thread(llm.get_simple_step, goal, available)
            action = step.get("action")
            params = step.get("parameters", {})
            if isinstance(params, str):
                params = {"action": "run", "command": params} if action == "command" else {"input": params}
            if action and action != "finish":
                await q.put(json.dumps({"type": "action", "action": action, "parameters": params}))
                res = await execute_capability(q, exec_id, action, params, artifacts)
                if getattr(res, 'success', False):
                    await q.put(json.dumps({"type": "observation", "content": json.dumps(res.data)}))
                else:
                    err = getattr(res, 'error', "Unknown error")
                    await q.put(json.dumps({"type": "observation", "content": f"Error: {err}"}))
                    
        elif intent == "moderate":
            steps = await asyncio.to_thread(llm.get_moderate_steps, goal, available)
            for i, step in enumerate(steps):
                action = step.get("action")
                params = step.get("parameters", {})
                if isinstance(params, str):
                    params = {"action": "run", "command": params} if action == "command" else {"input": params}
                if action and action != "finish":
                    await q.put(json.dumps({"type": "thought", "content": f"Executing moderate step {i+1}..."}))
                    await q.put(json.dumps({"type": "action", "action": action, "parameters": params}))
                    res = await execute_capability(q, exec_id, action, params, artifacts)
                    if getattr(res, 'success', False):
                        await q.put(json.dumps({"type": "observation", "content": json.dumps(res.data)}))
                    else:
                        err = getattr(res, 'error', "Unknown error")
                        await q.put(json.dumps({"type": "observation", "content": f"Error: {err}"}))
                        break # Stop sequential execution on error
                        
        else:
            # Complex (Planner)
            logger.info("Generating task plan...")
            await q.put(json.dumps({"type": "thought", "content": "Generating Execution Graph..."}))
            tasks = await asyncio.to_thread(llm.plan_task, goal)
            # Reformat to simple strings for the UI checkmarks
            ui_tasks = [t.get("input", "Task") for t in tasks] if tasks else ["Execute task"]
            await q.put(json.dumps({"type": "plan", "tasks": ui_tasks}))
            
            history = [{"role": "user", "content": f"Goal: {goal}"}]
            
            while True:
                step_result = await asyncio.to_thread(llm.step, history, available, ui_tasks)
                
                thought = step_result.get("thought", "")
                action = step_result.get("action", "")
                params = step_result.get("parameters", {})
                current_task_idx = step_result.get("current_task_idx", -1)
                
                if isinstance(params, str):
                    if action == "command":
                        params = {"action": "run", "command": params}
                    else:
                        params = {"input": params}
                
                logger.info(f"Thought: {thought}")
                await q.put(json.dumps({"type": "thought", "content": thought, "current_task_idx": current_task_idx}))
                
                if action == "finish":
                    break
                    
                logger.info(f"Action: {action} with {params}")
                await q.put(json.dumps({"type": "action", "action": action, "parameters": params}))
                
                res = await execute_capability(q, exec_id, action, params, artifacts)
                
                if not getattr(res, 'success', False):
                    err = getattr(res, 'error', None)
                    if not err and hasattr(res, 'data') and res.data:
                        err = res.data.get("output", "Unknown error")
                    err = err or "Unknown error"
                    logger.error(f"Action Failed: {err}")
                    history.append({"role": "assistant", "content": json.dumps(step_result)})
                    history.append({"role": "user", "content": f"Action failed: {err}. Proceed with recovery."})
                    await q.put(json.dumps({"type": "observation", "content": f"Error: {err}"}))
                else:
                    logger.info("Action Succeeded.")
                    history.append({"role": "assistant", "content": json.dumps(step_result)})
                    history.append({"role": "user", "content": f"Observation: {json.dumps(res.data)}"})
                    await q.put(json.dumps({"type": "observation", "content": json.dumps(res.data)}))

        plan = {
            "status": "completed",
            "duration_ms": int((time.time() - start_time) * 1000),
            "artifacts": artifacts
        }
        await q.put(json.dumps({"type": "finish", "result": plan}))
        
    except Exception as e:
        logger.error(f"Execution Failed: {str(e)}")
        await q.put(json.dumps({"type": "error", "error": str(e)}))
