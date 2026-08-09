"""
ReAct Agent
Implements bounded thought-action-observation loop.
"""
import logging
import json
import re
from typing import Any, List, Dict
from core.python.agents.core_types.scope import ExecutionScope
from core.python.contracts.provider import IProviderManager
from core.python.contracts.tool import IToolExecutor
from core.python.contracts.orchestration import AgentResult

logger = logging.getLogger("atlas.react")

class ReActAgent:
    def __init__(self, provider: IProviderManager, tool_executor: IToolExecutor):
        self.provider = provider
        self.tool_executor = tool_executor

    async def run(self, goal: str, context: str, scope: ExecutionScope) -> AgentResult:
        max_iterations = 10
        iterations = 0
        
        messages = [
            {"role": "system", "content": "You are a ReAct agent. You must respond in a specific format.\n\nFORMAT:\nThought: ...\nAction: tool_name\nAction Input: {...JSON...}\n\nIf you are done, respond with:\nThought: ...\nFinal Answer: ..."},
            {"role": "user", "content": f"Context:\n{context}\n\nGoal:\n{goal}"}
        ]
        
        while iterations < max_iterations:
            scope.check_cancellation()
            if scope.remaining() <= 0:
                return AgentResult(success=False, error="Execution deadline exceeded.")
            
            iterations += 1
            
            try:
                # Use generate if present (TimedProviderWrapper), else fallback to execute_prompt
                if hasattr(self.provider, "generate"):
                    response_text = await self.provider.generate(messages)
                else:
                    res = self.provider.execute_prompt("default", messages)
                    import asyncio
                    if asyncio.iscoroutine(res):
                        res = await res
                    response_text = str(res)
            except Exception as e:
                return AgentResult(success=False, error=f"LLM failure: {e}")
            
            messages.append({"role": "assistant", "content": response_text})
            
            action, action_input, final_answer = self._parse_response(response_text)
            
            if final_answer is not None:
                return AgentResult(success=True, data=final_answer)
                
            if action:
                if action_input is not None and "_raw_invalid_json" in action_input:
                    messages.append({"role": "user", "content": "Observation Error: Invalid JSON in Action Input. Please provide valid JSON."})
                    continue
                    
                try:
                    tool_result = await self.tool_executor.execute_tool(action, action_input or {})
                    obs = f"Observation: {tool_result.result}"
                    if tool_result.error:
                        obs += f" | Error: {tool_result.error}"
                    messages.append({"role": "user", "content": obs})
                    # Add publishing so client sees it
                    import asyncio
                    try:
                        loop = asyncio.get_running_loop()
                        from runtime.observability.trace_context import get_envelope
                        if hasattr(self.provider, "bus"):
                            pass # handled elsewhere
                        # Just printing for debugging since we don't have direct bus access
                        logger.info(f"ReActAgent OBS: {obs}")
                    except Exception:
                        pass
                except Exception as e:
                    messages.append({"role": "user", "content": f"Observation Error: {e}"})
            else:
                messages.append({"role": "user", "content": "Error: Could not parse Action. Make sure you provide 'Action: tool_name' and 'Action Input: {...}'."})
                
        return AgentResult(success=False, error="Max iterations reached without final answer.")

    def _parse_response(self, text: str) -> tuple[str, dict, str]:
        final_answer_match = re.search(r"Final Answer:\s*(.*)", text, re.DOTALL | re.IGNORECASE)
        if final_answer_match:
            return None, None, final_answer_match.group(1).strip()
            
        action_match = re.search(r"Action:\s*([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
        
        # Handle markdown blocks in Action Input
        input_match = re.search(r"Action Input:\s*(```json\s*)?({.*?})(```)?", text, re.DOTALL | re.IGNORECASE)
        if not input_match:
            input_match = re.search(r"Action Input:\s*(\{.*?\})", text, re.DOTALL | re.IGNORECASE)
        
        action = action_match.group(1).strip() if action_match else None
        
        if not input_match:
            return action, None, None
            
        try:
            # group(2) contains the JSON in the markdown regex, group(1) contains it in the fallback regex
            raw_json = input_match.group(2) if len(input_match.groups()) >= 2 and input_match.group(2) else input_match.group(1)
            if raw_json is None:
                raw_json = input_match.group(0) # fallback
            action_input = json.loads(raw_json.strip())
        except json.JSONDecodeError:
            return action, {"_raw_invalid_json": raw_json}, None
            
        return action, action_input, None
