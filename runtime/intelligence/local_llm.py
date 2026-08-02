"""
Phase A (Upgraded): Local LLM Auto-Detection — Smart, Cached, Full-System Scan

Strategy:
1. On FIRST run: scan the ENTIRE system for all available models
   (Ollama, llama.cpp binaries, huggingface cache, lm-studio, gpt4all, etc.)
2. Score each found model and choose the BEST one.
3. Only download if NOTHING suitable is found anywhere.
4. Cache the selected model to ~/.atlas/llm_config.json — never re-scan on subsequent boots.

Detection sources:
  - Ollama API tags
  - ~/.ollama/models/
  - ~/.cache/huggingface/
  - ~/.lm-studio/models/
  - ~/.local/share/nomic.ai/gpt4all/
  - System PATH: ollama, llamafile, llama-cli
"""
import os
import json
import logging
import subprocess
import asyncio
import glob
from typing import Optional, List, Dict, Any

logger = logging.getLogger("atlas.local_llm")

# ── Model Scoring Table ────────────────────────────────────────────────────────
# Score = quality/capability rating. Higher = better.
# The runtime picks the highest-scoring model that fits within available RAM.
MODEL_SCORES: Dict[str, int] = {
    # Qwen family
    "qwen2.5:14b": 95, "qwen2.5:7b": 80, "qwen2.5:3b": 65,
    # Llama family
    "llama3.1:8b": 82, "llama3.2:3b": 65, "llama3.2:1b": 45,
    "llama3:8b": 78, "llama3:70b": 98,
    # Mistral
    "mistral:7b": 77, "mistral-nemo:12b": 88,
    # Phi
    "phi4:14b": 90, "phi3.5:3.8b": 68, "phi3:mini": 55,
    # Gemma
    "gemma2:9b": 82, "gemma2:2b": 50,
    # DeepSeek
    "deepseek-r1:14b": 93, "deepseek-r1:8b": 84, "deepseek-r1:1.5b": 48,
    # Codellama / coding
    "codellama:13b": 80, "codellama:7b": 72,
    # HuggingFace models (partial name matching)
    "Meta-Llama-3.1-8B": 80, "Mistral-7B": 75, "Phi-3": 65,
}

# RAM thresholds for model families (GB)
MODEL_RAM_REQUIREMENTS: Dict[str, float] = {
    "70b": 40, "34b": 20, "14b": 10, "13b": 9,
    "12b": 8, "9b": 7, "8b": 6, "7b": 5,
    "3.8b": 4, "3b": 3, "2b": 3, "1.5b": 2, "1b": 2, "mini": 3,
}

# Best download defaults per RAM tier
DOWNLOAD_TIERS = [
    {"min_gb": 16, "model": "qwen2.5:14b",  "embed": "nomic-embed-text", "ram": 10},
    {"min_gb": 8,  "model": "llama3.1:8b",  "embed": "nomic-embed-text", "ram": 6},
    {"min_gb": 4,  "model": "llama3.2:3b",  "embed": "nomic-embed-text", "ram": 3},
    {"min_gb": 0,  "model": "phi3:mini",    "embed": "nomic-embed-text", "ram": 3},
]

CONFIG_PATH = "/code/ATLAS/.atlas/llm_config.json"


def _get_total_ram_gb() -> float:
    try:
        import psutil
        return psutil.virtual_memory().total / (1024 ** 3)
    except Exception:
        return 4.0


def _get_available_ram_gb() -> float:
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        return 4.0


def _is_ollama_running() -> bool:
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        return True
    except Exception:
        return False


def _get_ollama_models() -> List[Dict[str, Any]]:
    """Returns list of {name, size_gb} for all locally installed Ollama models."""
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as r:
            data = json.loads(r.read())
            models = []
            for m in data.get("models", []):
                name = m.get("name", "")
                size_bytes = m.get("size", 0)
                models.append({
                    "name": name,
                    "size_gb": size_bytes / (1024 ** 3),
                    "source": "ollama"
                })
            return models
    except Exception:
        return []


def _scan_filesystem_models() -> List[Dict[str, Any]]:
    """Scans common local directories for downloaded model files."""
    found = []
    home = os.path.expanduser("~")

    scan_dirs = [
        # Ollama blob cache
        os.path.join(home, ".ollama", "models", "manifests"),
        # HuggingFace
        os.path.join(home, ".cache", "huggingface", "hub"),
        # LM Studio
        os.path.join(home, ".lm-studio", "models"),
        # GPT4All
        os.path.join(home, ".local", "share", "nomic.ai", "gpt4all"),
        # llamafile
        os.path.join(home, ".llamafile"),
        # Common linux paths
        "/usr/local/share/ollama/models",
    ]

    for scan_dir in scan_dirs:
        if not os.path.exists(scan_dir):
            continue
        try:
            for root, dirs, files in os.walk(scan_dir):
                for f in files:
                    if f.endswith((".gguf", ".bin", ".safetensors")) or "manifest" in f.lower():
                        size_bytes = os.path.getsize(os.path.join(root, f))
                        found.append({
                            "name": f,
                            "path": os.path.join(root, f),
                            "size_gb": size_bytes / (1024 ** 3),
                            "source": "filesystem"
                        })
        except Exception:
            pass

    return found


def _score_model(name: str, available_ram_gb: float) -> int:
    """Returns quality score for a model name. Returns -1 if it won't fit in RAM."""
    name_lower = name.lower()

    # Check RAM requirement
    ram_needed = 3.0  # default
    for size_key, ram_gb in MODEL_RAM_REQUIREMENTS.items():
        if size_key in name_lower:
            ram_needed = ram_gb
            break

    if ram_needed > available_ram_gb:
        return -1  # won't fit

    # Check score table
    for model_key, score in MODEL_SCORES.items():
        if model_key.lower().split(":")[0] in name_lower or name_lower.startswith(model_key.lower().split(":")[0]):
            return score

    return 30  # unknown model — low score but may still work


def _select_best_from_found(all_models: List[Dict], available_ram_gb: float) -> Optional[Dict]:
    """Picks the highest-scoring model that fits in available RAM."""
    scored = []
    for m in all_models:
        score = _score_model(m["name"], available_ram_gb)
        if score > 0:
            scored.append((score, m))

    if not scored:
        return None

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_model = scored[0]
    logger.info(f"Best model found: {best_model['name']} (score={best_score})")
    return best_model


def _load_cached_config() -> Optional[Dict[str, Any]]:
    """Loads previously detected config — never re-scans."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def _save_config(config: Dict[str, Any]):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    logger.info(f"LLM config saved to {CONFIG_PATH}")


class LocalLLMManager:
    def __init__(self, bus=None):
        self.bus = bus
        self.ollama_available = False
        self.selected_model: Optional[str] = None
        self.embed_model: Optional[str] = None
        self.model_source: str = "none"   # "ollama" | "filesystem" | "downloaded"
        self._base_url = "http://localhost:11434"

    async def initialize(self):
        """
        Smart initialization:
        - If config exists → use cached config immediately (no scan).
        - If first run → full system scan, pick best, save config.
        - If nothing found → auto-download the best model for this PC's specs.
        """
        # ── Try cache first ─────────────────────────────────────────────────
        cached = _load_cached_config()
        if cached:
            self.selected_model = cached.get("model")
            self.embed_model = cached.get("embed_model", "nomic-embed-text")
            self.model_source = cached.get("source", "ollama")
            await self._publish(
                f"Using cached local model: {self.selected_model} "
                f"(source: {self.model_source}) — skipping scan"
            )
            # Just make sure Ollama is running
            if self.model_source == "ollama":
                await self._ensure_ollama_running()
                self.ollama_available = _is_ollama_running()
            return

        # ── First run: full system scan ─────────────────────────────────────
        await self._publish("First run — scanning entire system for local models...")

        total_ram = _get_total_ram_gb()
        available_ram = _get_available_ram_gb()
        await self._publish(f"System RAM: {total_ram:.1f} GB total, {available_ram:.1f} GB available")

        all_found: List[Dict] = []

        # Ensure Ollama is running for its API scan
        await self._ensure_ollama_running()
        if _is_ollama_running():
            self.ollama_available = True
            ollama_models = _get_ollama_models()
            await self._publish(f"Ollama: found {len(ollama_models)} installed model(s)")
            all_found.extend(ollama_models)

        # Filesystem scan
        await self._publish("Scanning filesystem for model files (HuggingFace, LM Studio, GPT4All, llamafile)...")
        fs_models = _scan_filesystem_models()
        await self._publish(f"Filesystem: found {len(fs_models)} model file(s)")
        all_found.extend(fs_models)

        # Pick best
        best = _select_best_from_found(all_found, available_ram)

        if best:
            self.selected_model = best["name"]
            self.model_source = best["source"]
            self.embed_model = "nomic-embed-text"

            await self._publish(
                f"✅ Selected: {self.selected_model} "
                f"({self.model_source}, {best.get('size_gb', 0):.1f} GB)"
            )

            # For filesystem models that aren't Ollama — try to register with Ollama
            if self.model_source == "filesystem" and best.get("path"):
                await self._try_register_with_ollama(best["name"], best["path"])
        else:
            # Nothing found anywhere — download best model for this spec
            tier = self._select_download_tier(available_ram)
            await self._publish(
                f"No local models found. Downloading {tier['model']} "
                f"(requires ~{tier['ram']}GB RAM)..."
            )
            await self._ensure_ollama_running()
            if not _is_ollama_running():
                await self._publish("WARNING: Ollama unavailable — running in cloud-only mode.", level="warning")
                return

            self.ollama_available = True
            await self._pull_model_with_progress(tier["model"])
            self.selected_model = tier["model"]
            self.embed_model = tier["embed"]
            self.model_source = "downloaded"

        # Ensure embed model is available
        if self.ollama_available:
            ollama_names = [m["name"].split(":")[0] for m in _get_ollama_models()]
            embed_base = self.embed_model.split(":")[0] if self.embed_model else ""
            if embed_base and embed_base not in ollama_names:
                await self._publish(f"Downloading embedding model: {self.embed_model}")
                await self._pull_model_with_progress(self.embed_model)
            else:
                await self._publish(f"Embedding model {self.embed_model} ready.")

        # Save config — never scan again
        config = {
            "model": self.selected_model,
            "embed_model": self.embed_model,
            "source": self.model_source,
            "total_ram_gb": total_ram,
            "scanned_at": __import__("time").time()
        }
        _save_config(config)
        await self._publish(f"Config saved. Future boots will skip the scan.")

    def _select_download_tier(self, available_ram_gb: float) -> Dict:
        for tier in DOWNLOAD_TIERS:
            if available_ram_gb >= tier["min_gb"]:
                return tier
        return DOWNLOAD_TIERS[-1]

    async def _ensure_ollama_running(self):
        """Starts the Ollama daemon if not running."""
        if _is_ollama_running():
            return
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            await asyncio.sleep(3)
        except FileNotFoundError:
            await self._publish("Ollama binary not found. Install from https://ollama.ai", level="warning")

    async def _try_register_with_ollama(self, name: str, path: str):
        """Tries to register a GGUF file with Ollama via Modelfile."""
        try:
            modelfile_content = f"FROM {path}"
            modelfile_path = f"/tmp/atlas_modelfile_{name.replace('/', '_')}"
            with open(modelfile_path, "w") as f:
                f.write(modelfile_content)

            proc = await asyncio.create_subprocess_exec(
                "ollama", "create", f"atlas-{name.split('.')[0]}", "-f", modelfile_path,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.wait()
            if proc.returncode == 0:
                self.selected_model = f"atlas-{name.split('.')[0]}"
                self.ollama_available = True
                await self._publish(f"Registered {name} with Ollama as {self.selected_model}")
        except Exception as e:
            logger.warning(f"Could not register model with Ollama: {e}")

    async def _pull_model_with_progress(self, model_name: str):
        """Streams download progress to EventBus."""
        try:
            import urllib.request
            url = f"{self._base_url}/api/pull"
            data = json.dumps({"name": model_name}).encode()
            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("Content-Type", "application/json")

            with urllib.request.urlopen(req, timeout=600) as response:
                last_pct = -1
                for line in response:
                    try:
                        msg = json.loads(line.decode().strip())
                        total = msg.get("total", 0)
                        completed = msg.get("completed", 0)
                        if total > 0:
                            pct = int(completed / total * 100)
                            if pct != last_pct and pct % 5 == 0:
                                await self._publish(f"⬇️ {model_name}: {pct}%")
                                last_pct = pct
                        elif msg.get("status") == "success":
                            await self._publish(f"✅ Download complete: {model_name}")
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Failed to pull {model_name}: {e}")
            await self._publish(f"Download failed: {model_name}", level="warning")

    def call_local(self, messages: List[Dict[str, str]], system: str = "") -> str:
        """Calls the local Ollama model synchronously."""
        if not self.ollama_available or not self.selected_model:
            raise RuntimeError("Local LLM not available")

        import urllib.request
        payload = {
            "model": self.selected_model,
            "messages": messages,
            "stream": False
        }
        if system:
            payload["system"] = system

        data = json.dumps(payload).encode()
        req = urllib.request.Request(f"{self._base_url}/api/chat", data=data, method="POST")
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=120) as r:
            result = json.loads(r.read())
            return result.get("message", {}).get("content", "")

    def get_embedding(self, text: str) -> List[float]:
        """Returns embedding vector for the given text using Ollama.
        Tries both /api/embed (new) and /api/embeddings (legacy) endpoints."""
        if not self.ollama_available or not self.embed_model:
            return []

        import urllib.request

        # Try new endpoint first (/api/embed, Ollama >= 0.3)
        for endpoint, payload_key, result_key in [
            ("/api/embed", "input", "embeddings"),
            ("/api/embeddings", "prompt", "embedding"),
        ]:
            try:
                payload = {"model": self.embed_model, payload_key: text}
                data = json.dumps(payload).encode()
                req = urllib.request.Request(
                    f"{self._base_url}{endpoint}", data=data, method="POST"
                )
                req.add_header("Content-Type", "application/json")
                with urllib.request.urlopen(req, timeout=30) as r:
                    result = json.loads(r.read())
                    if result_key == "embeddings":
                        embs = result.get("embeddings", [[]])
                        return embs[0] if embs else []
                    else:
                        return result.get("embedding", [])
            except Exception:
                continue

        return []

    def reset_config(self):
        """Deletes the cached config — forces a full re-scan on next boot."""
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
            logger.info("LLM config reset — will re-scan on next boot")

    async def _publish(self, message: str, level: str = "info"):
        if self.bus:
            await self.bus.publish("NOTIFICATION", {
                "type": "NOTIFICATION",
                "level": level,
                "source": "local_llm",
                "message": message
            })
        logger.info(f"[LocalLLM] {message}")
