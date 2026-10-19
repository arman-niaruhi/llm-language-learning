"""HTTP API for the multi-agent language learning system.

Run with:
    uv run uvicorn src.api:app --reload

Then POST to http://localhost:8000/ask with a JSON body such as:
    {"message": "How do you say 'book' in German?", "learning_language": "German"}

Every request to /ask must send the key from API_KEY in .env as the X-API-Key header:
    curl -X POST http://localhost:8000/ask -H "X-API-Key: <key>" -H "Content-Type: application/json" -d '{"message": "..."}'
"""

import json
import os
import secrets
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.vocabulary_agent import VocabularyAgent
from src.agents.grammar_agent import GrammarAgent
from src.agents.conversation_agent import ConversationAgent
from src.agents.web_search_agent import WebSearchAgent
from src.schemas.messages import AgentState, AgentType

load_dotenv()

app = FastAPI(title="Language Learning Agents")


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Reject requests without the configured key. Fails closed when API_KEY is unset."""
    expected = os.getenv("API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="API_KEY is not set on the server")
    if x_api_key is None or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def build_coordinator() -> CoordinatorAgent:
    """Create the coordinator with all specialized agents registered."""
    coordinator = CoordinatorAgent()
    coordinator.register_agent(VocabularyAgent())
    coordinator.register_agent(GrammarAgent())
    coordinator.register_agent(ConversationAgent())
    coordinator.register_agent(WebSearchAgent())
    return coordinator


coordinator = build_coordinator()


TUTORS = {
    "vocabulary": AgentType.VOCABULARY,
    "grammar": AgentType.GRAMMAR,
    "conversation": AgentType.CONVERSATION,
    "web_search": AgentType.WEB_SEARCH,
}


class HistoryTurn(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class AskRequest(BaseModel):
    message: str
    learning_language: str = "English"
    explanation_language: str = "English"
    difficulty_level: str = "beginner"
    # "auto" lets the coordinator pick the tutor; otherwise vocabulary, grammar or conversation.
    agent: str = "auto"
    # Earlier turns of this chat, oldest first, so replies can follow the conversation.
    history: list[HistoryTurn] = []


class AskResponse(BaseModel):
    agent: str
    response: str


def build_state(req: AskRequest) -> AgentState:
    return AgentState(
        user_input=req.message,
        learning_language=req.learning_language,
        explanation_language=req.explanation_language,
        difficulty_level=req.difficulty_level,
        history=[turn.model_dump() for turn in req.history],
        current_agent=TUTORS.get(req.agent, AgentType.COORDINATOR),
    )


@app.post("/ask", response_model=AskResponse, dependencies=[Depends(require_api_key)])
def ask(req: AskRequest) -> AskResponse:
    """Route a request through the coordinator and return the agent's answer."""
    state = build_state(req)
    result = coordinator.graph.invoke(state)
    return AskResponse(
        agent=result["current_agent"],
        response=result.get("response") or "No response generated",
    )


@app.post("/ask/stream", dependencies=[Depends(require_api_key)])
def ask_stream(req: AskRequest) -> StreamingResponse:
    """Same as /ask, but streams newline-delimited JSON as the answer is generated.

    The first line is {"agent": "..."}, then one {"delta": "..."} per chunk.
    A failure mid-stream is sent as {"error": "..."}.
    """
    state = build_state(req)

    def events():
        try:
            # A preselected tutor comes back as a plain string, so normalize it to the enum.
            agent_type = AgentType(coordinator.route(state))
            yield json.dumps({"agent": agent_type.value}) + "\n"
            for chunk in coordinator.agents[agent_type].stream_response(state):
                if chunk:
                    yield json.dumps({"delta": chunk}) + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(events(), media_type="application/x-ndjson")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
