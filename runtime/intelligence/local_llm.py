"""
Phase A: Local LLM Auto-Detection & Management

Detects the best available Ollama model based on system hardware.
Auto-downloads if missing, streams progress to the EventBus.
Falls back to cloud (OpenRouter) gracefully if Ollama is unavailable.
"""
import os
import json
import logging
import subprocess
import asyncio
from typing import Optional, List, Dict, Any

logger = logging.getLogger("atlas.local_llm")

# Model tiers based on available VRAM/RAM
MODEL_TIERS = [
    {"min_gb": 16, "model": "qwen2.5:14b",       "embed": "nomic-embed-text"},
    {"min_gb": 8,  "model": "llama3.1:8b",        "embed": "nomic-embed-text"},
    {"min_gb": 4,  "model": "llama3.2:3b",        "embed": "nomic-embed-text"},
    {"min_gb": 0,  "model": "phi3:mini",           "embed": "nomic-embed-text"},
]


def _get_available_memory_gb() -> float:
    """Returns total available system RAM in GB."""
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        return 4.0  # safe default


def _is_ollama_running() -> bool:
    """Checks if the Ollama daemon is reachable."""
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        return True
    except Exception:
        return False


def _get_ollama_models() -> List[str]:
    """Returns a list of locally available Ollama model names."""
    try:
        import urllib.request
        import json as j
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as r:
            data = j.loads(r.read())
            return [m["name"].split(":")[0] for m in data.get("models", [])]
    except Exception:
        return []


def _select_best_model(available_gb: float) -> Dict[str, str]:
    """Selects best model tier for the available memory."""
    for tier in MODEL_TIERS:
        if available_gb >= tier["min_gb"]:
            return tier
    return MODEL_TIERS[-1]  # fallback to smallest


class LocalLLMManager:
    def __init__(self, bus=None):
        self.bus = bus
        self.ollama_available = False
        self.selected_model: Optional[str] = None
        self.embed_model: Optional[str] = None
        self._base_url = "http://localhost:11434"

    async def initialize(self):
        """
        Main init: detects hardware, checks Ollama, selects model,
        downloads if missing. Publishes progress to EventBus.
        """
        await self._publish("Detecting system hardware...")
        available_gb = _get_available_memory_gb()
        await self._publish(f"Available RAM: {available_gb:.1f} GB")

        tier = _select_best_model(available_gb)
        self.selected_model = tier["model"]
        self.embed_model = tier["embed"]

        await self._publish(f"Selected local model: {self.selected_model}")

        # Check if Ollama is running
        if not _is_ollama_running():
            await self._publish("Ollama not running. Attempting to start...")
            try:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                await asyncio.sleep(3)  # Wait for Ollama daemon
            except FileNotFoundError:
                await self._publish("WARNING: Ollama is not installed. Using cloud-only mode.", level="warning")
                return

        if not _is_ollama_running():
            await self._publish("WARNING: Could not start Ollama. Using cloud-only mode.", level="warning")
            return

        self.ollama_available = True

        # Pull model if not present
        local_models = _get_ollama_models()
        model_base = self.selected_model.split(":")[0]
        if model_base not in local_models:
            await self._publish(f"Downloading {self.selected_model}... (this may take a few minutes)")
            await self._pull_model_with_progress(self.selected_model)
        else:
            await self._publish(f"Local model {self.selected_model} ready.")

        # Pull embedding model
        embed_base = self.embed_model.split(":")[0]
        if embed_base not in local_models:
            await self._publish(f"Downloading embedding model {self.embed_model}...")
            await self._pull_model_with_progress(self.embed_model)
        else:
            await self._publish(f"Embedding model {self.embed_model} ready.")

    async def _pull_model_with_progress(self, model_name: str):
        """Streams download progress to EventBus."""
        try:
            import urllib.request
            import json as j

            url = f"{self._base_url}/api/pull"
            data = json.dumps({"name": model_name}).encode()
            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("Content-Type", "application/json")

            with urllib.request.urlopen(req, timeout=600) as response:
                last_pct = -1
                for line in response:
                    try:
                        msg = j.loads(line.decode().strip())
                        total = msg.get("total", 0)
                        completed = msg.get("completed", 0)
                        if total > 0:
                            pct = int(completed / total * 100)
                            if pct != last_pct and pct % 10 == 0:
                                await self._publish(f"Downloading {model_name}: {pct}%")
                                last_pct = pct
                        elif msg.get("status") == "success":
                            await self._publish(f"Download complete: {model_name}")
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Failed to pull {model_name}: {e}")
            await self._publish(f"Download failed for {model_name}. Falling back to cloud.", level="warning")

    def call_local(self, messages: List[Dict[str, str]], system: str = "") -> str:
        """Calls the local Ollama model synchronously."""
        if not self.ollama_available or not self.selected_model:
            raise RuntimeError("Local LLM not available")

        import urllib.request
        import json as j

        payload = {
            "model": self.selected_model,
            "messages": messages,
            "stream": False
        }
        if system:
            payload["system"] = system

        data = j.dumps(payload).encode()
        req = urllib.request.Request(
            f"{self._base_url}/api/chat",
            data=data, method="POST"
        )
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=120) as r:
            result = j.loads(r.read())
            return result.get("message", {}).get("content", "")

    def get_embedding(self, text: str) -> List[float]:
        """Returns embedding vector for the given text."""
        if not self.ollama_available or not self.embed_model:
            return []

        import urllib.request
        import json as j

        payload = {"model": self.embed_model, "input": text}
        data = j.dumps(payload).encode()
        req = urllib.request.Request(
            f"{self._base_url}/api/embed",
            data=data, method="POST"
        )
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=30) as r:
            result = j.loads(r.read())
            embeddings = result.get("embeddings", [[]])
            return embeddings[0] if embeddings else []

    async def _publish(self, message: str, level: str = "info"):
        if self.bus:
            await self.bus.publish("NOTIFICATION", {
                "type": "NOTIFICATION",
                "level": level,
                "source": "local_llm",
                "message": message
            })
        logger.info(f"[LocalLLM] {message}")
