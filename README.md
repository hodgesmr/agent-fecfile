# FEC Filing Agent Skill

An [Agent Skill](https://agentskills.io) for analyzing Federal Election Commission (FEC) campaign finance filings.

This skill enables AI agents to fetch, parse, and analyze FEC filings directly within agent sessions. Parsing and filtering happen outside the model context, allowing agents to programmatically reduce large filings before analysis, saving tokens and enabling efficient queries against filings of any size. The skill includes detailed field mappings for common form types and schedules, helping agents accurately interpret campaign finance data like contributions, disbursements, and committee information. You can read more about how this skill was built [here](https://matthodges.com/posts/2025-12-19-ai-agent-fec/).

> [!NOTE]
> This Skill requires network access to fetch data from the FEC (`docquery.fec.gov`). It will not work in environments where external network access is restricted.

## Features

- Fetch and analyze FEC filings by filing ID
- Support for major form types (F1, F2, F3, F99)
- Detailed field mappings for contributions, disbursements, and schedules
- Auto-installing dependencies via uv

## Requirements

- An agent runtime that supports Agent Skills (e.g., [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) or [Codex CLI](https://developers.openai.com/codex/cli/))
- [uv](https://docs.astral.sh/uv/) (for running the fetch script)
- Python 3.9+

> [!TIP]
> For best results, use the most capable models available in your agent runtime (e.g., Claude Opus 4.5 or comparable frontier models). More capable models produce better analysis and more accurate field interpretations.

## Installation (Global)

Clone the repository to a permanent location and symlink the skill into your runtime's skills directory.

```bash
git clone --branch latest git@github.com:hodgesmr/agent-fecfile.git ~/agent-fecfile
```

**Symlink to your runtime's skills directory:**
```bash
# Claude Code CLI
ln -s ~/agent-fecfile/skills/fecfile ~/.claude/skills/fecfile

# Codex CLI
ln -s ~/agent-fecfile/skills/fecfile ~/.codex/skills/fecfile
```

Replace the target path with your runtime's skill directory as needed.

## Updating

```bash
cd ~/agent-fecfile && git fetch --tags --force && git checkout latest
```

Or pin a specific version:
```bash
cd ~/agent-fecfile && git fetch && git checkout 1.0.0
```

## Usage

Once installed, ask your agent to analyze FEC filings:

> [!WARNING]
> FEC filings should be considered [untrusted content](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/). A malicious campaign sneaking prompt injections into the memo text field of their F99 is probably unlikely, but not impossible.

- "Tell me about the committee for FEC 1896830"

```
⏺ Utah Republican Party

  FEC Filing 1896830 | Form F3XN (Monthly Report)

  Committee Details

  | Field           | Value                          |
  |-----------------|--------------------------------|
  | Committee Name  | Utah Republican Party          |
  | Address         | 420 East South Temple, Ste 390 |
  | City, State ZIP | Salt Lake City, UT 84111       |
  | Coverage Period | May 1-31, 2025                 |

  Financial Summary

  | Metric                  |     Amount |
  |-------------------------|------------|
  | Total Receipts          | $42,655.80 |
  | Total Disbursements     | $21,283.49 |
  | Cash on Hand (Start)    | $45,301.29 |
  | Cash on Hand (End)      | $66,673.60 |
  | Debts Owed By Committee |  $7,333.34 |

  Summary

  This is a monthly report (F3XN) for the Utah Republican Party state party committee,
  covering May 2025. The committee had a net positive month, raising ~$43K and
  spending ~$21K, ending with about $67K cash on hand.
  They carry roughly $7,300 in debt.
```

- "What are the largest expenditures in filing 1896830?"

```
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

- "Show me a table of the contribution counts and totals, by state, in fec filing 1896830"

```
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

## Finding Filing IDs

1. **FEC Website**: Visit [fec.gov](https://www.fec.gov) and search for a committee
2. **Direct URLs**: Filing IDs appear in URLs like `https://docquery.fec.gov/dcdev/posted/1690664.fec`
3. **FEC API**: Use the [FEC API](https://api.open.fec.gov/developers/)

## Skill Structure

```
skills/fecfile/
├── SKILL.md           # Main skill instructions
├── references/
│   ├── FORMS.md        # Form type reference (F1, F2, F3, F99)
│   └── SCHEDULES.md    # Schedule field mappings (A, B, C, D, E)
└── scripts/
    └── fetch_filing.py  # Fetches FEC data
```

## Manual Script Usage

You can also run the fetch script directly:

```bash
uv run skills/fecfile/scripts/fetch_filing.py 1896830
```

Dependencies are automatically installed by uv on first run.

## Acknowledgments

- Built on the excellent [fecfile](https://github.com/esonderegger/fecfile) library by Evan Sonderegger
- Inspired by Derek Willis's [llm-fecfile](https://github.com/dwillis/llm-fecfile) LLM plugin
- Uses data from the Federal Election Commission

## License

[MIT License](./LICENSE)
