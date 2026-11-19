import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Ensure Backend/.env is loaded
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Log directory
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LLM_LOG_FILE = LOG_DIR / "llm_interactions.log"


class LLMManager:
    """
    Centralized LLM execution & logging engine.
    Logs EVERY request and EVERY response with timestamps, parameters, latency,
    and token metrics to both stdout and a structured persistent log file.
    """

    MODEL_NAME = "qwen/qwen3.8-27b"
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            api_key = os.getenv("GROQ_API_KEY", "").strip()
            if not api_key:
                return None
            try:
                from groq import Groq
                cls._client = Groq(api_key=api_key)
            except Exception as e:
                print(f"[LLMManager] Groq initialization warning: {e}")
                cls._client = None
        return cls._client

    @classmethod
    def call_llm(
        cls,
        prompt: str,
        system_instruction: str = "You are an elite, objective technical interviewer and talent assessor.",
        temperature: float = 0.3,
        max_tokens: int = 1200,
        context_name: str = "General",
        response_format: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Executes an LLM chat completion, comprehensively logging both the request and response.
        """
        client = cls.get_client()
        timestamp_req = datetime.now(timezone.utc).isoformat()
        req_id = f"req_{int(time.time() * 1000)}"

        # -------------------------------------------------------------
        # 1. LOG REQUEST
        # -------------------------------------------------------------
        req_log_entry = {
            "event": "LLM_REQUEST",
            "request_id": req_id,
            "context": context_name,
            "timestamp": timestamp_req,
            "model": cls.MODEL_NAME,
            "system_instruction": system_instruction,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Terminal banner
        print("\n" + "=" * 70)
        print(f"🤖 [LLM REQUEST] Context: {context_name} | ID: {req_id}")
        print(f"🕒 Timestamp: {timestamp_req}")
        print(f"🧠 Model:     {cls.MODEL_NAME}")
        print("-" * 70)
        print("📋 System Instruction:")
        print(system_instruction[:300] + ("..." if len(system_instruction) > 300 else ""))
        print("-" * 70)
        print("💬 Prompt:")
        print(prompt[:600] + ("..." if len(prompt) > 600 else ""))
        print("=" * 70 + "\n")

        # Persist to log file
        cls._append_to_log(req_log_entry)

        if not client:
            print(f"[LLMManager] Groq client unavailable. Falling back to rule-based engine.")
            return None

        # -------------------------------------------------------------
        # 2. EXECUTE LLM CALL
        # -------------------------------------------------------------
        start_time = time.perf_counter()
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]

        kwargs: Dict[str, Any] = {
            "model": cls.MODEL_NAME,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        try:
            chat_completion = client.chat.completions.create(**kwargs)
            latency_ms = round((time.perf_counter() - start_time) * 1000, 1)
            timestamp_res = datetime.now(timezone.utc).isoformat()

            raw_response = chat_completion.choices[0].message.content or ""
            usage = getattr(chat_completion, "usage", None)
            tokens_info = {
                "prompt_tokens": getattr(usage, "prompt_tokens", None) if usage else None,
                "completion_tokens": getattr(usage, "completion_tokens", None) if usage else None,
                "total_tokens": getattr(usage, "total_tokens", None) if usage else None,
            }

            # -------------------------------------------------------------
            # 3. LOG RESPONSE
            # -------------------------------------------------------------
            res_log_entry = {
                "event": "LLM_RESPONSE",
                "request_id": req_id,
                "context": context_name,
                "timestamp": timestamp_res,
                "latency_ms": latency_ms,
                "model": cls.MODEL_NAME,
                "tokens": tokens_info,
                "response": raw_response,
            }

            # Terminal banner
            print("\n" + "#" * 70)
            print(f"✨ [LLM RESPONSE] Context: {context_name} | ID: {req_id} | Latency: {latency_ms}ms")
            print(f"🕒 Timestamp: {timestamp_res}")
            print(f"📊 Tokens:    Prompt={tokens_info.get('prompt_tokens')} | Completion={tokens_info.get('completion_tokens')} | Total={tokens_info.get('total_tokens')}")
            print("-" * 70)
            print("📝 Content:")
            print(raw_response[:800] + ("..." if len(raw_response) > 800 else ""))
            print("#" * 70 + "\n")

            # Persist to log file
            cls._append_to_log(res_log_entry)

            return raw_response

        except Exception as e:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 1)
            err_log_entry = {
                "event": "LLM_ERROR",
                "request_id": req_id,
                "context": context_name,
                "latency_ms": latency_ms,
                "error": str(e)
            }
            print(f"\n❌ [LLM ERROR] ID: {req_id} | {e}\n")
            cls._append_to_log(err_log_entry)
            return None

    @classmethod
    def _append_to_log(cls, entry: Dict[str, Any]):
        try:
            with open(LLM_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[LLMManager] Warning: failed to write to log file: {e}")
