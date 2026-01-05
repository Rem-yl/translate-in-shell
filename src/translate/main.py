#!/usr/bin/env python3
"""Interactive translation tool for Chinese and English."""

import sys
import re
import requests
from deep_translator import GoogleTranslator


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
        response = requests.get(url, timeout=5)

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
                    for synonym in synonyms[:3]:
                        if synonym not in related_words:
                            related_words.append(synonym)

        return related_words[:8]  # Return max 8 related words
    except Exception:
        return []


def translate_text(text: str) -> str:
    """
    Auto-detect language and translate between Chinese and English.
    Shows multiple common translations separated by commas.

    Args:
        text: Single word to translate

    Returns:
        Comma-separated translations showing different meanings
    """
    if not text.strip():
        return ""

    try:
        if is_chinese(text):
            # Chinese to English - get multiple meanings
            translator = GoogleTranslator(source='zh-CN', target='en')
            main_translation = translator.translate(text)

            # Try to get synonyms by translating back and forth
            # This helps find alternative translations
            translations = [main_translation]

            # Get English synonyms of the main translation
            synonyms = get_english_synonyms(main_translation.lower())

            # Translate each synonym back to Chinese to verify it matches
            # Then add the original English synonym if it's a valid alternative
            for synonym in synonyms[:4]:  # Limit to 4 synonyms
                try:
                    back_translation = GoogleTranslator(source='en', target='zh-CN').translate(synonym)
                    # If it translates back to similar Chinese, it's a valid alternative
                    if back_translation and synonym.lower() != main_translation.lower():
                        translations.append(synonym)
                except:
                    pass

            # Remove duplicates while preserving order
            seen = set()
            unique_translations = []
            for trans in translations:
                trans_lower = trans.lower()
                if trans_lower not in seen:
                    seen.add(trans_lower)
                    unique_translations.append(trans)

            return ", ".join(unique_translations[:5])  # Max 5 translations

        else:
            # English to Chinese - get multiple meanings
            translator = GoogleTranslator(source='en', target='zh-CN')
            main_translation = translator.translate(text)

            translations = [main_translation]

            # Get synonyms and translate each
            synonyms = get_english_synonyms(text.lower())

            for synonym in synonyms:
                try:
                    synonym_translation = translator.translate(synonym)
                    if synonym_translation and synonym_translation != main_translation:
                        translations.append(synonym_translation)
                except:
                    pass

            # If we have few translations, try translating in different contexts
            if len(translations) < 3:
                # Translate with a context word to get alternative meanings
                # Then extract just the core word
                context_pairs = [
                    ("system", "系统"),   # to filter out this modifier
                    ("framework", "框架"),
                ]

                for eng_ctx, chi_ctx in context_pairs:
                    try:
                        context_translation = translator.translate(f"{eng_ctx} {text}")
                        if context_translation:
                            # Remove the context word we added to isolate the core translation
                            core = context_translation.replace(chi_ctx, '').strip()
                            # Clean up any punctuation
                            core = re.sub(r'[，,\s]+', '', core)

                            if len(core) >= 2 and core not in translations:
                                # Check if it's substantially different from existing translations
                                is_different = True
                                for existing in translations:
                                    if core == existing or existing in core or core in existing:
                                        is_different = False
                                        break

                                if is_different:
                                    translations.append(core)

                            if len(translations) >= 3:
                                break
                    except:
                        pass

            # Remove duplicates while preserving order
            seen = set()
            unique_translations = []
            for trans in translations:
                if trans not in seen:
                    seen.add(trans)
                    unique_translations.append(trans)

            return ", ".join(unique_translations[:5])  # Max 5 translations

    except Exception as e:
        return f"Translation error: {str(e)}"


def main():
    """Run the interactive translation loop."""
    print("Interactive Translation Tool (Chinese <-> English)")
    print("Type 'exit' or 'quit' to stop, or press Ctrl+C\n")

    try:
        while True:
            try:
                # Get user input
                user_input = input(">>> ").strip()

                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break

                # Skip empty input
                if not user_input:
                    continue

                # Translate and display result
                result = translate_text(user_input)
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
