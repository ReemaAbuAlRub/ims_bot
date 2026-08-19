"""Renders the sidebar: corner logo, new-chat button, and thread list."""
import streamlit as st

from frontend.api_client import BackendClient
from frontend.ui import theme

_ACTIVE_THREAD_KEY = "active_thread_id"


class SidebarView:
    """Sidebar UI for branding, switching between chat threads, and deleting them."""

    def render(
        self,
        client: BackendClient,
        session_id: str,
        threads: list[dict],
        active_thread_id: str,
    ) -> None:
        """Draws the sidebar and applies any thread action the user picks."""
        with st.sidebar:
            theme.render_logo(width=140)
            st.divider()
            if st.button("+ New chat", use_container_width=True, key="new_chat"):
                created = client.create_thread(session_id)
                st.session_state[_ACTIVE_THREAD_KEY] = created["id"]
                st.rerun()
            st.caption("Previous chats")
            for thread in threads:
                self._render_thread_row(client, thread, active_thread_id)

    def _render_thread_row(self, client: BackendClient, thread: dict, active_thread_id: str) -> None:
        """Draws one thread as a list-style row with a delete affordance."""
        thread_id = thread["id"]
        prefix = "thread_active_" if thread_id == active_thread_id else "thread_"
        name_column, delete_column = st.columns([5, 1], gap="small")
        with name_column:
            if st.button(
                thread["title"], key=f"{prefix}{thread_id}", use_container_width=True, type="tertiary"
            ):
                st.session_state[_ACTIVE_THREAD_KEY] = thread_id
                st.rerun()
        with delete_column:
            if st.button("🗑", key=f"delete_{thread_id}", help="Delete chat", type="tertiary"):
                client.delete_thread(thread_id)
                if st.session_state.get(_ACTIVE_THREAD_KEY) == thread_id:
                    st.session_state.pop(_ACTIVE_THREAD_KEY, None)
                st.rerun()
