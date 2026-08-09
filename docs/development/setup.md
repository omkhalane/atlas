# ATLAS Development Setup

This guide provides instructions for setting up the ATLAS prototype for local development.

## Prerequisites

- **OS:** Linux (Ubuntu/Debian recommended for native Electron support) or macOS.
- **Node.js:** v18.x or v20.x
- **Python:** 3.10+
- **Package Managers:** `npm` (for VS Code frontend) and `pip` (for Python backend).
- **Browser:** Google Chrome, Brave, Chromium, or Microsoft Edge installed locally.

## 1. Clone the Repository

```bash
git clone <atlas-repo-url>
cd ATLAS
```

## 2. Install Python Backend Dependencies

The execution kernel and agent run on Python. Install the required dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Configure the Environment

Copy the `.env.example` to `.env` and fill in the necessary keys.

```bash
cp .env.example .env
```

**Required Environment Variables:**
- `OPENROUTER_API_KEY`: Required for Cloud LLM planning capabilities.

## 4. Install VS Code Frontend Dependencies

The frontend is a fork of VS Code. Installation requires standard VS Code build tools.

```bash
cd apps/vscode
npm install
```

> [!WARNING]
> Compiling the VS Code fork requires native build tools (e.g., `build-essential` on Ubuntu, or Xcode Command Line Tools on macOS) because it builds native Node modules (like `node-pty`).

## 5. Build the Frontend

Compile the client and the custom ATLAS extensions (`atlas-chat` and `copilot`).

```bash
cd apps/vscode
npm run build-fast
```

## 6. Running ATLAS

ATLAS is launched using a unified run script that starts the Python backend services and the Electron frontend simultaneously.

From the repository root:

```bash
./scripts/run.sh
```

**What this script does:**
1. Starts the `connector_server.py` (Browser CDP Proxy) on port 3210.
2. Starts the `ipc_server.py` (Execution Kernel API).
3. Launches the VS Code Electron application (`./scripts/code.sh --no-sandbox`).

> [!TIP]
> If you encounter issues where the frontend launches but the agent does not respond, verify that no stray Python processes are blocking ports 3210 or 8000. Use `killall python3` if necessary.

## 7. Testing

Unit tests are located in the `tests/` directory.

To run the Python backend tests:
```bash
pytest tests/
```

To run the VS Code frontend tests:
```bash
cd apps/vscode
npm run test
```

## 8. Debugging

### Backend Debugging
Logs for the Python execution kernel are output to stdout when running `./scripts/run.sh`. The Browser Connector Server logs its connection status to `/tmp/atlas_proxy.log`.

### Frontend Debugging
Use the developer tools within the ATLAS IDE (`Help -> Toggle Developer Tools`) to inspect UI issues in the `atlas-chat` extension.
