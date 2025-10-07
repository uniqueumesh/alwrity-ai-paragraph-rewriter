import requests
from typing import Optional


class TTSAPIError(Exception):
    pass


def synthesize_speech(text: str, api_key: str, voice: Optional[str] = None) -> bytes:
    """
    Convert text to speech using AssemblyAI TTS and return audio bytes.

    Note: This implementation assumes the API returns audio content directly.
    If the API returns an audio URL, you should fetch that URL to get bytes.
    """
    if not text or not text.strip():
        raise ValueError("Text is required for TTS")
    if not api_key or not api_key.strip():
        raise ValueError("AssemblyAI API key is required")

    url = "https://api.assemblyai.com/v2/tts"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
    }
    if voice:
        payload["voice"] = voice

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        # If audio bytes are returned directly
        if response.headers.get("Content-Type", "").startswith("audio"):
            return response.content
        # If API returns a URL instead
        try:
            audio_url = response.json().get("audio_url")
        except Exception:
            audio_url = None
        if not audio_url:
            raise TTSAPIError("Unexpected TTS response format")
        audio_resp = requests.get(audio_url)
        if audio_resp.status_code != 200:
            raise TTSAPIError(f"Failed to download TTS audio: {audio_resp.status_code}")
        return audio_resp.content

    raise TTSAPIError(f"AssemblyAI TTS error: {response.status_code} {response.text}")


