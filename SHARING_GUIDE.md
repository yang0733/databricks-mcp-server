# 🔒 Safe Code Sharing Guide

## ⚠️ Before Sharing - Security Checklist

### 🚨 **CRITICAL: Remove Your Credentials First!**

Your code currently contains **real credentials** in these places:

```
❌ Your PAT token: dapi1234567890abcdef1234567890abcdef...
❌ Your workspace: your-workspace.cloud.databricks.com
❌ Your email: your-email@company.com
```

**Files that contain your real credentials:**
- `ARCHITECTURE.md` (documentation examples)
- `local_mcp_server.py` (possibly in comments)
- `test_local.py` (test setup)
- `deploy_correct.sh` (deployment script)
- Various OAuth files

---

## ✅ Step-by-Step Sharing Process

### Step 1: Clean Up Credentials (REQUIRED!)

Run this script to sanitize your files:

```bash
cd /Users/cliff.yang/CursorProj/databricks_cli_mcp

# Replace your actual credentials with placeholders
find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.sh" \) \
  -not -path "./archive/*" \
  -not -path "./.venv/*" \
  -not -path "./env/*" \
  -exec sed -i '' 's/dapi1234567890abcdef1234567890abcdef[a-f0-9]*/dapi1234567890abcdef1234567890abcdef/g' {} \;

find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.sh" \) \
  -not -path "./archive/*" \
  -not -path "./.venv/*" \
  -not -path "./env/*" \
  -exec sed -i '' 's/e2-demo-west\.cloud\.databricks\.com/your-workspace.cloud.databricks.com/g' {} \;

find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.sh" \) \
  -not -path "./archive/*" \
  -not -path "./.venv/*" \
  -not -path "./env/*" \
  -exec sed -i '' 's/cliff\.yang@databricks\.com/your-email@company.com/g' {} \;

echo "✅ Credentials sanitized!"
```

### Step 2: Verify No Credentials Remain

```bash
# Check for any remaining credentials
echo "Checking for PAT tokens..."
grep -r "dapi[0-9a-f]\{32\}" --include="*.py" --include="*.md" --include="*.sh" \
  --exclude-dir=archive --exclude-dir=.venv --exclude-dir=env .

echo "Checking for your workspace..."
grep -r "e2-demo-west" --include="*.py" --include="*.md" --include="*.sh" \
  --exclude-dir=archive --exclude-dir=.venv --exclude-dir=env .

echo "Checking for your email..."
grep -r "cliff\.yang@" --include="*.py" --include="*.md" --include="*.sh" \
  --exclude-dir=archive --exclude-dir=.venv --exclude-dir=env .

echo "✅ If no results above, you're safe to share!"
```

### Step 3: Create Environment Template

Create `.env.example` file:

```bash
cat > .env.example << 'EOF'
# Databricks Configuration
# Copy this file to .env and fill in your actual values

# Required: Your Databricks workspace URL
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com

# Required: Your Databricks Personal Access Token
# Get from: Workspace -> User Settings -> Access Tokens
DATABRICKS_TOKEN=dapi1234567890abcdef1234567890abcdef

# Optional: For M2M OAuth (service principal)
DATABRICKS_CLIENT_ID=your-service-principal-app-id
DATABRICKS_CLIENT_SECRET=your-oauth-secret

# Optional: Deployment configuration
DATABRICKS_WAREHOUSE_ID=your-warehouse-id
DATABRICKS_CLUSTER_ID=your-cluster-id
EOF

echo "✅ Created .env.example"
```

### Step 4: Update .gitignore (Already Done ✅)

Your `.gitignore` already protects:
```
✅ .env
✅ .env.local
✅ .databricks_oauth_token
✅ *.log
```

### Step 5: Choose Sharing Method

---

## 📤 Sharing Methods

### Method 1: GitHub (Recommended) ⭐

#### A. Create GitHub Repository

```bash
cd /Users/cliff.yang/CursorProj/databricks_cli_mcp

# Initialize git (if not already done)
git init

# Add all files (credentials excluded by .gitignore)
git add .

# Commit
git commit -m "Initial commit: Databricks MCP Server"

# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR-USERNAME/databricks-mcp-server.git
git branch -M main
git push -u origin main
```

#### B. Make Repository Public or Private?

**Public Repository** (Open Source):
- ✅ Anyone can see and use your code
- ✅ Great for community contributions
- ✅ Showcases your work
- ⚠️ Must ensure NO credentials!

**Private Repository**:
- ✅ Only invited collaborators can see
- ✅ More control over who uses it
- ✅ Safer for company-specific modifications
- ⚠️ Still shouldn't have credentials!

#### C. Add Installation Instructions

Update your `README.md` with:

```markdown
## Setup for New Users

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/databricks-mcp-server.git
   cd databricks-mcp-server
   ```

2. **Set up credentials**
   ```bash
   cp .env.example .env
   # Edit .env with your Databricks workspace URL and PAT
   ```

3. **Install dependencies**
   ```bash
   uv sync
   # or: pip install -r requirements.txt
   ```

4. **Run the MCP server**
   ```bash
   ./start_local_mcp.sh
   ```

5. **Configure Cursor**
   See README.md for Cursor MCP configuration
```

---

### Method 2: Direct Zip File

If you don't want to use GitHub:

```bash
cd /Users/cliff.yang/CursorProj

# Create a clean archive (excludes sensitive files)
zip -r databricks-mcp-server.zip databricks_cli_mcp \
  -x "*.pyc" \
  -x "*__pycache__*" \
  -x "*.log" \
  -x "*/.venv/*" \
  -x "*/env/*" \
  -x "*/.env" \
  -x "*/.env.local" \
  -x "*/.databricks_oauth_token" \
  -x "*/archive/*" \
  -x "*/.git/*"

echo "✅ Created databricks-mcp-server.zip"
echo "You can share this file via email, Slack, Google Drive, etc."
```

---

### Method 3: Internal Git Server

If your company has GitLab, Bitbucket, or internal Git:

```bash
# Same as GitHub method, but use your internal Git URL
git remote add origin https://your-git-server.com/your-team/databricks-mcp-server.git
git push -u origin main
```

---

## 🔐 Security Best Practices

### What to NEVER Share

❌ **Personal Access Tokens** (PAT)
   - Starts with `dapi...`
   - Gives full access to your Databricks workspace
   - If exposed, revoke immediately!

❌ **OAuth Client Secrets**
   - Used for M2M authentication
   - Compromises service principal access

❌ **Your Workspace URL** (in final share)
   - Use placeholder: `your-workspace.cloud.databricks.com`

❌ **Your Email** (in examples)
   - Use placeholder: `your-email@company.com`

❌ **Log Files**
   - May contain credentials or sensitive data
   - Already in `.gitignore` ✅

### What's Safe to Share

✅ **All Python Code** (`*.py`)
   - No credentials hardcoded
   - Uses environment variables

✅ **Documentation** (`*.md`)
   - After replacing your credentials with placeholders

✅ **Configuration Templates** (`.env.example`, `app.yaml`)
   - No actual credentials

✅ **Shell Scripts** (`*.sh`)
   - After sanitizing credentials

✅ **Requirements Files** (`pyproject.toml`, `requirements.txt`)
   - Just dependency lists

---

## 📋 Pre-Share Checklist

Before sharing your code, verify:

- [ ] Ran credential sanitization script
- [ ] Verified no credentials remain (grep check)
- [ ] Created `.env.example` template
- [ ] Updated `README.md` with setup instructions
- [ ] `.gitignore` includes sensitive files
- [ ] No `.env` file in repository
- [ ] No log files in repository
- [ ] Tested that others can follow setup instructions

---

## 🚨 If You Accidentally Expose Credentials

### 1. Revoke the Token Immediately

```
Databricks Workspace → User Settings → Access Tokens → Revoke
```

### 2. If on GitHub, Remove from History

```bash
# Remove sensitive file from Git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (WARNING: Rewrites history!)
git push origin --force --all
```

### 3. Create New Token

Create a new PAT with appropriate permissions.

### 4. Rotate OAuth Secrets

If OAuth secrets were exposed, rotate them in the service principal settings.

---

## 💡 Recommended Sharing Approach

### For Open Source / Public Sharing:

1. ✅ Use GitHub with **public repository**
2. ✅ Sanitize all credentials (use script above)
3. ✅ Provide `.env.example`
4. ✅ Write clear setup instructions
5. ✅ Add LICENSE file (MIT, Apache 2.0, etc.)

### For Team / Internal Sharing:

1. ✅ Use internal Git or **private GitHub repo**
2. ✅ Still sanitize credentials (best practice!)
3. ✅ Each user sets up their own credentials
4. ✅ Document company-specific setup

### For Quick Sharing / Demo:

1. ✅ Create zip file (use script above)
2. ✅ Share via secure channel (not public)
3. ✅ Include setup instructions
4. ✅ Verify no credentials in archive

---

## 📖 Additional Files to Include

### LICENSE (if open source)

Choose a license:
- **MIT**: Most permissive, allows commercial use
- **Apache 2.0**: Similar to MIT, explicit patent grant
- **GPL-3.0**: Requires derivative works to be open source

```bash
# Add MIT License
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

### CONTRIBUTING.md

```markdown
# Contributing

## Setup Development Environment

1. Fork the repository
2. Clone your fork
3. Set up credentials in `.env`
4. Install dependencies: `uv sync`
5. Make your changes
6. Test locally
7. Submit a pull request

## Code Style

- Use Python 3.11+
- Follow PEP 8
- Add type hints
- Write docstrings for public functions
```

---

## 🎉 Summary

### Quick Steps to Share Safely:

1. **Sanitize credentials** (run the sed commands above)
2. **Verify no credentials remain** (run grep checks)
3. **Create `.env.example`** (template for others)
4. **Choose sharing method**:
   - GitHub (recommended)
   - Zip file
   - Internal Git
5. **Test that others can set up** (have someone follow your README)

### Remember:

✅ **Code = safe to share** (after sanitization)  
✅ **Templates = safe to share**  
❌ **Credentials = NEVER share**  
❌ **Your .env file = NEVER share**

**Your code is valuable! Share it safely.** 🔒

