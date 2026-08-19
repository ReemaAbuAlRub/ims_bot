"""Streamlit entrypoint: streamlit run frontend/app.py"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests
import streamlit as st

from frontend.api_client import BackendClient
from frontend.state.session import SessionIdentity
from frontend.ui import theme
from frontend.ui.chat_view import ChatView
from frontend.ui.sidebar import SidebarView

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
_ACTIVE_THREAD_KEY = "active_thread_id"


@st.cache_resource
def get_backend_client() -> BackendClient:
    """Returns a cached HTTP client for the FastAPI backend."""
    return BackendClient(BACKEND_URL)


def resolve_active_thread(client: BackendClient, session_id: str, threads: list[dict]) -> dict:
    """Returns the thread to display, creating one when the session has none."""
    if not threads:
        created = client.create_thread(session_id)
        st.session_state[_ACTIVE_THREAD_KEY] = created["id"]
        return created
    known_ids = {thread["id"] for thread in threads}
    active_id = st.session_state.get(_ACTIVE_THREAD_KEY)
    if active_id not in known_ids:
        active_id = threads[0]["id"]
        st.session_state[_ACTIVE_THREAD_KEY] = active_id
    return next(thread for thread in threads if thread["id"] == active_id)


def main() -> None:
    """Renders the branded chat page and drives one request/response cycle per turn."""
    theme.configure_page()
    client = get_backend_client()
    session_id = SessionIdentity().get_or_create()
    view = ChatView()

    try:
        threads = client.list_threads(session_id)
        active_thread = resolve_active_thread(client, session_id, threads)
        messages = client.get_thread(active_thread["id"])["messages"]
    except requests.exceptions.RequestException:
        st.error("Can't reach the chatbot service right now. Please make sure the backend is running.")
        return

    view.render_heading()
    view.render_history(messages)
    question = view.render_input()

    if question:
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    client.send_message(active_thread["id"], question)
                except requests.exceptions.RequestException:
                    st.error("Sorry, something went wrong while generating an answer.")
                else:
                    st.rerun()

    SidebarView().render(client, session_id, threads, active_thread["id"])


if __name__ == "__main__":
    main()
