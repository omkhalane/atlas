"""
Documents the required cancellation check pattern that must be applied
to ReAct and Plan-and-Execute agent loops.

Pattern:

    while True:
        scope.check_cancellation()          # <-- added
        thought = await provider.generate(...)
        scope.check_cancellation()          # <-- after every await
        result = await executor.execute_tool(...)
        ...

On ExecutionCancelledError:

    try:
        ...
    except ExecutionCancelledError as exc:
        # Save final state to IAgentStateRepository
        await state_repo.save(scope.execution_id, current_state)
        return AgentResult(cancelled=True, reason=str(exc))

This file is a design reference. The actual loop modification is in
planner.py (modified) and supervisor.py (modified).
"""
