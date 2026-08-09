# ATLAS Plugins and MCP Architecture

ATLAS supports two primary mechanisms for extending the capability set of the AI execution kernel: **Native Plugins** and **Model Context Protocol (MCP) Servers**.

Both mechanisms eventually surface capabilities into the `CapabilityRegistry` as `AdapterPort` instances, ensuring a unified execution interface for the planner and policy engine.

## 1. Model Context Protocol (MCP)

ATLAS implements an MCP Client (`plugins/mcp_client.py`) that allows the execution kernel to interface with external tools over standard input/output streams using JSON-RPC.

### Discovery and Configuration
- MCP Servers are configured via `mcp/registry/mcp_servers.json`.
- The `MCPManager` handles reading this registry and booting the requested servers.
- The `MCPClient` launches the target process and manages bidirectional communication over `stdin`/`stdout`.

### Lifecycle and Execution
1. **Initialization:** The client sends an `initialize` request to the MCP server.
2. **Tool Discovery:** The client queries `tools/list` to retrieve the available tools.
3. **Registration:** The `MCPManager` maps the discovered tools into the `CapabilityRegistry`.
4. **Execution:** When the runtime invokes an MCP capability, the `MCPAdapter` translates the `CapabilityRequest` into a `tools/call` RPC message.

```mermaid
flowchart LR
    Kernel[Execution Kernel] --> Registry[Capability Registry]
    Registry --> Adapter[MCP Adapter]
    Adapter -- "JSON-RPC (tools/call)" --> Process[MCP Server Process]
    Process -- "Result" --> Adapter
```

## 2. Native Plugins

Native plugins are Python modules that run directly within the ATLAS kernel process.

### Discovery and Loading
- Plugins are stored in `.atlas/plugins/` (by default) or installed via URL using the `MarketplaceManager`.
- The `PluginManager` uses `importlib` to dynamically load `*.py` files.
- It scans the loaded module for classes that inherit from `plugins.base.Plugin`.

### Registration
- A plugin instance exposes a manifest (`get_manifest()`) and a dictionary of adapters (`get_adapters()`).
- The `PluginManager` maps these adapters directly into the `CapabilityRegistry`.

### Security and Isolation
- **Native Plugins:** Because they run in the same Python process as the kernel, they have access to the full Python environment. They are inherently trusted and are not sandboxed.
- **MCP Servers:** MCP servers run in separate processes and communicate over standard streams. This provides a stronger isolation boundary, although security still depends on the permissions granted to the MCP server process.

---
**Implementation References:**
- `plugins/mcp_client.py`
- `plugins/manager.py`
- `runtime/managers/mcp_manager.py`
