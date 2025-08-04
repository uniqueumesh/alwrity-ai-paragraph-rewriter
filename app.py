import streamlit as st
from paragraph_rewriter import rewrite_paragraph, GeminiAPIError

# --- App Branding and Header ---
st.set_page_config(page_title="Alwrity - AI Paragraph Rewriter", page_icon="📝", layout="centered")
st.title("Alwrity - AI Paragraph Rewriter 📝")
st.markdown("""
Rewrite and enhance your paragraphs using advanced AI. Select your preferred style and instantly get a new version of your text.
""")

# --- Sidebar (API Key, About) ---
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Enter your Gemini API key", type="password")
st.sidebar.markdown("---")
st.sidebar.title("About Alwrity")
st.sidebar.info(
    """
    Alwrity - AI Paragraph Rewriter\n\nEffortlessly rewrite and enhance your text for clarity, tone, and engagement.\n\n[Visit Alwrity](https://alwrity.com)
    """
)

# --- Input Section ---
st.subheader("Enter your paragraph")
GEMINI_MAX_WORDS = 700
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

# --- Session State: Track previous outputs to avoid repeats ---
if "previous_hashes" not in st.session_state:
    st.session_state.previous_hashes = set()
if "last_output" not in st.session_state:
    st.session_state.last_output = ""

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
                previous_hashes=st.session_state.previous_hashes
            )
            st.session_state.last_output = rewritten
            st.session_state.previous_hashes.add(
                __import__('hashlib').sha256(rewritten.strip().encode("utf-8")).hexdigest()
            )
            st.success("Here's your rewritten paragraph:")
            st.text_area("Rewritten Paragraph", value=rewritten, height=180)
        except GeminiAPIError as e:
            st.error(f"Gemini API Error: {e}")
        except Exception as e:
            st.error(f"Error: {e}")

# --- Privacy Notice ---
st.info("Your API key is only used for this session and is never stored after you close the tool.")
