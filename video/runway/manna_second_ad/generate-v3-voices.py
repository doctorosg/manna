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


# The punctuation and brighter voice are intentional performance direction:
# astonishment first, then recognition and excitement on “Jesus”.
render(
    "natural-surprise-v3.wav",
    "Is that Jesus?!",
    "af_nova",
    1.00,
)

# “Reed” is supplied phonetically to remove the read/red ambiguity. The
# burned-in subtitle remains the correctly spelled sentence with “read”.
render(
    "natural-jesus-lesson-v3.wav",
    "You have to reed your Bible to know your Bible.",
    "bm_george",
    1.02,
)
