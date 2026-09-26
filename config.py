"""
Fitness & Wellness Agent - Configuration Loader
Supports:
1. Google Gemini (default: gemini-flash-lite-latest)
2. Local Ollama (default: qwen2.5:1.5b at http://localhost:11434)
3. Deterministic Fallback (if offline or API key missing)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Search for .env in project directory, then parent directory
env_path = BASE_DIR / ".env"
parent_env_path = BASE_DIR.parent / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
elif parent_env_path.exists():
    load_dotenv(dotenv_path=parent_env_path)
else:
    load_dotenv()

# LLM Provider Configuration ('gemini', 'ollama', or 'deterministic')
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

# Gemini Settings (Default: gemini-flash-lite-latest)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")

# Ollama Settings (Configurable for local execution)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

# Storage Path
MEMORY_STORAGE_PATH = BASE_DIR / "fitness_memory.json"
