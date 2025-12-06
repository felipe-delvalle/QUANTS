#!/bin/bash

# ============================================================
# Secure API Key Setup for Continue.dev
# ============================================================
# Helps you add API keys to Continue config securely
# ============================================================

CONFIG_FILE="/Users/freedom/QUANTS/.continue/config.json"
BACKUP_FILE="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Continue.dev API Key Setup                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Backup config
if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    echo -e "${GREEN}✓${NC} Backup created: ${BACKUP_FILE}"
fi

echo -e "${YELLOW}📋 Available Models:${NC}"
echo "1. GPT-5.1-Codex-Max (OpenAI)"
echo "2. Claude Haiku (Anthropic)"
echo "3. Claude Sonnet 4 (Anthropic)"
echo "4. GPT-4 (OpenAI)"
echo ""
echo -e "${YELLOW}⚠️  Security Note:${NC} Keys will be stored in config.json"
echo -e "${YELLOW}⚠️  Make sure config.json is in .gitignore!${NC}"
echo ""

read -p "Which model's API key do you want to add? (1-4, or 'all'): " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}OpenAI API Key Setup${NC}"
        echo "Get your key from: https://platform.openai.com/api-keys"
        echo ""
        read -sp "Enter your OpenAI API key (sk-...): " api_key
        echo ""
        
        # Use Python to update JSON (more reliable than sed)
        python3 << EOF
import json
import sys

with open("$CONFIG_FILE", "r") as f:
    config = json.load(f)

for model in config.get("models", []):
    if model.get("title") == "GPT-5.1-Codex-Max":
        model["apiKey"] = "$api_key"
        break

with open("$CONFIG_FILE", "w") as f:
    json.dump(config, f, indent=2)

print("✓ API key added for GPT-5.1-Codex-Max")
EOF
        ;;
    2)
        echo ""
        echo -e "${BLUE}Anthropic API Key Setup (Claude Haiku)${NC}"
        echo "Get your key from: https://console.anthropic.com/settings/keys"
        echo ""
        read -sp "Enter your Anthropic API key (sk-ant-...): " api_key
        echo ""
        
        python3 << EOF
import json

with open("$CONFIG_FILE", "r") as f:
    config = json.load(f)

for model in config.get("models", []):
    if model.get("title") == "Claude Haiku":
        model["apiKey"] = "$api_key"
        break

with open("$CONFIG_FILE", "w") as f:
    json.dump(config, f, indent=2)

print("✓ API key added for Claude Haiku")
EOF
        ;;
    3)
        echo ""
        echo -e "${BLUE}Anthropic API Key Setup (Claude Sonnet 4)${NC}"
        echo "Get your key from: https://console.anthropic.com/settings/keys"
        echo ""
        read -sp "Enter your Anthropic API key (sk-ant-...): " api_key
        echo ""
        
        python3 << EOF
import json

with open("$CONFIG_FILE", "r") as f:
    config = json.load(f)

for model in config.get("models", []):
    if model.get("title") == "Claude Sonnet 4":
        model["apiKey"] = "$api_key"
        break

with open("$CONFIG_FILE", "w") as f:
    json.dump(config, f, indent=2)

print("✓ API key added for Claude Sonnet 4")
EOF
        ;;
    4)
        echo ""
        echo -e "${BLUE}OpenAI API Key Setup (GPT-4)${NC}"
        echo "Get your key from: https://platform.openai.com/api-keys"
        echo ""
        read -sp "Enter your OpenAI API key (sk-...): " api_key
        echo ""
        
        python3 << EOF
import json

with open("$CONFIG_FILE", "r") as f:
    config = json.load(f)

for model in config.get("models", []):
    if model.get("title") == "GPT-4":
        model["apiKey"] = "$api_key"
        break

with open("$CONFIG_FILE", "w") as f:
    json.dump(config, f, indent=2)

print("✓ API key added for GPT-4")
EOF
        ;;
    all)
        echo ""
        echo -e "${BLUE}Setting up all models${NC}"
        echo ""
        
        read -sp "Enter your OpenAI API key (for Codex 5 and GPT-4): " openai_key
        echo ""
        read -sp "Enter your Anthropic API key (for Claude models): " anthropic_key
        echo ""
        
        python3 << EOF
import json

with open("$CONFIG_FILE", "r") as f:
    config = json.load(f)

for model in config.get("models", []):
    provider = model.get("provider", "")
    if provider == "openai":
        model["apiKey"] = "$openai_key"
    elif provider == "anthropic":
        model["apiKey"] = "$anthropic_key"

with open("$CONFIG_FILE", "w") as f:
    json.dump(config, f, indent=2)

print("✓ API keys added for all models")
EOF
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✓${NC} Configuration updated!"
echo ""
    echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Reload VS Code/Cursor or restart Continue extension"
echo "2. Open Continue chat (Cmd+Shift+L)"
echo "3. Select a model from the dropdown"
echo "4. Test with: 'What model are you?'"
echo ""
echo -e "${CYAN}💡 Tip:${NC} Check CONTINUE_SETUP_GUIDE.md for more details"
