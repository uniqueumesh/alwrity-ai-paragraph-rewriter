import requests
import random
import hashlib

# Gemini API endpoint (for text generation)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-pro:generateContent"

# Gemini input limits (tokens, but we use words as a proxy here)
GEMINI_MAX_WORDS = 700

class GeminiAPIError(Exception):
    pass

def rewrite_paragraph(paragraph: str, style: str, api_key: str, previous_hashes=None) -> str:
    """
    Rewrite the input paragraph using Gemini LLM for the specified style.
    Ensures the rewritten paragraph is not a repeat of the input or previous outputs.
    Args:
        paragraph (str): The paragraph to rewrite.
        style (str): The rewriting style or tone.
        api_key (str): User's Gemini API key.
        previous_hashes (set): Hashes of previous outputs (to avoid repeats).
    Returns:
        str: The rewritten paragraph.
    Raises:
        GeminiAPIError: If the Gemini API returns an error.
    """
    if len(paragraph.split()) > GEMINI_MAX_WORDS:
        raise ValueError(f"Input exceeds Gemini's max word limit of {GEMINI_MAX_WORDS} words.")

    prompt = (
        f"Rewrite the following paragraph in a {style} style. "
        "Do not repeat the input text verbatim. Make the output unique and different from the input, "
        "while preserving the original meaning.\n\nParagraph: "
        f"{paragraph}"
    )

    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    params = {"key": api_key}

    response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
    if response.status_code != 200:
        raise GeminiAPIError(f"Gemini API error: {response.status_code} {response.text}")
    result = response.json()
    try:
        rewritten = result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise GeminiAPIError("Unexpected response from Gemini API.")

    # Ensure output is not a repeat (hash check)
    output_hash = hashlib.sha256(rewritten.strip().encode("utf-8")).hexdigest()
    input_hash = hashlib.sha256(paragraph.strip().encode("utf-8")).hexdigest()
    if previous_hashes is None:
        previous_hashes = set()
    if output_hash == input_hash or output_hash in previous_hashes:
        # Try to nudge Gemini for a different output
        prompt += f"\nMake it even more different from the original. Add variation."
        data["contents"][0]["parts"][0]["text"] = prompt
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
        if response.status_code != 200:
            raise GeminiAPIError(f"Gemini API error: {response.status_code} {response.text}")
        result = response.json()
        try:
            rewritten = result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise GeminiAPIError("Unexpected response from Gemini API.")
        output_hash = hashlib.sha256(rewritten.strip().encode("utf-8")).hexdigest()
        if output_hash == input_hash or output_hash in previous_hashes:
            raise GeminiAPIError("Gemini LLM returned the same or similar output multiple times. Please try again.")
    return rewritten.strip()
