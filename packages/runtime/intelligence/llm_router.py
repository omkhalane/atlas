"""
Phase D: LLM Router

Routes each request to the correct LLM based on intent, difficulty, and task type.
The Runtime decides. The LLM does not choose itself.

Routing rules:
- easy/direct_answer         → No LLM needed (return direct_answer)
- easy/medium + no cloud     → Local Ollama
- coding task                → Claude (best code reasoning)
- research/long context      → Gemini (best large context)
- cheap/fast                 → GPT-4o-mini via OpenRouter
- default cloud              → OpenRouter with fallback chain
"""
import logging
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.intelligence.local_llm import LocalLLMManager
    from runtime.kernel.openrouter import OpenRouterClient

logger = logging.getLogger("atlas.llm_router")

# Cloud model routing rules (intent prefix → preferred model)
INTENT_MODEL_MAP = {
    "code":     "anthropic/claude-sonnet-4-5",
    "fix":      "anthropic/claude-sonnet-4-5",
    "debug":    "anthropic/claude-sonnet-4-5",
    "review":   "anthropic/claude-sonnet-4-5",
    "research": "google/gemini-2.5-pro",
    "summarize":"google/gemini-2.5-flash",
    "write":    "google/gemini-2.5-flash",
    "generate": "google/gemini-2.5-flash",
}


class ReasoningSession:
    """
    The output of the LLM Router.
    Wraps whichever LLM was selected with a unified call() interface.
    """
    def __init__(self, mode: str, local_llm=None, openrouter=None, model: str = None):
        self.mode = mode        # "local" | "cloud" | "direct"
        self.local_llm = local_llm
        self.openrouter = openrouter
        self.cloud_model = model

    def call(self, messages: list, system: str = "") -> str:
        if self.mode == "direct":
            return ""  # No LLM needed

        if self.mode == "local" and self.local_llm and self.local_llm.ollama_available:
            try:
                return self.local_llm.call_local(messages, system=system)
            except Exception as e:
                logger.warning(f"Local LLM call failed, escalating to cloud: {e}")
                # Fall through to cloud

        if self.openrouter:
            if self.cloud_model:
                # Try specific cloud model first
                try:
                    return self.openrouter._execute_with_fallback(
                        messages=messages,
                        system_prompt=system,
                        model_tier="cloud"
                    )
                except Exception as e:
                    logger.error(f"Cloud LLM {self.cloud_model} failed: {e}")

            return self.openrouter._execute_with_fallback(
                messages=messages,
                system_prompt=system,
                model_tier="cloud"
            )

        raise RuntimeError("No LLM available (local or cloud)")


class LLMRouter:
    def __init__(
        self,
        local_llm: Optional['LocalLLMManager'] = None,
        openrouter: Optional['OpenRouterClient'] = None
    ):
        self.local_llm = local_llm
        self.openrouter = openrouter

    def route(self, intent_result: Dict[str, Any]) -> ReasoningSession:
        """
        Given an intent classification, returns the right ReasoningSession.
        """
        difficulty = intent_result.get("difficulty", "hard")
        needs_cloud = intent_result.get("needs_cloud", True)
        intent = intent_result.get("intent", "")
        direct_answer = intent_result.get("direct_answer")

        # Case 1: Direct answer (no LLM needed at all)
        if direct_answer and difficulty == "easy":
            logger.info("Router: Direct answer — no LLM needed")
            return ReasoningSession("direct")

        # Always route to API LLM (cloud) as instructed
        intent_prefix = intent.split(".")[0] if "." in intent else intent
        cloud_model = INTENT_MODEL_MAP.get(intent_prefix)
        logger.info(f"Router: API LLM (Cloud) → {cloud_model or 'OpenRouter fallback chain'}")
        return ReasoningSession("cloud", local_llm=self.local_llm, openrouter=self.openrouter, model=cloud_model)
