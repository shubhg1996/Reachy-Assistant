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
        user_text = update.message.text
        chat_id = update.effective_chat.id

        current_loop = asyncio.get_running_loop()
        agent_reply = await current_loop.run_in_executor(
            None, self.runtime.run_turn, user_text
        )

        if agent_reply:
            # 1. Deliver the final conversational text reply from the LLM
            await update.message.reply_text(agent_reply)

            # 2. Check the runtime for any files generated during this specific turn
            if self.runtime.pending_output_files:
                for file_path in self.runtime.pending_output_files:
                    # Check if the photo file exists locally and transmit it natively over the wire
                    if os.path.exists(file_path):
                        print(
                            f"[Channel: Telegram] Uploading captured asset: {file_path}"
                        )
                        with open(file_path, "rb") as photo_file:
                            try:
                                await update.message.reply_photo(
                                    photo=photo_file,
                                    caption="📸 Image transmission complete.",
                                    write_timeout=60,  # Extends upload write frame to prevent exceptions
                                    read_timeout=60,
                                )
                            except Exception as upload_err:
                                print(
                                    f"[Channel: Telegram] Network upload notice (suppressed): {upload_err}"
                                )

            # 3. Cross-channel routing for physical text-to-speech voice if enabled
            if self.runtime.state.get("voice_out_enabled") and self.voice_out_channel:
                print(
                    f"[Channel: Telegram] Voice mode active. Routing text payload to speaker..."
                )
                threading.Thread(
                    target=self.voice_out_channel.send, args=(agent_reply,), daemon=True
                ).start()

    def stop(self):
        """Stops the polling pipeline cleanly."""
        if self._app and self._loop:
            print("[Channel: Telegram] Halting polling loops...")
            self._loop.call_soon_threadsafe(self._app.stop)
