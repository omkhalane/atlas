# Atlas Agent Utilities & Key Tester CLI

The `.agents/` directory contains CLI utilities and helper scripts for testing, managing, and verifying Atlas runtime providers and API keys.

---

## 🔑 Key Tester CLI (`key_tester.py`)

The Key Tester CLI automatically detects provider types from API keys, queries model catalogs, tests completion latency, and verifies key validity.

### 🚀 Quick Usage

Run interactively:
```bash
python3 .agents/key_tester.py
```

Pass key directly:
```bash
python3 .agents/key_tester.py --key sk-or-v1-803fe2...
```

Test local Ollama / LM Studio endpoint:
```bash
python3 .agents/key_tester.py --base-url http://localhost:11434 --provider ollama
```

Test specific provider & model:
```bash
python3 .agents/key_tester.py --key sk-ant-api03-... --provider anthropic --model claude-3-5-sonnet-20241022
```

---

## 🌟 Features
- **Provider Auto-Detection**: Auto-detects OpenRouter (`sk-or-`), Anthropic (`sk-ant-`), OpenAI (`sk-`), Groq (`gsk_`), Gemini (`AIzaSy`), or Local endpoints.
- **Model Catalog Auto-Discovery**: Lists up to 15+ available models accessible by the provided API key.
- **Inference Latency Test**: Measures exact completion latency in milliseconds (`[145.2ms]`).
- **Zero External Dependencies**: Runs using standard Python standard libraries.
