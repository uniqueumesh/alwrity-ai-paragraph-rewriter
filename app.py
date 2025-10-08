import streamlit as st  # type: ignore
import hashlib
import os
import base64
import warnings
from dotenv import load_dotenv
from streamlit.components.v1 import html  # type: ignore
from config.constants import GEMINI_MAX_WORDS
from errors.gemini_api_error import GeminiAPIError
from services.rewrite_paragraph import rewrite_paragraph
from utils.check_similarity import check_similarity
from services.tts import synthesize_speech, TTSAPIError

# --- App Branding and Header ---
st.set_page_config(page_title="Alwrity - AI Paragraph Rewriter", page_icon="📝", layout="centered")

# Suppress noisy FutureWarning from transformers/torch about encoder_attention_mask
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message=r".*encoder_attention_mask.*BertSdpaSelfAttention.*",
)

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
    "Paragraph",
    height=180,
    key="paragraph_input",
    placeholder="Type or paste your paragraph here — ALwrity will rewrite it beautifully (max 700 words)",
    label_visibility="collapsed",
)

# Live word counter under textarea
_words = len(paragraph.split()) if paragraph else 0
st.caption(f"{_words}/{GEMINI_MAX_WORDS} words")

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
if "tts_audio_b64" not in st.session_state:
    st.session_state.tts_audio_b64 = ""
if "tts_segments_b64" not in st.session_state:
    st.session_state.tts_segments_b64 = []

# Helper: toggle TTS state (no rerun in callback to avoid Streamlit no-op warning)
def _tts_toggle():
    st.session_state.tts_playing = not st.session_state.tts_playing

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
rewrite_clicked = st.button("Rewrite Paragraph", disabled=not paragraph.strip())
if rewrite_clicked:
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
                st.session_state.tts_audio_b64 = ""

                # Pre-generate segmented TTS via AssemblyAI for instant, reliable playback
                text_hash = hashlib.sha256(rewritten.strip().encode("utf-8")).hexdigest()
                assembly_key = os.getenv("ASSEMBLYAI_API_KEY", "")
                if not assembly_key:
                    try:
                        assembly_key = st.secrets["ASSEMBLYAI_API_KEY"]
                    except Exception:
                        assembly_key = ""
                st.session_state.tts_audio_b64 = ""
                st.session_state.tts_segments_b64 = []
                if assembly_key:
                    try:
                        # Split text into sentence-like chunks ~200-300 chars
                        import re
                        sentences = re.split(r'(?<=[.!?])\s+', rewritten.strip())
                        chunks = []
                        buf = ''
                        for s in sentences:
                            if len((buf + ' ' + s).strip()) <= 250:
                                buf = (buf + ' ' + s).strip()
                            else:
                                if buf:
                                    chunks.append(buf)
                                buf = s
                        if buf:
                            chunks.append(buf)
                        # Generate audio per chunk
                        seg_b64 = []
                        for chunk in chunks:
                            audio_bytes = synthesize_speech(chunk, assembly_key)
                            seg_b64.append(base64.b64encode(audio_bytes).decode('utf-8'))
                        st.session_state.tts_segments_b64 = seg_b64
                        st.session_state.tts_text_hash = text_hash
                    except Exception:
                        st.session_state.tts_segments_b64 = []
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

    # Listen/Pause toggle (prefer pre-generated audio if available; else browser TTS)
    listen_label = "Pause" if st.session_state.tts_playing else "Listen"
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        st.button(listen_label, key="tts_toggle", on_click=_tts_toggle)

    # Copy button using JS with secure clipboard API and textarea fallback for iframes
    with btn_col2:
        _copy_id = "copy-btn-" + hashlib.sha256(st.session_state.last_output.encode("utf-8")).hexdigest()[:8]
        import json as _json
        _copy_text_js = _json.dumps(st.session_state.last_output)
        html(
            f"""
            <style>
              .alwrity-copy-btn {{
                padding: 0.5rem 0.75rem;
                border-radius: 0.5rem;
                cursor: pointer;
              }}
              @media (prefers-color-scheme: dark) {{
                .alwrity-copy-btn {{ background:#1f2937; color:#f9fafb; border:1px solid #374151; }}
                .alwrity-copy-btn:hover {{ background:#273244; }}
              }}
              @media (prefers-color-scheme: light) {{
                .alwrity-copy-btn {{ background:#f3f4f6; color:#111827; border:1px solid #d1d5db; }}
                .alwrity-copy-btn:hover {{ background:#eaecef; }}
              }}
            </style>
            <button id=\"{_copy_id}\" class=\"alwrity-copy-btn\">Copy text</button>
            <script>
              (function(){{
                const btn = document.getElementById('{_copy_id}');
                const textToCopy = {_copy_text_js};
                async function copyText(t){{
                  try {{
                    if (navigator.clipboard && window.isSecureContext) {{
                      await navigator.clipboard.writeText(t);
                      return true;
                    }}
                  }} catch(e) {{}}
                  try {{
                    const ta = document.createElement('textarea');
                    ta.value = t;
                    ta.setAttribute('readonly','');
                    ta.style.position = 'fixed';
                    ta.style.top = '-1000px';
                    document.body.appendChild(ta);
                    ta.select();
                    const ok = document.execCommand('copy');
                    document.body.removeChild(ta);
                    return ok;
                  }} catch(e) {{ return false; }}
                }}
                if (btn) {{
                  btn.addEventListener('click', async () => {{
                    const ok = await copyText(textToCopy);
                    btn.textContent = ok ? 'Copied' : 'Copy failed';
                    setTimeout(()=>{{ btn.textContent = 'Copy text'; }}, 2000);
                  }});
                }}
              }})();
            </script>
            """,
            height=40,
        )

    # If we have segmented audio, queue it reliably across long texts
    if st.session_state.tts_segments_b64 and len(st.session_state.tts_segments_b64) > 0:
        import json as _json
        segs_js = _json.dumps(st.session_state.tts_segments_b64)
        play_js = """
            const segs = SEGS_PLACEHOLDER;
            if (!window.__alwrityTts) { window.__alwrityTts = { idx: 0, audio: new Audio() }; }
            const ctx = window.__alwrityTts;
            const startOrResume = () => {
              if (ctx.idx >= segs.length) { return; }
              ctx.audio.src = `data:audio/mp3;base64,${segs[ctx.idx]}`;
              ctx.audio.onended = () => { ctx.idx += 1; if (ctx.idx < segs.length) { startOrResume(); } };
              ctx.audio.play().catch(()=>{});
            };
            startOrResume();
        """.replace('SEGS_PLACEHOLDER', segs_js)
        pause_js = """
            if (window.__alwrityTts && window.__alwrityTts.audio) { window.__alwrityTts.audio.pause(); }
        """
        html(
            f"""
            <script>
                try {{ {play_js if st.session_state.tts_playing else pause_js} }} catch(e) {{}}
            </script>
            """,
            height=0,
            key="tts_queue"
        )
    else:
        # Fallback to browser TTS
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

    # No separate clipboard injection needed; handled inline with the button JS above
