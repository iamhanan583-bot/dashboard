import streamlit as st
import streamlit.components.v1 as components
import os
import sys
import json
import urllib.parse
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import time
import secrets

# ---------------------------------------------------------------------------
# 1. DATABASE CONFIGURATION (Supports Supabase DATABASE_URL & Secrets)
# ---------------------------------------------------------------------------
database_url = ""
if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
    database_url = st.secrets["DATABASE_URL"]
else:
    database_url = os.environ.get("DATABASE_URL", "")

def get_db_connection():
    try:
        if database_url:
            return psycopg2.connect(database_url, cursor_factory=RealDictCursor, sslmode="require")
        else:
            return psycopg2.connect(
                dbname=os.environ.get("DB_NAME", "postgres"),
                user=os.environ.get("DB_USER", "postgres"),
                password=os.environ.get("DB_PASSWORD", ""),
                host=os.environ.get("DB_HOST", "localhost"),
                port=int(os.environ.get("DB_PORT", 5432)),
                cursor_factory=RealDictCursor
            )
    except Exception as e:
        print(f"[DB Error]: {e}")
        return None

# ---------------------------------------------------------------------------
# 2. EMBEDDED FASTAPI / SERVER DISPATCHER
# ---------------------------------------------------------------------------
# Read index.html directly
html_file_path = os.path.join(os.path.dirname(__file__), "index.html")
html_content = ""
if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

# Setup Streamlit Page
st.set_page_config(
    page_title="Transworld GIS & NOC Portal",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container { padding: 0rem !important; margin: 0rem !important; max-width: 100% !important; }
        iframe { position: fixed; top: 0; left: 0; width: 100vw !important; height: 100vh !important; border: none; margin: 0; padding: 0; overflow: hidden; z-index: 999999; }
    </style>
""", unsafe_allow_html=True)

# Render the original unchanged portal inside the page
components.html(html_content, height=1000, scrolling=True)
