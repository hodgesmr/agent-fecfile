# Claude Code Plugin: fecfile

This repo contains a Claude Code plugin for analyzing FEC (Federal Election Commission) campaign finance filings. It includes an Agent Skill and an MCP server for secure API access.

## Key Details

- **Plugin name**: `fecfile`
- **Skill name**: `fecfile`
- **MCP server**: `fec-api` (provides `search_committees` and `get_filings` tools)
- **Dependencies**: `fecfile`, `mcp`, `httpx`, `keyring` - managed via inline script metadata (PEP 723), auto-installed by `uv run`
- **Data sources**:
  - Public: `docquery.fec.gov`
  - Authenticated: `api.open.fec.gov` (via MCP server)
- **Python**: Requires 3.9+

## Project Structure

```
agent-fecfile/
├── .claude-plugin/
│   ├── plugin.json              # Plugin manifest (version source of truth)
│   └── marketplace.json         # Marketplace catalog for plugin distribution
├── .mcp.json                    # MCP server configuration
├── mcp-server/
│   └── server.py                # MCP server (authenticated FEC API)
├── skills/fecfile/
│   ├── SKILL.md                 # Agent Skill instructions
│   ├── references/              # Form and schedule documentation
│   │   ├── FORMS.md             # Reference for FEC form types (F1, F2, F3, F99)
│   │   └── SCHEDULES.md         # Field mappings for Schedules A, B, C, D, E
│   └── scripts/
│       └── fetch_filing.py      # Fetches FEC filing data (public API)
├── README.md                    # Installation and usage for end users
├── CHANGELOG.md                 # Version history
└── release.sh                   # Automated release script
```

## Development Commands

**Public API (no key required):**
- `uv run skills/fecfile/scripts/fetch_filing.py <FILING_ID>`: Fetch a full filing as JSON
- `uv run skills/fecfile/scripts/fetch_filing.py <FILING_ID> --summary-only`: Summary only
- `uv run skills/fecfile/scripts/fetch_filing.py <FILING_ID> --schedule A`: Limit to a single schedule
- `uv run skills/fecfile/scripts/fetch_filing.py <FILING_ID> --stream`: JSONL streaming

**MCP Server:**
- The MCP server is automatically started by Claude Code when loaded as a plugin
- For other runtimes, configure MCP to run: `uv run mcp-server/server.py`
- The server loads the FEC API key from keyring once at startup

## Coding Style & Naming Conventions

- Python uses 4-space indentation and standard library `argparse` conventions
- MCP server uses the official `mcp` Python SDK with async/await
- Keep functions small and descriptive (e.g., `build_options`, `stream_filing`)
- Prefer straightforward, readable logic over clever abstractions
- No formatter is enforced; keep code PEP 8–friendly

## Testing Guidelines

- There is no automated test suite in this repository
- Validate changes manually by running scripts with a known filing ID
- For MCP server changes, test with `claude --plugin-dir .` from the repo root
- For large filings, verify `--summary-only` or `--stream` behavior

## Releases

Releases use semver tags (e.g., `2.0.0`) plus a `latest` tag that always points to the most recent stable release.

### Versioning Strategy

The version is tracked in **three places** that must stay in sync:

1. `.claude-plugin/plugin.json` - Primary source of truth
2. `skills/fecfile/SKILL.md` - Metadata frontmatter
3. `CHANGELOG.md` - Version history

### Release Process

1. Update the version in `.claude-plugin/plugin.json`:
   ```json
   {
     "version": "2.1.0"
   }
   ```

2. Update the version in `skills/fecfile/SKILL.md` frontmatter:
   ```yaml
   metadata:
     author: Matt Hodges
     version: "2.1.0"
   ```

3. Update `CHANGELOG.md`:
   - Add a new section at the top (below the header) for the new version
   - Use the format `## [X.Y.Z] - YYYY-MM-DD`
   - Document changes under `### Added`, `### Changed`, `### Fixed`, or `### Removed`
   - Add a comparison link at the bottom: `[X.Y.Z]: https://github.com/hodgesmr/agent-fecfile/compare/PREV...X.Y.Z`

4. Commit the version bump and changelog update

5. Run the release script:
   ```bash
   ./release.sh
   ```

The script extracts the version from plugin.json, creates the version tag, updates the `latest` tag, and pushes both.

## Architecture Notes

### MCP Server

The MCP server (`mcp-server/server.py`) provides secure API access:
- Loads FEC API key from system keyring **once at startup**
- Key held in memory, never exposed to the model
- Exposes `search_committees` and `get_filings` as MCP tools
- Uses stdio transport for communication with Claude Code
- Works with any MCP-compatible runtime (Claude Code, Codex, etc.)

### Agent Skill

The skill (`skills/fecfile/SKILL.md`) provides:
- Instructions for analyzing FEC filings
- Documentation of MCP tools
- Field reference for forms and schedules
- Large filing handling strategies

## Acknowledgments

- Built on the [fecfile](https://github.com/esonderegger/fecfile) library by Evan Sonderegger
- Inspired by [llm-fecfile](https://github.com/dwillis/llm-fecfile) by Derek Willis
