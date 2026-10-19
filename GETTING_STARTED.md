# Getting Started - 5 Minute Setup

## TL;DR

```bash
# 1. Install Ollama from https://ollama.ai
# 2. In terminal 1:
ollama serve

# 3. In terminal 2:
cd ~/Documents/llm-language-learning
ollama pull mistral          # First time only
uv sync                      # First time only  
uv run src/main.py           # Run the app
```

---

## Detailed Steps

### 1. Install Ollama (5 minutes)

- Go to https://ollama.ai
- Download for your OS (Mac/Windows/Linux)
- Install and verify: `ollama --version`

### 2. Start Ollama Server

Open a terminal and run:
```bash
ollama serve
```

Keep this window open. You should see:
```
Listening on 127.0.0.1:11434
```

### 3. Prepare Project (5 minutes, first time only)

In a **new terminal window**:

```bash
cd ~/Documents/llm-language-learning

# Download Ollama model (first time: ~3-5 min)
ollama pull mistral

# Install Python dependencies (first time: ~1-2 min)
uv sync
```

### 4. Run the App

```bash
uv run src/main.py
```

You'll see:
```
==============================================================
🎓 LANGUAGE LEARNING SYSTEM - Multi-Agent Coordinator
==============================================================
...
📝 You: 
```

### 5. Start Learning!

```
📝 You: What does "ephemeral" mean?
🤖 Processing with agent system...
🎯 Response:
[VOCABULARY]
Ephemeral means lasting for a very short time...
```

---

## Next Time (Just 2 Steps!)

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Run app
cd ~/Documents/llm-language-learning
uv run src/main.py
```

---

## Quick Commands

Once running:

```
/lang Spanish         → Switch to Spanish
/level intermediate   → Increase difficulty
/menu                → Show menu
/quit                → Exit
```

---

## Need Help?

| Problem | Solution |
|---------|----------|
| Connection refused | Make sure `ollama serve` is running |
| Model not found | Run `ollama pull mistral` |
| Slow responses | Use smaller model: `ollama pull orca-mini` |
| Module errors | Run `uv sync` |

---

## Full Docs

- **Setup Guide**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Full Docs**: See [README.md](README.md)
- **Architecture**: See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **Quick Ref**: See [QUICKSTART.md](QUICKSTART.md)

---

**That's it! Start learning 🚀**
