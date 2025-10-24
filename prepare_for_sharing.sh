#!/bin/bash

# Prepare Code for Sharing
# This script creates a CLEAN COPY of your code for sharing
# Your original working code remains UNCHANGED!

set -e

echo "🎯 Preparing Clean Code for Sharing..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}❌ Error: Must run from databricks_cli_mcp directory${NC}"
    exit 1
fi

# Create clean directory for sharing
SHARE_DIR="../databricks_cli_mcp_SHARE"
echo -e "${BLUE}📦 Creating clean copy for sharing...${NC}"

# Remove old share directory if exists
if [ -d "$SHARE_DIR" ]; then
    echo -e "${YELLOW}⚠️  Removing old share directory...${NC}"
    rm -rf "$SHARE_DIR"
fi

# Copy everything to share directory
echo -e "${BLUE}📋 Copying files...${NC}"
cp -r . "$SHARE_DIR"
cd "$SHARE_DIR"

echo -e "${GREEN}✅ Copy created at: $SHARE_DIR${NC}"
echo ""

# Function to sanitize files
sanitize() {
    local pattern=$1
    local replacement=$2
    local description=$3
    
    echo -e "${YELLOW}🔍 Sanitizing: ${description}${NC}"
    
    find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.sh" -o -name "*.yaml" -o -name "*.yml" \) \
        -not -path "./archive/*" \
        -not -path "./.venv/*" \
        -not -path "./venv/*" \
        -not -path "./env/*" \
        -not -path "./.git/*" \
        -exec sed -i '' "s/${pattern}/${replacement}/g" {} \;
    
    echo -e "${GREEN}✅ Done${NC}"
    echo ""
}

# Sanitize the COPY (not your original!)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}🧹 Cleaning credentials from the COPY...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Sanitize PAT tokens
sanitize "dapi1234567890abcdef1234567890abcdef[a-f0-9]*" "dapi1234567890abcdef1234567890abcdef" "PAT tokens"

# Sanitize workspace URL
sanitize "e2-demo-west\\.cloud\\.databricks\\.com" "your-workspace.cloud.databricks.com" "Workspace URL"

# Sanitize email addresses
sanitize "cliff\\.yang@databricks\\.com" "your-email@company.com" "Email addresses"

# Sanitize any other potential secrets
sanitize "your-llm-endpoint" "your-llm-endpoint" "LLM endpoint names"

# Remove sensitive files
echo -e "${YELLOW}🗑️  Removing sensitive files from copy...${NC}"
rm -f .env .env.local .databricks_oauth_token *.log 2>/dev/null || true
rm -rf archive/ backup_* 2>/dev/null || true
echo -e "${GREEN}✅ Done${NC}"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verify no credentials remain
echo -e "${YELLOW}🔍 Verifying no credentials remain in copy...${NC}"
echo ""

FOUND_ISSUES=0

# Check for PAT tokens
echo "Checking for PAT tokens..."
if grep -r "dapi1234567890abcdef1234567890abcdef" --include="*.py" --include="*.md" --include="*.sh" \
    --exclude-dir=.venv --exclude-dir=env --exclude-dir=.git . 2>/dev/null; then
    echo -e "${RED}❌ Found real PAT tokens!${NC}"
    FOUND_ISSUES=1
else
    echo -e "${GREEN}✅ No PAT tokens found${NC}"
fi
echo ""

# Check for workspace URL
echo "Checking for workspace URL..."
if grep -r "e2-demo-west" --include="*.py" --include="*.md" --include="*.sh" \
    --exclude-dir=.venv --exclude-dir=env --exclude-dir=.git . 2>/dev/null; then
    echo -e "${RED}❌ Found real workspace URL!${NC}"
    FOUND_ISSUES=1
else
    echo -e "${GREEN}✅ No workspace URL found${NC}"
fi
echo ""

# Check for email
echo "Checking for email addresses..."
if grep -r "cliff\\.yang@" --include="*.py" --include="*.md" --include="*.sh" \
    --exclude-dir=.venv --exclude-dir=env --exclude-dir=.git . 2>/dev/null; then
    echo -e "${RED}❌ Found real email addresses!${NC}"
    FOUND_ISSUES=1
else
    echo -e "${GREEN}✅ No email addresses found${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $FOUND_ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ Clean copy ready for sharing!${NC}"
    echo ""
    echo -e "${BLUE}📍 Location: $SHARE_DIR${NC}"
    echo ""
    echo -e "${GREEN}✅ Your original code is UNTOUCHED!${NC}"
    echo -e "${GREEN}   Continue using: $(pwd | sed 's/_SHARE$//')${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Next steps:"
    echo ""
    echo "Option A: Share via GitHub"
    echo "  cd $SHARE_DIR"
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Databricks MCP Server'"
    echo "  git remote add origin https://github.com/YOUR-USERNAME/databricks-mcp-server.git"
    echo "  git push -u origin main"
    echo ""
    echo "Option B: Share via Zip"
    echo "  cd $(dirname "$SHARE_DIR")"
    echo "  zip -r databricks-mcp-server.zip $(basename "$SHARE_DIR") \\"
    echo "    -x '*.pyc' '*__pycache__*' '*.log' '*/.venv/*' '*/env/*'"
    echo ""
    echo "After sharing, you can delete the copy:"
    echo "  rm -rf $SHARE_DIR"
    echo ""
else
    echo -e "${RED}❌ Some credentials may still remain!${NC}"
    echo ""
    echo "Please review the files above and manually remove any sensitive data."
    echo ""
    echo "The clean copy is at: $SHARE_DIR"
    echo "You can delete it and try again: rm -rf $SHARE_DIR"
    exit 1
fi

