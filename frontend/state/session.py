"""Derives a stable session id from the page URL so chats survive a refresh."""
import uuid

import streamlit as st

_QUERY_PARAM = "sid"


class SessionIdentity:
    """Reads the session id from the URL, creating and storing one on first visit."""

    def get_or_create(self) -> str:
        """Returns the browser's session id, adding it to the URL if absent."""
        session_id = st.query_params.get(_QUERY_PARAM)
        if not session_id:
            session_id = uuid.uuid4().hex
            st.query_params[_QUERY_PARAM] = session_id
        return session_id
