#!/usr/bin/env bash
set -e

# OnTradeSkills one-shot installer.
# Run with:
#   curl -fsSL https://raw.githubusercontent.com/dg405/ontradeskills/main/install.sh | bash

REPO_URL="https://github.com/dg405/ontradeskills.git"
INSTALL_DIR="$HOME/.claude/skills/ontradeskills"

say() { printf "%s\n" "$1"; }
warn() { printf "WARNING: %s\n" "$1" >&2; }
fail() { printf "ERROR: %s\n" "$1" >&2; exit 1; }

say ""
say "OnTradeSkills installer"
say "======================="
say ""

# 1. git is required.
if ! command -v git >/dev/null 2>&1; then
    fail "git is not installed. On macOS, install Homebrew from https://brew.sh and then run: brew install git"
fi

# 2. Claude Code is highly recommended.
if ! command -v claude >/dev/null 2>&1; then
    warn "The 'claude' command was not found on your PATH."
    warn "If you have not installed Claude Code yet, get it here: https://claude.com/claude-code"
    warn "Claude Code is included with the Claude Pro subscription (£15 +VAT per month)."
    say ""
fi

# 3. Clone or update the repo.
if [ -d "$INSTALL_DIR/.git" ]; then
    say "Updating existing install at $INSTALL_DIR"
    git -C "$INSTALL_DIR" pull --ff-only --quiet
else
    say "Downloading OnTradeSkills into $INSTALL_DIR"
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone --quiet "$REPO_URL" "$INSTALL_DIR"
fi

# 4. Run the symlink setup.
say ""
bash "$INSTALL_DIR/setup.sh"

# 5. Friendly next steps.
say ""
say "All set. Next steps:"
say ""
say "  1. Quit and restart Claude Code so it picks up the new skills."
say "  2. Make a folder anywhere on your laptop, for example:"
say "       mkdir ~/Documents/MyOnTradeVault"
say "  3. Open that folder in Claude Code."
say "  4. Type /init-ontrade and press enter."
say ""
say "After /init-ontrade finishes, open the same folder in Obsidian and follow"
say "the on-screen checklist to install the Dataview and Map View plugins."
say ""
