"""Almamlaka TV branding constants."""
import base64
from functools import lru_cache
from pathlib import Path

import streamlit as st

APP_TITLE = "Al Mamlaka Bot"
CHAT_HEADING = "Ask me anything"
PRIMARY_COLOR = "#9D0B0E"
BACKGROUND_COLOR = "#FFFFFF"
TEXT_COLOR = "#1A1A1A"
_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
LOGO_PATH = _ASSETS_DIR / "logo.jpg"
LOGO_WHITE_PATH = _ASSETS_DIR / "logo_white.png"
LOGO_ICON_PATH = _ASSETS_DIR / "logo_icon.png"


@lru_cache(maxsize=2)
def _data_uri(path: Path, mime_type: str) -> str:
    """Encodes an image file as a data URI so it can be used inside inline CSS."""
    return f"data:{mime_type};base64,{base64.b64encode(path.read_bytes()).decode()}"


def configure_page() -> None:
    """Sets page config and injects Almamlaka TV branded CSS."""
    page_icon = str(LOGO_ICON_PATH) if LOGO_ICON_PATH.exists() else None
    st.set_page_config(page_title=APP_TITLE, page_icon=page_icon, layout="centered")
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; }}
        [data-testid="stHeader"] {{ background-color: {PRIMARY_COLOR}; height: 3.5rem; }}
        [data-testid="stHeader"] * {{ color: #FFFFFF !important; }}
        {_header_logo_css()}
        h1, h2, h3 {{ color: {PRIMARY_COLOR} !important; }}
        [data-testid="stChatMessage"] {{ border-left: 3px solid {PRIMARY_COLOR}; }}
        .stChatInput textarea {{
            background-color: {BACKGROUND_COLOR} !important;
            color: {TEXT_COLOR} !important;
        }}
        .stChatInput textarea::placeholder {{ color: #6B6B6B !important; opacity: 1; }}

        /* Thread rows read as a list, not buttons: flat, left-aligned, hover-highlighted. */
        [data-testid="stSidebar"] [class*="st-key-thread_"] button {{
            justify-content: flex-start;
            text-align: left;
            background-color: transparent;
            border: none;
            color: {TEXT_COLOR};
            padding: 0.3rem 0.5rem;
            border-radius: 6px;
            font-weight: 400;
        }}
        [data-testid="stSidebar"] [class*="st-key-thread_"] button p {{
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        [data-testid="stSidebar"] [class*="st-key-thread_"] button:hover {{
            background-color: #EDEDED;
            color: {TEXT_COLOR};
        }}
        [data-testid="stSidebar"] [class*="st-key-thread_active_"] button {{
            background-color: #F6E9E9;
            color: {PRIMARY_COLOR};
            font-weight: 600;
        }}
        [data-testid="stSidebar"] [class*="st-key-delete_"] button {{
            border: none;
            background-color: transparent;
            color: #6B6B6B;
            padding: 0.3rem 0.2rem;
        }}
        [data-testid="stSidebar"] [class*="st-key-delete_"] button:hover {{
            color: {PRIMARY_COLOR};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _header_logo_css() -> str:
    """Pins the white knockout logo to the right of the red header ribbon."""
    if not LOGO_WHITE_PATH.exists():
        return ""
    return f"""
        [data-testid="stAppDeployButton"] {{ display: none; }}
        [data-testid="stHeader"]::after {{
            content: "";
            position: absolute;
            top: 0;
            bottom: 0;
            right: 3.25rem;
            width: 120px;
            background-image: url("{_data_uri(LOGO_WHITE_PATH, 'image/png')}");
            background-repeat: no-repeat;
            background-position: right center;
            background-size: contain;
            pointer-events: none;
        }}
    """


def render_logo(width: int = 160) -> None:
    """Shows the brand logo if available, otherwise falls back to a text title."""
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=width)
    else:
        st.markdown(f"**{APP_TITLE}**")
