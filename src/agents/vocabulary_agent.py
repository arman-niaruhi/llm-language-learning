"""Vocabulary learning agent."""

from typing import Optional
from src.agents.base_agent import BaseAgent
from src.schemas.messages import AgentType, AgentState


class VocabularyAgent(BaseAgent):
    """Agent specialized in vocabulary teaching and learning."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__(AgentType.VOCABULARY, model=model, api_key=api_key)

    def _build_prompt(self, state: AgentState) -> str:
        """Build vocabulary-specific prompt."""
        return f"""You are a vocabulary teacher helping someone learn {state.learning_language}.
Level: {state.difficulty_level}

{self._history_text(state)}User request: {state.user_input}

Provide:
1. Word definitions and examples
2. Usage in context
3. Related words or synonyms
4. Tips for remembering the word
Keep responses concise and educational.{self._explain_rule(state)}"""
