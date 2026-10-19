# Project Summary

## Overview

**Language Learning Multi-Agent System** is a sophisticated console application that uses multiple AI agents to help users learn languages. The system features:

- **Coordinator Agent**: Routes user requests to appropriate specialized agents
- **Vocabulary Agent**: Teaches words, definitions, and usage
- **Grammar Agent**: Explains grammar rules and provides corrections
- **Conversation Agent**: Practices dialogue and conversational skills
- **A2A Communication**: Agents communicate asynchronously via message broker
- **LangGraph**: Each agent has its own state graph for structured execution
- **Local LLM**: Uses Ollama for privacy and cost-effectiveness

## Architecture

### Core Components

```
┌─────────────────────────────────────────────┐
│  Interactive Console (src/main.py)          │
│  User input → Processing → Response         │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Coordinator Agent (CoordinatorAgent)       │
│  • Routes requests to specialized agents    │
│  • LLM-based request classification        │
│  • Response aggregation                    │
└──────────────┬──────────────────────────────┘
               │
        ┌──────┼──────┬──────────┐
        ▼      ▼      ▼          ▼
    ┌─────────────────────────────────────────┐
    │  Specialized Agents                      │
    │  • VocabularyAgent (word learning)      │
    │  • GrammarAgent (grammar rules)         │
    │  • ConversationAgent (practice)         │
    │  • (Extensible for more agents)         │
    └──────────────┬──────────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────────┐
    │  A2A Message Broker                     │
    │  • Inter-agent communication            │
    │  • Message queuing                      │
    │  • Message history                      │
    └──────────────┬──────────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────────┐
    │  LLM Layer (Ollama)                     │
    │  • Mistral (default)                    │
    │  • LLaMA 2                              │
    │  • Neural Chat                          │
    │  • Custom models                        │
    └─────────────────────────────────────────┘
```

### File Structure

```
language-learning-agents/
├── src/
│   ├── agents/                    # Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Base class for all agents
│   │   ├── coordinator_agent.py   # Main routing agent
│   │   ├── vocabulary_agent.py    # Word learning
│   │   ├── grammar_agent.py       # Grammar instruction
│   │   └── conversation_agent.py  # Practice dialogue
│   │
│   ├── communication/              # Agent-to-agent communication
│   │   ├── __init__.py
│   │   └── a2a_broker.py          # Message broker
│   │
│   ├── schemas/                    # Data models
│   │   ├── __init__.py
│   │   └── messages.py            # Message and state schemas
│   │
│   └── main.py                    # Console application entry point
│
├── examples/                       # Example usage
│   ├── __init__.py
│   ├── basic_usage.py             # Basic coordinator usage
│   ├── a2a_communication.py       # A2A messaging example
│   └── custom_agent.py            # Creating custom agents
│
├── pyproject.toml                 # Project configuration (uv)
├── README.md                      # Main documentation
├── QUICKSTART.md                  # Quick setup guide
├── PROJECT_SUMMARY.md             # This file
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
└── uv.lock                        # Dependency lock file
```

## Key Concepts

### 1. **Agent Type Hierarchy**

```python
AgentType (Enum)
├── COORDINATOR      # Main routing agent
├── VOCABULARY       # Word/definition learning
├── GRAMMAR          # Grammar rules and corrections
├── CONVERSATION     # Dialogue practice
└── (Extensible)     # Add new types as needed
```

### 2. **Message Types**

```python
MessageType (Enum)
├── REQUEST          # Agent request
├── RESPONSE         # Agent response
├── QUERY            # Information query
└── FEEDBACK         # Feedback/evaluation
```

### 3. **Agent State**

```python
AgentState
├── user_input       # User's input text
├── learning_language # Target language
├── difficulty_level  # beginner/intermediate/advanced
├── context          # Optional context data
├── messages         # Message history
├── current_agent    # Which agent is processing
└── response         # Final response
```

### 4. **Message Structure**

```python
AgentMessage
├── id               # Unique message ID
├── sender           # Source agent
├── recipient        # Target agent
├── message_type     # REQUEST/RESPONSE/etc
├── content          # Message body
├── payload          # Additional data
└── timestamp        # Message timestamp
```

## How It Works

### 1. User Input Flow

```
1. User enters text in console
2. LanguageLearningConsole.process_input() called
3. AgentState created with user input
4. Coordinator.graph.invoke(state) starts
```

### 2. Coordinator Processing

```
1. Route Node: LLM analyzes request type
   - Determines: VOCABULARY/GRAMMAR/CONVERSATION
   
2. Delegate Node: Sends to appropriate agent
   - Creates AgentMessage
   - Uses A2A broker to send
   - Calls agent.execute()
   
3. Aggregate Node: Formats response
   - Adds agent type prefix
   - Returns to console
```

### 3. Specialized Agent Processing

```
1. Receive request via A2A broker
2. Build LLM prompt with context
3. Call LLM (Ollama) for response
4. Return formatted response
5. Send response back via A2A
```

## Technology Stack

- **LangGraph**: State machine/graph execution
- **LangChain**: LLM abstractions and utilities
- **Ollama**: Local language models (primary)
- **Pydantic**: Data validation and serialization
- **Python uv**: Package manager and virtual environment
- **AsyncIO**: Asynchronous execution

## Configuration

### Environment Variables

```bash
# Ollama server URL (default: http://localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI key (for fallback, optional)
OPENAI_API_KEY=sk-...
```

### Model Selection

Default model: **Mistral** (fast, balanced)

To change:
1. Edit `src/agents/base_agent.py`
2. Change `model="mistral"` to another available model
3. Pull the model: `ollama pull <model>`

Available models:
- `mistral` - Fast, balanced (recommended)
- `llama2` - Larger, more capable
- `neural-chat` - Good for conversations
- `orca-mini` - Lightweight

## Extending the System

### Adding a New Agent Type

1. **Update schemas**:
```python
# src/schemas/messages.py
class AgentType(str, Enum):
    PRONUNCIATION = "pronunciation"  # Add this
```

2. **Create agent class**:
```python
# src/agents/pronunciation_agent.py
from src.agents.base_agent import BaseAgent

class PronunciationAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.PRONUNCIATION)
    
    def _build_prompt(self, state: AgentState) -> str:
        return "You are a pronunciation coach..."
```

3. **Register with coordinator**:
```python
# src/main.py
pronunciation_agent = PronunciationAgent()
console.coordinator.register_agent(pronunciation_agent)
```

4. **Update coordinator routing**:
```python
# src/agents/coordinator_agent.py
# Update _build_prompt() to include PRONUNCIATION
```

## Testing & Development

### Run Examples

```bash
# Basic usage
uv run examples/basic_usage.py

# A2A communication
uv run examples/a2a_communication.py

# Custom agent
uv run examples/custom_agent.py
```

### Debug Mode

```bash
# Enable debug logging
LANGCHAIN_DEBUG=true uv run src/main.py
```

### Check Message History

```python
from src.communication.a2a_broker import get_broker

broker = get_broker()
history = broker.get_message_history()
for msg in history:
    print(f"{msg.sender} -> {msg.recipient}: {msg.content}")
```

## Performance Considerations

1. **Model Size**: Mistral is ~5GB, LLaMA 2 is ~15GB
2. **Response Time**: 5-30 seconds depending on model and system
3. **Memory**: 8GB+ recommended
4. **Concurrency**: Current implementation is sequential per request

## Future Enhancements

- [ ] Multi-turn conversations with context persistence
- [ ] User progress tracking and analytics
- [ ] Spaced repetition for vocabulary
- [ ] Pronunciation assessment with audio
- [ ] Timed quizzes and assessments
- [ ] Custom learning paths
- [ ] Database persistence
- [ ] Web UI/API
- [ ] Multi-language translation
- [ ] Speech-to-text integration

## Troubleshooting

### "Connection refused" to Ollama
```bash
# Start Ollama in another terminal
ollama serve
```

### Model not found
```bash
# List available models
ollama list

# Pull a model
ollama pull mistral
```

### Slow responses
- Use smaller model: `ollama pull orca-mini`
- Close other applications
- Increase system RAM

### Module import errors
```bash
# Reinstall dependencies
uv sync
```

---

**For detailed setup, see [QUICKSTART.md](QUICKSTART.md)**

**For API details, see [README.md](README.md)**
