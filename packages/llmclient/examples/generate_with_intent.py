from llmclient import LLMClient

client = LLMClient()
try:
    intent, resp, params = client.generate_with_intent("say hello", ["chat"], timeout=5)
    print(f"Intent: {intent}, Response: {resp}")
except Exception as e:
    print(f"Failed: {e}")
