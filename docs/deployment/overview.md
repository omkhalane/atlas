# ATLAS Deployment Overview

This document outlines the deployment strategy for ATLAS. Because ATLAS is designed as a hybrid AI IDE containing both an Electron client and a Python backend, "deployment" generally refers to local installation or cloud workstation provisioning.

## 1. Local / Desktop Deployment (Prototype)

In its current prototype state, ATLAS is deployed and run locally on the developer's machine.

### Packaging
- The VS Code frontend can be packaged into standard Electron binaries (e.g., `.deb`, `.app`, `.exe`) using the standard VS Code build tools (`gulp vscode-linux-x64`, etc.).
- The Python runtime currently operates as an unpackaged local service running out of a virtual environment.

### Startup
The desktop deployment relies on a unified script (`scripts/run.sh`) to start both the Python backend and the Electron frontend.

## 2. Remote Backend Deployment (Future Architecture)

While currently running entirely on localhost, the architectural separation between the VS Code frontend (`apps/vscode`) and the Execution Kernel (`packages/runtime/main.py`) allows for future remote deployments.

In a remote deployment model:
1. The `ipc_server` (FastAPI) would run on a powerful cloud instance (e.g., AWS EC2, GCP Compute Engine).
2. The user would run only the ATLAS VS Code frontend locally.
3. The IDE would connect to the remote execution kernel via WebSocket/SSE over HTTPS.

> [!WARNING]
> Remote deployment is NOT fully supported in the current prototype. The Browser Connector (`connector_server.py`) expects the execution kernel to run on the same physical machine as the user's browser (binding to `127.0.0.1`). Moving the kernel to the cloud would require a secure, authenticated local tunnel to proxy CDP commands back to the user's machine.

## 3. Required Services & Infrastructure

For the current local deployment:
- **Port 8000:** Required for the FastAPI Execution Kernel.
- **Port 3210:** Required for the Browser CDP Proxy.
- **SQLite (Local):** Embedded database for Memory and State persistence (no external database server required).
- **Ollama (Optional):** If a local model is preferred for planning and intent detection, an Ollama daemon must be running locally.
- **OpenRouter (External):** Requires outbound internet access for cloud LLM reasoning.

## 4. CI/CD

There is no complex automated deployment pipeline currently implemented beyond GitHub Actions for testing. Local development relies heavily on `npm run build-fast` for the frontend.
