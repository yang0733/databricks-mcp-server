# Project Structure

## 📁 Clean & Organized Layout

```
databricks_cli_mcp/
│
├── 📘 README.md                    # Complete documentation (YOU ARE HERE!)
├── 📄 PROJECT_STRUCTURE.md         # This file
│
├── 🚀 Quick Start Scripts
│   ├── start_local_mcp.sh          # Start with PAT (recommended)
│   ├── start_oauth_proxy.sh        # Start with OAuth M2M
│   └── deploy_correct.sh           # Deploy to Databricks Apps
│
├── 🔧 Core Server
│   ├── server.py                   # Main FastMCP server
│   ├── local_mcp_server.py         # Local server variant
│   ├── app.py                      # Databricks Apps wrapper
│   └── app.yaml                    # Databricks Apps config
│
├── 🛠️ Infrastructure
│   ├── auth.py                     # Authentication logic
│   ├── databricks_client.py        # SDK client wrapper
│   ├── task_manager.py             # Async operations
│   └── tool_registry.py            # Tool schema converter
│
├── 🔌 Tools (50 Databricks Tools)
│   └── tools/
│       ├── clusters.py             # 7 cluster tools
│       ├── jobs.py                 # 6 job tools
│       ├── sql.py                  # 8 SQL tools
│       ├── unity_catalog.py        # 11 UC tools
│       ├── workspace.py            # 6 workspace tools
│       ├── notebooks.py            # 5 notebook tools
│       ├── repos.py                # 5 repo tools
│       └── secrets.py              # 4 secret tools
│
├── 🔐 OAuth Components (Optional)
│   └── oauth/
│       ├── cursor_oauth_proxy.py           # OAuth proxy for Cursor
│       ├── cursor_proxy.py                 # Generic proxy
│       └── programmatic_oauth_client.py    # OAuth M2M client
│
├── 🧪 Testing
│   ├── test_local.py               # Local server tests
│   └── tests/
│       └── test_deployed_now.py    # Deployed app tests
│
├── 🌐 Transport Layer
│   └── transports/
│       ├── base.py                 # Transport interface
│       └── websocket.py            # WebSocket transport
│
├── 📓 Notebooks (Examples)
│   └── notebooks/
│       ├── simple_test.py          # Basic test notebook
│       └── databricks_agent.py     # Full agent example
│
├── 📦 Configuration
│   ├── requirements.txt            # Python dependencies
│   ├── pyproject.toml              # Package config (uv)
│   ├── .gitignore                  # Git ignore rules
│   └── .python-version             # Python version (3.11.14)
│
└── 📚 Archive
    └── archive/                    # Old documentation (24 files)
```

## 📊 Statistics

- **Core Files**: 12 Python files
- **Tools**: 8 modules with 50 tools
- **Documentation**: 1 main README (down from 25 files!)
- **Scripts**: 3 executable scripts
- **Total Lines**: ~5,000 (clean & organized)

## 🎯 Key Files

### For Users

| File | Purpose |
|------|---------|
| `README.md` | Complete setup & usage guide |
| `start_local_mcp.sh` | One-command startup |
| `test_local.py` | Verify everything works |

### For Developers

| File | Purpose |
|------|---------|
| `server.py` | Main MCP server logic |
| `tools/*.py` | Implement Databricks operations |
| `auth.py` | Handle authentication |

### For Deployment

| File | Purpose |
|------|---------|
| `app.yaml` | Databricks Apps configuration |
| `deploy_correct.sh` | Automated deployment script |
| `requirements.txt` | Production dependencies |

## 🔄 What Changed

### Before Cleanup
```
❌ 25 markdown files (confusing!)
❌ 12 Python files scattered around
❌ Multiple duplicate docs
❌ Unclear structure
❌ Hard to navigate
```

### After Cleanup
```
✅ 1 comprehensive README
✅ Organized into logical directories
✅ Clear separation of concerns
✅ Easy to find everything
✅ Production-ready structure
```

## 🚀 Quick Commands

```bash
# Start server
./start_local_mcp.sh

# Test it works
python test_local.py

# Deploy to production
./deploy_correct.sh

# View logs
tail -f mcp_server.log
```

## 📝 Notes

- All old documentation moved to `archive/` (kept for reference)
- OAuth components in separate `oauth/` directory
- Tests in dedicated `tests/` directory
- Clean, professional structure following Python best practices

---

**Result**: A clean, maintainable, production-ready project! 🎉

