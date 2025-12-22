# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[1.0.2]: https://github.com/hodgesmr/agent-fecfile/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/hodgesmr/agent-fecfile/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/hodgesmr/agent-fecfile/compare/0.1.0...1.0.0
[0.1.0]: https://github.com/hodgesmr/agent-fecfile/compare/0.0.1...0.1.0
[0.0.1]: https://github.com/hodgesmr/agent-fecfile/releases/tag/0.0.1
