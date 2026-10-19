# Complete Setup Guide

## 🎯 What You're Building

A **multi-agent language learning system** with:
- ✅ Coordinator Agent (routes requests)
- ✅ Vocabulary Agent (teaches words)
- ✅ Grammar Agent (teaches grammar)
- ✅ Conversation Agent (practice dialogue)
- ✅ A2A Communication (agent-to-agent messaging)
- ✅ LangGraph (agent state graphs)
- ✅ Local LLM support (Ollama)
- ✅ Interactive console interface

---

## 📋 Prerequisites

- **Python 3.11+** (Check: `python3 --version`)
- **Ollama** (Download from https://ollama.ai)
- **At least 8GB RAM**

---

## 🚀 Step-by-Step Setup

### Step 1: Install Ollama

1. Visit [ollama.ai](https://ollama.ai)
2. Download and install for your OS
3. Open terminal and verify:
   ```bash
   ollama --version
   ```

### Step 2: Pull a Language Model

Choose one (Mistral is recommended for speed):

```bash
# Fast and balanced (recommended) ~5GB
ollama pull mistral

# Larger and more capable ~15GB
ollama pull llama2

# Good for conversations
ollama pull neural-chat

# Lightweight ~2GB
ollama pull orca-mini
```

View available models:
```bash
ollama list
```

### Step 3: Start Ollama Server

Open a dedicated terminal window and keep it running:

```bash
ollama serve
```

You should see:
```
Listening on 127.0.0.1:11434
```

**Keep this window open while using the app!**

### Step 4: Navigate to Project Directory

```bash
cd ~/Documents/llm-language-learning
```

(Or wherever you placed the project)

### Step 5: Install Python Dependencies

Using uv (Python package manager):

```bash
uv sync
```

This installs all dependencies in a virtual environment.

### Step 6: (Optional) Configure Environment

Copy the example env file:

```bash
cp .env.example .env
```

Edit `.env` if needed (usually default is fine):
```
OLLAMA_BASE_URL=http://localhost:11434
```

### Step 7: Run the Application

```bash
uv run src/main.py
```

**Or use the installed command:**
```bash
uv run learn
```

---

## 💬 Using the Application

Once started, you'll see:

```
==============================================================
🎓 LANGUAGE LEARNING SYSTEM - Multi-Agent Coordinator
==============================================================
Learning Language: English
Difficulty Level: beginner
--------------------------------------------------------------
Commands:
  /lang <language>     - Change learning language
  /level <difficulty>  - Change difficulty (beginner/intermediate/advanced)
  /menu                - Show this menu
  /quit                - Exit
  Or enter your question/request
==============================================================

📝 You: 
```

### Try These Commands:

```
📝 You: What does "serendipity" mean?
[VOCABULARY agent responds]

📝 You: Explain the past tense
[GRAMMAR agent responds]

📝 You: Let's practice conversation
[CONVERSATION agent responds]

📝 You: /lang Spanish
✓ Changed language to: Spanish

📝 You: /level intermediate
✓ Changed difficulty to: intermediate

📝 You: /quit
Goodbye! Keep learning! 👋
```

---

## 📊 Project Structure

```
llm-language-learning/
├── src/                       # Source code
│   ├── agents/               # AI agents
│   │   ├── base_agent.py      # Base class
│   │   ├── coordinator_agent.py
│   │   ├── vocabulary_agent.py
│   │   ├── grammar_agent.py
│   │   └── conversation_agent.py
│   │
│   ├── communication/        # Agent communication
│   │   └── a2a_broker.py     # Message broker
│   │
│   ├── schemas/             # Data models
│   │   └── messages.py      # Message definitions
│   │
│   └── main.py              # Console app
│
├── examples/                # Usage examples
│   ├── basic_usage.py
│   ├── a2a_communication.py
│   └── custom_agent.py
│
├── README.md                # Full documentation
├── QUICKSTART.md            # Quick start
├── PROJECT_SUMMARY.md       # Architecture details
├── SETUP_GUIDE.md           # This file
├── pyproject.toml           # Project config (uv)
└── .env.example             # Environment template
```

---

## 🛠️ Troubleshooting

### Problem: "Connection refused" error

**Solution**: Make sure Ollama is running
```bash
# In a separate terminal
ollama serve
```

### Problem: Model not found

**Solution**: Pull the model
```bash
ollama pull mistral
ollama list  # View installed models
```

### Problem: Slow responses

**Solution**: Use a smaller model
```bash
ollama pull orca-mini
```

Then edit `src/agents/base_agent.py` line 14:
```python
def __init__(self, agent_type: AgentType, model: str = "orca-mini", ...):
```

### Problem: "Module not found" errors

**Solution**: Reinstall dependencies
```bash
uv sync
```

### Problem: Out of memory

**Solution**: Close other applications or use smaller model
```bash
ollama pull orca-mini  # Only 2GB
```

---

## 🔧 Customization

### Change Default Model

Edit `src/agents/base_agent.py` line 14:
```python
# From:
def __init__(self, agent_type: AgentType, model: str = "mistral", ...):

# To:
def __init__(self, agent_type: AgentType, model: str = "llama2", ...):
```

### Change Ollama Server URL

Create/edit `.env`:
```
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

### Add New Agent Type

See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for extending the system.

---

## 📚 Learning Resources

- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **LangChain**: https://js.langchain.com/docs/
- **Ollama**: https://ollama.ai
- **Python AsyncIO**: https://docs.python.org/3/library/asyncio.html

---

## 🚀 Next Steps

1. **Run the application**: `uv run src/main.py`
2. **Try examples**: `uv run examples/basic_usage.py`
3. **Explore code**: Check out `src/agents/` and `src/communication/`
4. **Create custom agent**: See `examples/custom_agent.py`
5. **Read architecture**: See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## 📝 Important Notes

- **Keep Ollama running** in a separate terminal while using the app
- **First request is slower** (model initialization)
- **Responses depend on model size** and your system specs
- **All processing is local** - no data sent to external services

---

## 🆘 Need Help?

1. Check [QUICKSTART.md](QUICKSTART.md) for quick answers
2. Read [README.md](README.md) for full documentation
3. See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for architecture
4. Check examples in `examples/` directory

---

**Ready to learn? 🎓 Run: `uv run src/main.py`**
