# Language Learning Multi-Agent System

A sophisticated language learning system featuring a coordinator agent that orchestrates multiple specialized agents for different learning aspects. Each agent is built with **LangGraph** and communicates via **Agent-to-Agent (A2A)** protocol.

## 🎯 Features

- **Coordinator Agent**: Routes user requests to appropriate specialized agents
- **Vocabulary Agent**: Teaches words, definitions, synonyms, and usage examples
- **Grammar Agent**: Explains grammar rules, provides corrections, and exercises
- **Conversation Agent**: Practices dialogue and conversational skills
- **A2A Communication**: Agents communicate asynchronously using a message broker
- **LangGraph Integration**: Each agent has its own state graph for structured execution
- **Multi-language Support**: Learn any language with difficulty level adjustment

## 📦 Project Structure

```
language-learning-agents/
├── src/
│   ├── agents/
│   │   ├── base_agent.py          # Base class for all agents
│   │   ├── coordinator_agent.py   # Main routing agent
│   │   ├── vocabulary_agent.py    # Word learning
│   │   ├── grammar_agent.py       # Grammar instruction
│   │   └── conversation_agent.py  # Practice dialogue
│   ├── communication/
│   │   └── a2a_broker.py         # Agent-to-agent message broker
│   ├── schemas/
│   │   └── messages.py           # Message and state schemas
│   └── main.py                   # Console application
├── pyproject.toml
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai) installed locally (or OpenAI API key as fallback)

### Installation

1. Navigate to the project:
```bash
cd llm-language-learning
```

2. **Setup Ollama** (if using local models):
```bash
# Install Ollama from https://ollama.ai
# Pull a model (default: mistral)
ollama pull mistral
# Or use other models
ollama pull llama2
ollama pull neural-chat
# Start Ollama server
ollama serve
```

3. (Optional) Create `.env` file to configure:
```bash
# For custom Ollama URL
echo "OLLAMA_BASE_URL=http://localhost:11434" > .env

# Or for OpenAI (if not using Ollama)
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

4. Install dependencies using uv:
```bash
uv sync
```

### Running the Application

Start the interactive learning console:

```bash
uv run src/main.py
```

Or use the installed command:
```bash
uv run learn
```

## 💬 Usage Examples

Once running, you can interact with the system:

```
📝 You: What does "serendipity" mean?
🤖 Processing with agent system...
🎯 Response:
[VOCABULARY]
Serendipity is the occurrence of finding valuable things by chance...

📝 You: How do I use past tense in Spanish?
🎯 Response:
[GRAMMAR]
Spanish past tense has two main forms: preterite and imperfect...

📝 You: Let's practice a conversation
🎯 Response:
[CONVERSATION]
Great! Let's start. Buenos días! How was your day?
```

### Commands

- `/lang <language>` - Change learning language (e.g., `/lang Spanish`)
- `/level <difficulty>` - Set difficulty: `beginner`, `intermediate`, `advanced`
- `/menu` - Show menu
- `/quit` - Exit application

## 🏗️ Architecture

### Agent System

Each agent extends `BaseAgent` and implements:
- `_build_prompt()`: Creates context-specific prompts
- `process_input()`: Handles input processing
- `generate_response()`: Uses LLM for responses

### LangGraph Integration

Each agent has a state graph with nodes:
- **process**: Input processing
- **respond**: LLM response generation

```python
workflow = StateGraph(AgentState)
workflow.add_node("process", self.process_input)
workflow.add_node("respond", self.generate_response)
workflow.set_entry_point("process")
```

### A2A Communication

The `A2ABroker` handles inter-agent communication:

```python
# Send message
await agent.send_message(
    AgentType.VOCABULARY,
    "What does X mean?",
    MessageType.REQUEST
)

# Receive message
message = await broker.receive_message(AgentType.VOCABULARY)
```

### Coordinator Routing

The coordinator analyzes requests and routes them:

1. **Route**: LLM analyzes request type
2. **Delegate**: Sends to appropriate agent via A2A
3. **Aggregate**: Formats final response

## 🔧 Configuration

Modify agent behavior in `src/agents/`:

### Change Model
```python
agent = VocabularyAgent()
# Default is gpt-4o-mini, change in BaseAgent.__init__()
```

### Add New Agents

1. Create new agent class:
```python
class PronunciationAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.PRONUNCIATION)
    
    def _build_prompt(self, state: AgentState) -> str:
        return "..."
```

2. Register with coordinator:
```python
console.coordinator.register_agent(PronunciationAgent())
```

3. Update routing in `CoordinatorAgent._build_prompt()`

## 📊 Message Flow

```
User Input
    ↓
Coordinator (Route Node)
    ↓
Agent Type Determination (LLM)
    ↓
A2A Broker (Send Message)
    ↓
Specialized Agent (Process + Respond)
    ↓
A2A Broker (Message History)
    ↓
Coordinator (Aggregate Response)
    ↓
Console Output
```

## 🛠️ Development

### Run with debugging:
```bash
OPENAI_LOG=debug uv run src/main.py
```

### Check message history:
```python
broker = get_broker()
history = broker.get_message_history()
```

## 📝 Technologies

- **LangGraph**: State graph management for agents
- **LangChain**: LLM framework and utilities
- **Ollama**: Local language models (primary)
- **OpenAI API**: Cloud-based language model (fallback)
- **Pydantic**: Data validation and schemas
- **uv**: Python package manager

## 🎓 Learning Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://js.langchain.com/docs/)
- [OpenAI API](https://platform.openai.com/docs)

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add new agent types
- Improve routing logic
- Enhance A2A communication
- Add persistence layer

---

**Happy Learning! 🚀**