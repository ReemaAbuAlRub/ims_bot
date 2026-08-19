"""Renders the chat transcript and input box. Owns no business logic."""
import streamlit as st

from frontend.ui import theme


class ChatView:
    """Pure presentation layer over Streamlit's chat primitives."""

    def render_heading(self) -> None:
        """Renders the heading shown above the chat transcript."""
        st.title(theme.CHAT_HEADING)

    def render_history(self, messages: list[dict]) -> None:
        """Renders each prior message bubble in order."""
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def render_input(self) -> str | None:
        """Renders the chat input box and returns the submitted text, if any."""
        return st.chat_input("Ask a question about the Digital Expansion Initiative...")
