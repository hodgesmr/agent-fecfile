# FEC Filing Agent Skill

An [Agent Skill](https://agentskills.io) for analyzing Federal Election Commission (FEC) campaign finance filings.

This skill enables AI agents to fetch, parse, and analyze FEC filings directly within agent sessions. Parsing and filtering happen outside the model context, allowing agents to programmatically reduce large filings before analysis, saving tokens and enabling efficient queries against filings of any size.

The skill includes detailed field mappings for common form types and schedules, helping agents accurately interpret campaign finance data like contributions, disbursements, and committee information.

## Features

- Fetch and analyze FEC filings by filing ID
- Search for committees and filings via the FEC API
- Support for major form types (F1, F2, F3, F99)
- Detailed field mappings for contributions, disbursements, and schedules
- Auto-installing dependencies via uv

## Requirements

- An agent runtime that supports Agent Skills (e.g., [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) or [Codex CLI](https://developers.openai.com/codex/cli/))
- [uv](https://docs.astral.sh/uv/) (This skill uses `uv` to manage its own dependencies in isolation)
- An [FEC API key](https://api.open.fec.gov/developers/) (optional, for committee/filing search)
- Python 3.9+

## Installation (Global)

Clone the repository to a permanent location and symlink the skill into your runtime's skills directory.

```bash
git clone --branch latest git@github.com:hodgesmr/agent-fecfile.git ~/agent-fecfile
```

**Symlink to your agent's skills directory:**
```bash
# Claude Code CLI
ln -sfn ~/agent-fecfile/skills/fecfile ~/.claude/skills/fecfile

# Codex CLI
ln -sfn ~/agent-fecfile/skills/fecfile ~/.codex/skills/fecfile
```

Replace the target path with your agent runtime's skill directory as needed.

## Updating

```bash
cd ~/agent-fecfile && git fetch --tags --force && git checkout latest
```

Or pin a specific version:
```bash
cd ~/agent-fecfile && git fetch && git checkout 1.0.0
```

## Usage

Once installed, ask your agent to analyze FEC filings.

> [!TIP]
> For best results, use the most capable models available in your agent runtime (e.g., Claude Opus 4.5 or comparable frontier models). More capable models produce better analysis and more accurate field interpretations.

### Basic Usage (With A Filing ID)

If you already have an FEC filing ID, you can work with it directly, without needing an API key:

```text
❯ What are the largest expenditures in filing 1896830?
```

```text
⏺ FEC Filing 1896830 - Largest Expenditures

  | #   | Recipient                  |    Amount | Date       | Purpose          |
  |-----|----------------------------|-----------|------------|------------------|
  | 1   | Trump National Doral Hotel | $1,013.61 | 2025-05-19 | RNC training     |
  | 2   | Uber.com                   |    $19.77 | 2025-05-06 | Travel - Cabfare |
  |     | TOTAL (itemized)           | $1,033.38 |            |                  |

  Note

  Only 2 expenditures are itemized on Schedule B. The filing shows $21,283.49 in total
  disbursements, meaning most spending (~$20,250) was below the $200 itemization
  threshold and appears only in summary totals.

  The largest single itemized expense was for RNC training at Trump National Doral Hotel
  in May 2025.
```

```text
❯ Show me a table of the contribution counts and totals, by state, in fec filing 1896830
```

```text
⏺ FEC Filing 1896830 - Contributions by State

  | State | Count |      Total | % of Total |
  |-------|-------|------------|------------|
  | UT    |    32 | $35,042.25 |      87.0% |
  | VA    |     2 |  $2,400.00 |       6.0% |
  | GA    |     1 |    $750.00 |       1.9% |
  | MI    |     1 |    $750.00 |       1.9% |
  | MD    |     2 |    $750.00 |       1.9% |
  | FL    |     1 |    $600.00 |       1.5% |
  | TOTAL |    39 | $40,292.25 |       100% |

  Utah dominates with 87% of the total contributions. The committee received from
  6 states total, with only 7 out-of-state contributions.
```

### FEC API Setup (Optional)

The skill includes `fec_api.py` for searching committees and filings via the authenticated FEC API.

#### 1. Get an API Key

1. Visit https://api.open.fec.gov/developers/
2. Go to "Sign up for an API key" and fill out the form
3. You'll receive your API key via email

#### 2. Store Your API Key

To shield the key from LLM model consumption, the skill looks for the API key in your system keyring. The script uses the Python [keyring](https://pypi.org/project/keyring/) library, which supports a variety of operating system keyrings.

On macOS:

```bash
security add-generic-password -s "fec-api" -a "api-key" -w
```

When the script accesses the key, macOS will prompt you to allow access.

### Searching For Committees and Filings

Once your API key is stored, queries become more powerful. You can use the agent skill to search for committees and filings for you.

```text
❯ What are the top expenditures in Utah Republican Party's most recent filing?
```

```text
⏺ Top Expenditures in Utah Republican Party's Most Recent Filing

  Filing: 1934772 (November 2025 Monthly Report - Amended)
  Coverage Period: November 1-30, 2025
  Total Disbursements: $10,250.00
  ┌──────┬─────────────────────────┬───────────┬────────────────────────┬────────────┐
  │ Rank │          Payee          │  Amount   │        Purpose         │    Date    │
  ├──────┼─────────────────────────┼───────────┼────────────────────────┼────────────┤
  │ 1    │ Alta Club               │ $2,176.65 │ Fundraising Event Fees │ 2025-11-23 │
  ├──────┼─────────────────────────┼───────────┼────────────────────────┼────────────┤
  │ 2    │ ClickUp                 │ $2,030.18 │ Office Subscription    │ 2025-11-14 │
  ├──────┼─────────────────────────┼───────────┼────────────────────────┼────────────┤
  │ 3    │ Right Insight LLC       │ $1,525.00 │ Digital Consulting     │ 2025-11-05 │
  ├──────┼─────────────────────────┼───────────┼────────────────────────┼────────────┤
  │ 4    │ Buckeye Premium Finance │ $1,071.48 │ Rent                   │ 2025-11-26 │
  ├──────┼─────────────────────────┼───────────┼────────────────────────┼────────────┤
  │ 5    │ Marvellous Catering Co  │ $712.78   │ Food and Beverage      │ 2025-11-25 │
  ├──────┼─────────────────────────┼───────────┼────────────────────────┼────────────┤
  │ 6    │ Google                  │ $480.35   │ Office Subscriptions   │ 2025-11-24 │
  ├──────┼─────────────────────────┼───────────┼────────────────────────┼────────────┤
  │ 7    │ Thomas S. Monson Center │ $472.65   │ Donation               │ 2025-11-23 │
  ├──────┼─────────────────────────┼───────────┼────────────────────────┼────────────┤
  │ 8    │ Google                  │ $267.57   │ Office Subscriptions   │ 2025-11-24 │
  ├──────┼─────────────────────────┼───────────┼────────────────────────┼────────────┤
  │ 9    │ Marvellous Catering Co  │ $238.00   │ Food and Beverage      │ 2025-11-12 │
  ├──────┼─────────────────────────┼───────────┼────────────────────────┼────────────┤
  │ 10   │ Intuit                  │ $220.16   │ Office Subscriptions   │ 2025-11-24 │
  └──────┴─────────────────────────┴───────────┴────────────────────────┴────────────┘
  The largest expenditure was for a fundraising event at the Alta Club in Salt Lake City.
  The committee spent heavily on software subscriptions (ClickUp, Google, Intuit) and
  digital consulting services.
```

## Security Notes

- **Network access**: This skill requires network access to fetch data from the FEC (`docquery.fec.gov`). It will not work in environments where external network access is restricted.
- **Untrusted content**: FEC filings should be considered [untrusted content](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/). A malicious campaign sneaking prompt injections into the memo text field of their F99 is probably unlikely, but not impossible.
- **Keyring access**: Even though the API key is securely stored in the system keyring, the agent may still attempt to access it by writing bespoke scripts. Always monitor the agent's attempted actions before unlocking access to the secret store.

## Skill Structure

```
skills/fecfile/
├── SKILL.md            # Main skill instructions
├── references/
│   ├── FORMS.md        # Form type reference (F1, F2, F3, F99)
│   └── SCHEDULES.md    # Schedule field mappings (A, B, C, D, E)
└── scripts/
    ├── fetch_filing.py # Fetches FEC filing data (public API)
    └── fec_api.py      # Committee and filing search (authenticated API)
```

## Acknowledgments

- Built on the excellent [fecfile](https://github.com/esonderegger/fecfile) library by Evan Sonderegger
- Inspired by Derek Willis's [llm-fecfile](https://github.com/dwillis/llm-fecfile) LLM plugin
- Uses data from the Federal Election Commission

## License

[MIT License](./LICENSE)
