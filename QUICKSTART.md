# Quick Start Guide

## 1️⃣ Install Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai)

## 2️⃣ Pull a Model

Open terminal and run:

```bash
# For Mistral (recommended, fast)
ollama pull mistral

# Or other options
ollama pull llama2          # Larger, more capable
ollama pull neural-chat     # Good for conversations
ollama pull orca-mini       # Lightweight
```

## 3️⃣ Start Ollama Server

In a separate terminal, start the Ollama server:

```bash
ollama serve
```

You should see:
```
Listening on 127.0.0.1:11434
```

## 4️⃣ Install Project Dependencies

```bash
cd llm-language-learning
uv sync
```

## 5️⃣ Run the Application

```bash
uv run src/main.py
```

## 6️⃣ Start Learning!

The application will check if Ollama is running and start the interactive console:

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

## 📚 Example Interactions

```
📝 You: What does "serendipity" mean?
🤖 Processing with agent system...
🎯 Response:
[VOCABULARY]
Serendipity refers to finding something valuable or delightful by chance...

📝 You: Explain present perfect tense
🎯 Response:
[GRAMMAR]
The present perfect tense is used to describe actions that started in the past...

📝 You: Let's have a conversation
🎯 Response:
[CONVERSATION]
Great! Let me start - How was your day today?
```

## 🔧 Configuration

### Custom Ollama URL

Create `.env` file:
```
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

### Switch Models Per Run

The agents use "mistral" by default. To use a different model:

Edit `src/agents/base_agent.py` and change:
```python
def __init__(self, agent_type: AgentType, model: str = "llama2", use_ollama: bool = True):
```

## 🐛 Troubleshooting

### "Connection refused" Error
- Make sure Ollama server is running: `ollama serve`
- Check it's accessible: `curl http://localhost:11434`

### Model Not Found
```bash
# List available models
ollama list

# Pull the missing model
ollama pull mistral
```

### Slow Responses
- Use a smaller model: `ollama pull orca-mini`
- Close other applications
- Check system resources

### Change Difficulty
```
📝 You: /level intermediate
✓ Changed difficulty to: intermediate
```

## 📝 Changing Languages

```
📝 You: /lang Spanish
✓ Changed language to: Spanish

📝 You: What does "hola" mean?
```

## 🎓 Tips

1. **Start simple**: Begin with vocabulary at beginner level
2. **Practice regularly**: Use the conversation agent daily
3. **Mix topics**: Switch between vocabulary, grammar, and conversation
4. **Increase difficulty**: Gradually move to intermediate then advanced
5. **Ask follow-ups**: The agents will provide more detail if you ask

---

**Happy Learning! 🚀**
