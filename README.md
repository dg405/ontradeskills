# OnTradeSkills

Claude Code plugin for on-trade spirits sales teams. Operates a structured Obsidian vault in your current working directory (override with `$ONTRADE_VAULT`) covering brands, products, venues, groups, distributors, and contracts. 

This plugin is supposed to be personalised by you, it's not designed to accommodate everyone's workflows out-the-box. Please personalise it to your needs by asking Claude to make changes to the skills and vault. 

## Install

```bash
~/.claude/skills/ontradeskills/setup.sh
```

Symlinks each skill into `~/.claude/skills/` so the slash commands are picked up by Claude Code globally.


## How to use it

Step 1: Install the skills (quit and restart Claude Desktop to see the new skills)
Step 2: Create a new working directory folder on your laptop
Step 3: Open the new working directory folder in a new Claude Code session
Step 4: Run the /init-ontrade skill to initialise the vault in your working directory
Step 5: Start running the skills to add content and build the knowledge base

## Recommendations

- Instead of updating anything in Obsidian manually, always ask Claude to add/link/edit pages. It keeps the content more structured and consistent. 
- Ask Claude to add and update the skill files/templates/pages if it's not working exactly how you want it to. Claude is very good at making precise edits which will make your skills more personalised (e.g. change the way Claude analyses contracts or cocktail menus). A good example of this is that when I wanted long/lat coords on every location I just told Claude to update the skills/templates and existing pages and it did all of it successfully in seconds. 

## Commands

| Command | What it does |
|---------|--------------|
| `/init-ontrade` | Bootstrap the vault: folders, templates, dashboards, git init. Idempotent. |
| `/discover <ICP or area>` | Find new venues matching an ICP, write stubs into `Venues/` and rank in `Dashboards/Discoveries.md`. |
| `/analysemenu <venue-or-url>` | Fetch + analyse a venue's drinks menu (4-tier reliability ladder), append a dated analysis block to the venue note, and rank placement opportunities for your portfolio. Auto-creates a venue stub if given a URL. |
| `/uploadcontract [path-or-attachment]` | Save a contract PDF/docx into `Contracts/raw/`, extract YAML fields via LLM, create the contract note, and backlink venue/distributor/products. |
| `/analysecontract <contract>` | Re-read a contract note + raw file, append a dated risk/review block. |

## Vault layout

```
<your-folder>/
  Brands/<Brand Name>/<brand>.md, <product>.md ...
  Venues/<Venue>.md
  Groups/<Group>.md
  Distributors/<Distributor>.md
  Contracts/<contract>.md
  Contracts/raw/<original-files>
  Templates/, Dashboards/, Attachments/
```

Create a new folder, open Claude Code inside it, then run `/init-ontrade`.

## Requirements

- Obsidian (with the [Dataview](https://blacksmithgu.github.io/obsidian-dataview/) community plugin installed for dashboards and the [Map View](obsidian://show-plugin?id=obsidian-map-view) plugin to view venues on a map).
- **Recommended but not required:** `pdftotext` (`brew install poppler`) and `pandoc` (`brew install pandoc`) for contract extraction. The `/init-ontrade` skill will check.
- Headless Chrome via the bundled `mcp__Claude_in_Chrome` MCP for tier-3 menu fetching (already available in your Claude Code).
