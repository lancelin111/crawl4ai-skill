#!/bin/bash
# Crawl4AI Skill - One-click Installation Script
# Usage: curl -fsSL https://raw.githubusercontent.com/lancelin111/crawl4ai-skill/main/install.sh | bash

set -e

echo "========================================"
echo "  Crawl4AI Skill - One-Click Install"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 9 ]; then
            echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION detected"
            return 0
        fi
    fi
    echo -e "${RED}✗${NC} Python 3.9+ is required"
    exit 1
}

# Install the package
install_package() {
    echo ""
    echo "Installing crawl4ai-skill..."

    # If in the project directory, install locally
    if [ -f "pyproject.toml" ]; then
        echo "  Installing from local source..."
        pip install -e . --quiet
    else
        # Install from GitHub
        echo "  Installing from GitHub..."
        pip install git+https://github.com/lancelin111/crawl4ai-skill.git --quiet
    fi

    echo -e "${GREEN}✓${NC} Package installed"
}

# Install Playwright browser
install_browser() {
    echo ""
    echo "Installing Chromium browser for Playwright..."
    python3 -m playwright install chromium --quiet 2>/dev/null || python3 -m playwright install chromium
    echo -e "${GREEN}✓${NC} Browser installed"
}

# Setup crawl4ai
setup_crawl4ai() {
    echo ""
    echo "Setting up crawl4ai..."
    # crawl4ai-setup may not exist, so we check first
    if command -v crawl4ai-setup &> /dev/null; then
        crawl4ai-setup 2>/dev/null || true
    fi
    echo -e "${GREEN}✓${NC} crawl4ai ready"
}

# Verify installation
verify_install() {
    echo ""
    echo "Verifying installation..."
    if crawl4ai-skill --version &> /dev/null; then
        VERSION=$(crawl4ai-skill --version 2>&1 | tail -1)
        echo -e "${GREEN}✓${NC} crawl4ai-skill $VERSION"
    else
        echo -e "${YELLOW}!${NC} CLI command not in PATH, try: python -m src.cli --help"
    fi
}

# Main
main() {
    check_python
    install_package
    install_browser
    setup_crawl4ai
    verify_install

    echo ""
    echo "========================================"
    echo -e "${GREEN}Installation complete!${NC}"
    echo "========================================"
    echo ""
    echo "Quick start:"
    echo "  crawl4ai-skill search \"python tutorials\""
    echo "  crawl4ai-skill crawl https://example.com"
    echo ""
    echo "For login features:"
    echo "  crawl4ai-skill login twitter --cookies \"auth_token=xxx\""
    echo "  crawl4ai-skill crawl-with-login https://x.com/user -p twitter"
    echo ""
}

main "$@"
