"""OpenClaw System Gateway: Coordinates hardware initialization, runtimes, skills, and surfaces."""

import time

from llmclient import LLMClient
from reachy_mini_lib import ReachyRobot

from .agent.memory_manager import MemoryManager
from .agent.runtime import AgentRuntime
from .channels.telegram_channel import TelegramChannel
from .channels.voice_channel import VoiceChannel
from .channels.whatsapp_channel import WhatsAppChannel
from .skills.express_emotion import ExpressEmotionSkill
from .skills.take_picture import TakePictureSkill
from .skills.toggle_modality import ToggleModalitySkill


class Gateway:
    """Manages the gateway layer, coordinating hardware initialization, runtimes, skills, and surfaces."""

    def __init__(self):
        """Initialize the gateway, setting up hardware and runtime dependencies."""
        # 1. Connect to the underlying physical or simulated hardware platform
        self.robot = ReachyRobot(media_backend="gstreamer")

        # 2. Instantiate core memory and agent runtime management dependencies
        self.memory_manager = MemoryManager()
        self.runtime = AgentRuntime(
            llm_client=None, memory_manager=self.memory_manager
        )  # Client dynamically attached below

        self.voice_channel = None
        self.voice_channel = None
        self.whatsapp_channel = None
        self.telegram_channel = None

    def initialize(self):
        """Prepare state profiles, wakes motor matrices, and attaches plugin skills."""
        print("[Gateway] Bootstrapping robot runtime platforms...")

        # Wake up motors with gravity compensation defaults
        self.robot.torque.wake_up()

        # 2. PHYSICAL MOTION WAKE MATRIX
        # Smoothly actuate Reachy Mini from its collapsed resting pose to its alert starting posture
        print("[Gateway] Actuating Reachy Mini to default alert pose...")
        try:
            # Set head to look straight ahead (roll=0, pitch=0, yaw=0) over 1.5 seconds
            self.robot.motion.set_head(
                roll_deg=0.0, pitch_deg=0.0, yaw_deg=0.0, duration=1.5
            )
            # Set antennas to neutral holding positions
            self.robot.motion.set_antennas(right_deg=0.0, left_deg=0.0, duration=1.0)
            # Center the body yaw axis
            self.robot.motion.set_body_yaw(yaw_deg=0.0, duration=1.0)

            # Brief sleep block to allow the physical motors to complete the transit before initializing the LLM client
            time.sleep(1.5)
            print("[Gateway] Reachy Mini is now standing alert.")
        except Exception as pose_err:
            print(
                f"[Gateway] Warning: Initial hardware wake pose transition failed: {pose_err}"
            )

        # Ingest the underlying OpenRouter orchestration client from runtime context

        llm_client = (
            LLMClient()
        )  # Automatically pulls OPENROUTER_API_KEY from environment
        self.runtime.llm = llm_client

        # Dynamic Tool Binding: Register modular system skills natively
        # Dynamic Tool Binding updates
        self.runtime.register_skill(TakePictureSkill(self.robot))
        self.runtime.register_skill(ExpressEmotionSkill(self.robot))
        self.runtime.register_skill(ToggleModalitySkill(self.runtime))

        # Surface Binding: Mount the physical voice tracking loop
        self.voice_channel = VoiceChannel(self.runtime, self.robot)

        # Mount your brand new WhatsApp channel!
        self.whatsapp_channel = WhatsAppChannel(self.runtime)
        self.whatsapp_channel.listen()

        # Mount your brand new Telegram channel!
        self.telegram_channel = TelegramChannel(
            self.runtime, voice_out_channel=self.voice_channel
        )
        self.telegram_channel.listen()

    def run(self):
        """Enters the persistent execution phase."""
        if not self.voice_channel:
            raise RuntimeError("Gateway run invoked before initialization completed.")

        print("\n🤖 [Gateway] Reachy Assistant fully active via OpenClaw.")
        self.voice_channel.listen()

        import time

        # We removed the try/except. Let main.py handle the interrupt safely.
        while True:
            # 0.1s tick makes it instantly responsive to Ctrl+C
            time.sleep(0.1)

    def shutdown(self):
        """Clean execution drop safely returning physical motors back to sleep poses."""
        print("\n[Gateway] Intercepted shutdown signal. Safely parking robot...")
        if self.voice_channel:
            self.voice_channel.stop()
        if self.whatsapp_channel:
            self.whatsapp_channel.stop()
        if self.telegram_channel:
            self.telegram_channel.stop()

        try:
            self.robot.torque.goto_sleep_pose()
            print("[Gateway] Reachy Mini motors successfully set to sleep pose.")
        except Exception as e:
            print(f"[Gateway] Error during hardware parking matrix drop: {e}")
        print("[Gateway] Shutdown complete.")
