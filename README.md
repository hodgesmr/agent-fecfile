# FEC Filing Skill for Claude Code

A Claude Code Agent Skill for analyzing Federal Election Commission (FEC) campaign finance filings.

## Features

- Fetch and analyze FEC filings by filing ID
- Support for all major form types (F1, F2, F3, F99)
- Detailed field mappings for contributions, disbursements, and schedules
- Auto-installing dependencies via uv

## Requirements

- [Claude Code](https://claude.ai/code)
- [uv](https://docs.astral.sh/uv/) (for running the fetch script)
- Python 3.9+

## Installation

### Option 1: Upload ZIP to Claude (Easiest)

1. Download `fec-filing-skill.zip` from the [Releases page](../../releases)
2. In Claude, go to **Settings > Capabilities**
3. In the Skills section, click **"Upload skill"**
4. Upload the ZIP file

The skill is now available in your Claude sessions.

### Option 2: Clone this repository (Project Skill)

```bash
git clone <repo-url> fec-skill
cd fec-skill
```

The skill is automatically available when using Claude Code in this directory.

### Option 3: Install as a Personal Skill

Copy the skill to your personal skills directory:

```bash
git clone <repo-url> /tmp/fec-skill
cp -r /tmp/fec-skill/.claude/skills/fec-filing ~/.claude/skills/
```

The skill is now available globally in all Claude Code sessions.

### Option 4: Add to an Existing Project

```bash
mkdir -p your-project/.claude/skills
cp -r .claude/skills/fec-filing your-project/.claude/skills/
```

## Usage

Once installed, ask Claude Code to analyze FEC filings:

- "Analyze FEC filing 1896830"
- "Who are the largest contributors in filing 1896830?"
- "What are the biggest expenditures in this filing?"
- "Show me contributions from California"

Claude will automatically use the skill to fetch and analyze the filing data.

## Finding Filing IDs

1. **FEC Website**: Visit [fec.gov](https://www.fec.gov) and search for a committee
2. **Direct URLs**: Filing IDs appear in URLs like `https://docquery.fec.gov/dcdev/posted/1690664.fec`
3. **FEC API**: Use the [FEC API](https://api.open.fec.gov/developers/)

## Skill Structure

```
.claude/skills/fec-filing/
├── SKILL.md           # Main skill instructions
├── FORMS.md           # Form type reference (F1, F2, F3, F99)
├── SCHEDULES.md       # Schedule field mappings (A, B, C, D, E)
└── scripts/
    └── fetch_filing.py  # Fetches FEC data (auto-installs dependencies)
```

## Manual Script Usage

You can also run the fetch script directly:

```bash
uv run .claude/skills/fec-filing/scripts/fetch_filing.py 1896830
```

Dependencies are automatically installed by uv on first run.

## Creating a Release (Maintainers)

To create a new release with the ZIP file:

```bash
# Generate the ZIP
./scripts/package-skill.sh

# Create a GitHub release and attach the ZIP
gh release create v1.0.0 fec-filing-skill.zip --title "v1.0.0" --notes "Initial release"
```

## License

MIT
