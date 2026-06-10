"""OpenClaw WhatsApp Surface: Handles remote text messaging interface."""

import threading
import time

import requests  # Assuming a lightweight local HTTP bridge/webhook to a WhatsApp client API


class WhatsAppChannel:
    def __init__(self, agent_runtime, bridge_url="http://localhost:3000"):
        self.runtime = agent_runtime
        self.bridge_url = bridge_url
        self._running = False
        self.last_checked_timestamp = time.time()

    def listen(self):
        """Starts the background listening loop for incoming messages."""
        if self._running:
            return
        self._running = True
        print("[Channel: WhatsApp] Initializing WhatsApp bridge surface...")

        # Start a polling or webhook monitoring thread
        threading.Thread(target=self._poll_messages_loop, daemon=True).start()

    def stop(self):
        """Stops the channel."""
        self._running = False

    def _poll_messages_loop(self):
        """Polls a local whatsapp-web.js api bridge for new messages."""
        while self._running:
            try:
                # Example endpoint fetching unread incoming messages from your bridge
                response = requests.get(
                    f"{self.bridge_url}/v1/messages?unread=true", timeout=2
                )
                if response.status_code == 200:
                    messages = response.json().get("messages", [])
                    for msg in messages:
                        self._handle_incoming_message(msg)
            except Exception as e:
                # Suppress flood logs, but track connectivity drops
                pass
            time.sleep(2.0)  # Rest between poll frames

    def _handle_incoming_message(self, msg_payload):
        """Processes text turns through the main runtime engine."""
        user_text = msg_payload.get("body", "")
        chat_id = msg_payload.get("from")  # Unique phone identification string

        if not user_text.strip():
            return

        print(f"\n💬 [Channel: WhatsApp] Incoming from {chat_id}: '{user_text}'")

        # Route directly to your shared, stateful agent engine
        agent_reply = self.runtime.run_turn(user_text)

        # Send the final conversational output back to the user on WhatsApp
        if agent_reply:
            self.send(agent_reply, target_id=chat_id)

    def send(self, text: str, target_id: str):
        """Pushes textual replies back to the remote WhatsApp recipient endpoint."""
        print(f"[Channel: WhatsApp] Sending response out to {target_id}...")
        try:
            payload = {"to": target_id, "body": text}
            requests.post(f"{self.bridge_url}/v1/messages", json=payload, timeout=5)
        except Exception as e:
            print(f"[Channel: WhatsApp] Failed to transmit message payload: {e}")
