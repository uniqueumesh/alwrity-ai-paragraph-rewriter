import streamlit as st
import hashlib
import os
from dotenv import load_dotenv
from streamlit.components.v1 import html
from config.constants import GEMINI_MAX_WORDS
from errors.gemini_api_error import GeminiAPIError
from services.rewrite_paragraph import rewrite_paragraph
from utils.check_similarity import check_similarity

# --- App Branding and Header ---
st.set_page_config(page_title="Alwrity - AI Paragraph Rewriter", page_icon="📝", layout="centered")

# Gemini config and utilities are imported from modular files

# --- API Key Loading (Secrets or .env) ---
load_dotenv()
# Prefer local .env during development to avoid Streamlit secrets errors
api_key = os.getenv("GEMINI_API_KEY", "")
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = ""

# --- Input Section ---
paragraph = st.text_area(
    "",
    height=180,
    key="paragraph_input",
    placeholder="Type or paste your paragraph here — ALwrity will rewrite it beautifully (max 700 words)"
)

# Guide above the dropdown menus
st.markdown(
    "<div style=\"font-size:1.1rem; font-weight:500; margin: 0.75rem 0;\">Set the rewrite mode, pick a tone that fits, and choose the language from the dropdown.</div>",
    unsafe_allow_html=True
)

# --- Compact Horizontal Controls below input ---
language_options = [
    "English",
    "Spanish",
    "French",
    "German",
    "Hindi",
    "Custom..."
]

col_mode, col_style, col_lang = st.columns(3)
with col_mode:
    mode = st.selectbox(
        "Choose mode:",
        ["Strict (preserve meaning)", "Creative (more freedom)"],
        index=0,
        key="mode_select",
        label_visibility="collapsed"
    )
with col_style:
    style = st.selectbox(
        "Choose a style or tone:",
        [
            "Clear and Engaging",
            "Formal",
            "Casual",
            "Concise",
            "Friendly",
            "Persuasive",
            "Professional"
        ],
        index=0,
        key="style_select",
        label_visibility="collapsed"
    )
with col_lang:
    language_choice = st.selectbox(
        "Target language:",
        language_options,
        index=0,
        key="language_select",
        label_visibility="collapsed"
    )
    if language_choice == "Custom...":
        custom_language = st.text_input("Enter custom language", key="language_custom", placeholder="Type a language")
        target_language = custom_language.strip() if custom_language else ""
    else:
        target_language = language_choice

# --- Session State: Track previous outputs to avoid repeats ---
if "previous_hashes" not in st.session_state:
    st.session_state.previous_hashes = set()
if "last_output" not in st.session_state:
    st.session_state.last_output = ""
if "tts_text_hash" not in st.session_state:
    st.session_state.tts_text_hash = ""
if "tts_playing" not in st.session_state:
    st.session_state.tts_playing = False

# Helper: toggle TTS state and immediately rerun to refresh button label and JS
def _tts_toggle():
    st.session_state.tts_playing = not st.session_state.tts_playing
    try:
        st.rerun()
    except Exception:
        try:
            st.experimental_rerun()
        except Exception:
            pass

# --- Set prompt and similarity threshold based on mode ---
if mode == "Strict (preserve meaning)":
    prompt_instructions = (
        "It is essential that the rewritten paragraph conveys exactly the same meaning, facts, and details as the original. "
        "Do not add, remove, or change any information—just rephrase for style and clarity."
    )
    similarity_threshold = 0.8
else:
    prompt_instructions = (
        "You may rephrase and creatively enhance the paragraph in a {style} style. "
        "It's okay to make stylistic changes or slight modifications, but keep the core message intact."
    )
    similarity_threshold = 0.6

# Append language directive to the prompt instructions
if 'target_language' in locals() and target_language:
    prompt_instructions += f" Write the output in {target_language}."

# --- Semantic Similarity Check is imported from utils.check_similarity ---

# --- Action Button ---
if st.button("Rewrite Paragraph"):
    if not api_key or not api_key.strip():
        st.error("API key not configured. Set GEMINI_API_KEY in Streamlit secrets or in a local .env file.")
    elif not paragraph.strip():
        st.warning("Please enter a paragraph to rewrite.")
    elif len(paragraph.split()) > GEMINI_MAX_WORDS:
        st.error(f"Input exceeds Gemini's max word limit of {GEMINI_MAX_WORDS} words.")
    else:
        try:
            with st.spinner("Rewriting your paragraph..."):
                rewritten = rewrite_paragraph(
                    paragraph,
                    style,
                    api_key,
                    previous_hashes=st.session_state.previous_hashes,
                    prompt_instructions=prompt_instructions
                )
                # Also compute similarity and update state within spinner to avoid gaps
                similarity = check_similarity(paragraph, rewritten)
                st.session_state.last_output = rewritten
                st.session_state.previous_hashes.add(
                    hashlib.sha256(rewritten.strip().encode("utf-8")).hexdigest()
                )
                # Reset TTS state for new output
                st.session_state.tts_text_hash = ""
                st.session_state.tts_playing = False
            if similarity < similarity_threshold:
                st.warning(f"Warning: The rewritten paragraph may not preserve the original meaning (similarity: {similarity:.2f}). Please review or try again.")


        except GeminiAPIError as e:
            st.error(f"Gemini API Error: {e}")
        except Exception as e:
            st.error(f"Error: {e}")

# --- Rewritten Output (persistent) and TTS Controls ---
if st.session_state.last_output:
    st.success("Here's your rewritten paragraph:")
    st.text_area("Rewritten Paragraph", value=st.session_state.last_output, height=180)

    # Determine current text hash and reset speech state if text changed
    current_hash = hashlib.sha256(st.session_state.last_output.strip().encode("utf-8")).hexdigest()
    text_changed = st.session_state.tts_text_hash != current_hash
    if text_changed:
        st.session_state.tts_text_hash = current_hash
        st.session_state.tts_playing = False
        # Stop any ongoing speech in the browser
        html("""
            <script>
                try { window.speechSynthesis.cancel(); } catch(e) {}
            </script>
        """, height=0)

    # Listen/Pause toggle using browser TTS for immediate playback
    listen_label = "Pause" if st.session_state.tts_playing else "Listen"
    st.button(listen_label, key="tts_toggle", on_click=_tts_toggle)

    # Inject JS to speak or stop immediately based on state
    # Encode text to safely pass to JS
    import json as _json
    text_js = _json.dumps(st.session_state.last_output)
    if st.session_state.tts_playing:
        html(f"""
            <script>
                try {{
                    const txt = {text_js};
                    window.speechSynthesis.cancel();
                    const u = new SpeechSynthesisUtterance(txt);
                    window.speechSynthesis.speak(u);
                }} catch(e) {{}}
            </script>
        """, height=0)
    else:
        html("""
            <script>
                try { window.speechSynthesis.cancel(); } catch(e) {}
            </script>
        """, height=0)
