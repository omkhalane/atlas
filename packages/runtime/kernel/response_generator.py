"""
Phase G: Response Generator

Formats final responses before sending to the UI.
For deterministic results (file list, command output) — formats directly, NO LLM.
For complex synthesis (research, code review) — delegates to cloud LLM via ReasoningSession.
"""
import logging
from typing import List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.kernel.task import ExecutionTask
    from runtime.intelligence.llm_router import ReasoningSession

logger = logging.getLogger("atlas.response_gen")

# These capability results are always formatted deterministically
DETERMINISTIC_CAPABILITIES = {"filesystem", "command", "memory", "clipboard", "search"}


class ResponseGenerator:
    def __init__(self, reasoning_session: 'ReasoningSession' = None):
        self.session = reasoning_session

    def generate(self, task: 'ExecutionTask', intent_result: dict) -> str:
        """
        Generates the final response to send to the user.
        Decides whether to format directly or involve an LLM.
        """
        results = task.results if hasattr(task, 'results') else []
        direct_answer = intent_result.get("direct_answer")
        needs_cloud = intent_result.get("needs_cloud", False)
        difficulty = intent_result.get("difficulty", "hard")

        # Case 1: Direct answer (intent detector pre-computed it — no LLM!)
        if direct_answer and difficulty == "easy":
            logger.info("ResponseGenerator: Using direct answer")
            return direct_answer

        # Case 2: All steps used deterministic capabilities — format without LLM
        all_caps = set()
        if hasattr(task, 'graph') and task.graph:
            all_caps = {node.action for node in task.graph}

        if all_caps and all_caps.issubset(DETERMINISTIC_CAPABILITIES) and not needs_cloud:
            logger.info("ResponseGenerator: Deterministic formatting — no LLM")
            return self._format_deterministic(task, results)

        # Case 3: Complex — use cloud LLM to synthesize a coherent answer
        logger.info("ResponseGenerator: Cloud LLM synthesis")
        return self._format_with_llm(task, results, intent_result)

    def _format_deterministic(self, task: 'ExecutionTask', results: list) -> str:
        """Formats deterministic results into clean markdown — no LLM."""
        lines = [f"**Task complete:** {task.goal}\n"]
        for i, r in enumerate(results, 1):
            if not r:
                continue
            data = getattr(r, 'data', None)
            error = getattr(r, 'error', None)
            success = getattr(r, 'success', True)

            if not success and error:
                lines.append(f"**Step {i}:** ❌ {error}")
            elif data:
                if isinstance(data, dict):
                    output = data.get("output") or data.get("result") or data.get("files") or str(data)
                    lines.append(f"**Step {i}:** ✅ {output}")
                else:
                    lines.append(f"**Step {i}:** ✅ {data}")
            else:
                lines.append(f"**Step {i}:** ✅ Done")

        return "\n".join(lines)

    def _format_with_llm(self, task: 'ExecutionTask', results: list, intent_result: dict) -> str:
        """Synthesizes complex results via the cloud LLM."""
        import os
        if not os.getenv("OPENROUTER_API_KEY"):
            return "This is a mocked final response indicating successful execution."

        if not self.session:
            return self._format_deterministic(task, results)

        # Build a compact results summary (not a full dump)
        result_summaries = []
        for i, r in enumerate(results, 1):
            if not r:
                continue
            data = getattr(r, 'data', None)
            error = getattr(r, 'error', None)
            success = getattr(r, 'success', True)
            if not success:
                result_summaries.append(f"Step {i}: FAILED - {error}")
            elif data:
                summary = str(data)[:500]  # Truncate large outputs
                result_summaries.append(f"Step {i}: SUCCESS - {summary}")

        results_text = "\n".join(result_summaries) or "No results collected."

        system = (
            "You are the Atlas Response Generator. "
            "Synthesize execution results into a clear, concise answer for the user. "
            "Be direct. Use markdown. Never add disclaimers or apologies."
        )
        messages = [
            {
                "role": "user",
                "content": (
                    f"Goal: {task.goal}\n\n"
                    f"Execution Results:\n{results_text}\n\n"
                    "Write a clear, complete response to the user."
                )
            }
        ]

        try:
            return self.session.call(messages, system=system)
        except Exception as e:
            logger.error(f"ResponseGenerator LLM call failed: {e}")
            return self._format_deterministic(task, results)
