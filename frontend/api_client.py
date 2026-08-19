"""HTTP client for the backend chat API. Holds no RAG/business logic."""
import requests


class BackendClient:
    """Talks to the FastAPI backend for threads, messages, and answers."""

    def __init__(self, base_url: str, timeout_seconds: float = 90.0):
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def list_threads(self, session_id: str) -> list[dict]:
        """Returns the session's threads, newest first."""
        response = self._request("GET", "/threads", params={"session_id": session_id})
        return response.json()

    def create_thread(self, session_id: str) -> dict:
        """Creates a new empty thread for the session."""
        response = self._request("POST", "/threads", json={"session_id": session_id})
        return response.json()

    def get_thread(self, thread_id: str) -> dict:
        """Returns one thread including its stored messages."""
        response = self._request("GET", f"/threads/{thread_id}")
        return response.json()

    def delete_thread(self, thread_id: str) -> None:
        """Deletes a thread and its messages."""
        self._request("DELETE", f"/threads/{thread_id}")

    def send_message(self, thread_id: str, question: str) -> str:
        """Sends a question and returns the assistant's answer."""
        response = self._request("POST", "/chat", json={"thread_id": thread_id, "question": question})
        return response.json()["answer"]

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Issues a request to the backend and raises on any error status."""
        response = requests.request(
            method, f"{self._base_url}{path}", timeout=self._timeout_seconds, **kwargs
        )
        response.raise_for_status()
        return response
