"""Arabic voice/text processing adapted from the project's original streamlit_app.py."""
import os
import re
import tempfile
from functools import lru_cache

MEDICAL_ARABIC_PROMPT = """هذا تسجيل طبي باللغة العربية. المريض يصف أعراضه للطبيب.
قد تتضمن الأعراض: صداع، دوخة، غثيان، قيء، حمى، ألم في الصدر،
ألم في البطن، ألم في الظهر، ألم في الحلق، ضيق في التنفس،
سعال، تعب، ضعف، حساسية، سكري، ارتفاع ضغط الدم، ألم في الأذن،
ألم في العين، ألم في الأسنان، ألم في الذراع، خفقان القلب،
فقدان الشهية، الإسهال، الإمساك، التهاب، نزيف."""

ARABIC_CORRECTIONS = {
    "داوخة": "دوخة", "دوخه": "دوخة", "غثيانن": "غثيان", "غسيان": "غثيان",
    "صداء": "صداع", "صدااع": "صداع", "قئ": "قيء", "قيئ": "قيء",
    "حمىة": "حمى", "حمه": "حمى", "الام": "ألم", "الم": "ألم",
    "ضيق التنفسس": "ضيق التنفس", "ضيق نفس": "ضيق في التنفس",
    "سعالل": "سعال", "كحه": "سعال", "كحة": "سعال",
    "سكرى": "سكري", "السكريي": "السكري", "ضغط الدمم": "ضغط الدم",
    "اسهال": "إسهال", "الاسهال": "الإسهال", "امساك": "إمساك", "الامساك": "الإمساك",
}


def contains_arabic(text):
    return bool(re.search(r"[\u0600-\u06ff]", text or ""))


def correct_arabic_medical_text(text):
    # Use word boundaries to avoid replacing parts of longer words.
    for wrong, correct in sorted(ARABIC_CORRECTIONS.items(), key=lambda item: -len(item[0])):
        text = re.sub(r"(?<!\w)" + re.escape(wrong) + r"(?!\w)", correct, text)
    return text


def translate_arabic_to_english(text):
    from deep_translator import GoogleTranslator, MyMemoryTranslator
    text = text.strip()
    if not text:
        return ""
    failures = []
    for provider in (
        lambda: GoogleTranslator(source="ar", target="en"),
        lambda: MyMemoryTranslator(source="ar-SA", target="en-GB"),
    ):
        try:
            result = provider().translate(text)
            if result and result.strip():
                return result.strip()
        except Exception as exc:
            failures.append(str(exc))
    raise RuntimeError("Arabic translation failed with both providers: " + "; ".join(failures))


@lru_cache(maxsize=1)
def _whisper():
    from faster_whisper import WhisperModel
    return WhisperModel("small", device="cpu", compute_type="int8")


def transcribe_audio(audio_bytes, language="ar"):
    if language not in ("ar", "en"):
        raise ValueError("Language must be 'ar' or 'en'")
    path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp:
            temp.write(audio_bytes)
            path = temp.name
        options = dict(language=language, task="transcribe", beam_size=5,
                       temperature=0.0, condition_on_previous_text=True, vad_filter=False)
        if language == "ar":
            options["initial_prompt"] = MEDICAL_ARABIC_PROMPT
        segments, _ = _whisper().transcribe(path, **options)
        transcript = " ".join(seg.text.strip() for seg in segments).strip()
        return correct_arabic_medical_text(transcript) if language == "ar" else transcript
    finally:
        if path and os.path.exists(path):
            os.remove(path)
