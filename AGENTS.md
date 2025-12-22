# Agent Skill: fecfile

This repo contains an Agent Skill for analyzing FEC (Federal Election Commission) campaign finance filings.

## Key Details

- **Skill name**: `fecfile`
- **Dependencies**: `fecfile` - managed via inline script metadata (PEP 723), auto-installed by `uv run`
- **Data source**: FEC API at `docquery.fec.gov`
- **Python**: Requires 3.9+

## Project Structure

- `skills/fecfile/` - The skill itself
  - `SKILL.md` - Main skill entrypoint and usage guide
  - `references/FORMS.md` - Reference for FEC form types (F1, F2, F3, F99)
  - `references/SCHEDULES.md` - Field mappings for Schedules A, B, C, D, E
  - `scripts/fetch_filing.py` - Fetches FEC filing data via the fecfile library
- `README.md` - Installation and usage for end users

## Development Commands

- `uv run skills/fecfile/scripts/fetch_filing.py <FILING_ID>`: Fetch a full filing as JSON.
- `uv run skills/fecfile/scripts/fetch_filing.py <FILING_ID> --summary-only`: Summary only, no itemizations.
- `uv run skills/fecfile/scripts/fetch_filing.py <FILING_ID> --schedule A`: Limit to a single schedule.
- `uv run skills/fecfile/scripts/fetch_filing.py <FILING_ID> --stream`: JSONL streaming for large filings.

## Coding Style & Naming Conventions

- Python uses 4-space indentation and standard library `argparse` conventions.
- Keep functions small and descriptive (e.g., `build_options`, `stream_filing`).
- Prefer straightforward, readable logic over clever abstractions.
- No formatter is enforced; keep code PEP 8–friendly and consistent with `fetch_filing.py`.

## Testing Guidelines

- There is no automated test suite in this repository.
- Validate changes manually by running the script with a known filing ID.
- For large filings, verify `--summary-only` or `--stream` behavior to avoid memory issues.

## Releases

Releases use semver tags (e.g., `1.0.0`) plus a `latest` tag that always points to the most recent stable release.

### Release Process

1. Update the version in `skills/fecfile/SKILL.md` frontmatter:
   ```yaml
   metadata:
     author: Matt Hodges
     version: "1.1.0"
   ```
2. Commit the version bump
3. Run the release script:
   ```bash
   ./release.sh
   ```

The script extracts the version from SKILL.md, creates the version tag, updates the `latest` tag, and pushes both.

## Acknowledgments

- Built on the [fecfile](https://github.com/esonderegger/fecfile) library by Evan Sonderegger
- Inspired by [llm-fecfile](https://github.com/dwillis/llm-fecfile) by Derek Willis
