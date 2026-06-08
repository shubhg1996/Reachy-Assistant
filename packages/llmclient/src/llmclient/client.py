"""LLM client for interacting with OpenRouter API."""

import os

import requests


class LLMClient:
    """LLM client for interacting with OpenRouter API."""

    def __init__(self, api_key=None, base_url="https://openrouter.ai/api/v1"):
        """Initialize the LLM client with an API key and base URL."""
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Set OPENROUTER_API_KEY or pass it.")
        self.base_url = base_url

    def generate(self, prompt, model="openai/gpt-3.5-turbo", **kwargs):
        """Generate a response from the LLM model based on the given prompt."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
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
