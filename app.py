import streamlit as st
import streamlit.components.v1 as components
import os

# Streamlit Page Config - Full width layout
st.set_page_config(
    page_title="Transworld GIS & NOC Portal",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit default headers, margins, and footers for seamless full-screen view
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding: 0rem !important;
            margin: 0rem !important;
            max-width: 100% !important;
        }
        iframe {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw !important;
            height: 100vh !important;
            border: none;
            margin: 0;
            padding: 0;
            overflow: hidden;
            z-index: 999999;
        }
    </style>
""", unsafe_allow_html=True)

# Load index.html exactly without any modifications
html_file_path = os.path.join(os.path.dirname(__file__), "index.html")

if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_code = f.read()
    components.html(html_code, height=1000, scrolling=True)
else:
    st.error("Error: index.html file not found in repository!")
