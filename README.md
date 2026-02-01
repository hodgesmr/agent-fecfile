# agent-fecfile

![agent-fecfile](./agent-fecfile.jpeg)

## FEC Filing Plugin for Claude Code

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code/plugins) for analyzing Federal Election Commission (FEC) campaign finance filings. Includes an [Agent Skill](https://agentskills.io) and an MCP server for secure API access.

This plugin enables AI agents to fetch, parse, and analyze FEC filings directly within agent sessions. Parsing and filtering happen outside the model context, allowing agents to programmatically reduce large filings before analysis, saving tokens and enabling efficient queries against filings of any size.

The plugin includes detailed field mappings for common form types and schedules, helping agents accurately interpret campaign finance data like contributions, disbursements, and committee information.

## Features

- Fetch and analyze FEC filings by filing ID
- Search for committees and filings via the FEC API (MCP server)
- Support for major form types (F1, F2, F3, F99)
- Detailed field mappings for contributions, disbursements, and schedules
- **Secure API key handling**: Key loaded once at server startup, never exposed to the model
- Auto-installing dependencies via uv

## Requirements

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) (for plugin installation)
- [uv](https://docs.astral.sh/uv/) (for running Python scripts)
- Python 3.9+
- An [FEC API key](https://api.open.fec.gov/developers/) (optional, for committee/filing search)

## Installation

### Claude Code Plugin (Recommended)

The easiest way to use this is as a Claude Code plugin. Clone the repository and load it as a plugin:

```bash
# Clone to a permanent location
git clone --branch latest git@github.com:hodgesmr/agent-fecfile.git ~/agent-fecfile

# Load as a plugin (in Claude Code)
claude --plugin-dir ~/agent-fecfile
```

When loaded as a plugin:
- The Agent Skill is automatically available
- The MCP server starts automatically, providing `search_committees` and `get_filings` tools
- The FEC API key is loaded once at startup and kept secure

To make the plugin permanent, add it to your Claude Code configuration.

### Alternative: Standalone Skill Installation

For agent runtimes that don't support Claude Code plugins (like Codex CLI), you can install just the Agent Skill:

```bash
# Clone the repository
git clone --branch latest git@github.com:hodgesmr/agent-fecfile.git ~/agent-fecfile

# Symlink to your agent's skills directory
# Claude Code CLI
ln -sfn ~/agent-fecfile/skills/fecfile ~/.claude/skills/fecfile

# Codex CLI
ln -sfn ~/agent-fecfile/skills/fecfile ~/.codex/skills/fecfile
```

In standalone mode:
- Use `mcp-server/fec_api_cli.py` for committee/filing search
- The API key is retrieved from keyring on each script invocation

## Updating

```bash
cd ~/agent-fecfile && git fetch --tags --force && git checkout latest
```

Or pin a specific version:
```bash
cd ~/agent-fecfile && git fetch && git checkout 2.0.0
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

The plugin includes an MCP server (or standalone CLI) for searching committees and filings via the authenticated FEC API.

#### 1. Get an API Key

1. Visit https://api.open.fec.gov/developers/
2. Go to "Sign up for an API key" and fill out the form
3. You'll receive your API key via email

#### 2. Store Your API Key

To shield the key from LLM model consumption, the API key must be stored in your system keyring. The MCP server and CLI scripts use the Python [keyring](https://pypi.org/project/keyring/) library, which supports a variety of operating system keyrings.

**macOS:**

1. Open Keychain Access (Applications → Utilities → Keychain Access)
2. Click File → New Password Item (or press ⌘N)
3. Fill in:
   - Keychain Item Name: `fec-api`
   - Account Name: `api-key`
   - Password: *your API key*
4. Click Add

**Linux (GNOME Keyring):**

```bash
secret-tool store --label="FEC API Key" service fec-api username api-key
```

**Windows:**

Use the Credential Manager or configure keyring appropriately.

For other supported systems, consult the [keyring documentation](https://keyring.readthedocs.io/en/latest/).

### Searching For Committees and Filings

Once your API key is stored, queries become more powerful. You can search for committees and filings without knowing the filing ID in advance.

**Plugin Mode (Claude Code):**

The MCP server provides `search_committees` and `get_filings` tools. The API key is loaded once at server startup and kept in memory—it is never visible to the model.

```text
❯ What are the top expenditures in Utah Republican Party's most recent filing?
```

**Standalone Mode (Codex, etc.):**

Use the CLI script directly:

```bash
# Search for a committee
uv run ~/agent-fecfile/mcp-server/fec_api_cli.py search-committees "Utah Republican Party"

# Get filings for a committee
uv run ~/agent-fecfile/mcp-server/fec_api_cli.py get-filings C00089482 --limit 5
```

```text
⏺ Top Expenditures - Utah Republican Party (December 2025)

  Filing 1942957 | Coverage: Dec 1-31, 2025 | Total Disbursements: $20,500.65
  ┌─────────────────────────┬───────────┬────────────────────────┬────────┐
  │          Payee          │  Amount   │        Purpose         │  Date  │
  ├─────────────────────────┼───────────┼────────────────────────┼────────┤
  │ USPS                    │ $4,699.58 │ Direct Mail            │ Dec 23 │
  ├─────────────────────────┼───────────┼────────────────────────┼────────┤
  │ CPMI Solutions          │ $4,396.30 │ Direct Mailing         │ Dec 22 │
  ├─────────────────────────┼───────────┼────────────────────────┼────────┤
  │ NationBuilder           │ $2,925.00 │ Office Subscriptions   │ Dec 1  │
  └─────────────────────────┴───────────┴────────────────────────┴────────┘
```

## Architecture

### Plugin Mode (Claude Code)

```
agent-fecfile/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (version: 2.0.0)
├── .mcp.json                # MCP server configuration
├── mcp-server/
│   ├── server.py            # MCP server (loads API key at startup)
│   └── fec_api_cli.py       # Standalone CLI (for non-MCP usage)
└── skills/
    └── fecfile/
        ├── SKILL.md         # Agent Skill instructions
        ├── references/      # Form and schedule documentation
        └── scripts/
            └── fetch_filing.py  # Public FEC filing fetcher
```

When used as a Claude Code plugin:
- The MCP server loads the FEC API key from keyring **once at startup**
- The key is held in memory and never exposed to the model
- MCP tools (`search_committees`, `get_filings`) are available alongside the skill

### Standalone Mode (Codex, etc.)

When used as a standalone skill:
- Use `mcp-server/fec_api_cli.py` for committee/filing search
- The API key is retrieved from keyring **on each invocation**
- The key passes through the Python process but is sanitized from error output

## Security Notes

- **API key security**: In plugin mode, the FEC API key is loaded once at MCP server startup and held in memory. The key is never included in tool outputs or error messages visible to the model. In standalone mode, the key is retrieved from keyring for each script invocation.

- **Network access**: This plugin requires network access to fetch data from the FEC (`docquery.fec.gov`, `api.open.fec.gov`). It will not work in environments where external network access is restricted.

- **Untrusted content**: FEC filings should be considered [untrusted content](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/). A malicious campaign sneaking prompt injections into the memo text field of their F99 is probably unlikely, but not impossible.

- **Keyring access**: The MCP server accesses the keyring at startup. In standalone mode, scripts access keyring on each invocation. Monitor agent actions that request keyring access.

> [!CAUTION]
> The user experience of macOS Keychain is [not great](https://github.com/jaraco/keyring/issues/644) and will likely result in many repeated password prompts. This may tempt the user to "Always Allow" access to the key by Python. Doing so can expose the key to the LLM agent if it then tries to write Python to read the key itself. Other system keyrings may have a better user experience.

## Plugin vs Standalone Comparison

| Feature | Plugin Mode (Claude Code) | Standalone Mode (Codex, etc.) |
|---------|---------------------------|-------------------------------|
| Installation | `claude --plugin-dir` | Symlink to skills directory |
| API key loading | Once at startup | Each script invocation |
| API key visibility | Never exposed to model | Passes through Python, sanitized |
| Committee/filing search | MCP tools (automatic) | CLI script (manual) |
| Skill availability | Automatic | Automatic |

## Skill Structure

```
skills/fecfile/
├── SKILL.md            # Main skill instructions
├── references/
│   ├── FORMS.md        # Form type reference (F1, F2, F3, F99)
│   └── SCHEDULES.md    # Schedule field mappings (A, B, C, D, E)
└── scripts/
    └── fetch_filing.py # Fetches FEC filing data (public API)
```

## Acknowledgments

- Built on the excellent [fecfile](https://github.com/esonderegger/fecfile) library by Evan Sonderegger
- Inspired by Derek Willis's [llm-fecfile](https://github.com/dwillis/llm-fecfile) LLM plugin
- Uses data from the Federal Election Commission

## License

[MIT License](./LICENSE)
