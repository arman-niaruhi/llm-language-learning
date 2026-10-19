"""Example of A2A communication between agents."""

import asyncio
from src.agents.vocabulary_agent import VocabularyAgent
from src.communication.a2a_broker import get_broker
from src.schemas.messages import AgentType, MessageType


async def example_agent_communication():
    """Demonstrate A2A communication."""

    broker = get_broker()
    vocab_agent = VocabularyAgent()

    # Define a handler for messages
    async def handle_vocab_response(message):
        print(f"\n📬 Message received by {message.recipient}:")
        print(f"  From: {message.sender}")
        print(f"  Type: {message.message_type}")
        print(f"  Content: {message.content}")

    # Subscribe to messages
    broker.subscribe(AgentType.VOCABULARY, handle_vocab_response)

    # Send a message
    print("📤 Sending message to vocabulary agent...")
    await vocab_agent.send_message(
        AgentType.VOCABULARY,
        "Explain the word 'ubiquitous'",
        MessageType.REQUEST,
        {"language": "English", "level": "intermediate"}
    )

    # Give it time to process
    await asyncio.sleep(1)

    # Print message history
    print(f"\n📋 Message History:")
    history = broker.get_message_history(AgentType.VOCABULARY)
    for msg in history:
        print(f"  {msg.sender} -> {msg.recipient}: {msg.content[:50]}...")


if __name__ == "__main__":
    asyncio.run(example_agent_communication())
