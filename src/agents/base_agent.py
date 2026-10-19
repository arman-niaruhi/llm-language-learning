"""Base agent class for language learning system."""

import os
import time
from abc import ABC
from typing import Optional
from langgraph.graph import StateGraph, END
from src.schemas.messages import AgentType, AgentState, AgentMessage, MessageType
from src.communication.a2a_broker import get_broker

DEFAULT_MODEL = "llama3.1"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
HISTORY_TURNS = 6
DEFAULT_STREAM_DELAY = 0.03  # seconds between streamed chunks


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, agent_type: AgentType, model: Optional[str] = None, api_key: Optional[str] = None, **llm_kwargs):
        self.agent_type = agent_type
        # LLM_PROVIDER=groq sends every agent to Groq's hosted Llama models (GROQ_MODEL).
        # Otherwise the local Ollama model names from .env are used.
        self.provider = "groq"

        if self.provider == "groq":
            from langchain_openai import ChatOpenAI
            self.model = model or os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
            self.llm = ChatOpenAI(
                model=self.model,
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key or os.getenv("GROQ_API_KEY"),
                temperature=0.7,
            )
        else:
            from langchain_ollama import ChatOllama

            self.model = (
                model
                or os.getenv(f"{agent_type.value.upper()}_MODEL")
                or os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)
            )
            ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.llm = ChatOllama(
                model=self.model,
                base_url=ollama_base_url,
                temperature=0.7,
                **llm_kwargs
            )

        self.broker = get_broker()
        self.broker.register_agent(agent_type)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        workflow = StateGraph(AgentState)

        workflow.add_node("process", self.process_input)
        workflow.add_node("respond", self.generate_response)

        workflow.add_edge("process", "respond")
        workflow.add_edge("respond", END)

        workflow.set_entry_point("process")

        return workflow.compile()

    def process_input(self, state: AgentState) -> AgentState:
        """Process the input. Override in subclasses."""
        return state

    def generate_response(self, state: AgentState) -> AgentState:
        """Generate a response using the LLM."""
        response = self.llm.invoke(self._build_prompt(state))
        state.response = response.content
        return state

    def stream_response(self, state: AgentState):
        """Yield the response text as the LLM produces it, at most one chunk per STREAM_DELAY seconds.

        Hosted models can stream faster than people read, so chunks are paced.
        Set STREAM_DELAY=0 in .env for full speed.
        """
        delay = float(os.getenv("STREAM_DELAY", DEFAULT_STREAM_DELAY))
        last = 0.0
        for chunk in self.llm.stream(self._build_prompt(state)):
            wait = delay - (time.monotonic() - last)
            if wait > 0:
                time.sleep(wait)
            last = time.monotonic()
            yield chunk.content

    def _build_prompt(self, state: AgentState) -> str:
        """Build the prompt for the LLM. Override in subclasses."""
        return state.user_input

    @staticmethod
    def _explain_rule(state: AgentState) -> str:
        """Final instruction forcing the reply language; empty when it matches the learned language."""
        if state.explanation_language.lower() == state.learning_language.lower():
            return ""
        rule = (
            f"\n\nIMPORTANT: Write your entire reply, including headings, explanations and instructions, "
            f"in {state.explanation_language}. Only the {state.learning_language} words and example "
            f"sentences stay in {state.learning_language}. Do not answer in English."
        )
        if state.explanation_language.lower() == "persian":
            rule += "\nمهم: تمام پاسخ، شامل عنوان‌ها و توضیحات، باید به زبان فارسی (خط فارسی) باشد."
        return rule

    @staticmethod
    def _history_text(state: AgentState) -> str:
        """Recent conversation turns formatted for inclusion in a prompt."""
        turns = state.history[-HISTORY_TURNS:]
        if not turns:
            return ""
        lines = [f"{t['role'].capitalize()}: {t['content']}" for t in turns]
        return "Conversation so far:\n" + "\n".join(lines) + "\n\n"

    def process_message(self, message: AgentMessage) -> AgentState:
        """Process an incoming A2A message."""
        return self.execute(AgentState(user_input=message.content))

    def execute(self, state: AgentState) -> AgentState:
        """Execute the agent graph."""
        state.current_agent = self.agent_type
        return AgentState(**self.graph.invoke(state))

    def _make_message(
        self,
        recipient: AgentType,
        content: str,
        message_type: MessageType,
        payload: Optional[dict]
    ) -> AgentMessage:
        return AgentMessage(
            sender=self.agent_type,
            recipient=recipient,
            message_type=message_type,
            content=content,
            payload=payload
        )

    async def send_message(
        self,
        recipient: AgentType,
        content: str,
        message_type: MessageType = MessageType.REQUEST,
        payload: dict = None
    ) -> None:
        """Send a message to another agent."""
        await self.broker.send_message(self._make_message(recipient, content, message_type, payload))

    def post_message(
        self,
        recipient: AgentType,
        content: str,
        message_type: MessageType = MessageType.REQUEST,
        payload: dict = None
    ) -> None:
        """Send a message from synchronous code (async handlers are not notified)."""
        self.broker.post_message(self._make_message(recipient, content, message_type, payload))
