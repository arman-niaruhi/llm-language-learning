"""Agent-to-Agent (A2A) communication broker."""

import asyncio
from collections import defaultdict
from typing import Callable, Any, Optional
from src.schemas.messages import AgentMessage, AgentType, MessageType


class A2ABroker:
    """Broker for agent-to-agent communication."""

    def __init__(self):
        self.message_queues: dict[AgentType, asyncio.Queue] = {}
        self.message_handlers: dict[AgentType, list[Callable]] = defaultdict(list)
        self.message_history: list[AgentMessage] = []

    def register_agent(self, agent_type: AgentType) -> None:
        """Register an agent with the broker."""
        if agent_type not in self.message_queues:
            self.message_queues[agent_type] = asyncio.Queue()

    def subscribe(self, agent_type: AgentType, handler: Callable) -> None:
        """Subscribe a handler to messages for a specific agent."""
        self.message_handlers[agent_type].append(handler)

    def post_message(self, message: AgentMessage) -> bool:
        """Record and enqueue a message without awaiting. Returns True if the recipient is registered."""
        self.message_history.append(message)
        if message.recipient not in self.message_queues:
            return False
        self.message_queues[message.recipient].put_nowait(message)
        return True

    async def send_message(self, message: AgentMessage) -> None:
        """Send a message from one agent to another."""
        if self.post_message(message):
            for handler in self.message_handlers[message.recipient]:
                await handler(message)

    async def receive_message(self, agent_type: AgentType) -> Optional[AgentMessage]:
        """Receive a message for a specific agent."""
        if agent_type in self.message_queues:
            try:
                return await asyncio.wait_for(
                    self.message_queues[agent_type].get(),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                return None
        return None

    def get_message_history(self, agent_type: Optional[AgentType] = None) -> list[AgentMessage]:
        """Get message history, optionally filtered by agent type."""
        if agent_type:
            return [m for m in self.message_history
                    if m.sender == agent_type or m.recipient == agent_type]
        return self.message_history

    def clear_history(self) -> None:
        """Clear message history."""
        self.message_history.clear()


# Global broker instance
_broker_instance: Optional[A2ABroker] = None


def get_broker() -> A2ABroker:
    """Get or create the global A2A broker."""
    global _broker_instance
    if _broker_instance is None:
        _broker_instance = A2ABroker()
    return _broker_instance
