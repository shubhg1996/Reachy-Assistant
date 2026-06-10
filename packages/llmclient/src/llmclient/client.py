"""LLM client for interacting with OpenRouter API."""

import base64
import json
import mimetypes
import os

import requests


class LLMClient:
    def __init__(self, api_key=None, base_url="https://openrouter.ai/api/v1"):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Set OPENROUTER_API_KEY or pass it.")
        self.base_url = base_url
        self.timeout = 10

    def generate(self, prompt, model="openai/gpt-3.5-turbo", **kwargs):
        """Simple text generation."""
        headers = self._headers()
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs,
        }
        response = requests.post(
            f"{self.base_url}/chat/completions", json=payload, headers=headers
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def generate_with_intent(
        self,
        user_text,
        intents,
        intent_descriptions=None,
        model="openai/gpt-3.5-turbo",
        timeout=10,
        **kwargs,
    ):
        """Generate a response and classify intent in one API call.
        intent_descriptions: dict mapping intent name to what action the robot will take.
        """
        if intent_descriptions is None:
            intent_descriptions = {
                intent: "The robot will perform an action." for intent in intents
            }

        desc_text = "\n".join(
            [f'- "{intent}": {desc}' for intent, desc in intent_descriptions.items()]
        )
        system_prompt = f"""You are a helpful assistant for the Reachy Mini robot.
    Your tasks:
    1. Classify the user's intent from the list: {", ".join(intents)}. Use "chat" if none match.
    2. Generate a natural language response to the user.

    IMPORTANT: Your response will be spoken by the robot. For each intent, the robot will also perform an action:
    {desc_text}
    If intent is "chat", no action is performed.

    Output a JSON object with:
    {{"intent": "intent_name", "response": "your spoken response"}}
    Do not include any other text."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ]
        payload = {"model": model, "messages": messages, "temperature": 0.7, **kwargs}
        print("[LLM] Calling OpenRouter with intent detection...")
        try:
            # Pass timeout to the _post method (ensure it uses the timeout argument)
            data = self._post("chat/completions", payload, timeout=timeout)
        except Exception as e:
            print(f"[LLM] Error or timeout: {e}")
            # Fallback: treat as chat and generate a simple response
            fallback_response = f"I heard you say: '{user_text}'. I'm having trouble connecting right now, but I'm here to help!"
            return "chat", fallback_response, {}

        content = data["choices"][0]["message"]["content"]
        print(f"[LLM] Raw response: {content[:100]}...")
        try:
            result = json.loads(content)
            intent = result.get("intent", "chat")
            response = result.get("response", "I'm not sure how to respond.")
            params = result.get("parameters", {})
            return intent, response, params
        except json.JSONDecodeError:
            print("[LLM] Invalid JSON – treating as plain chat response")
            return "chat", content, {}

    def _post(self, endpoint, payload, timeout=None):
        url = f"{self.base_url}/{endpoint}"
        timeout = timeout or self.timeout  # fallback to instance default
        try:
            resp = requests.post(
                url, json=payload, headers=self._headers(), timeout=timeout
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {url} timed out after {timeout}s")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def encode_image_to_base64(self, file_path: str) -> str:
        """Convert a local image file into a base64 string for LLM injection."""
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "image/jpeg"

        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

        return f"data:{mime_type};base64,{encoded_string}"
