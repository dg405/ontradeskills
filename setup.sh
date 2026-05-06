#!/usr/bin/env bash
set -e

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
GLOBAL_SKILLS_DIR="$HOME/.claude/skills"

echo "Setting up OnTradeSkills..."
mkdir -p "$GLOBAL_SKILLS_DIR"

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
done

echo ""
echo "Done. Run /init-ontrade in Claude Code to bootstrap the vault."
