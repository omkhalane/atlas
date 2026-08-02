import json
import logging
from runtime.kernel.task import ExecutionTask
from runtime.kernel.openrouter import OpenRouterClient
from runtime.events.bus import EventBus

logger = logging.getLogger("atlas.aggregator")

class ResultAggregator:
    def __init__(self, llm_client: OpenRouterClient, bus: EventBus):
        self.llm = llm_client
        self.bus = bus

    async def summarize(self, task: ExecutionTask) -> str:
        # Collect all successful results
        raw_results = []
        for node in task.graph:
            if node.result:
                raw_results.append(f"[{node.action}] {json.dumps(node.result)}")
                
        aggregated_text = "\n".join(raw_results)

        if not task.needs_cloud_reasoning:
            # Deterministic, simple task
            if not aggregated_text:
                return "Task completed successfully with no output."
            return f"Task completed.\nRaw Output:\n```\n{aggregated_text}\n```"

        # Cloud reasoning needed
        await self.bus.publish("THOUGHT", {"task_id": task.id, "content": "Analyzing aggregated data..."})
        
        prompt = f"""
You are the Atlas Response Builder. The local runtime has executed the user's task.
Synthesize the raw execution results into a human-readable, helpful response.

USER REQUEST:
{task.goal}

EXECUTION RESULTS:
{aggregated_text if aggregated_text else 'No data returned.'}

Please respond concisely and accurately based on the results. Do NOT apologize or explain how you obtained the data.
"""
        try:
            # Using the same openrouter client for simplicity, though in reality 
            # this might use a larger model (e.g., Claude 3.5 Sonnet vs Haiku)
            final_response = self.llm._call_openrouter([{"role": "user", "content": prompt}])
            return final_response
        except Exception as e:
            logger.error(f"Failed to build response: {e}")
            return f"Task completed, but failed to synthesize response. Raw data:\n{aggregated_text}"
