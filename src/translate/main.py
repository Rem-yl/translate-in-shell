#!/usr/bin/env python3
"""Interactive translation tool for Chinese and English."""

import sys
import re
from deep_translator import GoogleTranslator


def is_chinese(text: str) -> bool:
    """Check if text contains Chinese characters."""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def translate_text(text: str) -> str:
    """
    Auto-detect language and translate between Chinese and English.

    Args:
        text: The text to translate

    Returns:
        Translated text
    """
    if not text.strip():
        return ""

    try:
        if is_chinese(text):
            # Chinese to English
            translator = GoogleTranslator(source='zh-CN', target='en')
            return translator.translate(text)
        else:
            # English to Chinese
            translator = GoogleTranslator(source='en', target='zh-CN')
            return translator.translate(text)
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
                user_input = input("Enter word to translate: ").strip()

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
