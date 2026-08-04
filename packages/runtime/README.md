# @atlas/runtime

Core execution engine and AI agent runtime for the Atlas platform.

## Overview

`@atlas/runtime` powers task execution, LLM routing, capability discovery, state management, and policy enforcement across Atlas applications (Desktop, VS Code integration, CLI).

## Key Components

- **Kernel**: Core event loop, execution supervisor, and state persistence.
- **LLM Router**: Multi-model intelligence routing and tool call dispatching.
- **Capabilities Registry**: Dynamic action and tool registration.
- **Policy & Safety**: Approval rules, permissions, and sandbox enforcement.

## Usage

```python
from atlas.runtime.kernel import AtlasKernel

kernel = AtlasKernel()
kernel.initialize()
```
