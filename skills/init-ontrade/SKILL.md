---
name: init-ontrade
description: Bootstrap the on-trade Obsidian vault in the current working directory (or $ONTRADE_VAULT). Creates the folder tree (Brands, Venues, Groups, Distributors, Contracts/raw, Templates, Dashboards, Attachments), copies template and dashboard notes, initialises git, and checks that pdftotext / pandoc are available. Idempotent, safe to re-run. Use when the user says "init ontrade", "/init-ontrade", "set up the on-trade vault", or it's the first run of this plugin.
argument-hint: ""
allowed-tools: [Bash, Read, Write]
---

# /init-ontrade

Bootstraps the on-trade vault. Idempotent, re-running fixes missing folders/templates without overwriting user content.

## Steps

1. **Resolve the vault root.**
   - Honour `$ONTRADE_VAULT` if set; otherwise use the current working directory.
   - Run: `python3 ~/.claude/skills/ontradeskills/skills/_lib/vault.py vault` and use the printed path.

2. **Create the folder tree.** Run a single `mkdir -p` covering:
   ```
   $VAULT/{Brands,Venues,Groups,Distributors,Contracts/raw,Templates,Dashboards,Attachments,.cache}
   ```

3. **Copy templates and dashboards** from this plugin's `assets/` folder. Source = `~/.claude/skills/ontradeskills/assets/`. Use `cp -n` so existing user-edited files are never clobbered.
   - Templates → `$VAULT/Templates/`
   - Dashboards → `$VAULT/Dashboards/`

4. **Seed `.gitignore`** if missing:
   ```
   .cache/
   .obsidian/workspace*
   ```

5. **Initialise git** if `$VAULT/.git` does not exist:
   ```bash
   git -C "$VAULT" init -q
   git -C "$VAULT" add -A
   git -C "$VAULT" commit -q -m "init: ontrade vault scaffolding" --allow-empty
   ```
   If git is already initialised, skip. Do **not** auto-commit user changes.

6. **Tool check.** Report (don't fail) on the availability of:
   - `pdftotext --version`, needed for tier-2 menu fetching and `/uploadcontract` PDFs.
   - `pandoc --version`, optional, for `.docx` contracts.
   If missing, tell the user the install hint: `brew install poppler pandoc`.

7. **Print a summary** of what was created vs already existed, then print the following Obsidian setup checklist:

   ```
   Obsidian setup checklist
   ========================
   1. Open Obsidian, click "Open folder as vault", and pick this folder.
   2. Install the Dataview plugin (required for dashboards):
      Settings > Community plugins > Browse > search "Dataview" > Install > Enable.
   3. Install the Map View plugin (required to see venues on a map):
      Settings > Community plugins > Browse > search "Map View" > Install > Enable.
      Once enabled, open any venue note. The location field will plot it on the map.
   ```

## Notes

- Never delete or rename user files. The skill only adds.
- The dashboards depend on Obsidian's Dataview plugin.
- Venue map pins depend on Obsidian's Map View plugin. The `location` field on every venue note is a string in `"lat, lng"` format that Map View reads natively.
- The Obsidian setup checklist text printed to the user must not contain em dashes.
