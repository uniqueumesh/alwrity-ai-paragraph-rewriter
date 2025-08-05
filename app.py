import streamlit as st
import requests
import hashlib
from sentence_transformers import SentenceTransformer, util
import torch

# --- App Branding and Header ---
st.set_page_config(page_title="Alwrity - AI Paragraph Rewriter", page_icon="📝", layout="centered")
st.title("Alwrity - AI Paragraph Rewriter 📝")
st.markdown("""
Rewrite and enhance your paragraphs using advanced AI. Select your preferred style and instantly get a new version of your text.
""")

# Gemini API endpoint (for text generation)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-pro:generateContent"
GEMINI_MAX_WORDS = 700

class GeminiAPIError(Exception):
    pass

# Load the semantic similarity model (do this once, outside the function)
@st.cache_resource(show_spinner=False)
def get_similarity_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

# --- Sidebar (API Key, About, and Mode Selection) ---
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Enter your Gemini API key", type="password")
st.sidebar.markdown("---")
mode = st.sidebar.radio(
    "Rewriting Mode:",
    ["Strict (preserve meaning)", "Creative (more freedom)"]
)
st.sidebar.markdown("---")
st.sidebar.title("About Alwrity")
st.sidebar.info(
    """
    Alwrity - AI Paragraph Rewriter\n\nEffortlessly rewrite and enhance your text for clarity, tone, and engagement.\n\n[Visit Alwrity](https://alwrity.com)
    """
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

# --- Semantic Similarity Check ---
def check_similarity(input_text, output_text):
    model = get_similarity_model()
    emb1 = model.encode(input_text, convert_to_tensor=True)
    emb2 = model.encode(output_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(emb1, emb2).item()
    return similarity

# --- Action Button ---
if st.button("Rewrite Paragraph"):
    if not api_key or not api_key.strip():
        st.error("Please enter your Gemini API key in the sidebar.")
    elif not paragraph.strip():
        st.warning("Please enter a paragraph to rewrite.")
    elif len(paragraph.split()) > GEMINI_MAX_WORDS:
        st.error(f"Input exceeds Gemini's max word limit of {GEMINI_MAX_WORDS} words.")
    else:
        try:
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