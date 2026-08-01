# Runtime Architecture

## Purpose

The runtime is Atlas's execution authority. It converts approved plans into durable, logged, verified capability executions.

## Overview

The runtime owns retries, recovery, permissions, logging, transactions, scheduling handoff, and verification. It receives a typed plan from the planner, validates the plan, asks the security engine for authorization, executes capability steps, records events, and verifies final state.

## Motivation

The planner is probabilistic and should not be trusted with direct execution. The runtime provides deterministic control around an uncertain planner by enforcing contracts and checking observed state.

## Architecture

```mermaid
flowchart TB
    Plan[Plan] --> Validator[Plan Validator]
    Validator --> Permission[Permission Gate]
    Permission --> Transaction[Execution Transaction]
    Transaction --> CapabilityRunner[Capability Runner]
    CapabilityRunner --> Verifier[Outcome Verifier]
    Verifier --> Ledger[Execution Ledger]
    Ledger --> Result[Capability Result]
```

## Design Decisions

Runtime execution is transaction-oriented. A transaction records requested effects, applied effects, compensating actions, logs, and verification status. Atlas should support idempotency keys for repeated requests and resumable execution for interrupted workflows.

## Component Diagram

```mermaid
flowchart LR
    Runtime --> PlanValidator
    Runtime --> PermissionGate
    Runtime --> TransactionManager
    Runtime --> CapabilityRunner
    Runtime --> RecoveryManager
    Runtime --> VerificationEngine
    Runtime --> AuditLogger
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant P as Planner
    participant R as Runtime
    participant S as Security Engine
    participant C as Capability
    participant V as Verifier

    P->>R: Submit plan
    R->>R: Validate schema and dependency graph
    R->>S: Authorize requested effects
    S-->>R: Decision
    R->>C: Execute step with transaction context
    C-->>R: Step result
    R->>V: Verify observed outcome
    V-->>R: Verified or failed
```

## Folder Structure

```text
atlas/core/runtime/
  engine.py
  transactions.py
  recovery.py
  verification.py
  idempotency.py
  errors.py
```

## Public Interfaces

`Runtime.execute(plan: Plan) -> ExecutionResult` is the main interface. Supporting types are `ExecutionTransaction`, `StepResult`, `VerificationStatus`, `RecoveryAction`, and `RuntimeErrorCode`.

## Implementation Strategy

Implement the runtime with an in-memory ledger first, then add durable storage. Keep capability invocation behind an interface so tests can inject fake capabilities and adapters.

## Testing

Tests must cover successful execution, invalid plans, denied permissions, partial failure, retry exhaustion, idempotent replay, rollback, and verification failure.

## Security

The runtime must fail closed. If authorization, verification, policy loading, or audit logging fails, execution stops.

## Future Improvements

Add distributed execution, durable queues, crash recovery, and policy simulation once the local runtime is stable.

## References

- [Capability Engine](/code/ATLAS/docs/architecture/capability-engine.md)
- [Security](/code/ATLAS/docs/architecture/security.md)
- [API Contracts](/code/ATLAS/docs/api/contracts.md)
