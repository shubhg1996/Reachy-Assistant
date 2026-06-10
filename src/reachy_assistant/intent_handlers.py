class IntentHandlers:
    def __init__(self, camera_handler):
        self.camera_handler = camera_handler
        # Map intent names to handler methods
        self.handlers = {
            "take_picture": self._handle_take_picture,
            "chat": self._handle_chat,
        }
        # Descriptions of what each intent does (used by the LLM to align its response)
        self.intent_descriptions = {
            "take_picture": "The robot will take a photo using its camera.",
            "chat": "No action – just respond naturally.",
        }

    @property
    def intents(self):
        """Return list of available intent names."""
        return list(self.handlers.keys())

    def get_intent_descriptions(self):
        """Return dict of intent -> description for LLM prompting."""
        return self.intent_descriptions

    def process(self, intent, response, parameters):
        handler = self.handlers.get(intent, self.handlers["chat"])
        return handler(intent, response, parameters)

    def _handle_take_picture(self, intent, response, parameters):
        path, status = self.camera_handler.take_picture()
        if path:
            response += f" (Saved picture as {path})"
        else:
            response += f" (Failed to take picture: {status})"
        return response

    def _handle_chat(self, intent, response, parameters):
        return response
