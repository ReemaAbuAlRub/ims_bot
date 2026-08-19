"""Orchestrates retrieval, prompt assembly, and the LLM call for one chat turn."""
from backend.core.llm_client import ClaudeClient
from backend.core.prompt_builder import PromptBuilder
from backend.core.retriever import Retriever
from backend.models.message import ChatMessage


class ConversationService:
    """Use-case entry point: answer(question, history) -> answer text."""

    def __init__(self, retriever: Retriever, prompt_builder: PromptBuilder, llm_client: ClaudeClient):
        self._retriever = retriever
        self._prompt_builder = prompt_builder
        self._llm_client = llm_client

    def answer(self, question: str, history: list[ChatMessage]) -> str:
        """Retrieves relevant chunks and returns Claude's grounded reply."""
        chunks = self._retriever.retrieve(question, history)
        context_block = self._prompt_builder.build_context_block(chunks)
        system_block = self._prompt_builder.build_system_block()
        messages = self._build_messages(history, question, context_block)
        return self._llm_client.generate_reply(system_block, messages)

    def _build_messages(self, history: list[ChatMessage], question: str, context_block: str) -> list[dict]:
        """Builds the Messages API turns: prior history + context-augmented question."""
        history_turns = [{"role": m.role.value, "content": m.content} for m in history]
        current_turn = {"role": "user", "content": f"{context_block}\n\nUser question: {question}"}
        return [*history_turns, current_turn]
