"""
translator.py — Core translation logic using deep-translator (no API key needed).
Supports 100+ languages and automatic language detection.
"""

from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

# ---------------------------------------------------------------------------
# Supported languages — pulled once from GoogleTranslator so the list is
# always up-to-date with the library version.
# ---------------------------------------------------------------------------
SUPPORTED_LANGUAGES = GoogleTranslator().get_supported_languages(as_dict=True)
# e.g. {"afrikaans": "af", "albanian": "sq", ...}


def get_language_list():
    """Return a list of dicts: [{"name": "Afrikaans", "code": "af"}, ...]"""
    return [
        {"name": name.title(), "code": code}
        for name, code in sorted(SUPPORTED_LANGUAGES.items())
    ]


def detect_language(text: str) -> str:
    """
    Detect the language of *text* and return its ISO-639-1 code.
    Returns 'unknown' when detection fails.
    """
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def translate_text(text: str, source: str = "auto", target: str = "en") -> dict:
    """
    Translate *text* from *source* language to *target* language.

    Parameters
    ----------
    text   : str  — The text to translate.
    source : str  — Source language code ('auto' for auto-detect).
    target : str  — Target language code (e.g. 'es', 'fr', 'hi').

    Returns
    -------
    dict with keys:
        translated_text  — The translated string.
        detected_language — Detected source language code (if auto-detect).
        source           — Source language code used.
        target           — Target language code used.
        success          — Boolean indicating success.
        error            — Error message (empty string on success).
    """
    try:
        # Detect language when source is set to 'auto'
        detected = detect_language(text) if source == "auto" else source

        # Perform translation
        translator = GoogleTranslator(source=source, target=target)
        result = translator.translate(text)

        return {
            "translated_text": result,
            "detected_language": detected,
            "source": source,
            "target": target,
            "success": True,
            "error": "",
        }
    except Exception as exc:
        return {
            "translated_text": "",
            "detected_language": "",
            "source": source,
            "target": target,
            "success": False,
            "error": str(exc),
        }
