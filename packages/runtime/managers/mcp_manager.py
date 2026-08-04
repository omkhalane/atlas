import json
import os
import logging
from typing import Dict, Any, TYPE_CHECKING
from plugins.mcp_client import MCPClient

if TYPE_CHECKING:
    from runtime.capabilities.registry import CapabilityRegistry

logger = logging.getLogger("atlas.mcp_manager")

class MCPManager:
    def __init__(self, registry: 'CapabilityRegistry', config_path: str = "/code/ATLAS/.atlas/mcp_servers.json"):
        self.registry = registry
        self.config_path = config_path
        self.servers: Dict[str, MCPClient] = {}

    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            return {"mcpServers": {}}
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse {self.config_path}")
            return {"mcpServers": {}}

    def _save_config(self, config: Dict[str, Any]):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    async def start_all(self):
        """Spawns all configured MCP servers and registers them."""
        config = self._load_config()
        servers_config = config.get("mcpServers", {})
        
        for name, details in servers_config.items():
            if name in self.servers:
                continue # already running
                
            command = details.get("command")
            args = details.get("args", [])
            env_vars = details.get("env", {})
            
            # Merge with system env
            full_env = os.environ.copy()
            full_env.update(env_vars)
            
            try:
                client = MCPClient(command, args, full_env)
                await client.start()
                self.servers[name] = client
                self.registry.register_mcp(name, client)
                logger.info(f"Successfully started MCP server: {name}")
            except Exception as e:
                logger.error(f"Failed to start MCP server {name}: {e}")

    async def add_server(self, name: str, command: str, args: list, env: dict) -> bool:
        """Adds a server to config and starts it immediately."""
        config = self._load_config()
        if "mcpServers" not in config:
            config["mcpServers"] = {}
            
        config["mcpServers"][name] = {
            "command": command,
            "args": args,
            "env": env
        }
        self._save_config(config)
        
        # Start the newly added server
        full_env = os.environ.copy()
        full_env.update(env)
        try:
            client = MCPClient(command, args, full_env)
            await client.start()
            self.servers[name] = client
            self.registry.register_mcp(name, client)
            logger.info(f"Successfully added and started MCP server: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to start new MCP server {name}: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Returns the status of all configured MCP servers."""
        config = self._load_config()
        statuses = []
        
        for name, details in config.get("mcpServers", {}).items():
            running = name in self.servers
            tools = []
            if running:
                tools = [{"name": t["name"], "description": t.get("description", "")} for t in self.servers[name].get_tools()]
            
            statuses.append({
                "name": name,
                "command": details.get("command"),
                "status": "running" if running else "stopped",
                "tools": tools
            })
            
        return {"servers": statuses}
