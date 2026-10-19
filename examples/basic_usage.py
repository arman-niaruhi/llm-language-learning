"""Basic usage example of the language learning system."""

import asyncio
from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.vocabulary_agent import VocabularyAgent
from src.agents.grammar_agent import GrammarAgent
from src.agents.conversation_agent import ConversationAgent
from src.schemas.messages import AgentState


async def main():
    """Basic usage example."""

    # Initialize agents
    coordinator = CoordinatorAgent()
    vocab_agent = VocabularyAgent()
    grammar_agent = GrammarAgent()
    conv_agent = ConversationAgent()

    # Register agents with coordinator
    coordinator.register_agent(vocab_agent)
    coordinator.register_agent(grammar_agent)
    coordinator.register_agent(conv_agent)

    # Create state
    state = AgentState(
        user_input="What does serendipity mean?",
        learning_language="English",
        difficulty_level="beginner"
    )

    # Process through coordinator
    result = coordinator.graph.invoke(state)

    print(f"Response: {result['response']}")


if __name__ == "__main__":
    asyncio.run(main())
