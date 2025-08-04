import streamlit as st
from paragraph_rewriter import rewrite_paragraph

# --- App Branding and Header ---
st.set_page_config(page_title="Alwrity - AI Paragraph Rewriter", page_icon="📝", layout="centered")
st.title("Alwrity - AI Paragraph Rewriter 📝")
st.markdown("""
Rewrite and enhance your paragraphs using advanced AI. Select your preferred style and instantly get a new version of your text.
""")

# --- Input Section ---
st.subheader("Enter your paragraph")
paragraph = st.text_area("Paste your paragraph here:", height=180)

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
    index=0
)

# --- Action Button ---
if st.button("Rewrite Paragraph"):
    if not paragraph.strip():
        st.warning("Please enter a paragraph to rewrite.")
    else:
        with st.spinner("Rewriting your paragraph..."):
            rewritten = rewrite_paragraph(paragraph, style)
        st.success("Here's your rewritten paragraph:")
        st.text_area("Rewritten Paragraph", value=rewritten, height=180)

# --- Sidebar ---
st.sidebar.title("About Alwrity")
st.sidebar.info(
    """
    Alwrity - AI Paragraph Rewriter\n
    Effortlessly rewrite and enhance your text for clarity, tone, and engagement.\n
    [Visit Alwrity](https://alwrity.com)
    """
)
