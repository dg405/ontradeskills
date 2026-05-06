---
name: analysemenu
description: Analyse a venue's drinks menu and recommend placement opportunities for the user's portfolio. Accepts either an existing venue note name or a raw menu URL (auto-creates a venue stub if the URL doesn't match an existing venue). Uses a 4-tier reliability ladder — plain HTTP → PDF → headless Chrome → vision OCR — and appends a dated analysis block to the venue note. Use when the user says "/analysemenu", "analyse this menu", or pastes a bar menu URL.
argument-hint: <venue-name | menu-url>
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, AskUserQuestion, mcp__Claude_in_Chrome__tabs_context_mcp, mcp__Claude_in_Chrome__tabs_create_mcp, mcp__Claude_in_Chrome__navigate, mcp__Claude_in_Chrome__get_page_text, mcp__Claude_in_Chrome__computer, mcp__Claude_in_Chrome__find, mcp__Claude_in_Chrome__read_network_requests, mcp__Claude_in_Chrome__javascript_tool, mcp__Claude_in_Chrome__list_connected_browsers, mcp__Claude_in_Chrome__select_browser]
---

# /analysemenu

Reliably extract a venue's cocktail menu, then rank where the user's portfolio fits. Reliability is the priority — escalate through tiers until the menu is actually readable.

## Inputs

User argument: $ARGUMENTS — either a venue title (matches a `Venues/*.md` note) or a URL.

If empty, ask via AskUserQuestion which venue or paste a menu URL.

## Steps

### 1. Resolve venue and menu URL

- `VAULT=$(python3 ~/.claude/skills/ontradeskills/skills/_lib/vault.py vault)`
- If the argument is a URL (starts with `http://` or `https://`):
  1. Use WebFetch on the URL with prompt: "Extract the venue/business name (look at <title>, og:site_name, the h1, or the domain). Return just the name and any address/city you can see."
  2. Slugify the name and run `python3 …/vault.py find-venue "<name>"`. If a venue note matches, use it. Otherwise create a new stub at `$VAULT/Venues/<Title Case Name>.md` from `$VAULT/Templates/venue.md` with `menu_url: <the URL>`, `website` set to the URL's origin, and `tags: [discovered]`. For the `instagram` frontmatter field: only populate it if you are extremely confident the handle belongs to this specific venue. For `location`: populate `"lat, lng"` as a string (e.g. `"51.5130, -0.1319"`) if an address is visible on the fetched page or derivable from the URL — leave `location: ""` otherwise. Tell the user a stub was created.
- Else treat it as a venue title:
  1. `find-venue` to locate the note. If none, ask the user to confirm a name and create a fresh stub or abort.
  2. Read `menu_url` from frontmatter. If missing, fall back to `website`, then ask the user for a URL.

### 2. Tiered fetch (reliability ladder)

Track which tier succeeded into a variable `TIER`. Try in order, stop at first usable result.

**Tier 1 — HTTP / HTML.**
```bash
python3 ~/.claude/skills/ontradeskills/skills/_lib/fetch.py http "$URL" > /tmp/ontrade-menu.out
```
The first line is a JSON header. If `usable: true`, set `TIER=html` and use the body. If header says `escalate: pdf`, jump to tier 2 immediately. If `usable: false`, continue.

**Tier 2 — PDF.**
```bash
python3 …/fetch.py download "$URL" /tmp/ontrade-menu.pdf
python3 …/fetch.py pdf /tmp/ontrade-menu.pdf > /tmp/ontrade-menu.out
```
If `usable: true` → `TIER=pdf`.

**Tier 3 — Headless Chrome + network sniffing.** Use the bundled MCP `mcp__Claude_in_Chrome`:

Browser selection: call `list_connected_browsers`. Pick the first browser in the list and call `select_browser` with its deviceId. Never prompt the user to choose.

1. `tabs_context_mcp` with `createIfEmpty: true` to get a tab.
2. `navigate` to `$URL`.
3. Wait 3s for JS to render, then run both in parallel:
   a. `get_page_text` — check if text is menu-shaped (> 500 chars with drink hints).
   b. `read_network_requests` — scan all XHR/fetch calls made during page load. Look for responses with JSON payloads that contain arrays of items with fields like `name`, `price`, `description`, `ingredients`, or `category`. If found, parse that JSON directly — this is faster and more complete than any visual approach.
4. If either (a) or (b) yields usable menu data → `TIER=browser`. Prefer (b) if both work.
5. If both are thin (< 500 chars, no drink hints), continue to Tier 4.

**Tier 4 — Vision.** Last resort:
1. With the same browser tab, scroll to the top, then take screenshots in passes (scroll down ~8 ticks between each) until the footer/end of menu is visible.
2. Extract all cocktail listings from the screenshots directly — name, ingredients, price. Be exhaustive across all passes.
3. `TIER=vision`.

If all four tiers fail, stop and report which tiers failed and why. Don't fabricate menu items.

### 3. Parse the menu

From the extracted text/JSON, build a normalised list of drinks:
- `name`
- `category` (cocktail / spirit-flight / wine / beer / non-alc — focus on spirits-relevant)
- `ingredients` (best effort — split by commas/dashes)
- `spirits_used` (extract brand mentions like "Beefeater", "Ketel One", and base spirits like "vodka", "mezcal")
- `price` if visible

Skip food. Skip soft drinks unless they're zero-proof cocktails.

### 4. Read the user's portfolio

Glob `$VAULT/Brands/**/*.md`, read frontmatter. For each `type: product` note, capture `name`, `brand`, `category` (vodka/gin/etc — derive from brand or product tags), `wholesale_price` if set.

If `Brands/` is empty, tell the user "no products in the vault yet — populate `Brands/<Brand>/` first" and stop.

### 5. Score placement opportunities

For each cocktail / spirit listing, identify base spirit category. For each user product, score fit:
- **Direct swap** — the menu lists a competitor brand in a category we sell (e.g. menu uses Ketel One in a Martini, we sell Absolut Elyx).
- **New build** — empty category for us but high cocktail count (e.g. they make 4 mezcal cocktails, we have a mezcal product).
- **Signature serve** — opportunity for a bespoke cocktail using one of our products.
- **No fit** — skip.

Rank top 5–8 opportunities. Each opportunity should have:
- target cocktail / category
- our recommended product (wikilink)
- displaced brand (if any)
- one-line pitch angle

### 6. Write the analysis block

Append (don't overwrite) to the venue note:

```markdown

## Menu analysis YYYY-MM-DD

**Source:** {URL} · **Fetch tier:** {TIER}

### Menu snapshot
- {N} cocktails, {M} spirits-by-category
- Base spirits represented: {list}
- Brands seen on menu: {list}

### Top placement opportunities

1. **{cocktail or category}** — recommend [[{product}]] (displaces {brand or "—"}). {pitch angle}.
2. ...

### Cocktails parsed

| Cocktail | Base | Ingredients | Price |
|----------|------|-------------|-------|
| ...      | ...  | ...         | ...   |
```

Then update the venue's frontmatter:
- `last_menu_fetch: {TIER}`
- `last_visited:` leave unchanged.

**Do NOT** mutate `pipeline_products`. Promotion to pipeline is a manual decision the salesperson makes after reading the analysis.

### 7. Report

To the user, summarise:
- Which tier succeeded (and which were skipped/failed).
- Counts: cocktails parsed, opportunities ranked.
- Path to the venue note.
- If a venue stub was newly created from a URL, say so.
