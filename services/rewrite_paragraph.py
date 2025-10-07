import requests
import hashlib
from errors.gemini_api_error import GeminiAPIError
from config.constants import GEMINI_API_URL, GEMINI_MAX_WORDS


def rewrite_paragraph(paragraph: str, style: str, api_key: str, previous_hashes=None, prompt_instructions=None) -> str:
    """
    Rewrite the input paragraph using Gemini LLM for the specified style.
    Ensures the rewritten paragraph is not a repeat of the input or previous outputs.
    """
    if len(paragraph.split()) > GEMINI_MAX_WORDS:
        raise ValueError(f"Input exceeds Gemini's max word limit of {GEMINI_MAX_WORDS} words.")

    prompt = (
        f"Rewrite the following paragraph in a {style} style. "
        f"{prompt_instructions}\n\nParagraph: {paragraph}"
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



