"""Grammar learning agent."""

from typing import Optional
from src.agents.base_agent import BaseAgent
from src.schemas.messages import AgentType, AgentState


class GrammarAgent(BaseAgent):
    """Agent specialized in grammar teaching and error correction."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__(AgentType.GRAMMAR, model=model, api_key=api_key)

    def _build_prompt(self, state: AgentState) -> str:
        """Build grammar-specific prompt."""
        return f"""You are a grammar teacher helping someone learn {state.learning_language}.
Level: {state.difficulty_level}

{self._history_text(state)}User request: {state.user_input}

Provide:
1. Grammar rules explanation
2. Examples of correct usage
3. Common mistakes to avoid
4. Practice exercises if relevant
Be clear and systematic in your explanations.{self._explain_rule(state)}"""
