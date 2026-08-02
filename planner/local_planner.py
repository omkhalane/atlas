import json
import logging
from typing import List, Dict, Any, Tuple
from runtime.kernel.openrouter import OpenRouterClient
from runtime.kernel.task import TaskNode

logger = logging.getLogger("atlas.planner")

class LocalPlanner:
    def __init__(self, llm_client: OpenRouterClient):
        self.llm = llm_client
        
    def generate_plan(self, context: str) -> Tuple[str, List[TaskNode], bool]:
        """
        Analyzes context and generates an execution plan.
        Returns:
            intent (str), graph (List[TaskNode]), needs_cloud_reasoning (bool)
        """
        prompt = f"""
You are the Atlas Planner. Analyze the user request and available capabilities in the context.
Your job is ONLY to plan, not execute. Break the request into a graph of discrete task nodes.

CRITICAL INSTRUCTION: You MUST strictly adhere to any rules or facts listed in the LONG TERM MEMORY section of the context. If a user asks you to do something, check if a procedural rule applies first.

{context}

Respond STRICTLY with a JSON object in this format:
{{
    "intent": "brief description of user intent",
    "needs_cloud_reasoning": false, // set to true ONLY if it requires generating complex text, summarizing large docs, etc.
    "graph": [
        {{
            "id": "step_1",
            "action": "filesystem", // MUST exactly match a capability ID
            "parameters": {{"action": "list_files", "path": "."}},
            "dependencies": [] // Array of step IDs that must complete before this runs
        }},
        {{
            "id": "step_2",
            "action": "browser", // MUST exactly match a capability ID
            "parameters": {{"script": "console.log('hello')"}},
            "dependencies": ["step_1"] // Wait for step_1
        }}
    ]
}}
"""
        try:
            res_text = self.llm._call_openrouter([{"role": "user", "content": prompt}])
            
            # Clean markdown formatting if present
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```")[1].strip()
                
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
            return "error", [], False
