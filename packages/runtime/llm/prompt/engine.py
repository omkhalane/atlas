"""
Prompt Engine & Template System
Formats ContextSnapshot using Markdown templates and handles cache markers.
"""
import os
from typing import List
from runtime.llm.contracts import ExecutionContext, LLMMessage


class PromptEngine:
    def __init__(self, template_dir: str = None):
        self.template_dir = template_dir or os.path.join(os.path.dirname(__file__), "templates")

    def load_template(self, task_type: str) -> str:
        filepath = os.path.join(self.template_dir, f"{task_type}.md")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return "You are Atlas, an AI assistant."

    def build_prompt_messages(self, ctx: ExecutionContext, raw_messages: List[LLMMessage]) -> List[LLMMessage]:
        template_content = self.load_template(ctx.task_type)
        
        formatted_messages: List[LLMMessage] = []
        # Prepend task template as system prompt if not present
        has_system = any(m.role == "system" for m in raw_messages)
        if not has_system:
            sys_msg = LLMMessage(role="system", content=template_content)
            if ctx.metadata.get("enable_prompt_cache", True):
                sys_msg.cache_control = {"type": "ephemeral"}
            formatted_messages.append(sys_msg)

        for m in raw_messages:
            formatted_messages.append(m)

        return formatted_messages
