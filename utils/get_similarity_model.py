import streamlit as st
from sentence_transformers import SentenceTransformer


@st.cache_resource(show_spinner=False)
def get_similarity_model():
    return SentenceTransformer('all-MiniLM-L6-v2')



