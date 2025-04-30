import streamlit as st
import os
import asyncio

from AutoDocCoder.main import main

st.set_page_config(page_title="API Doc to Script Generator", page_icon="🤖", layout="wide")

st.title("📜 AutoDoc Coder")
st.markdown("Upload your docs or drop a link — get back structured, secure, and standards-compliant API code")

# ---- Sidebar ----
source_type = st.sidebar.radio("Select Source Type", ["URL", "PDF"])
api_source = None
uploaded_file = None

if source_type == "URL":
    api_source = st.text_input("Enter API Documentation URL")
else:
    uploaded_file = st.file_uploader("Upload API Documentation PDF", type=["pdf"])

language = st.selectbox("Select Programming Language", ["Python", "Java", "JavaScript (beta)", "C++ (beta)"])
use_case = st.text_area("Describe Your Use Case", height=150)

execute = st.button("🚀 Generate Script")

if execute:
    if api_source and use_case:
        try:
            with st.spinner("Processing... ⏳"):
                output_code = asyncio.run(main(api_source, use_case, language, source_type))
            st.subheader("🧩 Generated Code Snippet:")
            st.code(output_code, language=language.lower())
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    elif uploaded_file and use_case:
        try:
            with st.spinner("Processing... ⏳"):
                output_code = asyncio.run(main(uploaded_file, use_case, language, source_type))
            st.subheader("🧩 Generated Code Snippet:")
            st.code(output_code, language=language.lower())
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    else:
        st.error("Please provide both API URL and Use Case.")
