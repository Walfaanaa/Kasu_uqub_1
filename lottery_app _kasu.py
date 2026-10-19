
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
ENV_FILE = APP_DIR / ".env"

load_dotenv(ENV_FILE, override=True)

def get_setting(secret_key, env_key):
    try:
        value = st.secrets.get(secret_key)
        if value and str(value).strip():
            return str(value)
    except Exception:
        pass

    value = os.getenv(env_key)
    return value if value and value.strip() else None

AUTHORIZED_CODE = get_setting(
    "ADMIN_PASSWORD",
    "STREAMLIT_ADMIN_PASSWORD"
)

RESET_PASSWORD = get_setting(
    "RESET_PASSWORD",
    "STREAMLIT_RESET_PASSWORD"
)

# Temporary diagnostics; remove after testing.
st.write("Environment file exists:", ENV_FILE.is_file())
st.write("Admin password loaded:", bool(AUTHORIZED_CODE))
st.write("Reset password loaded:", bool(RESET_PASSWORD))
