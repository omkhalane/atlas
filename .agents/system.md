# ATLAS System Architecture Overview

This document serves as a guide for AI agents and developers interacting with the ATLAS codebase. It details the current state of the architecture, highlighting what components are fully functional and which are stubbed out with mock or placeholder implementations for rapid prototyping.

## Fully Implemented Systems (What Works)

The following components are fully functional, tested, and rely on real implementations:

1. **Core Runtime & Capability Engine** (`atlas/core/runtime/`, `atlas/core/capabilities/`)
   - Strict contract validation using Pydantic models.
   - Deterministic execution loop that validates, authorizes, executes, and verifies capabilities.
   - Registration and mapping of capability IDs to their underlying adapter ports.

2. **Transaction Ledger & Event Bus** (`atlas/core/runtime/ledger.py`, `atlas/core/events/`)
   - Fully functional SQLite-backed append-only ledger (`SQLiteLedger`) that durably records system traces.
   - An in-memory Event Bus for publish-subscribe event routing.

3. **Memory Store & Context Engine** (`atlas/core/memory/`, `atlas/core/context/`)
   - `MemoryStore` uses SQLite to persist "Facts" (semantic data) along with provenance and a TTL (Time-To-Live).
   - `RetentionManager` applies automatic expiration to data to prevent infinite growth.
   - `ContextEngine` successfully aggregates memory searches and real-time state into a unified `ContextSnapshot`.

4. **State Collectors** (`atlas/integrations/filesystem/`, `atlas/integrations/git/`)
   - Real, functional indexers that parse directory structures and use Python's `subprocess` to accurately report Git branch, commit, and dirty state.

5. **Cross-Platform OS Adapters** (`atlas/adapters/`)
   - **Filesystem**: Native read/write operations across Linux, macOS, and Windows.
   - **Process**: Native shell execution using `subprocess` with strict timeout controls.
   - **Clipboard**: Functional implementations using `xclip`, `pbcopy`, and `Get-Clipboard`.
   - **Notifications**: Functional alerts using native OS tools.
   - **AdapterFactory**: Dynamically discovers and loads the correct OS adapter based on OS.

6. **Workflow Engine & Plugin Manager** (`atlas/core/workflows/`, `atlas/core/plugins/`)
   - `WorkflowEngine` successfully compiles declarative `Step` structures into executable `Plan`s.
   - `PluginManager` uses `importlib` to dynamically load external plugins.

7. **Sensitivity Filter** (`atlas/core/security/filters.py`)
   - Active Regex-based data redaction that successfully scrubs text strings and nested dictionaries of PII.

8. **Browser Integration** (`atlas/integrations/browser/`)
   - Fully utilizes the native `atlas-browser` engine via subprocess piping, allowing automated script execution inside an auto-launched Chrome instance via Chrome DevTools Protocol.

9. **OCR Engine** (`atlas/integrations/ocr/`)
   - Fully utilizes the heavyweight `atlas-ocr` (PaddleOCR) engine to lazily load and perform genuine ML-driven text extraction on images.

10. **Speech Transcription** (`atlas/integrations/voice/`)
    - Fully utilizes `atlas-voice` (faster-whisper) with CTranslate2 to perform hyper-fast, on-device audio transcription.

11. **Docker Integration** (`atlas/integrations/docker/`)
    - Fully integrates the `atlas-docker` Python SDK to list and manage container status natively via the Docker Engine API.

---

## Mocks and Placeholders (Fake Code / Limitations)

1. **Security Engine / Policy Decisions** (`atlas/core/security/engine.py`)
   - **Status**: MOCK / STUB
   - **Reality**: The infrastructure is there, but it lacks a complex RBAC, cryptographic signature validation, or a user-interactive prompt system.

2. **Memory Semantic Search** (`atlas/core/memory/store.py`)
   - **Status**: STUB
   - **Reality**: Fulfills the interface for "searching" memories, but uses a naive SQLite `LIKE %query%` textual search instead of genuine vector embeddings (e.g., ChromaDB).

---

## Workspace Repository File Tree

```text
/code/ATLAS
├── .agents
│   └── system.md (This architecture document)
├── atlas
│   ├── adapters
│   │   ├── linux       (Linux specific port implementations)
│   │   ├── macos       (macOS specific port implementations)
│   │   ├── windows     (Windows specific port implementations)
│   │   ├── ports       (Abstract base classes for OS ports)
│   │   └── factory.py  (Auto-discovers ports based on sys.platform)
│   ├── core
│   │   ├── capabilities (Executes capability payloads via mapped ports)
│   │   ├── context      (Snapshot engine mapping state variables)
│   │   ├── contracts    (Pydantic base classes for strong typing)
│   │   ├── events       (Internal message bus)
│   │   ├── memory       (SQLite semantic store and TTL retention)
│   │   ├── plugins      (Dynamic importlib plugin loader)
│   │   ├── runtime      (Core loop and SQLite trace ledger)
│   │   ├── security     (PII Regex filters and RBAC engine)
│   │   └── workflows    (Declarative workflow compiler)
│   └── integrations
│       ├── browser      (Contains the integrated atlas-browser execution harness)
│       ├── docker       (Contains the integrated atlas-docker Python SDK)
│       ├── filesystem   (Filesystem state indexers)
│       ├── git          (Git repository state indexers)
│       ├── ocr          (Contains the heavy atlas-ocr PaddleOCR ML bindings)
│       └── voice        (Contains the heavy atlas-voice faster-whisper CTranslate2 bindings)
├── hypermemoryai
│   └── atlas          (The unified Python Virtual Environment housing all heavy ML and API dependencies)
├── demo.py              (End-to-end integration test orchestrating the runtime loop)
├── pyproject.toml
└── requirements.txt
```
