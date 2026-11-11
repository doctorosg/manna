from pathlib import Path

import soundfile as sf
from kokoro_onnx import Kokoro


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_DIR = Path("/tmp/manna-kokoro-tts")

kokoro = Kokoro(
    str(MODEL_DIR / "kokoro-v1.0.onnx"),
    str(MODEL_DIR / "voices-v1.0.bin"),
)


def render(filename: str, text: str, voice: str, speed: float) -> None:
    samples, sample_rate = kokoro.create(
        text=text,
        voice=voice,
        speed=speed,
        lang="en-us",
    )
    sf.write(PROJECT_DIR / filename, samples, sample_rate)


# Generate a small casting set so the final reaction is selected from expressive
# performances instead of merely increasing the volume of the previous flat take.
for filename, voice, speed in (
    ("reaction-v4-heart.wav", "af_heart", 0.94),
    ("reaction-v4-bella.wav", "af_bella", 0.94),
    ("reaction-v4-sky.wav", "af_sky", 0.94),
    ("reaction-v4-nova.wav", "af_nova", 0.94),
):
    render(filename, "Is THAT... JESUS?!", voice, speed)


# The selected construction uses separately acted phrases. This creates a real
# anticipatory beat before the name, which can then receive a rising pitch and
# stronger vocal energy without making the entire sentence sound artificial.
render("reaction-v4-lead.wav", "Is that...?", "af_heart", 1.02)
render("reaction-v4-name.wav", "JESUS?!", "af_heart", 0.88)
