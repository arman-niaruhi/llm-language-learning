"""Conversation practice agent."""

from typing import Optional
from src.agents.base_agent import BaseAgent
from src.schemas.messages import AgentType, AgentState


class ConversationAgent(BaseAgent):
    """Agent specialized in conversation practice and dialogue."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__(AgentType.CONVERSATION, model=model, api_key=api_key)

    def _build_prompt(self, state: AgentState) -> str:
        """Build conversation-specific prompt."""
        return f"""You are a conversational partner helping someone practice {state.learning_language}.
Level: {state.difficulty_level}

{self._history_text(state)}User input: {state.user_input}

Please:
1. Respond naturally to continue the conversation
2. Use appropriate vocabulary for the level
3. Gently correct major errors
4. Ask follow-up questions to keep the conversation going
5. Provide pronunciation tips if needed

Keep the conversation flowing and encouraging.{self._explain_rule(state)}"""
