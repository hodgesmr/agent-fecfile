# FEC Filing Agent Skill

An [Agent Skill](https://agentskills.io) for analyzing Federal Election Commission (FEC) campaign finance filings.

This skill was originally ported from Derek Willis's [llm-fecfile](https://github.com/dwillis/llm-fecfile), an LLM plugin that provides FEC filing analysis as fragments for Simon Willison's [LLM](https://llm.datasette.io/) CLI tool. The core functionality and field mapping guidance have been adapted into the Agent Skill format, making FEC data analysis available directly within agent sessions. I wrote about that initial process [here](https://matthodges.com/posts/2025-12-19-ai-agent-fec/).

> [!NOTE]
> This Skill requires local network access to fetch data from the FEC (`docquery.fec.gov`). It will not work in environments where external network access is restricted.

## Features

- Fetch and analyze FEC filings by filing ID
- Support for major form types (F1, F2, F3, F99)
- Detailed field mappings for contributions, disbursements, and schedules
- Auto-installing dependencies via uv

## Requirements

- An agent runtime that supports Agent Skills (e.g., [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) or [Codex CLI](https://developers.openai.com/codex/cli/))
- [uv](https://docs.astral.sh/uv/) (for running the fetch script)
- Python 3.9+

## Installation (Global)

Clone the repository once, then copy the skill into your user-level skills directory.

```bash
git clone git@github.com:hodgesmr/agent-fecfile.git /tmp/agent-fecfile
```

### Claude Code CLI

```bash
cp -R /tmp/agent-fecfile/skills/fecfile ~/.claude/skills/
```

### Codex CLI

```bash
cp -R /tmp/agent-fecfile/skills/fecfile ~/.codex/skills/
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

MIT
