"""
Phase C: Intent Detector + Difficulty Classifier

Uses the LOCAL LLM only (Ollama). Fast, private, no API cost.
Returns structured intent classification that drives the entire downstream flow.

For simple greetings/small talk — returns direct_answer immediately (zero API calls).
"""
import json
import re
import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.intelligence.local_llm import LocalLLMManager

logger = logging.getLogger("atlas.intent")

# Simple patterns handled entirely locally — no planning, no cloud
SIMPLE_CHAT_PATTERNS = [
    (r"^(hey|hi|hello|howdy|yo|sup|hiya|greetings)\b", "Hey! How can I help you today?"),
    (r"^how are you", "I'm running great, thanks for asking! What can I do for you?"),
    (r"^(what'?s? up|wassup|whats good)", "All systems running smoothly! What do you need?"),
    (r"^(thanks?|thank you|thx|ty)\b", "You're welcome! Anything else I can help with?"),
    (r"^(ok|okay|got it|sure|alright|sounds good|cool)\s*\.?\s*$", "Got it!"),
    (r"^(bye|goodbye|see ya|cya|later|good night|goodnight)\b", "Goodbye! See you soon."),
    (r"^(good morning|good afternoon|good evening)\b", "Hello! How can I assist you today?"),
    (r"^(who are you|what are you|what is atlas)\b", "I'm Atlas, your AI operating system. I can browse, code, manage files, and automate tasks. What do you need?"),
    (r"^(help|help me)\s*\.?\s*$", "I can browse the web, run code, manage files, search, read emails, and much more. Just tell me what you need!"),
]

TASK_SIGNAL_PATTERN = re.compile(
    r"\b(create|build|fix|update|edit|delete|remove|move|copy|run|open|install|configure|deploy|test|search|find|write|summarize|analyze|browse|launch|start|stop|check|inspect|resolve|review|refactor|task|workflow|project|folder|file)\b"
)

INTENT_SYSTEM_PROMPT = """\
You are Atlas Intent Detector. Respond ONLY with a single JSON object — no text before or after.

Return this exact schema:
{"intent":"string","difficulty":"easy|medium|hard|expert","confidence":0.0-1.0,"needs":["capability_ids"],"needs_cloud":false,"direct_answer":null}

Rules:
- difficulty easy: single-step, trivial (what time is it, list files, git status)
- difficulty medium: multi-step deterministic (create folder and move files)
- difficulty hard: research or complex reasoning (fix bug, book flight)
- difficulty expert: deep synthesis (review entire codebase security)
- needs_cloud: true ONLY for 100+ page summarization, advanced code review, creative long-form writing
- direct_answer: fill this if difficulty=easy AND no tool call is needed, else null
- needs: array from: filesystem, command, browser, memory, clipboard, search, media

User request to classify:"""


class IntentDetector:
    def __init__(self, local_llm: Optional['LocalLLMManager'] = None, openrouter=None):
        self.local_llm = local_llm
        self.openrouter = openrouter

    def _contains_task_signal(self, goal: str) -> bool:
        return bool(TASK_SIGNAL_PATTERN.search(goal))

    def detect(self, goal: str, conversation_context: List[dict] = None) -> Dict[str, Any]:
        """
        Classifies intent. Returns structured dict for the LLM Router.
        Simple greetings → direct_answer immediately (no LLM call).
        All other intents → local Ollama → fallback to OpenRouter free tier.
        """
        # ── Fast path: simple chat patterns (regex, zero LLM calls) ───────
        clean_goal = goal.strip().rstrip("!?.").lower()
        for pattern, response in SIMPLE_CHAT_PATTERNS:
            if re.search(pattern, clean_goal):
                if self._contains_task_signal(clean_goal):
                    continue
                logger.info(f"Intent: simple chat (regex match) → direct answer")
                return {
                    "intent": "chat.greeting",
                    "difficulty": "easy",
                    "confidence": 1.0,
                    "needs": [],
                    "needs_cloud": False,
                    "direct_answer": response
                }

        # ── Fast path: web & browser intent (instant response) ─────────────
        browser_keywords = [
            "open gmail", "open website", "open mail", "gmail", "ycombinator", "y combinator", 
            "navigate to", "open browser", "mail to", "send mail", "send email", "email to", 
            "summarise my mails", "summarize my emails", "summarise mails", "summarize emails", 
            "open gmail in browser", "check gmail", "read gmail", "compose mail", "compose email"
        ]
        if any(w in clean_goal for w in browser_keywords):
            logger.info("Intent: web application (fast match) → browser requirement")
            return {
                "intent": "open_web_application",
                "difficulty": "easy",
                "confidence": 0.95,
                "needs": ["browser"],
                "needs_cloud": False,
                "direct_answer": None
            }

        # ── Fast path: filesystem intent ──────────────────────────────────
        if any(w in clean_goal for w in ["create file", "write file", "list files", "make directory", "create folder"]):
            logger.info("Intent: filesystem action (fast match) → filesystem requirement")
            return {
                "intent": "filesystem_action",
                "difficulty": "easy",
                "confidence": 0.95,
                "needs": ["filesystem", "command"],
                "needs_cloud": False,
                "direct_answer": None
            }

        # ── API LLM Intent Classification ──────────────────────────────────
        messages = [{"role": "user", "content": f"{INTENT_SYSTEM_PROMPT}\n\n{goal}"}]

        raw = None
        if self.openrouter:
            try:
                raw = self.openrouter._execute_with_fallback(
                    messages=messages,
                    system_prompt="",
                    model_tier="cloud"
                )
            except Exception as e:
                logger.error(f"API LLM intent classification failed: {e}")

        if raw:
            result = self._parse_json(raw)
            if result:
                logger.info(
                    f"Intent: {result['intent']} [{result['difficulty']}] "
                    f"cloud={result['needs_cloud']}"
                )
                return result

        return self._default_intent()

    def _parse_json(self, raw: str) -> Optional[Dict[str, Any]]:
        """Robustly extracts JSON from LLM output."""
        # Strip markdown fences
        text = raw.strip()
        if "```" in text:
            match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
            if match:
                text = match.group(1).strip()

        # Find the JSON object
        match = re.search(r"\{[\s\S]+\}", text)
        if match:
            text = match.group(0)

        try:
            result = json.loads(text)
            result.setdefault("intent", "unknown")
            result.setdefault("difficulty", "hard")
            result.setdefault("confidence", 0.5)
            result.setdefault("needs", [])
            result.setdefault("needs_cloud", True)
            result.setdefault("direct_answer", None)
            return result
        except Exception as e:
            logger.debug(f"JSON parse failed: {e} | raw: {raw[:100]}")
            return None

    def _default_intent(self) -> Dict[str, Any]:
        """Safe default — full planning pipeline, cloud if needed."""
        return {
            "intent": "unknown",
            "difficulty": "hard",
            "confidence": 0.0,
            "needs": [],
            "needs_cloud": True,
            "direct_answer": None
        }
