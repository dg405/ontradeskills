---
name: discover
description: Discover new on-trade venues matching an ICP or area. Searches the web for bars, restaurants, and hotels that match the user's target profile, deduplicates against existing Venues/, writes stub venue notes with frontmatter (address, group, socials), and ranks them in Dashboards/Discoveries.md. Use when the user says "/discover", "find new venues", "find bars in Shoreditch", or wants to expand their venue book.
argument-hint: <ICP or area, e.g. "premium cocktail bars in Shoreditch">
allowed-tools: [Bash, Read, Write, Glob, Grep, WebSearch, WebFetch, AskUserQuestion]
---

# /discover

Find new venues matching the user's ICP and seed stub notes in the vault.

## Inputs

The user's argument: $ARGUMENTS

If empty, ask via AskUserQuestion: "What ICP or area should I discover venues for?" with sample options: "Premium cocktail bars in Shoreditch", "5★ hotel bars in central London", "Independent neighbourhood bars in Bristol".

## Steps

1. **Resolve vault root** via `python3 ~/.claude/skills/ontradeskills/skills/_lib/vault.py vault`.

2. **List existing venues** so we don't duplicate:
   ```bash
   ls "$VAULT/Venues/" 2>/dev/null
   ```
   Treat slugified comparisons as authoritative: `python3 ~/.claude/skills/ontradeskills/skills/_lib/vault.py slug "<name>"`.

3. **Research.** Use WebSearch with 2–4 targeted queries covering:
   - "best <ICP> in <area>" listicles
   - Industry award lists (World's 50 Best Bars, Class Awards, Time Out, Eater)
   - Local press / city guides
   - Group websites (e.g. for hotel groups, list their property bars)

   Use WebFetch on the most useful 2–3 results to extract structured venue info.

4. **For each candidate venue** gather (best effort):
   - Name (canonical, no honorifics)
   - Address, city, postcode
   - GPS coordinates as a string `"lat, lng"` — derive from the address using your training knowledge, or from any map link found on the venue's page. If genuinely uncertain, leave `location: ""` rather than guessing.
   - Website + Instagram handle if findable
   - Parent group (if the venue is part of one)
   - 1-line "why it fits" the ICP

   Skip anything you can't even pin a name + city to.

5. **Deduplicate** against existing `Venues/*.md` using slug comparison. Skip duplicates silently.

6. **Write a stub note per new venue** at `$VAULT/Venues/<Title Case Name>.md`. Use the venue template at `$VAULT/Templates/venue.md` as the structure. Frontmatter to fill:
   - `type: venue`
   - `address`, `city`, `postcode`, `country`
   - `location: "lat, lng"` if coordinates were found; leave `location: ""` otherwise
   - `group: [[<Group Name>]]` if known (do **not** create the Group note — leave it as a dangling link with a `# TODO group note` line in the body)
   - `website`, `instagram`
   - `tags: [discovered]`
   - leave `distributors`, `listed_products`, `pipeline_products`, `contracts` as empty lists
   Body: short "## Overview" paragraph with the "why it fits" line and the ICP query as context.

7. **Append to `$VAULT/Dashboards/Discoveries.md`** under a new dated heading `## <YYYY-MM-DD> — <ICP>` listing the new venues as wikilinks, ranked best-fit first with a one-line justification each. Don't replace earlier sections.

8. **Report** back to the user: count of new stubs created, count of duplicates skipped, and any venues where info was too thin to stub (with reasons).

## Rules

- Never auto-create Group or Distributor notes. Stubs only.
- Never invent an address/postcode you didn't see in a source.
- Mark every stub `tags: [discovered]` so the Discoveries dashboard can filter.
- Default to UK/Europe spirits-trade conventions unless the area implies otherwise.
