#!/usr/bin/env python3
"""
Atlas API Key Tester & Model Auto-Detector CLI
"""
import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional

# ANSI Colors for rich CLI output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def auto_detect_provider(api_key: str, base_url: Optional[str] = None) -> str:
    if base_url:
        if "11434" in base_url or "ollama" in base_url:
            return "ollama"
        if "openrouter" in base_url:
            return "openrouter"
        if "anthropic" in base_url:
            return "anthropic"
        if "generativelanguage" in base_url or "google" in base_url:
            return "gemini"

    key = api_key.strip()
    if key.startswith("sk-or-"):
        return "openrouter"
    elif key.startswith("sk-ant-"):
        return "anthropic"
    elif key.startswith("gsk_"):
        return "groq"
    elif key.startswith("AIzaSy"):
        return "gemini"
    elif key.startswith("sk-") or key.startswith("sk-proj-"):
        return "openai"
    else:
        return "openai"  # default to OpenAI-compatible format


def fetch_models(provider: str, api_key: str, base_url: Optional[str] = None) -> List[str]:
    headers = {"User-Agent": "Atlas-Key-Tester/1.0"}

    if provider == "openrouter":
        url = "https://openrouter.ai/api/v1/models"
        headers["Authorization"] = f"Bearer {api_key}"
    elif provider == "anthropic":
        url = "https://api.anthropic.com/v1/models"
        headers["x-api-key"] = api_key
        headers["anthropic-version"] = "2023-06-01"
    elif provider == "ollama":
        url = f"{base_url or 'http://localhost:11434'}/api/tags"
    elif provider == "groq":
        url = "https://api.groq.com/openai/v1/models"
        headers["Authorization"] = f"Bearer {api_key}"
    elif provider == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    else:  # openai / default
        target_base = (base_url or "https://api.openai.com/v1").rstrip("/")
        url = f"{target_base}/models"
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        models = []
        if provider == "ollama" and "models" in data:
            models = [m.get("name") for m in data["models"] if "name" in m]
        elif provider == "gemini" and "models" in data:
            models = [m.get("name", "").replace("models/", "") for m in data["models"] if "name" in m]
        elif "data" in data and isinstance(data["data"], list):
            models = [m.get("id") for m in data["data"] if "id" in m]
        elif isinstance(data, list):
            models = [m.get("id") for m in data if "id" in m]

        return models
    except Exception as e:
        print(f"{YELLOW}⚠️ Could not auto-fetch models catalog: {e}{RESET}")
        return []


def test_completion(provider: str, api_key: str, model: str, base_url: Optional[str] = None) -> Dict[str, Any]:
    t0 = time.time()

    if provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Respond with OK"}],
            "max_tokens": 10
        }
    elif provider == "ollama":
        target_base = (base_url or "http://localhost:11434").rstrip("/")
        url = f"{target_base}/api/chat"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Respond with OK"}],
            "stream": False
        }
    else:  # openai / openrouter / groq / custom
        target_base = (base_url or ("https://openrouter.ai/api/v1" if provider == "openrouter" else "https://api.openai.com/v1")).rstrip("/")
        url = f"{target_base}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Respond with OK"}],
            "max_tokens": 10
        }

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw_res = json.loads(resp.read().decode("utf-8"))

        latency_ms = round((time.time() - t0) * 1000, 2)

        content = ""
        if "choices" in raw_res and len(raw_res["choices"]) > 0:
            content = raw_res["choices"][0]["message"].get("content", "")
        elif "content" in raw_res and isinstance(raw_res["content"], list):
            content = raw_res["content"][0].get("text", "")
        elif "message" in raw_res:
            content = raw_res["message"].get("content", "")

        return {
            "success": True,
            "latency_ms": latency_ms,
            "response": content.strip(),
            "model": model,
            "provider": provider
        }
    except urllib.error.HTTPError as e:
        err_text = e.read().decode("utf-8") if e.fp else str(e)
        return {"success": False, "code": e.code, "error": err_text}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    print(f"\n{BOLD}{CYAN}===================================================={RESET}")
    print(f"{BOLD}{CYAN}   Atlas AI Platform — API Key & Model Detector CLI   {RESET}")
    print(f"{BOLD}{CYAN}===================================================={RESET}\n")

    parser = argparse.ArgumentParser(description="Atlas API Key & Model Auto-Detector CLI")
    parser.add_argument("--key", help="API Key to test")
    parser.add_argument("--provider", help="Provider type (openai, anthropic, gemini, openrouter, ollama, groq)")
    parser.add_argument("--base-url", help="Custom Base URL (e.g. http://localhost:11434 or http://127.0.0.1:8000/v1)")
    parser.add_argument("--model", help="Specific model to test completion for")

    args = parser.parse_args()

    api_key = args.key or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

    if not api_key and not args.base_url:
        print(f"{YELLOW}No API key passed via args or environment variables.{RESET}")
        api_key = input(f"{BOLD}Enter API Key to test: {RESET}").strip()

    if not api_key and not args.base_url:
        print(f"{RED}❌ Error: No API Key or Base URL provided. Exiting.{RESET}")
        sys.exit(1)

    provider = args.provider or auto_detect_provider(api_key or "", args.base_url)

    print(f"{BOLD}🔑 Key Preview:{RESET} {api_key[:12]}...{api_key[-4:] if len(api_key)>16 else ''}")
    print(f"{BOLD}📡 Detected Provider:{RESET} {CYAN}{provider.upper()}{RESET}")
    if args.base_url:
        print(f"{BOLD}🌐 Base URL:{RESET} {args.base_url}")

    print(f"\n{BOLD}🔍 Fetching Available Models Catalog...{RESET}")
    models = fetch_models(provider, api_key or "", args.base_url)

    if models:
        print(f"{GREEN}✓ Found {len(models)} accessible model(s):{RESET}")
        for idx, m in enumerate(models[:15], 1):
            print(f"  {CYAN}{idx}. {m}{RESET}")
        if len(models) > 15:
            print(f"  ... and {len(models) - 15} more models")
    else:
        print(f"{YELLOW}⚠️ Could not list models automatically. Proceeding with default model.{RESET}")

    # Select target model to test
    target_model = args.model
    if not target_model:
        if provider == "openrouter":
            target_model = "anthropic/claude-sonnet-4-5" if "anthropic/claude-sonnet-4-5" in models else (models[0] if models else "meta-llama/llama-3.3-70b-instruct")
        elif provider == "anthropic":
            target_model = "claude-3-5-sonnet-20241022"
        elif provider == "gemini":
            target_model = "gemini-2.5-flash"
        elif provider == "ollama":
            target_model = models[0] if models else "qwen2.5-coder:7b"
        else:
            target_model = models[0] if models else "gpt-4o"

    print(f"\n{BOLD}🧪 Testing Chat Completion Inference on model: {YELLOW}{target_model}{RESET} ...")
    res = test_completion(provider, api_key or "", target_model, args.base_url)

    if res["success"]:
        print(f"\n{BOLD}{GREEN}✅ SUCCESS! Key is valid and active.{RESET}")
        print(f"  {BOLD}Model:{RESET} {res['model']}")
        print(f"  {BOLD}Latency:{RESET} {GREEN}{res['latency_ms']} ms{RESET}")
        print(f"  {BOLD}Sample Response:{RESET} \"{res['response']}\"")
        print(f"\n{BOLD}{GREEN}🎉 Provider profile ready for use in Atlas Runtime!{RESET}\n")
    else:
        print(f"\n{BOLD}{RED}❌ CONNECTION FAILED!{RESET}")
        print(f"  {BOLD}Error Details:{RESET} {RED}{res.get('error', 'Unknown Error')}{RESET}\n")


if __name__ == "__main__":
    main()
