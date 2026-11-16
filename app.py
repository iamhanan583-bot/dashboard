import streamlit as st
import streamlit.components.v1 as components
import os
import sys
import subprocess
import time

# 1. Setup Database Environment from Streamlit Secrets
if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
    os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]

# 2. Start the Backend API Server (server.py) in Background
@st.cache_resource
def start_backend_server():
    server_script = os.path.join(os.path.dirname(__file__), "server.py")
    if os.path.exists(server_script):
        cmd = [sys.executable, server_script]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        return proc
    return None

start_backend_server()

# 3. Streamlit Page Config
st.set_page_config(
    page_title="Transworld GIS & NOC Portal",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 4. Full screen styling
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container { padding: 0rem !important; margin: 0rem !important; max-width: 100% !important; }
        iframe { position: fixed; top: 0; left: 0; width: 100vw !important; height: 100vh !important; border: none; margin: 0; padding: 0; overflow: hidden; z-index: 999999; }
    </style>
""", unsafe_allow_html=True)

# 5. Load index.html without any modifications
html_file_path = os.path.join(os.path.dirname(__file__), "index.html")
if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_code = f.read()
    components.html(html_code, height=1000, scrolling=True)
else:
    st.error("Error: index.html not found!")e not found in repository!")
