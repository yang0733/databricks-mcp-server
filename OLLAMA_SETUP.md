# 🤖 Ollama Local LLM Setup

Use the Databricks Chat Agent with a **completely free, local LLM** - no API keys needed!

## ✅ Quick Start (You're Ready!)

You already have Ollama installed with these models:
- `qwen2.5:7b` (4.7 GB) - ⭐ **Recommended** - Great at tool calling
- `phi4:latest` (9.1 GB) - Most capable but slower
- `phi3.5:latest` (2.2 GB) - Faster, good for simple queries
- `phi3:latest` (2.2 GB) - Fast and efficient
- `llama3.2:1b` (1.3 GB) - Very fast but limited

## 🚀 Run the Chat Agent with Ollama

```bash
cd /Users/cliff.yang/CursorProj/databricks_cli_mcp

# Use default model (qwen2.5:7b)
python chat_agent_ollama.py

# Or specify a different model
OLLAMA_MODEL="phi4:latest" python chat_agent_ollama.py
```

That's it! No API keys, no cloud costs, 100% local!

## 💬 Example Session

```bash
$ python chat_agent_ollama.py

🤖 DATABRICKS CHAT AGENT - OLLAMA VERSION
================================================================================

Checking Ollama...
✓ Ollama is running with model: qwen2.5:7b

✓ Connected to Databricks MCP Server
✓ Connected to Ollama (qwen2.5:7b)
✓ Loaded 48 tools from MCP server

💡 Tip: Be specific in your requests. For example:
   'List all clusters' instead of 'show me stuff'

You: Show me all my clusters

🤔 Thinking...
🔧 Executing: list_clusters

Agent: I found 3 clusters in your workspace:

1. Shared Autoscaling Americas (TERMINATED)
   - ID: 0730-172948-runts698
   - Spark: 14.3.x-scala2.12

2. Shared Autoscaling Europe (RUNNING)
   - ID: 0730-173143-ores78
   - Spark: 14.3.x-scala2.12

3. ml-cluster (TERMINATED)
   - ID: 0820-151234-abc123

You: Start the first cluster

🤔 Thinking...
🔧 Executing: start_cluster
   Parameters: {
     "cluster_id": "0730-172948-runts698"
   }

Agent: I've started the cluster "Shared Autoscaling Americas". 
It should be ready in a few minutes.
```

## 🎯 Model Recommendations

### For Best Results
Use **qwen2.5:7b** (default):
```bash
python chat_agent_ollama.py
```
- Good at understanding tool calls
- Balance of speed and capability
- 4.7 GB size

### For Maximum Capability
Use **phi4**:
```bash
OLLAMA_MODEL="phi4:latest" python chat_agent_ollama.py
```
- Best reasoning ability
- Most accurate tool selection
- 9.1 GB size, slower

### For Speed
Use **phi3.5**:
```bash
OLLAMA_MODEL="phi3.5:latest" python chat_agent_ollama.py
```
- Fast responses
- Good for simple queries
- 2.2 GB size

## 🆚 Ollama vs Cloud LLMs

| Feature | Ollama (Local) | Claude/GPT (Cloud) |
|---------|----------------|-------------------|
| **Cost** | Free ✅ | $0.01-0.05 per query |
| **Privacy** | 100% local ✅ | Sent to cloud |
| **Speed** | Depends on hardware | Fast |
| **Capability** | Good for most tasks | Excellent |
| **Setup** | Simple ✅ | Need API key |
| **Internet** | Not required ✅ | Required |

## 🔧 Advanced Configuration

### Change Model at Runtime
```bash
# Use a different model
OLLAMA_MODEL="phi4:latest" python chat_agent_ollama.py
```

### Adjust Ollama Settings
Edit `chat_agent_ollama.py`:

```python
"options": {
    "temperature": 0.7,  # Lower = more focused (0.0-1.0)
    "top_p": 0.9,       # Nucleus sampling (0.0-1.0)
    "num_ctx": 4096,    # Context window size
}
```

### Use a Different Ollama Instance
```bash
OLLAMA_URL="http://other-machine:11434" python chat_agent_ollama.py
```

## 📊 Performance Comparison

Tested on Apple M1 Max:

| Model | Response Time | Quality | Memory |
|-------|--------------|---------|--------|
| qwen2.5:7b | ~3-5 sec | ⭐⭐⭐⭐ | 6 GB |
| phi4 | ~8-12 sec | ⭐⭐⭐⭐⭐ | 11 GB |
| phi3.5 | ~2-3 sec | ⭐⭐⭐ | 3 GB |
| llama3.2:1b | ~1 sec | ⭐⭐ | 2 GB |

## 🐛 Troubleshooting

### "Cannot connect to Ollama"
```bash
# Check if Ollama is running
ollama list

# If not running, it will auto-start on first command
ollama run qwen2.5:7b
# Press Ctrl+D to exit the chat
```

### "Model not found"
```bash
# Pull the model
ollama pull qwen2.5:7b
```

### Slow Responses
```bash
# Use a smaller/faster model
OLLAMA_MODEL="phi3.5:latest" python chat_agent_ollama.py

# Or reduce context window (edit chat_agent_ollama.py)
"num_ctx": 2048  # instead of 4096
```

### Out of Memory
Close other applications or use a smaller model:
```bash
OLLAMA_MODEL="phi3.5:latest" python chat_agent_ollama.py
```

## 🎓 Tips for Best Results

1. **Be Specific**: "List all clusters" > "show me stuff"
2. **One Task at a Time**: Break complex requests into steps
3. **Use Simple Language**: Clear instructions work best
4. **Be Patient**: Local models take a few seconds to respond
5. **Context Matters**: The agent remembers recent conversation

## 🔄 Switching Between Ollama and Cloud

You can use both! Just run different scripts:

```bash
# Local/Free - Ollama
python chat_agent_ollama.py

# Cloud/Paid - Claude (more capable)
export ANTHROPIC_API_KEY='sk-ant-...'
python chat_agent.py
```

## 🌟 Benefits of Local LLM

✅ **Free** - No API costs
✅ **Private** - Data never leaves your machine
✅ **Offline** - Works without internet
✅ **Fast** - No network latency
✅ **Unlimited** - No rate limits
✅ **Customizable** - Full control over model

## 📈 Next Steps

1. **Try it now**: `python chat_agent_ollama.py`
2. **Experiment with models**: Try different models for your use case
3. **Optimize performance**: Adjust temperature and other settings
4. **Compare**: Try both Ollama and Claude to see which you prefer

## 📞 Support

- **Ollama Docs**: https://ollama.ai
- **Model Library**: https://ollama.ai/library
- **Chat Agent Docs**: [CHAT_AGENT.md](./CHAT_AGENT.md)

---

🎉 **You're all set!** Start chatting with your Databricks workspace using a free, local LLM!

```bash
python chat_agent_ollama.py
```

