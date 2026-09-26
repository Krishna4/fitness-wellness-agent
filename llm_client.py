"""
Fitness & Wellness Agent - Provider-Isolated LLM Client
Interfaces with:
1. Google Gemini (gemini-flash-lite-latest) via REST API
2. Local Ollama (qwen2.5:1.5b / llama3)
3. Graceful deterministic fallback
"""

import json
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from config import (
    LLM_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OLLAMA_HOST,
    OLLAMA_MODEL
)

def retry_with_backoff(func, max_retries=3, initial_delay=1.5):
    """Executes func with exponential backoff for rate limits."""
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            err_str = str(e).lower()
            if attempt < max_retries - 1 and ("429" in err_str or "quota" in err_str or "resource_exhausted" in err_str):
                time.sleep(delay)
                delay *= 2.0
            else:
                raise e


class LLMClient:
    """Unified LLM interface supporting Gemini and Ollama with offline fallback."""

    def __init__(self, provider: Optional[str] = None):
        self.provider = (provider or LLM_PROVIDER).lower()
        self.gemini_key = GEMINI_API_KEY
        self.gemini_model = GEMINI_MODEL
        self.ollama_host = OLLAMA_HOST
        self.ollama_model = OLLAMA_MODEL

    def generate(self, prompt: str, system_instruction: str = "") -> str:
        """Generate text response with transparent logging of prompt, model, and latency."""
        start_time = time.time()
        active_model = self.gemini_model if self.provider == "gemini" else self.ollama_model

        print(f"\n" + "─" * 70, flush=True)
        print(f"🤖 [LLM INVOCATION] Provider: {self.provider.upper()} | Model: {active_model}", flush=True)
        print(f"   [System Directive]: {system_instruction[:90]}..." if system_instruction else "   [System Directive]: Default", flush=True)
        print(f"   [Input Prompt]: \"{prompt[:130]}...\"", flush=True)

        response = ""
        try:
            if self.provider == "gemini" and self.gemini_key:
                try:
                    response = self._call_gemini(prompt, system_instruction)
                except Exception as e:
                    print(f"   ⚠️ [Gemini Error]: {e} -> Attempting fallback...", flush=True)
                    response = self._call_ollama(prompt, system_instruction) if self._is_ollama_available() else self._offline_fallback(prompt)

            elif self.provider == "ollama":
                try:
                    response = self._call_ollama(prompt, system_instruction)
                except Exception as e:
                    print(f"   ⚠️ [Ollama Error]: {e} -> Attempting fallback...", flush=True)
                    response = self._offline_fallback(prompt)
            else:
                response = self._offline_fallback(prompt)

        finally:
            elapsed = time.time() - start_time
            preview = response.replace('\n', ' ')[:95]
            print(f"   ✓ [LLM Response Received in {elapsed:.2f}s]: \"{preview}...\"", flush=True)
            print("─" * 70 + "\n", flush=True)

            # Append to persistent trace log
            try:
                with open("llm_execution.log", "a", encoding="utf-8") as f:
                    log_entry = {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "provider": self.provider,
                        "model": active_model,
                        "prompt": prompt,
                        "system_instruction": system_instruction,
                        "latency_sec": round(elapsed, 2),
                        "response_preview": preview
                    }
                    f.write(json.dumps(log_entry) + "\n")
            except Exception:
                pass

        return response

    def _call_gemini(self, prompt: str, system_instruction: str = "") -> str:
        """Call Google Gemini REST API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_key}"
        
        contents = []
        if system_instruction:
            contents.append({"role": "user", "parts": [{"text": f"System Guidelines: {system_instruction}\n\nUser Task: {prompt}"}]})
        else:
            contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 600
            }
        }

        def _request():
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode())
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()

        return retry_with_backoff(_request)

    def _call_ollama(self, prompt: str, system_instruction: str = "") -> str:
        """Call local Ollama instance."""
        url = f"{self.ollama_host}/api/generate"
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        payload = {
            "model": self.ollama_model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 400
            }
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("response", "").strip()

    def _is_ollama_available(self) -> bool:
        """Check if local Ollama daemon is reachable."""
        try:
            req = urllib.request.Request(f"{self.ollama_host}/api/tags")
            with urllib.request.urlopen(req, timeout=1):
                return True
        except Exception:
            return False

    def _offline_fallback(self, prompt: str) -> str:
        """Deterministic rule-based fallback if external LLMs are unreachable."""
        return "Guidance generated via deterministic rule engine (Offline/Grounding Mode)."
