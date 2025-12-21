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
- **Dependencies**: `fecfile`, `pandas` - managed via inline script metadata (PEP 723), auto-installed by `uv run`
- **Data source**: FEC API at `docquery.fec.gov`
- **Python**: Requires 3.9+

## Common Tasks

Fetch a filing:
```bash
uv run .claude/skills/fecfile/scripts/fetch_filing.py <FILING_ID> [options]
```

Pre-filter options:
- `--summary-only` - Only filing summary (no itemizations)
- `--schedule A` - Only Schedule A (contributions)
- `--schedule B` - Only Schedule B (disbursements)
- `--schedules A,B` - Multiple schedules

## Large Filing Handling

FEC filings vary enormously in size. Small filings can be used directly, but large filers (ActBlue, WinRed, presidential campaigns) may have hundreds of thousands of itemizations.

1. **Pre-filter** - Use `--summary-only` or `--schedule X` to filter at parse time
2. **Check size** - Count itemizations before consuming
3. **Post-filter** - Use pandas to aggregate/limit large results (see SKILL.md for patterns)

## Acknowledgments

- Built on the [fecfile](https://github.com/esonderegger/fecfile) library by Evan Sonderegger
- Inspired by [llm-fecfile](https://github.com/dwillis/llm-fecfile) by Derek Willis
