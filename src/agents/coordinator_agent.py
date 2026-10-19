"""Coordinator agent that routes requests to specialized agents."""

import re
from typing import Optional
from src.agents.base_agent import BaseAgent
from src.schemas.messages import AgentType, AgentState, MessageType
from langgraph.graph import StateGraph, END

ROUTABLE = {
    "VOCABULARY": AgentType.VOCABULARY,
    "GRAMMAR": AgentType.GRAMMAR,
    "CONVERSATION": AgentType.CONVERSATION,
}


class CoordinatorAgent(BaseAgent):
    """Main coordinator agent that manages other agents."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__(AgentType.COORDINATOR, model=model, api_key=api_key)
        self.agents = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """Register a specialized agent."""
        self.agents[agent.agent_type] = agent

    def _build_graph(self) -> StateGraph:
        """Build coordinator graph with routing."""
        workflow = StateGraph(AgentState)

        workflow.add_node("route", self.route_request)
        workflow.add_node("delegate", self.delegate_to_agent)
        workflow.add_node("aggregate", self.aggregate_response)

        workflow.add_edge("route", "delegate")
        workflow.add_edge("delegate", "aggregate")
        workflow.add_edge("aggregate", END)
        workflow.set_entry_point("route")

        return workflow.compile()

    def _build_prompt(self, state: AgentState) -> str:
        """Build routing prompt."""
        return f"""Analyze this request from someone learning {state.learning_language} and determine which agent should handle it.

{self._history_text(state)}Request: {state.user_input}

Available agents:
- VOCABULARY: for word meanings, definitions, synonyms, translations
- GRAMMAR: for grammar rules, sentence structure, corrections
- CONVERSATION: for practice conversations and dialogue, including replies to an ongoing conversation

Return JSON with:
{{"agent": "VOCABULARY|GRAMMAR|CONVERSATION", "reason": "brief explanation"}}

Respond ONLY with valid JSON."""

    def route(self, state: AgentState) -> AgentType:
        """Pick the tutor for this request, unless one was preselected."""
        if state.current_agent in ROUTABLE.values():
            return state.current_agent

        response = self.llm.invoke(self._build_prompt(state))
        match = re.search(r"VOCABULARY|GRAMMAR|CONVERSATION", response.content.upper())
        return ROUTABLE[match.group(0)] if match else AgentType.VOCABULARY

    def route_request(self, state: AgentState) -> AgentState:
        state.current_agent = self.route(state)
        return state

    def delegate_to_agent(self, state: AgentState) -> AgentState:
        """Delegate request to the appropriate agent."""
        target_agent = self.agents.get(state.current_agent)

        if target_agent:
            self.post_message(
                state.current_agent,
                state.user_input,
                MessageType.REQUEST,
                {"difficulty_level": state.difficulty_level}
            )
            state.response = target_agent.execute(state).response

        return state

    def aggregate_response(self, state: AgentState) -> AgentState:
        """Aggregate responses from agents."""
        return state
