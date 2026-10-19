"""Example of creating a custom agent."""

import asyncio
from src.agents.base_agent import BaseAgent
from src.schemas.messages import AgentType, AgentState


class CustomPronunciationAgent(BaseAgent):
    """Custom agent for pronunciation practice."""

    def __init__(self):
        # Create a new agent type
        class ExtendedAgentType(AgentType):
            PRONUNCIATION = "pronunciation"

        # Register the new type
        agent_type = ExtendedAgentType.PRONUNCIATION
        super().__init__(agent_type)

    def _build_prompt(self, state: AgentState) -> str:
        """Build pronunciation-specific prompt."""
        return f"""You are a pronunciation coach helping someone learn {state.learning_language}.
Level: {state.difficulty_level}

User request: {state.user_input}

Please:
1. Provide phonetic spelling
2. Give pronunciation tips
3. Explain common mistakes
4. Provide example sentences
Keep responses clear and educational."""


async def main():
    """Example of using custom agent."""

    # Initialize custom agent
    pronunciation_agent = CustomPronunciationAgent()

    # Create state
    state = AgentState(
        user_input="How do I pronounce 'worcestershire'?",
        learning_language="English",
        difficulty_level="beginner"
    )

    # Execute agent
    print("🎤 Pronunciation Coach")
    print("-" * 40)
    result = pronunciation_agent.execute(state)

    print(f"\nResponse:\n{result.response}")


if __name__ == "__main__":
    asyncio.run(main())
