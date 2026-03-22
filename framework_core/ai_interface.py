
import requests
import json
import os


class AIEngine:
    """
    Encapsulates communication with a local Ollama language-model service.
    Sends prompts, requests JSON-formatted responses for predictable parsing,
    and returns a safe, structured fallback when the model output is missing
    or malformed.
    """

    def __init__(self, config, model: str = None):
        self.url = config.ollama_url
        # Example local endpoint (uncomment to override during development):
        # self.url = "http://localhost:11434/api/chat"
        self.model = model or os.getenv(config.ollama_url, config.ollama_model)

    def generate(self, prompt: str) -> dict:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"  # 🔥 Force JSON response
        }

        try:
            response = requests.post(self.url, json=payload, timeout=60)
            response.raise_for_status()

            raw_output = response.json().get("response", "")

            try:
                return json.loads(raw_output)
            except json.JSONDecodeError:
                # Model returned non-JSON text; provide a predictable fallback
                return {
                    "detected_error": "Unknown",
                    "suggested_locator": "N/A",
                    "reason": raw_output.strip()
                }

        except Exception as e:
            # Network, timeout, or engine-level failure — return structured error info
            return {
                "detected_error": "AI Engine Failure",
                "suggested_locator": "N/A",
                "reason": str(e)
            }
