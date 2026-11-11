from pathlib import Path

import soundfile as sf
from kokoro_onnx import Kokoro


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_DIR = Path("/tmp/manna-kokoro-tts")

kokoro = Kokoro(
    str(MODEL_DIR / "kokoro-v1.0.onnx"),
    str(MODEL_DIR / "voices-v1.0.bin"),
)


def render_text(filename: str, text: str, voice: str, speed: float) -> None:
    samples, sample_rate = kokoro.create(
        text=text,
        voice=voice,
        speed=speed,
        lang="en-us",
    )
    sf.write(PROJECT_DIR / filename, samples, sample_rate)


def render_phonemes(filename: str, phonemes: str, voice: str, speed: float) -> None:
    samples, sample_rate = kokoro.create(
        text=phonemes,
        voice=voice,
        speed=speed,
        lang="en-us",
        is_phonemes=True,
    )
    sf.write(PROJECT_DIR / filename, samples, sample_rate)


# A fresh single-take performance is used as the source for the shocked
# reaction. Dynamic pitch and loudness shaping are applied after rendering.
render_text(
    "reaction-v5-raw.wav",
    "IS THAT JESUS?!",
    "af_bella",
    0.90,
)

# Do not allow the ambiguous spelling “read” to reach the phonemizer. The IPA
# sequence ɹˈiːd explicitly forces present-tense “reed”. The two halves are
# separate files so the requested two-second pause is deterministic.
render_phonemes(
    "jesus-lesson-v5-part1.wav",
    "juː hæv tə ɹˈiːd jʊɹ bˈaɪbəl.",
    "bm_george",
    0.98,
)
render_phonemes(
    "jesus-lesson-v5-part2.wav",
    "tə nˈoʊ jʊɹ bˈaɪbəl.",
    "bm_george",
    0.98,
)
