"""Thin wrapper around the Anthropic Messages API."""
import anthropic


class ClaudeClient:
    """Sends a system prompt + conversation to Claude and returns the reply text."""

    def __init__(self, api_key: str, model: str, max_tokens: int):
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    def generate_reply(self, system_block: list[dict], messages: list[dict]) -> str:
        """Calls the Messages API and returns the concatenated text response."""
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system_block,
            messages=messages,
        )
        return "".join(block.text for block in response.content if block.type == "text")
