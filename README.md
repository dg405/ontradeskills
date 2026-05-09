# OnTradeSkills

**Your AI sidekick for on-trade spirits sales.**

Prospect a city. Analyse a cocktail menu against your portfolio. Drop in a 30-page contract and get the financials calculated. Add a whole brand from a single product photo. Pull a monthly activity report. All by chatting with Claude.

OnTradeSkills is a free, open-source plugin built specifically for spirits sales teams selling into the on-trade. You don't need to be technical. You don't need to write code. You just need ten minutes and a laptop.

> Watch the 3-minute demo: [https://www.youtube.com/watch?v=yCTEd_-aSyI](https://www.youtube.com/watch?v=yCTEd_-aSyI)

---

## Some of the things it can do

**Prospect a whole city in seconds.** Type `/discover cocktail bars in Manchester` and Claude finds venues that match your ICP, writes a profile for each one, and ranks them in a discoveries dashboard. Click into any profile to see Claude's notes and the venue plotted on a map.

**Analyse any cocktail menu for portfolio fit.** Paste a bar's drinks-menu URL and Claude reads every cocktail, works out which of your products fit, and writes a placement plan. You see exactly which serves you should pitch and why.

**Upload a contract and get the financials worked out.** Drag in a PDF or Word doc. Claude pulls out the parties, products, supports, volumes, and dates, then calculates profitability using the real margins you've stored against each distributor. The original file is saved to your vault and the contract gets linked to every venue, product, and distributor it touches.

**Add a brand from a single image.** Take a photo of a brand's product range and ask Claude to add it. New brand page, product pages, and pricing all created in seconds. No more admin.

**Generate reports on demand.** Ask for a monthly activity summary, a top-10 venue list, a deck for tomorrow's pitch. Claude reads your vault and writes it for you.

**Map a whole pub group.** "Find every venue in the Drake & Morgan group and add them to my vault." Done. With a parent page, links to all 16 venues, and a map.

---

## What you'll need

Three things, one of them free, one of them a paid subscription, and ten minutes.

1. **Claude Code**, the AI assistant that runs the skills.
   - Get it: [https://claude.com/claude-code](https://claude.com/claude-code)
   - Claude Code is included with the **Claude Pro** subscription, which costs **£15 (+VAT) per month**. Sign up here: [https://www.claude.com/pricing](https://www.claude.com/pricing)
2. **Obsidian**, the free notes app where your knowledge vault lives. This is where every brand, venue, contract, and dashboard ends up. You get a beautiful linked database for free.
   - Download it: [https://obsidian.md](https://obsidian.md)
3. **A laptop** (Mac or Windows) and **ten minutes** to install.

---

## Install (one command)

After you've installed Claude Code and Obsidian, open the **Terminal** app on your Mac (search for "Terminal" in Spotlight) and paste in this single line, then press enter:

```bash
curl -fsSL https://raw.githubusercontent.com/dg405/ontradeskills/main/install.sh | bash
```

**What this does, in plain English:**
- Downloads the OnTradeSkills plugin into a hidden folder in your home directory.
- Links each skill into Claude Code so it can find them.
- Tells you when it's done.

**Then quit and reopen Claude Code** so it picks up the new skills.

If you're on Windows, install [Git for Windows](https://git-scm.com/download/win) first, then run the same command in Git Bash.

---

## First run

1. **Make a new folder on your laptop.** This will be your vault. Anywhere works. For example:
   ```
   ~/Documents/MyOnTradeVault
   ```
2. **Open that folder in Claude Code.** Right-click the folder, "Open in Terminal", then run `claude`. Or open Claude Code and point it at the folder.
3. **Type `/init-ontrade` and press enter.** Claude builds out the vault scaffolding (folders, templates, dashboards) inside that folder.
4. **Open the same folder in Obsidian.** In Obsidian, click "Open folder as vault" and pick the folder you just made. Follow the on-screen checklist to install the **Dataview** and **Map View** community plugins. Both take 30 seconds.

That's it. You're ready.

---

## Try it out

Three things to try first, lifted straight from the demo. Just type these into Claude Code:

```
/discover cocktail bars in Manchester serving premium rum
```

```
/analysemenu https://www.example-bar.com/cocktails
```

```
/uploadcontract
```
(then drag your contract PDF into the Claude Code window)

Watch the magic. Then open Obsidian to see the new pages, dashboards, and maps.

---

## Make it yours

This is the bit nobody else can do.

**The skills are just text files. Claude can edit them.** If contracts aren't analysed the way you want, tell Claude. If you want a new dashboard, tell Claude. If you want a new skill (say, `/competitorcheck` for monitoring competitor placements), tell Claude.

Examples of things you can ask Claude to do:

- "Update the venue template to include a 'last-visit' date field, and add it to every existing venue page."
- "Add a new dashboard that ranks distributors by total profit across all active contracts."
- "Make /discover also pull each venue's Instagram handle when it can find one."

You don't have to know how to code. You describe what you want; Claude makes the edit; you watch it work.

---

## What gets created

Inside whatever folder you ran `/init-ontrade` in:

```
your-folder/
  Brands/        One folder per brand, with a brand page and product pages
  Venues/        One page per venue, with location, contact, and analysis
  Groups/        Pub groups (Drake & Morgan, Young's, etc.) with their venues
  Distributors/  One page per distributor, with margins and product lists
  Contracts/     One page per contract, with financial calculations
    raw/         The original PDFs and Word docs
  Templates/     The blank templates Claude uses for new pages
  Dashboards/    Live dashboards: Discoveries, Pipeline, Expiring Contracts, etc.
  Attachments/   Any other files
```

Everything is just Markdown text files. You own them. You can copy them, back them up, sync them to iCloud, share them with your team, anything.

---

## Optional power-ups

**Better PDF and Word support.** Install `poppler` and `pandoc` so Claude can read more contract formats:

```bash
brew install poppler pandoc
```

(If you don't have Homebrew, install it from [https://brew.sh](https://brew.sh) first.)

**Connect your other tools.** Claude Code supports connectors for Gmail, PowerPoint, Word, Google Drive, your CRM, and more. Once connected, the skills can read your emails, generate decks, update your CRM, and so on. Set them up from inside Claude Code.

---

## Help

- **Stuck?** Ask Claude. Seriously. Open Claude Code and describe what's not working. It can read its own skill files and fix them.
- **Found a bug or have a feature request?** Open an issue: [https://github.com/dg405/ontradeskills/issues](https://github.com/dg405/ontradeskills/issues)
- **Want to share what you've built?** Pull requests welcome. The whole point is that everyone can fork this and make it their own.

---

## Commands at a glance

| Command | What it does |
|---------|--------------|
| `/init-ontrade` | One-time setup. Creates the vault scaffolding in the current folder. Safe to re-run. |
| `/discover <ICP or area>` | Finds new venues that match your criteria, writes profiles, ranks them. |
| `/analysemenu <venue or URL>` | Reads a cocktail menu, identifies opportunities for your portfolio, ranks placements. |
| `/uploadcontract` | Ingests a contract PDF or Word doc, extracts the details, calculates profitability, creates all the links. |
| `/analysecontract <contract>` | Re-reads an existing contract and writes a fresh risk and financials review. |

---

OnTradeSkills is free and open source. Fork it, customise it, build on it. If you make something cool, let me know.
