# 🚀 Quick Share Reference Card

## ⚠️ BEFORE SHARING: Run This One Command

```bash
cd /Users/cliff.yang/CursorProj/databricks_cli_mcp
./prepare_for_sharing.sh
```

**This will:**
- ✅ Create a CLEAN COPY of your code (in `databricks_cli_mcp_SHARE/`)
- ✅ Sanitize the COPY only (replace credentials with placeholders)
- ✅ Your ORIGINAL code stays UNTOUCHED
- ✅ Your local MCP server keeps working
- ✅ Verify no credentials remain in the copy

**Important:** This creates a separate copy for sharing. Your working code is NOT modified!

---

## 📤 How to Share

### Option 1: GitHub (Best for Open Source)

```bash
cd ../databricks_cli_mcp_SHARE  # Go to the clean copy
git init
git add .
git commit -m "Databricks MCP Server"
git remote add origin https://github.com/YOUR-USERNAME/databricks-mcp-server.git
git push -u origin main
```

**Then share:** `https://github.com/YOUR-USERNAME/databricks-mcp-server`

**After pushing:** `rm -rf ../databricks_cli_mcp_SHARE` (delete the copy)

---

### Option 2: Zip File (Best for Email/Slack)

```bash
cd /Users/cliff.yang/CursorProj
zip -r databricks-mcp-server.zip databricks_cli_mcp_SHARE \
  -x "*.pyc" "*__pycache__*" "*.log" "*/.venv/*" "*/env/*"
```

**Then share:** `databricks-mcp-server.zip`

**After sharing:** `rm -rf databricks_cli_mcp_SHARE` (delete the copy)

---

## ✅ Pre-Share Checklist

- [ ] Ran `./prepare_for_sharing.sh`
- [ ] Script said "Clean copy ready for sharing"
- [ ] Verified `databricks_cli_mcp_SHARE/` directory was created
- [ ] Chose sharing method (GitHub or zip)
- [ ] Shared the CLEAN COPY (not your working code!)
- [ ] Deleted `databricks_cli_mcp_SHARE/` after sharing

---

## 📖 What Recipients Will Do

1. **Get your code** (clone or unzip)
2. **Copy `.env.example` to `.env`**
3. **Fill in THEIR credentials** (not yours!)
4. **Run the server**: `./start_local_mcp.sh`

---

## 🔐 Security Guarantee

✅ **Your `.gitignore` protects:**
- `.env` (your real credentials)
- `.env.local`
- `.databricks_oauth_token`
- `*.log` files

✅ **After sanitization:**
- No PAT tokens in code
- No workspace URLs
- No email addresses

---

## 🆘 Emergency: If You Expose Credentials

1. **Revoke token immediately**: Databricks → Settings → Access Tokens → Revoke
2. **Create new token**: Generate fresh PAT
3. **Update local `.env`**: Use new token

---

## 📚 More Information

- **Complete guide**: `cat SHARING_GUIDE.md`
- **Setup template**: `cat .env.example`
- **Architecture**: `cat ARCHITECTURE.md`
- **README**: `cat README.md`

---

## 🎯 Remember

- **Code** = Public (after sanitization) ✅
- **Credentials** = Private (never share) ❌
- **Templates** = Public (guide others) ✅

**That's it! Share safely! 🚀**

