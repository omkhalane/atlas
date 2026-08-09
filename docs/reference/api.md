# ATLAS API Reference

The ATLAS Execution Kernel exposes a FastAPI HTTP and WebSocket server running on `localhost:8000`. This API acts as the bridge between the IDE frontend and the AI backend.

## Execution and Intent

### `POST /api/execute`
Starts a new execution goal.
- **Payload:** `{"goal": "string", "conversation_id": "string", "folder_id": "string"}`
- **Behavior:** Triggers the `IntentDetector`. If the intent is classified as `easy`, it returns a direct answer synchronously. Otherwise, it dispatches the goal to the execution background task and returns `done: False`.

### `GET /api/stream/{exec_id}`
Server-Sent Events (SSE) endpoint to stream real-time agent execution events.
- **Events:** Publishes `THOUGHT`, `message`, `error`, and `finish` events to power the real-time UI in the IDE.

### `GET /api/stream/global`
Global SSE endpoint for system-wide notifications.

### `POST /api/approve/{exec_id}`
Currently a no-op endpoint kept for backward compatibility. Auto-approval is globally active in the prototype.

## LLM Configuration

- **`GET /api/llm/status`**: Returns the current local LLM detection status (e.g., if Ollama is running).
- **`GET /api/llm/providers`**: Lists all configured LLM providers.
- **`POST /api/llm/providers`**: Adds a new LLM provider profile.
- **`POST /api/llm/providers/{provider_id}/test`**: Tests the connection to a specific provider.
- **`POST /api/llm/providers/default`**: Sets the default provider profile.
- **`GET /api/llm/models`**: Lists available models for all configured providers.
- **`POST /api/llm/reset`**: Clears cached LLM configs to force a re-scan.

## Conversations and History

- **`GET /api/conversations`**: Lists all active conversations.
- **`GET /api/conversations/{conversation_id}`**: Retrieves the message history and artifacts for a specific conversation.
- **`GET /api/history`**: Retrieves execution task history (up to the requested `limit`).
- **`POST /api/undo/{exec_id}`**: Attempts to rollback a completed task using the `RollbackEngine`.

## Plugins and MCP

- **`GET /api/mcp`**: Lists status of all configured MCP servers.
- **`POST /api/mcp`**: Dynamically adds and starts a new MCP server.
- **`GET /api/plugins`**: Lists all loaded native Python plugins.
- **`POST /api/plugins/install`**: Installs a new plugin from a provided URL via the `MarketplaceManager`.

## Browser Automation

- **`GET /api/browser/cdp-version`**: Retrieves the CDP version information for the local system browser. Proxied through the Connector Server (`:3210`).
- **`WS /api/browser/cdp-proxy`**: A WebSocket endpoint that acts as a bidirectional proxy between the ATLAS IDE/Kernel and the local system browser's DevTools WebSocket.

## Utility

- **`GET /api/ai/metrics`**: Returns observability metrics for the AI runtime.
- **`GET /api/ai/health`**: Returns health checks for the AI runtime components.
- **`POST /api/upload`**: Handles file uploads to the runtime.
- **`GET /api/file?path={path}`**: Retrieves a file from the local filesystem (used for rendering artifacts).
- **`GET /api/browser_screenshot`**: Captures and returns a screenshot of the primary monitor using `mss` and `opencv`.

---
**Implementation Reference:**
- `packages/runtime/main.py`
