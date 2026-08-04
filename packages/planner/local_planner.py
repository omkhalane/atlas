import json
import logging
import re
from typing import Any, List, Tuple, TYPE_CHECKING
from urllib.parse import quote_plus

if TYPE_CHECKING:
    from runtime.kernel.openrouter import OpenRouterClient

logger = logging.getLogger("atlas.planner")


class LocalPlanner:
    def __init__(self, llm_client: "OpenRouterClient"):
        self.llm = llm_client

    def _extract_goal_and_capabilities(self, context: str) -> Tuple[str, List[str]]:
        goal = context
        if "USER REQUEST:" in context:
            goal = context.split("USER REQUEST:", 1)[1].strip()

        capability_ids: List[str] = ["browser", "filesystem", "command", "search", "media", "clipboard", "memory"]
        in_capabilities = False
        parsed_ids = []
        for line in context.splitlines():
            stripped_line = line.strip()
            if stripped_line == "AVAILABLE CAPABILITIES:":
                in_capabilities = True
                continue
            if in_capabilities and stripped_line in {"RECENT HISTORY:", "USER REQUEST:"}:
                break
            if in_capabilities and stripped_line.startswith("-"):
                match = re.match(r"^-\s*([a-zA-Z0-9_\-]+)", stripped_line)
                if match:
                    parsed_ids.append(match.group(1))

        if parsed_ids:
            capability_ids = parsed_ids

        return goal.strip(), capability_ids

    def _fallback_plan(self, goal: str, capability_ids: List[str]) -> Tuple[str, List[Any], bool]:
        from runtime.kernel.task import TaskNode

        goal_lower = goal.lower()

        def has(capability: str) -> bool:
            return capability in capability_ids

        if has("browser") and any(word in goal_lower for word in ["gmail", "email", "mail", "browser", "website", "web", "open", "browse", "search", "visit", "navigate"]):
            target_url = "https://mail.google.com/"
            if any(word in goal_lower for word in ["search", "find"]):
                query = quote_plus(goal)
                target_url = f"https://www.google.com/search?q={query}"
            else:
                url_match = re.search(r"https?://\S+", goal)
                if url_match:
                    target_url = url_match.group(0).rstrip(".,)]")

            script = f'new_tab("{target_url}")\nwait_for_load()\nprint(page_info())'
            return (
                "browser.open",
                [TaskNode(id="step_1", action="browser", parameters={"script": script}, dependencies=[])],
                False,
            )

        if has("filesystem") and any(word in goal_lower for word in ["folder", "directory", "file", "create", "make", "write", "update", "delete", "remove", "move", "copy", "rename"]):
            if has("command"):
                return (
                    "filesystem.inspect",
                    [TaskNode(id="step_1", action="command", parameters={"command": "pwd && ls -la"}, dependencies=[])],
                    False,
                )

            return (
                "filesystem.inspect",
                [TaskNode(id="step_1", action="filesystem", parameters={"action": "list_files", "path": "."}, dependencies=[])],
                False,
            )

        if has("command"):
            command = f"printf %s {json.dumps(goal)}"
            return (
                "command.run",
                [TaskNode(id="step_1", action="command", parameters={"command": command}, dependencies=[])],
                False,
            )

        if has("search"):
            return (
                "search.query",
                [TaskNode(id="step_1", action="search", parameters={"query": goal}, dependencies=[])],
                False,
            )

        return (
            "fallback.note",
            [TaskNode(id="step_1", action="command", parameters={"command": "echo 'Atlas fallback: no direct capability plan available'"}, dependencies=[])],
            False,
        )

    def generate_plan(self, context: str) -> Tuple[str, List[Any], bool]:
        """
        Analyzes context and generates an execution plan.
        Returns:
            intent (str), graph (List[TaskNode]), needs_cloud_reasoning (bool)
        """
        from runtime.kernel.task import TaskNode

        goal, capability_ids = self._extract_goal_and_capabilities(context)

        prompt = f"""
You are the Atlas Planner. Analyze the user request and available capabilities in the context.
Your job is ONLY to plan, not execute. Break the request into a graph of discrete task nodes.

CRITICAL INSTRUCTION: You MUST strictly adhere to any rules or facts listed in the LONG TERM MEMORY section of the context. If a user asks you to do something, check if a procedural rule applies first.

{context}

Respond STRICTLY with a JSON object in this format:
{{
    "intent": "brief description of user intent",
    "needs_cloud_reasoning": false,
    "graph": [
        {{
            "id": "step_1",
            "action": "filesystem",
            "parameters": {{"action": "list_files", "path": "."}},
            "dependencies": []
        }},
        {{
            "id": "step_2",
            "action": "browser",
            "parameters": {{"script": "console.log('hello')"}},
            "dependencies": ["step_1"]
        }}
    ]
}}
"""
        try:
            res_text = self.llm._call_openrouter([{"role": "user", "content": prompt}])

            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```", 1)[1].strip()

            data = json.loads(res_text)

            nodes = []
            for node_data in data.get("graph", []):
                nodes.append(TaskNode(
                    id=node_data.get("id"),
                    action=node_data.get("action"),
                    parameters=node_data.get("parameters", {}),
                    dependencies=node_data.get("dependencies", [])
                ))

            return data.get("intent", "unknown"), nodes, data.get("needs_cloud_reasoning", False)

        except Exception as e:
            logger.error(f"Failed to generate plan: {e}")
            return self._fallback_plan(goal, capability_ids)
