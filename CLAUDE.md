# Claude Code Skill: fecfile

This repo contains a Claude Code Agent Skill for analyzing FEC (Federal Election Commission) campaign finance filings.

## Project Structure

- `.claude/skills/fecfile/` - The skill itself
  - `SKILL.md` - Main skill instructions and metadata
  - `FORMS.md` - Reference for FEC form types (F1, F2, F3, F99)
  - `SCHEDULES.md` - Field mappings for Schedules A, B, C, D, E
  - `scripts/fetch_filing.py` - Fetches FEC filing data via the fecfile library

## Key Details

- **Skill name**: `fecfile`
- **Dependencies**: Managed via inline script metadata (PEP 723) - use `uv run` to auto-install
- **Data source**: FEC API at `docquery.fec.gov`
- **Python**: Requires 3.9+

## Common Tasks

Fetch a filing:
```bash
uv run .claude/skills/fecfile/scripts/fetch_filing.py <FILING_ID>
```

## Origin

Ported from [llm-fecfile](https://github.com/dwillis/llm-fecfile) by Derek Willis.
