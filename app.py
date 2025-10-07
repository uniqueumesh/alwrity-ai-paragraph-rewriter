import streamlit as st
import hashlib
import os
from dotenv import load_dotenv
from config.constants import GEMINI_MAX_WORDS
from errors.gemini_api_error import GeminiAPIError
from services.rewrite_paragraph import rewrite_paragraph
from utils.check_similarity import check_similarity

# --- App Branding and Header ---
st.set_page_config(page_title="Alwrity - AI Paragraph Rewriter", page_icon="📝", layout="centered")
st.title("Alwrity - AI Paragraph Rewriter 📝")
st.markdown("""
Rewrite and enhance your paragraphs using advanced AI. Select your preferred style and instantly get a new version of your text.
""")

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

# --- Mode Selection (moved from sidebar) ---
st.subheader("Rewriting mode")
mode = st.radio(
    "Choose mode:",
    ["Strict (preserve meaning)", "Creative (more freedom)"],
    index=0,
    key="mode_select"
)

# --- Input Section ---
st.subheader("Enter your paragraph")
paragraph = st.text_area(
    f"Paste your paragraph here (max {GEMINI_MAX_WORDS} words):",
    height=180,
    key="paragraph_input"
)

st.subheader("Select rewriting style/tone")
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
    key="style_select"
)

# --- Language Selection ---
st.subheader("Select output language")
language_options = [
    "English",
    "Spanish",
    "French",
    "German",
    "Hindi",
    "Custom..."
]
language_choice = st.selectbox(
    "Target language:",
    language_options,
    index=0,
    key="language_select"
)
if language_choice == "Custom...":
    custom_language = st.text_input("Enter custom language", key="language_custom")
    target_language = custom_language.strip() if custom_language else ""
else:
    target_language = language_choice

# --- Session State: Track previous outputs to avoid repeats and store feedback ---
if "previous_hashes" not in st.session_state:
    st.session_state.previous_hashes = set()
if "last_output" not in st.session_state:
    st.session_state.last_output = ""
if "feedback" not in st.session_state:
    st.session_state.feedback = []

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
            similarity = check_similarity(paragraph, rewritten)
            if similarity < similarity_threshold:
                st.warning(f"Warning: The rewritten paragraph may not preserve the original meaning (similarity: {similarity:.2f}). Please review or try again.")
            st.session_state.last_output = rewritten
            st.session_state.previous_hashes.add(
                hashlib.sha256(rewritten.strip().encode("utf-8")).hexdigest()
            )
            st.success("Here's your rewritten paragraph:")
            st.text_area("Rewritten Paragraph", value=rewritten, height=180)

            # --- Feedback Section ---
            st.markdown("**Was the meaning preserved?**")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("👍 Yes", key="feedback_yes"):
                    st.session_state.feedback.append({
                        "input": paragraph,
                        "output": rewritten,
                        "preserved": True,
                        "comment": ""
                    })
                    st.success("Thank you for your feedback!")
            with col2:
                if st.button("👎 No", key="feedback_no"):
                    st.session_state.feedback.append({
                        "input": paragraph,
                        "output": rewritten,
                        "preserved": False,
                        "comment": ""
                    })
                    st.info("Thank you for your feedback!")
            feedback_comment = st.text_area("Optional: Leave a comment about the rewrite", key="feedback_comment")
            if st.button("Submit Comment", key="submit_comment"):
                if st.session_state.feedback:
                    st.session_state.feedback[-1]["comment"] = feedback_comment
                    st.success("Your comment has been submitted!")
                else:
                    st.warning("Please provide a thumbs up or down before submitting a comment.")

        except GeminiAPIError as e:
            st.error(f"Gemini API Error: {e}")
        except Exception as e:
            st.error(f"Error: {e}")

# --- Privacy Notice ---
st.info("Your API key is only used for this session and is never stored after you close the tool.")