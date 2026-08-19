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

_ACTIVE_THREAD_KEY = "active_thread_id"


def load_secrets_into_env() -> None:
    """Exposes Streamlit Cloud secrets as env vars so backend settings can read them."""
    try:
        secrets = dict(st.secrets)
    except FileNotFoundError:
        return
    for key, value in secrets.items():
        if isinstance(value, str):
            os.environ.setdefault(key, value)


def get_backend_url() -> str | None:
    """Returns the remote backend URL, or None when the backend runs in-process."""
    return os.environ.get("BACKEND_URL") or None


@st.cache_resource
def get_backend_client():
    """Returns an HTTP client when BACKEND_URL is set, else an in-process client."""
    backend_url = get_backend_url()
    if backend_url:
        return BackendClient(backend_url)
    from frontend.local_client import LocalBackendClient

    return LocalBackendClient()


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
    load_secrets_into_env()
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
