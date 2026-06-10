"""OpenClaw Telegram Surface: Handles remote text messaging via native long-polling bot API."""

import asyncio
import os
import re
import threading

from telegram import Bot
from telegram.ext import Application, ContextTypes, MessageHandler, filters


class TelegramChannel:
    def __init__(self, agent_runtime, token=None, voice_out_channel=None):
        self.runtime = agent_runtime
        self.voice_out_channel = voice_out_channel
        # Pull from environment or fallback
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN")

        if not self.token:
            print("⚠️ Warning: TELEGRAM_BOT_TOKEN not found in environment!")

        self._loop = None
        self._app = None

    def listen(self):
        """Starts the native Telegram async polling loop in a background thread."""
        if not self.token:
            return

        print("[Channel: Telegram] Initializing native Telegram bot surface...")

        # Fire up the async loop inside a dedicated background thread
        threading.Thread(target=self._start_async_loop, daemon=True).start()

    def _start_async_loop(self):
        # Create an isolated async event loop for this background thread
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        # Build the application instance
        self._app = Application.builder().token(str(self.token)).build()

        # Register the incoming message handler
        self._app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )

        print(
            "🤖 [Channel: Telegram] Bot listening natively. Text your bot to communicate!"
        )

        # FIX: Explicitly disable signal interceptions so it runs smoothly inside a thread
        self._loop.run_until_complete(
            self._app.run_polling(
                close_loop=False,
                stop_signals=False,
            )
        )

    async def _handle_message(self, update, context):
        """Call whenever someone texts the Telegram bot."""
        user_text = update.message.text
        chat_id = update.effective_chat.id

        print(f"\n💬 [Channel: Telegram] Incoming from chat {chat_id}: '{user_text}'")

        # Offload the blocking runtime turn to our worker thread executor
        current_loop = asyncio.get_running_loop()
        agent_reply = await current_loop.run_in_executor(
            None, self.runtime.run_turn, user_text
        )

        if agent_reply:
            # Regex pattern to seek out our embedded file path token
            file_match = re.search(r"\[FILE_PATH:\s*(.*?)\]", agent_reply)

            if file_match:
                photo_path = file_match.group(1).strip()
                # Clean up the spoken/text response by removing the structural token
                clean_reply = re.sub(r"\[FILE_PATH:\s*(.*?)\]", "", agent_reply).strip()

                # Send the cleaned up text message context first
                if clean_reply:
                    await update.message.reply_text(clean_reply)

                # Check if the photo file exists locally and transmit it natively over the wire!
                if os.path.exists(photo_path):
                    print(
                        f"[Channel: Telegram] Uploading photo asset over Telegram API: {photo_path}"
                    )
                    with open(photo_path, "rb") as photo_file:
                        await update.message.reply_photo(
                            photo=photo_file, caption="📸 Here is your captured frame!"
                        )
                else:
                    await update.message.reply_text(
                        "⚠️ Image file generated but target asset path was lost."
                    )
            else:
                # Fallback path if no file tokens are attached to this conversational turn
                await update.message.reply_text(agent_reply)

            # Cross-channel routing for physical voice if enabled globally
            if self.runtime.state.get("voice_out_enabled") and self.voice_out_channel:
                print(
                    f"[Channel: Telegram] Voice mode active. Routing text payload to speaker..."
                )
                # Strip out the token from what the robot physically reads out loud in the room
                voice_text = re.sub(r"\[FILE_PATH:\s*(.*?)\]", "", agent_reply).strip()
                threading.Thread(
                    target=self.voice_out_channel.send, args=(voice_text,), daemon=True
                ).start()

    def stop(self):
        """Stops the polling pipeline cleanly."""
        if self._app and self._loop:
            print("[Channel: Telegram] Halting polling loops...")
            self._loop.call_soon_threadsafe(self._app.stop)
