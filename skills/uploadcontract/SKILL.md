---
name: uploadcontract
description: Ingest a contract PDF or docx (passed by path or attached to the chat), copy it into Contracts/raw/, extract structured fields (venue, group, distributor, products, dates, value, key terms) into a new contract note, and backlink the venue/distributor/product notes. Surfaces ambiguous fields as a "Review needed" checklist instead of guessing. Use when the user says "/uploadcontract", "upload this contract", drags a contract PDF into the chat, or asks to log a new contract.
argument-hint: [path-to-contract-pdf-or-docx]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion]
---

# /uploadcontract

Turn a raw contract document into a structured vault note with backlinks.

## Inputs

User argument: $ARGUMENTS — optional path. Otherwise, look for an attached file in the most recent user message (Claude Code surfaces dropped/pasted attachments as readable file paths in the conversation context).

## Steps

### 1. Locate the source file

Resolve in this order:
1. If $ARGUMENTS is a non-empty path: expand `~`, verify with `test -f`. If readable → use it.
2. Otherwise, scan the conversation for an attachment with extension `.pdf`, `.docx`, or `.doc`. If exactly one is present, use it.
3. Otherwise ask via AskUserQuestion: "I need either a path argument or a contract attached to the message. What do you want to do?" with options "Cancel — I'll re-run with a file", "Attach now and re-run".

If multiple candidates exist (e.g. a path arg AND an attachment), the explicit path wins; mention to the user that the attachment was ignored.

### 2. Copy into the vault

```bash
VAULT=$(python3 ~/.claude/skills/ontradeskills/skills/_lib/vault.py vault)
mkdir -p "$VAULT/Contracts/raw"
```

Compute a normalised filename: `<venue-slug-or-unknown>-<YYYY>-<short-hash>.<ext>` where the year is best-guess from filename or "unknown" for now (can be corrected after extraction). Short-hash is the first 7 chars of `shasum -a 1` of the source.

Copy with `cp -n` (don't overwrite if a file with that name already exists; if collision, append `-2`, `-3` etc).

Record the destination path in `RAW_PATH`.

### 3. Extract text

Detect available tools first, then use the best method:

**PDF files:**
1. If `pdftotext` is available (`which pdftotext` exits 0): run `pdftotext -layout "$RAW_PATH" -`. If output is < 200 chars, the PDF is likely scanned — fall back to native (step 3 below).
2. Otherwise (no pdftotext, or scanned PDF): pass the file directly to Claude natively. Read the PDF using the Read tool — Claude handles PDFs natively without any extraction step.

**docx / doc files:**
1. If `pandoc` is available (`which pandoc` exits 0): run `pandoc "$RAW_PATH" -t plain`.
2. Otherwise: pass the file directly to Claude natively using the Read tool — Claude handles docx natively without pandoc.

Cap extracted text at ~80 KB before passing to the LLM extraction step (truncate but keep both ends — first 60 KB and last 20 KB — so trailing schedules/exhibits aren't lost). For native reads, Claude processes the full file directly and this cap does not apply.

### 4. Extract structured fields

Read the contract text and extract:
- `counterparty_venue` (the venue or holding company on the other side)
- `counterparty_group` (parent group if mentioned)
- `distributor` (who supplies the products)
- `products` (list of SKUs/brands covered — contracts may name brands rather than specific SKUs)
- `start_date` (ISO yyyy-mm-dd)
- `end_date` (ISO yyyy-mm-dd)
- `exclusivity` (categories or brands the venue is exclusive to)
- `value_gbp` (annual or total contract value if stated)
- `terms_summary` (≤3 sentences, plain English)
- `key_clauses` (bullet list of notable clauses: rebates, listing fees, free bottles, volume forecasts, marketing spend, training commitments, termination)

For each product or brand in the contract, also extract:
- `cash_retro_per_bottle` (£ per bottle cash rebate/retro, if stated)
- `listing_fee` (one-off listing fee paid to the venue, if stated)
- `free_bottles` (number of free bottles committed, if stated)
- `volume_forecast` (bottle forecast for the contract period, if stated)

For each field, mark a confidence flag. Anything not stated unambiguously goes into the "Review needed" section, not into frontmatter.

### 5. Calculate contract profitability

For each product or brand covered by the contract:

1. **Look up pricing** — read the `distributor` note's Portfolio & Pricing table. Match the product or brand name to find `Wholesale Price` and `COGS`.
   - If the contract names a brand (not a specific SKU), use the brand's average row if one exists in the table (e.g. `[[Grey Goose]] (average)`). If no average row exists, calculate the average `Wholesale Price` and `COGS` across all that brand's SKUs in the table.
   - If no distributor pricing data is available, note this in "Review needed" and skip the calculation.

2. **Calculate per-product profit:**
   ```
   Gross profit per bottle  = Wholesale Price − COGS
   Net profit per bottle    = Gross profit per bottle − cash_retro_per_bottle
   Free bottle cost         = free_bottles × COGS
   Product contract profit  = (Net profit per bottle × volume_forecast) − listing_fee − free_bottle_cost
   ```

3. **Sum** product contract profits for the **total estimated contract profit**.

4. Include the workings clearly in the contract note body under `## Profitability estimate` so the salesperson can see the assumptions.

### 5. Resolve cross-references

For each extracted entity, look up the matching vault note (slug-match):
- venue → `$VAULT/Venues/<slug>.md` (use `find-venue` helper)
- group → `$VAULT/Groups/<slug>.md`
- distributor → `$VAULT/Distributors/<slug>.md`
- each product → `$VAULT/Brands/**/<slug>.md`

**Venue not found:** if no matching venue note exists, create a stub at `$VAULT/Venues/<Title Case Name>.md` from `$VAULT/Templates/venue.md`. Populate whatever the contract reveals: `address`, `city`, `postcode`, `country`, `group`, `distributors` (from the contract's distributor field). Leave `location: ""`, `instagram:`, and `menu_url:` blank. Add `tags: [discovered]`. Tell the user a stub was created and they should fill in the remaining details. Then proceed with backlinking as normal.

For all other entity types (group, distributor, product): if no matching note exists, leave the wikilink as a dangling link and add a TODO line in the contract note's "Review needed" section.

### 6. Write the contract note

Path: `$VAULT/Contracts/<venue-slug>-<YYYY>.md` (collision: append `-v2`, `-v3`).

Use `$VAULT/Templates/contract.md` as the structure. Frontmatter populated from the extraction; only confident values. `raw: [[Contracts/raw/<filename>]]`. `status: active`.

Body sections:
- `## Terms summary` — the 3-sentence plain-English summary
- `## Key clauses` — bullets
- `## Profitability estimate` — show the workings from step 5 per product/brand, then the total. Format:
  ```
  | Product | Wholesale | COGS | Gross/bottle | Retro/bottle | Net/bottle | Forecast | Free bottles | Listing fee | Est. profit |
  ```
  If pricing data was missing for any product, note it as "pricing not available — add to distributor note".
- `## Review needed` — checkboxed list of low-confidence fields and missing cross-references

### 7. Backlink

For every confidently resolved cross-reference:
- Append the contract wikilink to the **venue's** `contracts:` frontmatter list. (Read note → parse frontmatter → add → write back.) Skip if already present.
- Same for the distributor's note (use a `contracts:` field there if present, otherwise add it).
- For each product, append the contract wikilink to the product's `contracts:` field.

### 8. Report

Tell the user:
- The path of the new contract note and the copied raw file.
- Counts: fields extracted vs flagged for review, backlinks added, dangling references created.
- A quick read of the most important terms (end date, value, exclusivity).

## Rules

- Never mutate `pipeline_products` or `listed_products` — that's `/analysemenu` territory and a salesperson decision.
- Never invent contract terms. If unclear, it goes into `## Review needed`.
- Never overwrite a previously copied raw file — collisions get a numeric suffix.
