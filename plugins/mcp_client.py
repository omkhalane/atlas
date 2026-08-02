import asyncio
import json
import logging
import uuid
from typing import Dict, Any, List, Optional
from runtime.adapters.ports import AdapterPort
from runtime.contracts import CapabilityRequest, CapabilityResult

logger = logging.getLogger("atlas.mcp")

class MCPClient:
    def __init__(self, command: str, args: List[str], env: Optional[Dict[str, str]] = None):
        self.command = command
        self.args = args
        self.env = env
        self.process = None
        self._request_id = 0
        self._pending_requests: Dict[int, asyncio.Future] = {}
        self._tools_cache = []

    async def start(self):
        self.process = await asyncio.create_subprocess_exec(
            self.command, *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=self.env
        )
        # Start reader tasks
        asyncio.create_task(self._read_stdout())
        asyncio.create_task(self._read_stderr())
        
        # Initialize connection
        await self.send_request("initialize", {
            "clientInfo": {"name": "atlas-mcp", "version": "1.0"},
            "capabilities": {}
        })
        await self.send_notification("initialized", {})
        
        # Fetch tools
        res = await self.send_request("tools/list", {})
        self._tools_cache = res.get("tools", [])

    async def _read_stdout(self):
        while True:
            line = await self.process.stdout.readline()
            if not line:
                break
            try:
                msg = json.loads(line.decode().strip())
                if "id" in msg and msg["id"] in self._pending_requests:
                    fut = self._pending_requests.pop(msg["id"])
                    if not fut.done():
                        if "error" in msg:
                            fut.set_exception(Exception(msg["error"]))
                        else:
                            fut.set_result(msg.get("result", {}))
            except json.JSONDecodeError:
                pass
        
        # Process exited or stdout closed, reject pending
        for req_id, fut in list(self._pending_requests.items()):
            if not fut.done():
                fut.set_exception(Exception("MCP Process exited unexpectedly"))
        self._pending_requests.clear()

    async def _read_stderr(self):
        while True:
            line = await self.process.stderr.readline()
            if not line:
                break
            logger.debug(f"MCP [{self.command}]: {line.decode().strip()}")

    async def send_request(self, method: str, params: dict) -> dict:
        self._request_id += 1
        req_id = self._request_id
        fut = asyncio.get_running_loop().create_future()
        self._pending_requests[req_id] = fut
        
        msg = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params
        }
        self.process.stdin.write((json.dumps(msg) + "\n").encode())
        await self.process.stdin.drain()
        
        try:
            return await asyncio.wait_for(fut, timeout=10.0)
        except asyncio.TimeoutError:
            self._pending_requests.pop(req_id, None)
            raise Exception(f"MCP request {method} timed out")

    async def send_notification(self, method: str, params: dict):
        msg = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        self.process.stdin.write((json.dumps(msg) + "\n").encode())
        await self.process.stdin.drain()

    def get_tools(self) -> List[dict]:
        return self._tools_cache


class MCPAdapter(AdapterPort):
    def __init__(self, mcp_client: MCPClient):
        super().__init__()
        self.mcp_client = mcp_client

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        # Since AdapterPort execute is sync in Atlas V1, we run the coroutine safely
        # Note: In a fully async system this would be async. For now we use asyncio.run
        # but since api.py runs execute_capability asynchronously, we can wrap it.
        tool_name = request.parameters.get("action")
        args = {k: v for k, v in request.parameters.items() if k != "action"}
        
        try:
            # We must run this async inside the sync port if it's called from a thread,
            # or if called from the main event loop, we need a slight adjustment.
            # Assuming execute is run via asyncio.to_thread in most places, or awaited directly.
            # We will use an asyncio loop here.
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We are in a thread running the event loop
                import nest_asyncio
                nest_asyncio.apply()
                
            res = loop.run_until_complete(
                self.mcp_client.send_request("tools/call", {
                    "name": tool_name,
                    "arguments": args
                })
            )
            
            # The MCP result is usually a list of content blocks
            content = res.get("content", [])
            output = "\\n".join([c.get("text", "") for c in content if c.get("type") == "text"])
            
            is_error = res.get("isError", False)
            if is_error:
                return CapabilityResult(success=False, error=output)
                
            return CapabilityResult(success=True, data={"output": output})
            
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
