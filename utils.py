# app/utils.py

import os
import openai


def load_transcript(file_path: str) -> str:
    """
    Loads the raw transcript from a text file and performs basic cleaning.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # Normalize whitespace
    text = text.replace('\r\n', ' ').replace('\n', ' ')
    text = ' '.join(text.split())
    return text

def get_openai_api_key() -> str:
    """
    Returns the OpenAI API key from environment variables or any other secure location.
    Adjust as needed for your environment.
    """
    return os.environ.get("openai.api_key", "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")

def openai_setup():
    """
    Sets up the OpenAI API key. Call this once at app startup.
    """
    openai.api_key="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"
