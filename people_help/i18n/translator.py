"""
Translation service with feature flag.

IMPORTANT: Translation is currently DISABLED and will return English text only.
To enable translations in the future, set TRANSLATION_ENABLED=true in .env
"""
import os
from typing import Dict, Optional

# Feature flag - DISABLED by default
TRANSLATION_ENABLED = os.getenv("TRANSLATION_ENABLED", "false").lower() == "true"

# Placeholder translations - will be populated when translation is enabled
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {},
    "yo": {},
    "ha": {},
    "ig": {}
}


def translate(key: str, language: str = "en", **kwargs) -> str:
    """
    Translate a key to the specified language.
    
    Args:
        key: Translation key
        language: Target language code (en, yo, ha, ig)
        **kwargs: Variables to interpolate into the translation
    
    Returns:
        Translated string (currently returns key as-is since translation is disabled)
    """
    if not TRANSLATION_ENABLED:
        # Translation disabled - return the key as-is
        return key
    
    # Future implementation: lookup translation from TRANSLATIONS dict
    translation = TRANSLATIONS.get(language, {}).get(key, key)
    
    # Interpolate variables if provided
    if kwargs:
        try:
            translation = translation.format(**kwargs)
        except KeyError:
            pass
    
    return translation


def get_language_name(language_code: str) -> str:
    """Get the full name of a language from its code."""
    language_names = {
        "en": "English",
        "yo": "Yoruba",
        "ha": "Hausa",
        "ig": "Igbo"
    }
    return language_names.get(language_code, "Unknown")
