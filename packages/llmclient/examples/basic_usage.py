"""Basic usage example for the LLM client."""

from llmclient import LLMClient

client = LLMClient()  # reads OPENROUTER_API_KEY from env

response = client.generate("Explain quantum computing in one sentence")
print(response)
