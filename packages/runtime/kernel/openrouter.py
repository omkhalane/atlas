import os
import requests
import json
import time
from typing import Dict, Any, List

class OpenRouterClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self._load_config()

    def _load_config(self):
        config_path = "/code/ATLAS/config.json"
        # Free OpenRouter models — no credits needed
        self.free_models = [
            "meta-llama/llama-3.1-8b-instruct:free",
            "google/gemma-2-9b-it:free",
            "mistralai/mistral-7b-instruct:free",
            "microsoft/phi-3-mini-128k-instruct:free",
        ]
        self.local_models = self.free_models  # alias
        self.cloud_models = [
            "anthropic/claude-sonnet-4-5",
            "google/gemini-2.5-pro",
            "google/gemini-2.5-flash"
        ]
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    cfg = json.load(f)
                    if "openrouter" in cfg:
                        if "free_models" in cfg["openrouter"]:
                            self.free_models = cfg["openrouter"]["free_models"]
                            self.local_models = self.free_models
                        if "cloud_models" in cfg["openrouter"]:
                            self.cloud_models = cfg["openrouter"]["cloud_models"]
            except Exception as e:
                print(f"Failed to load config: {e}")

    def _execute_with_fallback(self, messages, system_prompt="", response_format=None, model_tier="cloud"):
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is missing.")
            
        final_messages = []
        if system_prompt:
            final_messages.append({"role": "system", "content": system_prompt})
        final_messages.extend(messages)
        
        models_to_try = self.cloud_models + self.free_models if model_tier == "cloud" else self.free_models

        for model_name in models_to_try:
            try:
                payload = {
                    "model": model_name,
                    "messages": final_messages
                }
                if response_format:
                    payload["response_format"] = response_format
                    
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 402:
                    print(f"402 Payment Required for {model_name} — trying next model")
                    continue

                if response.status_code == 400:
                    print(f"400 Bad Request for {model_name}: {response.text[:200]}")
                    continue

                if response.status_code == 401:
                    print(f"Authentication Error (401). Check API key.")
                    raise Exception("401 Unauthorized")

                if response.status_code == 429:
                    print(f"Rate limited (429) for {model_name}. Trying next model...")
                    continue

                if response.status_code >= 500:
                    print(f"Server Error ({response.status_code}) for {model_name}. Trying next...")
                    continue

                response.raise_for_status()
                response_json = response.json()

                if "choices" in response_json and len(response_json["choices"]) > 0:
                    content = response_json["choices"][0]["message"].get("content", "")
                    if content:
                        return content
            except Exception as e:
                print(f"Exception calling OpenRouter model {model_name}: {e}")
                continue
        
        raise Exception("OpenRouter request failed.")

    # Backward-compatibility alias used by LocalPlanner
    def _call_openrouter(self, messages, system_prompt="", model_tier="local") -> str:
        return self._execute_with_fallback(messages, system_prompt=system_prompt, model_tier=model_tier)

    def classify_intent(self, goal: str) -> Dict[str, Any]:
        if not self.api_key:
            return {"intent": "complex", "capabilities": []}
            
        system_prompt = """
You are the ATLAS Intent Classifier.
Analyze the user's goal and classify it into one of three categories: 'simple', 'moderate', or 'complex'.
- 'simple': Requires exactly 1 step (e.g. 'What is the date', 'List files', 'Git status').
- 'moderate': Deterministic but requires multiple steps (e.g. 'Delete file X', 'Restart docker container').
- 'complex': Ambiguous, requires planning, reasoning, or heavy decomposition (e.g. 'Book a hotel', 'Research topic', 'Download 50 dog images').

Also list the specific capabilities needed (e.g. 'command', 'filesystem', 'browser', 'media').
Output JSON:
{"intent": "simple|moderate|complex", "capabilities": ["..."]}
"""
        try:
            content = self._execute_with_fallback(
                messages=[{"role": "user", "content": goal}], 
                system_prompt=system_prompt,
                response_format={"type": "json_object"},
                model_tier="local"
            )
            return json.loads(content)
        except Exception as e:
            print(f"Classification Error: {e}")
            return {"intent": "complex", "capabilities": []}

    def plan_task(self, goal: str) -> list:
        if not self.api_key:
            return [{"id": "t1", "capability": "command", "input": "echo 'Mock plan'", "depends_on": []}]
            
        system_prompt = """
You are the ATLAS Autonomous Planner. 
Your objective is to break down the user's goal into a logical sequence of deterministic tasks forming a Dependency Graph (DAG).
Independent tasks must not depend on each other so they can run in parallel.
Produce a JSON response with a single field "tasks" containing a list of objects.
Each object MUST have:
- "id": A unique string ID for this task (e.g. "t1", "t2").
- "capability": The ID of the capability to use (e.g., 'command', 'filesystem', 'browser')
- "input": A description of the input for this step.
- "depends_on": A list of task IDs that must complete before this task can start. (Empty list [] if it has no dependencies).

Example:
{"tasks": [
  {
    "id": "fetch_data",
    "capability": "browser",
    "input": "Navigate to site and extract data",
    "depends_on": []
  },
  {
    "id": "process_data",
    "capability": "command",
    "input": "Run processing script on the extracted data",
    "depends_on": ["fetch_data"]
  }
]}
"""
        try:
            content = self._execute_with_fallback(
                messages=[{"role": "user", "content": f"Goal: {goal}"}], 
                system_prompt=system_prompt,
                response_format={"type": "json_object"},
                model_tier="local"
            )
            return json.loads(content).get("tasks", [])
        except Exception as e:
            print(f"Planning Error: {e}")
            return [{"id": "err", "capability": "command", "input": f"echo 'Error planning {e}'", "depends_on": []}]

    def get_moderate_steps(self, goal: str, available_capabilities: list) -> list:
        if not self.api_key:
            return []
            
        system_prompt = f"""
You are the ATLAS Capability Router.
The user's goal is 'moderate' complexity (deterministic).
Available capabilities: {json.dumps(available_capabilities)}
Provide a JSON array "steps" containing a list of actions to execute sequentially.
Each action must have "action" (capability id) and "parameters".
Example:
{{"steps": [{{"action": "command", "parameters": {{"action": "run", "command": "rm foo.txt"}}}}]}}
"""
        try:
            content = self._execute_with_fallback(
                messages=[{"role": "user", "content": f"Goal: {goal}"}], 
                system_prompt=system_prompt,
                response_format={"type": "json_object"},
                model_tier="local"
            )
            return json.loads(content).get("steps", [])
        except Exception as e:
            print(f"Moderate Routing Error: {e}")
            return []

    def get_simple_step(self, goal: str, available_capabilities: list) -> dict:
        if not self.api_key:
            return {"action": "finish", "parameters": {}}
            
        system_prompt = f"""
You are the ATLAS Capability Router.
The user's goal is 'simple'. It requires EXACTLY 1 step.
Available capabilities: {json.dumps(available_capabilities)}
Provide a JSON object with "action" (capability id) and "parameters".
Example:
{{"action": "command", "parameters": {{"action": "run", "command": "date"}}}}
"""
        try:
            content = self._execute_with_fallback(
                messages=[{"role": "user", "content": f"Goal: {goal}"}], 
                system_prompt=system_prompt,
                response_format={"type": "json_object"},
                model_tier="local"
            )
            return json.loads(content)
        except Exception as e:
            print(f"Simple Routing Error: {e}")
            return {"action": "finish", "parameters": {}}

    def step(self, history: List[Dict[str, str]], available_capabilities: List[Dict[str, Any]], tasks: list = None) -> Dict[str, Any]:
        if not self.api_key:
            print("WARNING: OPENROUTER_API_KEY not set. Mocking step.")
            return {"thought": "I will finish immediately", "action": "finish", "parameters": {}}

        skill_path = "/code/ATLAS/atlas/integrations/browser/atlas-browser/skills/browser-harness/SKILL.md"
        browser_skills = ""
        if os.path.exists(skill_path):
            with open(skill_path, "r") as f:
                browser_skills = f.read()
                
        tasks_text = json.dumps(tasks) if tasks else "[]"

        system_prompt = f"""
You are the ATLAS Autonomous ReAct Agent executing a COMPLEX plan.
Your current plan checklist is: {tasks_text}

Available Capabilities: {json.dumps(available_capabilities, indent=2)}

CRITICAL: Plugins and Native Integrations are ALWAYS preferred over Browser automation.
If you must use the browser, use the `browser` capability and provide your browser-harness Python code in the `script` parameter. Do NOT use the `command` capability for browser tasks.
{browser_skills}

At each step, produce a JSON response with exactly four fields:
1. "thought": Short description of the execution status (e.g. 'Reading Gmail', 'Executing search').
2. "action": The ID of the capability to use (e.g. "command", "filesystem"), or "finish" if complete.
3. "parameters": Parameters for the action.
4. "current_task_idx": The integer index (0-based) of the plan task you are currently working on.
"""
        try:
            content = self._execute_with_fallback(
                messages=history, 
                system_prompt=system_prompt,
                response_format={"type": "json_object"},
                model_tier="cloud"
            )
            return json.loads(content)
        except Exception as e:
            print(f"Step Error: {e}")
            return {"thought": "Execution failed due to API errors.", "action": "finish", "parameters": {}}
