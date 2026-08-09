"""
Code/File Specialized Worker
Reuses ReAct infrastructure but specialized with a coding-focused prompt.
"""
import logging
from core.python.agents.core_agents.react import ReActAgent
from core.python.contracts.provider import IProviderManager
from core.python.contracts.tool import IToolExecutor
from core.python.agents.core_types.scope import ExecutionScope
from core.python.contracts.orchestration import AgentResult

logger = logging.getLogger("atlas.code_worker")

class CodeWorker(ReActAgent):
    def __init__(self, provider: IProviderManager, tool_executor: IToolExecutor):
        super().__init__(provider, tool_executor)
        
    async def run(self, goal: str, context: str, scope: ExecutionScope) -> AgentResult:
        max_iterations = 15
        iterations = 0
        
        system_prompt = (
            "You are a specialized Code and File Worker.\n"
            "You have access to filesystem and command tools. "
            "Use them to read, write, and analyze code safely.\n\n"
            "FORMAT:\nThought: ...\nAction: tool_name\nAction Input: {...JSON...}\n\n"
            "If you are done, respond with:\nThought: ...\nFinal Answer: ..."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nGoal:\n{goal}"}
        ]
        
        while iterations < max_iterations:
            scope.check_cancellation()
            if scope.remaining() <= 0:
                return AgentResult(success=False, error="Execution deadline exceeded.")
            
            iterations += 1
            
            try:
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
                        print(f"CodeWorker OBS: {obs}", flush=True)
                    except Exception:
                        pass
                except Exception as e:
                    messages.append({"role": "user", "content": f"Observation Error: {e}"})
            else:
                messages.append({"role": "user", "content": "Error: Could not parse Action. Make sure you provide 'Action: tool_name' and 'Action Input: {...}'."})
                
        return AgentResult(success=False, error="Max iterations reached without final answer.")
