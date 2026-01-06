#!/usr/bin/env python3
"""Interactive translation tool for Chinese and English."""

import sys
import re
import requests
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import GoogleTranslator
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


class TranslationCache:
    """Manages persistent translation cache in user's home directory."""

    def __init__(self):
        """Initialize cache and load from disk."""
        # Cache file in user's home directory
        self.cache_file = Path.home() / ".translate_cache.json"
        self.cache = {}

        # Load existing cache
        self._load()

    def _load(self):
        """Load cache from JSON file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}

    def _save(self):
        """Save cache to JSON file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get(self, word: str) -> str | None:
        """
        Get cached translation for a word.

        Args:
            word: The word to look up

        Returns:
            Cached translation or None if not found
        """
        return self.cache.get(word)

    def add(self, word: str, translation: str):
        """
        Add a translation to cache and save to disk.

        Args:
            word: Original word/text
            translation: Translated result
        """
        self.cache[word] = translation
        self._save()

    def get_cache_info(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache file path and entry count
        """
        return {
            'path': str(self.cache_file),
            'entries': len(self.cache)
        }


def is_chinese(text: str) -> bool:
    """Check if text contains Chinese characters."""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def get_english_synonyms(word: str) -> list:
    """
    Get synonyms and different meanings for an English word.

    Args:
        word: English word to look up

    Returns:
        List of related words/synonyms representing different meanings
    """
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url, timeout=2)  # Reduced from 5s to 2s

        if response.status_code != 200:
            return []

        data = response.json()
        related_words = []

        # Extract synonyms from the API response
        for entry in data:
            if 'meanings' in entry:
                for meaning in entry['meanings']:
                    # Get synonyms if available
                    synonyms = meaning.get('synonyms', [])
                    for synonym in synonyms[:2]:  # Reduced from 3 to 2 per meaning
                        if synonym not in related_words:
                            related_words.append(synonym)

        return related_words[:3]  # Reduced from 8 to 3 total synonyms
    except Exception:
        return []


def translate_text(text: str, cache: TranslationCache | None = None) -> str:
    """
    Auto-detect language and translate between Chinese and English.
    Shows multiple common translations separated by commas.

    Args:
        text: Single word to translate
        cache: Optional translation cache to check/store results

    Returns:
        Comma-separated translations showing different meanings
    """
    if not text.strip():
        return ""

    # Check cache first
    if cache:
        cached = cache.get(text)
        if cached:
            return cached

    try:
        if is_chinese(text):
            # Chinese to English - get multiple meanings
            translator = GoogleTranslator(source='zh-CN', target='en')
            main_translation = translator.translate(text)

            translations = [main_translation]

            # Get English synonyms of the main translation
            # Simply add them without back-translation verification (too slow)
            synonyms = get_english_synonyms(main_translation.lower())
            for synonym in synonyms[:3]:  # Max 3 synonyms
                if synonym.lower() != main_translation.lower():
                    translations.append(synonym)

            # Remove duplicates while preserving order
            seen = set()
            unique_translations = []
            for trans in translations:
                trans_lower = trans.lower()
                if trans_lower not in seen:
                    seen.add(trans_lower)
                    unique_translations.append(trans)

            result = ", ".join(unique_translations[:4])  # Max 4 translations

            # Save to cache
            if cache:
                cache.add(text, result)

            return result

        else:
            # English to Chinese - get multiple meanings
            translator = GoogleTranslator(source='en', target='zh-CN')
            main_translation = translator.translate(text)

            translations = [main_translation]

            # Get synonyms and translate each IN PARALLEL
            synonyms = get_english_synonyms(text.lower())

            if synonyms:
                # Translate synonyms concurrently for speed
                def translate_synonym(syn):
                    try:
                        return translator.translate(syn)
                    except:
                        return None

                with ThreadPoolExecutor(max_workers=3) as executor:
                    future_to_synonym = {executor.submit(translate_synonym, syn): syn for syn in synonyms[:3]}

                    for future in as_completed(future_to_synonym):
                        result = future.result()
                        if result and result != main_translation:
                            translations.append(result)

            # Only use context-based translation if we have very few results
            if len(translations) < 2:
                # Simple fallback: translate with one context word
                try:
                    context_translation = translator.translate(f"system {text}")
                    if context_translation:
                        core = context_translation.replace('系统', '').strip()
                        core = re.sub(r'[，,\s]+', '', core)
                        if len(core) >= 2 and core not in translations:
                            translations.append(core)
                except:
                    pass

            # Remove duplicates while preserving order
            seen = set()
            unique_translations = []
            for trans in translations:
                if trans not in seen:
                    seen.add(trans)
                    unique_translations.append(trans)

            result = ", ".join(unique_translations[:4])  # Max 4 translations

            # Save to cache
            if cache:
                cache.add(text, result)

            return result

    except Exception as e:
        return f"Translation error: {str(e)}"


def main():
    """Run the interactive translation loop."""
    print("Interactive Translation Tool (Chinese <-> English)")
    print("Type 'exit' or 'quit' to stop, or press Ctrl+C\n")

    # Initialize translation cache
    cache = TranslationCache()
    cache_info = cache.get_cache_info()
    print(f"Cache: {cache_info['path']}")
    print(f"Loaded {cache_info['entries']} cached translation(s)\n")

    # Create a completer for common exit commands
    exit_completer = WordCompleter(['exit', 'quit', 'q'], ignore_case=True)

    try:
        while True:
            try:
                # Get user input with full line editing support
                user_input = prompt(">>> ", completer=exit_completer).strip()

                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break

                # Skip empty input
                if not user_input:
                    continue

                # Translate and display result
                result = translate_text(user_input, cache=cache)
                print(f"{result}\n")

            except EOFError:
                # Handle Ctrl+D
                print("\nGoodbye!")
                break

    except KeyboardInterrupt:
        # Handle Ctrl+C
        print("\n\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
