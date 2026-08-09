"""
Browser Specialized Worker
Reuses ReAct infrastructure but specialized with a browser-focused prompt.
"""
import logging
from core.python.agents.core_agents.react import ReActAgent
from core.python.contracts.provider import IProviderManager
from core.python.contracts.tool import IToolExecutor
from core.python.agents.core_types.scope import ExecutionScope
from core.python.contracts.orchestration import AgentResult
from core.python.agents.core_types.policy import AuthorizationManager, CapabilityState

logger = logging.getLogger("atlas.browser_worker")

class BrowserWorker(ReActAgent):
    def __init__(self, provider: IProviderManager, tool_executor: IToolExecutor, auth_manager: AuthorizationManager = None):
        super().__init__(provider, tool_executor)
        self.auth_manager = auth_manager
        
    async def run(self, goal: str, context: str, scope: ExecutionScope) -> AgentResult:
        max_iterations = 20
        iterations = 0
        
        system_prompt = (
            "You are a specialized Web Browser Worker.\n"
            "You have access to actual Playwright CDP tools via the 'mcp_chrome-devtools' capability.\n"
            "Assume all interactions are sandboxed and monitored.\n\n"
            "To use browser tools, you MUST use the capability 'mcp_chrome-devtools' and provide the tool name as the 'action' parameter.\n"
            "Available actions include: navigate_page, click, type_text, evaluate_script, take_screenshot.\n\n"
            "FORMAT:\nThought: ...\nAction: mcp_chrome-devtools\nAction Input: {\"action\": \"navigate_page\", \"url\": \"https://example.com\"}\n\n"
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
                
            if self.auth_manager:
                state = await self.auth_manager.request_capability("BROWSER_CONTROL")
                if state == CapabilityState.REVOKED:
                    return AgentResult(success=False, error="BROWSER_CONTROL capability was revoked.")
                elif state == CapabilityState.EXPIRED:
                    continue  # Loop around to request again
                elif state != CapabilityState.GRANTED:
                    return AgentResult(success=False, error=f"Unexpected capability state: {state}")
            
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
                except Exception as e:
                    messages.append({"role": "user", "content": f"Observation Error: {e}"})
            else:
                messages.append({"role": "user", "content": "Error: Could not parse Action. Make sure you provide 'Action: tool_name' and 'Action Input: {...}'."})
                
        return AgentResult(success=False, error="Max iterations reached without final answer.")
