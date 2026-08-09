# Prototype Status and Known Limitations

This document outlines the current state of the ATLAS repository. 

**ATLAS is a functional closed-source prototype.** It is highly capable but contains several mock implementations, hardcoded behaviors, and non-production-ready configurations. 

## Implemented and Working

- **VS Code Frontend Fork:** Fully functional customized IDE building on a recent fork. The custom extensions (`atlas-chat` and `copilot`) communicate flawlessly with the backend.
- **Execution Kernel:** The core FastApi server, Event Bus, and DAG orchestration correctly schedule and execute tasks.
- **Browser Capability (via CDP):** Effectively discovers and connects to the user's active local browsers using port 3210.
- **Intent Detection & Routing:** Successfully routes "easy" questions directly to a fast path and delegates complex reasoning to the OpenRouter fallback.
- **Native Plugin Architecture:** Python plugins correctly load dynamically and map to the `CapabilityRegistry`.
- **MCP Protocol:** Supports the basic `tools/list` and `tools/call` implementation, allowing integration with compliant external MCP servers.
- **SSE Streaming:** Real-time event streaming (`/api/stream/{exec_id}`) from backend to frontend works flawlessly.

## Partially Implemented / Experimental

- **Local LLM Execution:** The framework exists to interface with a local Ollama daemon, but the current configuration forces "API LLM Mode" (Cloud API Models strictly enabled) during boot (`_boot_local_llm` in `atlas_kernel.py`).
- **Memory Engine:** Basic semantic indexing exists, but long-term memory retrieval and pruning strategies are rudimentary.
- **Verification Engine:** Deterministic verification rules exist for some capabilities but are not globally comprehensive.
- **Rollback Engine:** A `/api/undo` endpoint exists, but state-rollback logic for complex capabilities (like filesystem or browser changes) is fragile.

## Mocked or Hardcoded

- **Policy Engine Auto-Approval:** The `PermissionGateway` is currently hardcoded to grant `["SAFE", "READ", "WRITE", "BROWSER", "NETWORK", "DANGEROUS"]` automatically without prompting the user, defeating the security model for the sake of development velocity.
- **Fallback Planning:** If the Cloud LLM fails to generate a valid DAG, the `LocalPlanner` falls back to brittle, hardcoded scripts (e.g., automatically launching Gmail if `browser` and "email" are detected).

## NOT Production-Ready

- **Local Binding:** The Execution Kernel and Browser Connector blindly bind to `127.0.0.1` and lack authentication headers. They must not be exposed to a local network.
- **Secrets Management:** The environment variables (`.env`) assume a purely local setup.
- **Browser Harness Execution:** While the CDP proxy is clever, executing arbitrary generated JavaScript in the user's authenticated browser profile carries immense security risks.
- **Test Coverage:** Unit tests exist in `tests/`, but lack comprehensive integration testing across the frontend/backend divide.

## Future Work / Roadmap

1. **Reinforce Security:** Move away from auto-approval. Implement the IDE prompt for "DANGEROUS" operations.
2. **Robust Local LLM:** Transition planning from OpenRouter back to a localized, fine-tuned model (via Ollama/Llama.cpp) to eliminate internet dependency.
3. **Packaging:** Bundle the Python execution kernel into an executable (e.g., PyInstaller) that ships alongside the Electron app to eliminate the need for virtual environments and `pip install`.
4. **Sandboxed Browser Sessions:** Provide an option to launch an isolated, ephemeral browser profile instead of exclusively relying on the user's active session.
