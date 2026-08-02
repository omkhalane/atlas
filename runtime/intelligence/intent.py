"""
Phase C: Intent Detector + Difficulty Classifier

Uses the LOCAL LLM only (Ollama). Fast, private, deterministic routing.
Returns structured intent classification that drives the entire downstream flow.
"""
import json
import logging
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.intelligence.local_llm import LocalLLMManager

logger = logging.getLogger("atlas.intent")

INTENT_SYSTEM_PROMPT = """\
You are the Atlas Intent Detector. Your ONLY job is to classify the user's request.

Analyze and return a JSON object with these exact fields:
{
  "intent": "short.description",        // e.g. "filesystem.open", "browser.download", "code.fix"
  "difficulty": "easy|medium|hard|expert",
  "confidence": 0.0-1.0,
  "needs": ["capability_ids"],           // e.g. ["filesystem"], ["browser", "filesystem"]
  "needs_cloud": false,                  // true ONLY for: summarizing 100+ pages, code review, creative writing
  "direct_answer": null                  // If easy and answerable directly, put the answer here. Otherwise null.
}

Difficulty scale:
- easy:   Single-step, deterministic (e.g. "list files", "open firefox", "what time is it")
- medium: Multi-step, deterministic (e.g. "create folder and move files", "restart service")
- hard:   Requires research or reasoning (e.g. "find bug in project", "book flight")
- expert: Complex synthesis across many sources (e.g. "review entire codebase security")

Available capabilities: filesystem, command, browser, memory, clipboard, search, mcp_*, media

Output ONLY the JSON object. No explanation."""


class IntentDetector:
    def __init__(self, local_llm: Optional['LocalLLMManager'] = None, openrouter=None):
        self.local_llm = local_llm
        self.openrouter = openrouter  # fallback if Ollama unavailable

    def detect(self, goal: str, conversation_context: list = None) -> Dict[str, Any]:
        """
        Classifies the user's intent using the local LLM.
        Falls back to OpenRouter local tier if Ollama unavailable.
        Returns a structured dict for the LLM Router and Planner.
        """
        messages = []
        if conversation_context:
            # Include only last 3 turns for intent detection (not full history)
            for msg in conversation_context[-3:]:
                messages.append(msg)
        messages.append({"role": "user", "content": goal})

        raw = None

        # Try local first
        if self.local_llm and self.local_llm.ollama_available:
            try:
                raw = self.local_llm.call_local(messages, system=INTENT_SYSTEM_PROMPT)
            except Exception as e:
                logger.warning(f"Local LLM intent detection failed: {e}, falling back to cloud")

        # Fallback to OpenRouter (local tier = cheap/fast)
        if raw is None and self.openrouter:
            try:
                raw = self.openrouter._execute_with_fallback(
                    messages=messages,
                    system_prompt=INTENT_SYSTEM_PROMPT,
                    response_format={"type": "json_object"},
                    model_tier="local"
                )
            except Exception as e:
                logger.error(f"OpenRouter intent detection also failed: {e}")

        if not raw:
            return self._default_intent(goal)

        # Parse result
        try:
            # Strip markdown code fences if present
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            result = json.loads(raw.strip())
            result.setdefault("intent", "unknown")
            result.setdefault("difficulty", "hard")
            result.setdefault("confidence", 0.5)
            result.setdefault("needs", [])
            result.setdefault("needs_cloud", True)
            result.setdefault("direct_answer", None)
            logger.info(f"Intent detected: {result['intent']} [{result['difficulty']}] cloud={result['needs_cloud']}")
            return result
        except Exception as e:
            logger.error(f"Failed to parse intent JSON: {e} | raw: {raw[:200]}")
            return self._default_intent(goal)

    def _default_intent(self, goal: str) -> Dict[str, Any]:
        """Safe fallback intent — always routes to full planning pipeline."""
        return {
            "intent": "unknown.complex",
            "difficulty": "hard",
            "confidence": 0.0,
            "needs": [],
            "needs_cloud": True,
            "direct_answer": None
        }
