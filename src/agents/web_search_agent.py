"""Web search agent that answers with live results from the internet."""

import os
from typing import Optional
import requests
from src.agents.base_agent import BaseAgent, HISTORY_TURNS
from src.schemas.messages import AgentType, AgentState

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
# Groq's built-in browser_search tool is only available on the gpt-oss models.
WEB_SEARCH_MODEL = "openai/gpt-oss-120b"


class WebSearchAgent(BaseAgent):
    """Agent that searches the web for current or factual information and cites its sources."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__(AgentType.WEB_SEARCH, model=model, api_key=api_key)
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

    def _messages(self, state: AgentState) -> list[dict]:
        system = (
            f"You are a helpful assistant for someone learning {state.learning_language} "
            f"(level: {state.difficulty_level}). Search the web for current, factual or specific "
            "questions. Answer clearly and include clickable Markdown links to the sources you used. "
            "Never invent source URLs." + self._explain_rule(state)
        )
        return [
            {"role": "system", "content": system},
            *state.history[-HISTORY_TURNS:],
            {"role": "user", "content": state.user_input},
        ]

    def search(self, state: AgentState) -> str:
        """Answer the request using Groq's browser_search tool."""
        response = requests.post(
            GROQ_CHAT_URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": WEB_SEARCH_MODEL,
                "messages": self._messages(state),
                "tools": [{"type": "browser_search"}],
                "tool_choice": "required",
                "temperature": 0.2,
                "max_completion_tokens": 4096,
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def generate_response(self, state: AgentState) -> AgentState:
        state.response = self.search(state)
        return state

    def stream_response(self, state: AgentState):
        """The search runs server-side, so the finished answer arrives in one piece."""
        yield self.search(state)
