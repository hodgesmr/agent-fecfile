# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-01

### Added

- **Claude Code Plugin architecture**: The project is now a Claude Code plugin with bundled MCP server
- **MCP server** (`mcp-server/server.py`): Provides `search_committees` and `get_filings` tools
  - Loads FEC API key from system keyring **once at startup**
  - Key held in memory, never exposed to the model
  - Works with any MCP-compatible runtime (Claude Code, Codex, etc.)
- **Plugin manifest** (`.claude-plugin/plugin.json`): Defines plugin metadata and version
- **Marketplace catalog** (`.claude-plugin/marketplace.json`): Enables installation via `/plugin marketplace add`
- **MCP configuration** (`.mcp.json`): Configures the MCP server for Claude Code

### Changed

- **BREAKING**: Project restructured as a Claude Code plugin
- Moved FEC API functionality from `scripts/fec_api.py` to MCP server
- Updated SKILL.md to document both MCP tools and standalone CLI usage
- Updated README with plugin installation instructions and comparison table
- Version now tracked in plugin.json (single source of truth)

### Removed

- `skills/fecfile/scripts/fec_api.py` - functionality moved to MCP server

## [1.1.0] - 2026-02-01

### Added

- New `fec_api.py` script for searching committees and retrieving filings via the authenticated FEC API
- Secure credential storage using the system keyring (macOS Keychain, Windows Credential Manager, Linux Secret Service)
- Filtering options for filing queries: form type, cycle, report type
- Sorting options for filing results
- API key sanitization in error output to prevent accidental exposure
- Committee → filings → analysis workflow documentation in SKILL.md
- Keyring setup instructions in README.md

## [1.0.5] - 2025-01-15

### Changed

- Reverted to symlinks for skill installation (better developer experience)

## [1.0.4] - 2025-12-22

### Added

- Field Name Policy section in SKILL.md to prevent agents from guessing field names

## [1.0.3] - 2025-12-22

### Added

- CHANGELOG.md documenting project history
- Changelog maintenance instructions in release process

## [1.0.2] - 2025-12-22

### Fixed

- Fixed release script update flow for moving the `latest` tag

## [1.0.1] - 2025-12-22

### Fixed

- Use `cp` instead of symlinks for skill installation (improves compatibility)

## [1.0.0] - 2025-12-22

### Added

- Versioned release workflow with semver tags
- `latest` tag that always points to most recent stable release
- `release.sh` script for automated releases

### Changed

- Restructured SKILL.md to emphasize size-checking workflow
- Consolidated agent instructions into AGENTS.md
- Expanded field documentation for financial reports and schedules
- Improved size checking guidance: use `--summary-only` first
- Reorganized skills directory structure
- Moved reference files into `references/` folder

## [0.1.0] - 2025-12-21

Initial feature-complete release (pre-versioning).

### Added

- Streaming mode with `--stream` flag for constant-memory processing of large filings
- Pre-filtering CLI options (`--schedule`, `--summary-only`) to `fetch_filing.py`
- Large filing handling guidance
- CLAUDE.md project documentation
- AGENTS.md with development instructions
- Reference documentation for FEC forms and schedules

### Changed

- Renamed repository to claude-fecfile with fecfile skill
- Removed web upload option, focused on local Claude Code usage

## [0.0.1] - 2025-12-18

### Added

- Initial commit: FEC Filing skill for Claude Code
- Basic `fetch_filing.py` script for fetching FEC filings
- Acknowledgments section crediting fecfile library and llm-fecfile inspiration

[2.0.0]: https://github.com/hodgesmr/agent-fecfile/compare/1.1.0...2.0.0
[1.1.0]: https://github.com/hodgesmr/agent-fecfile/compare/1.0.5...1.1.0
[1.0.5]: https://github.com/hodgesmr/agent-fecfile/compare/1.0.4...1.0.5
[1.0.4]: https://github.com/hodgesmr/agent-fecfile/compare/1.0.3...1.0.4
[1.0.3]: https://github.com/hodgesmr/agent-fecfile/compare/1.0.2...1.0.3
[1.0.2]: https://github.com/hodgesmr/agent-fecfile/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/hodgesmr/agent-fecfile/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/hodgesmr/agent-fecfile/compare/0.1.0...1.0.0
[0.1.0]: https://github.com/hodgesmr/agent-fecfile/compare/0.0.1...0.1.0
[0.0.1]: https://github.com/hodgesmr/agent-fecfile/releases/tag/0.0.1
