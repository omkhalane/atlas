# System Context Diagrams

## Purpose

This document collects canonical diagrams used by the Atlas handbook.

## Overview

These diagrams describe Atlas at system, runtime, and adapter levels.

## Motivation

Shared diagrams reduce ambiguity across architecture and implementation phase documents.

## Architecture

```mermaid
flowchart TB
    User --> Atlas
    Atlas --> OperatingSystem
    Atlas --> Applications
    Atlas --> LocalStorage
    Atlas --> OptionalProviders
```

## Design Decisions

Diagrams use Mermaid so they remain version-controlled and reviewable.

## Component Diagram

```mermaid
flowchart TB
    subgraph Atlas
        Core
        Capabilities
        Adapters
        Plugins
    end
    Core --> Capabilities
    Capabilities --> Adapters
    Plugins --> Capabilities
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant A as Atlas
    participant OS as OS
    U->>A: Intent
    A->>OS: Authorized capability
    OS-->>A: Observed result
    A-->>U: Explanation
```

## Folder Structure

Diagram source belongs under `docs/diagrams`.

## Public Interfaces

Diagrams communicate architecture contracts to contributors.

## Implementation Strategy

Update diagrams in the same pull request as architecture changes.

## Testing

Markdown rendering should be checked during documentation CI.

## Security

Do not include secrets, real user paths, or private environment details in diagrams.

## Future Improvements

Add generated SVG artifacts for release documentation.

## References

- [Architecture](/code/ATLAS/ARCHITECTURE.md)
