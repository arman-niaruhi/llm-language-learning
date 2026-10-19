from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum
from datetime import datetime


class AgentType(str, Enum):
    """Types of agents in the system."""
    COORDINATOR = "coordinator"
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"
    CONVERSATION = "conversation"
    PRONUNCIATION = "pronunciation"
    VISION = "vision"


class MessageType(str, Enum):
    """Types of messages between agents."""
    REQUEST = "request"
    RESPONSE = "response"
    QUERY = "query"
    FEEDBACK = "feedback"


class AgentMessage(BaseModel):
    """Message passed between agents using A2A communication."""

    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    sender: AgentType
    recipient: AgentType
    message_type: MessageType
    content: str
    payload: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


class AgentState(BaseModel):
    """Shared state for agent execution."""

    user_input: str
    learning_language: str = "English"
    explanation_language: str = "English"
    difficulty_level: str = "beginner"  # beginner, intermediate, advanced
    context: Optional[dict] = None
    history: list[dict] = Field(default_factory=list)  # [{"role": "user"|"assistant", "content": str}]
    messages: list[AgentMessage] = Field(default_factory=list)
    current_agent: AgentType = AgentType.COORDINATOR
    response: Optional[str] = None

    class Config:
        use_enum_values = True
