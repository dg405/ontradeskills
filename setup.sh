#!/usr/bin/env bash
set -e

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
GLOBAL_SKILLS_DIR="$HOME/.claude/skills"

echo "Linking OnTradeSkills into $GLOBAL_SKILLS_DIR"
mkdir -p "$GLOBAL_SKILLS_DIR"

linked=0
for skill_dir in "$INSTALL_DIR"/skills/*; do
    [ -d "$skill_dir" ] || continue
    skill_name="$(basename "$skill_dir")"
    # skip private helper directories (e.g. _lib)
    case "$skill_name" in _*) continue ;; esac

    target="$GLOBAL_SKILLS_DIR/$skill_name"
    if [ -L "$target" ] || [ -d "$target" ]; then
        rm -rf "$target"
    fi
    ln -snf "$skill_dir" "$target"
    echo "  Linked /$skill_name"
    linked=$((linked + 1))
done

echo ""
echo "Linked $linked skills."

# Friendly heads-up if Obsidian is missing on macOS.
if [ "$(uname)" = "Darwin" ] && [ ! -d "/Applications/Obsidian.app" ]; then
    echo ""
    echo "Heads up: Obsidian does not appear to be installed."
    echo "Download it (free) from https://obsidian.md before running /init-ontrade."
fi
