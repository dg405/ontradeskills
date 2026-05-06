---
name: analysecontract
description: Re-read an existing contract note plus its raw PDF/docx, recalculate profitability using current distributor pricing, flag risk (exclusivity, volume shortfalls, expiry windows), and append a dated review block to the contract note. Re-runnable as terms or context change. Use when the user says "/analysecontract", "review this contract", or wants a risk read on a stored contract.
argument-hint: <contract-note-name-or-path>
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion]
---

# /analysecontract

Risk and opportunity read on a contract that's already been ingested via `/uploadcontract`.

## Inputs

User argument: $ARGUMENTS — a contract note name (e.g. `connaught-2026`) or a full path. If empty, ask via AskUserQuestion which contract; offer the most recent 4 from `Contracts/*.md` as options.

## Steps

1. **Resolve the contract note.**
   - `VAULT=$(python3 ~/.claude/skills/ontradeskills/skills/_lib/vault.py vault)`
   - Look in `$VAULT/Contracts/` for an exact slug match, then a substring match.
   - Read frontmatter and body.

2. **Re-read the raw file** linked in `raw:` — extract text again (same logic as `/uploadcontract` step 3). This guards against the contract note's body drifting out of sync with the original document.

3. **Recalculate profitability** using current distributor pricing (prices may have changed since upload):

   Read the `distributor` note's Portfolio & Pricing table. For each product or brand in the contract:
   - Match to `Wholesale Price` and `COGS` columns. If a brand (not SKU), use the average row or calculate average across that brand's SKUs.
   - Re-run the formula:
     ```
     Gross profit per bottle  = Wholesale Price − COGS
     Net profit per bottle    = Gross profit per bottle − cash_retro_per_bottle
     Free bottle cost         = free_bottles × COGS
     Product contract profit  = (Net profit per bottle × volume_forecast) − listing_fee − free_bottle_cost
     ```
   - Compare the result to any previous `## Profitability estimate` block — note if it has changed and why (e.g. COGS increased).
   - If distributor pricing is missing for any product, flag in action items.

4. **Risk + opportunity scan.** Score and surface:
   - **Expiry window** — days until `end_date`. Flag <90 days as 🔴, <180 as 🟡.
   - **Exclusivity** — categories or brands locked. Flag any that conflict with the user's portfolio (look at `Brands/**` to see which categories we sell into the venue).
   - **Volume commitments** — note forecast volumes; if the venue's `listed_products` count looks lower than the implied commitment, flag.
   - **Marketing / rebate obligations** — anything requiring spend or activity.
   - **Termination clauses** — notice periods, breach triggers.
   - **Counterparty changes** — if the venue note's `group` differs from the contract's `counterparty_group`, flag a possible ownership change.

5. **Append a dated review block** to the contract note (do **not** overwrite earlier reviews):

```markdown

## Contract review YYYY-MM-DD

**Expiry:** {N} days ({end_date})
**Status flags:** 🔴/🟡/🟢

### Profitability (current pricing)

| Product | Wholesale | COGS | Gross/bottle | Retro/bottle | Net/bottle | Forecast | Free bottles | Listing fee | Est. profit |
|---------|-----------|------|--------------|--------------|------------|----------|--------------|-------------|-------------|
| ...     | ...       | ...  | ...          | ...          | ...        | ...      | ...          | ...         | ...         |
**Total estimated contract profit: £{X}**
_{note any change vs prior estimate and reason}_

### Risk & flags
- ...

### Action items
- [ ] ...

### Cross-checks
- {any mismatches between contract terms and current venue/distributor data}
```

6. **Update frontmatter** only if the raw file extraction surfaced a new fact that was previously missing (e.g. an `end_date` that had been left blank). Never overwrite an existing confident value silently — if something looks wrong, raise it in the review block instead.

7. **Report** to the user: total estimated contract profit, top 3 risk flags, the file path, and a one-line "next action" (e.g. "renewal conversation needed in 60 days").

## Rules

- Always append, never replace.
- The risk read is advisory — don't change `status` or other action-bearing fields.
- If the raw file is missing or unreadable, abort and ask the user to re-upload.
