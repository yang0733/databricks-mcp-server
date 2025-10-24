#!/bin/bash

# Sanitize Credentials Script
# This script replaces your real credentials with placeholder values
# Run this BEFORE sharing your code!

set -e

echo "🔒 Sanitizing Credentials from Code..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}❌ Error: Must run from databricks_cli_mcp directory${NC}"
    exit 1
fi

# Backup files before sanitization
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
echo -e "${YELLOW}📦 Creating backup in: ${BACKUP_DIR}${NC}"
mkdir -p "$BACKUP_DIR"
cp -r . "$BACKUP_DIR/" 2>/dev/null || true
echo ""

# Function to sanitize files
sanitize() {
    local pattern=$1
    local replacement=$2
    local description=$3
    
    echo -e "${YELLOW}🔍 Sanitizing: ${description}${NC}"
    
    find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.sh" -o -name "*.yaml" -o -name "*.yml" \) \
        -not -path "./backup_*/*" \
        -not -path "./archive/*" \
        -not -path "./.venv/*" \
        -not -path "./venv/*" \
        -not -path "./env/*" \
        -not -path "./.git/*" \
        -exec sed -i '' "s/${pattern}/${replacement}/g" {} \;
    
    echo -e "${GREEN}✅ Done${NC}"
    echo ""
}

# Sanitize PAT tokens
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sanitize "dapi1234567890abcdef1234567890abcdef[a-f0-9]*" "dapi1234567890abcdef1234567890abcdef" "PAT tokens"

# Sanitize workspace URL
sanitize "e2-demo-west\.cloud\.databricks\.com" "your-workspace.cloud.databricks.com" "Workspace URL"

# Sanitize email addresses
sanitize "cliff\.yang@databricks\.com" "your-email@company.com" "Email addresses"

# Sanitize any other potential secrets
sanitize "your-llm-endpoint" "your-llm-endpoint" "LLM endpoint names"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verify no credentials remain
echo -e "${YELLOW}🔍 Verifying no credentials remain...${NC}"
echo ""

FOUND_ISSUES=0

# Check for PAT tokens
echo "Checking for PAT tokens..."
if grep -r "dapi1234567890abcdef1234567890abcdef" --include="*.py" --include="*.md" --include="*.sh" \
    --exclude-dir=backup_* --exclude-dir=archive --exclude-dir=.venv --exclude-dir=env --exclude-dir=.git . 2>/dev/null; then
    echo -e "${RED}❌ Found real PAT tokens!${NC}"
    FOUND_ISSUES=1
else
    echo -e "${GREEN}✅ No PAT tokens found${NC}"
fi
echo ""

# Check for workspace URL
echo "Checking for workspace URL..."
if grep -r "e2-demo-west" --include="*.py" --include="*.md" --include="*.sh" \
    --exclude-dir=backup_* --exclude-dir=archive --exclude-dir=.venv --exclude-dir=env --exclude-dir=.git . 2>/dev/null; then
    echo -e "${RED}❌ Found real workspace URL!${NC}"
    FOUND_ISSUES=1
else
    echo -e "${GREEN}✅ No workspace URL found${NC}"
fi
echo ""

# Check for email
echo "Checking for email addresses..."
if grep -r "cliff\.yang@" --include="*.py" --include="*.md" --include="*.sh" \
    --exclude-dir=backup_* --exclude-dir=archive --exclude-dir=.venv --exclude-dir=env --exclude-dir=.git . 2>/dev/null; then
    echo -e "${RED}❌ Found real email addresses!${NC}"
    FOUND_ISSUES=1
else
    echo -e "${GREEN}✅ No email addresses found${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $FOUND_ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ All credentials successfully sanitized!${NC}"
    echo ""
    echo "Your code is now safe to share! 🎉"
    echo ""
    echo "Next steps:"
    echo "  1. Review the changes: git diff"
    echo "  2. Commit the sanitized version: git add . && git commit -m 'Sanitize credentials'"
    echo "  3. Push to GitHub or share as zip"
    echo ""
    echo "Backup saved in: ${BACKUP_DIR}"
else
    echo -e "${RED}❌ Some credentials may still remain!${NC}"
    echo ""
    echo "Please review the files above and manually remove any sensitive data."
    echo ""
    echo "If you need to restore the backup:"
    echo "  rm -rf ./*"
    echo "  cp -r ${BACKUP_DIR}/* ."
    exit 1
fi

