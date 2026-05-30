#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📦 Installing git-copilot...${NC}"

# Detect platform
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case "$ARCH" in
    x86_64|amd64) ARCH="x86_64" ;;
    aarch64|arm64) ARCH="aarch64" ;;
    *) echo -e "${YELLOW}⚠️  Unsupported architecture: $ARCH, falling back to pip...${NC}" ;;
esac

# Check if Python is available
if command -v python3 &>/dev/null; then
    # Install via pip from GitHub
    echo -e "${BLUE}🔧 Installing from GitHub source via pip...${NC}"
    
    # Create temp dir
    TMPDIR=$(mktemp -d)
    cd "$TMPDIR"
    
    # Download the repo
    curl -sL "https://github.com/zhirenhun-stack/git-copilot/archive/main.tar.gz" | tar xz --strip=1 2>/dev/null || {
        # Fallback: git clone
        git clone --depth 1 "https://github.com/zhirenhun-stack/git-copilot.git" "$TMPDIR/repo" 2>/dev/null
        cd "$TMPDIR/repo"
    }
    
    pip3 install -e . 2>/dev/null || pip3 install --user -e .
    
    cd /tmp
    rm -rf "$TMPDIR"
    
    echo -e "${GREEN}✅ git-copilot installed!${NC}"
    echo ""
    echo -e "Try it:  ${BLUE}git add . && git-copilot gen${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Python 3 not found. Please install Python 3.8+ first.${NC}"
    echo "  https://www.python.org/downloads/"
    exit 1
fi
