# agent-fecfile

![agent-fecfile](./agent-fecfile.jpeg)

## FEC Filing Plugin for Claude Code

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code/plugins) for analyzing Federal Election Commission (FEC) campaign finance filings. Includes an [Agent Skill](https://agentskills.io) and an [MCP server](https://modelcontextprotocol.io) for API access.

This plugin enables AI agents to fetch, parse, and analyze FEC filings directly within agent sessions. Parsing and filtering happen outside the model context, allowing agents to programmatically reduce large filings before analysis, saving tokens and enabling efficient queries against filings of any size.

The plugin includes detailed field mappings for common form types and schedules, helping agents accurately interpret campaign finance data like contributions, disbursements, and committee information.

## Features

- Fetch and analyze FEC filings by filing ID (Agent Skill)
- Search for committees and filings via the FEC API (MCP server)
- Support for major form types (F1, F2, F3, F99)
- Detailed field mappings for contributions, disbursements, and schedules
- Auto-installing dependencies via uv

## Requirements

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) or another MCP-compatible runtime (e.g., [Codex CLI](https://developers.openai.com/codex/cli/))
- [uv](https://docs.astral.sh/uv/) (for running Python scripts)
- Python 3.9+
- An [FEC API key](https://api.open.fec.gov/developers/) (optional, for committee/filing search)

## Installation

### Claude Code Plugin (Recommended)

The easiest way to use this is as a Claude Code plugin. Clone the repository and load it as a plugin:

```bash
# Clone to a permanent location
git clone --branch latest git@github.com:hodgesmr/agent-fecfile.git ~/agent-fecfile

# Load as a plugin in Claude Code
claude --plugin-dir ~/agent-fecfile
```

When loaded as a plugin:
- The Agent Skill is automatically available
- The MCP server starts automatically, providing `search_committees` and `get_filings` tools
- The FEC API key is loaded once at startup

To make the plugin permanent, add it to your Claude Code configuration.

### Other Compatible Runtimes (Codex, etc.)

For agent runtimes that support Agent Skills and MCP but not Claude Code plugins, you can:

1. **Install the Agent Skill** by symlinking to your runtime's skills directory:

```bash
# Clone the repository
git clone --branch latest git@github.com:hodgesmr/agent-fecfile.git ~/agent-fecfile

# Symlink to your agent's skills directory
ln -sfn ~/agent-fecfile/skills/fecfile ~/.codex/skills/fecfile
```

2. **Configure the MCP server** in your runtime's MCP configuration:

```json
{
  "mcpServers": {
    "fec-api": {
      "command": "uv",
      "args": ["run", "~/agent-fecfile/mcp-server/server.py"]
    }
  }
}
```

The MCP server loads the FEC API key from the system keyring once at startup.

#### Updating

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

The MCP server provides committee and filing search via the authenticated FEC API.

#### 1. Get an API Key

1. Visit https://api.open.fec.gov/developers/
2. Go to "Sign up for an API key" and fill out the form
3. You'll receive your API key via email

#### 2. Store Your API Key

To shield the key from LLM model consumption, the API key must be stored in your system keyring. The MCP server uses the Python [keyring](https://pypi.org/project/keyring/) library, which supports a variety of operating system keyrings.

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

### Searching For Committees and Filings

Once your API key is stored, queries become more powerful. You can search for committees and filings without knowing the filing ID in advance.

The MCP server provides `search_committees` and `get_filings` tools. The API key is loaded once at server startup and kept in memory—it is never visible to the model.

```text
❯ What are the top expenditures in Utah Republican Party's most recent filing?
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
  ├─────────────────────────┼───────────┼────────────────────────┼────────┤
  │ NationBuilder           │ $2,646.00 │ Office Subscriptions   │ Dec 29 │
  ├─────────────────────────┼───────────┼────────────────────────┼────────┤
  │ Chartwells              │ $1,907.24 │ Event Registration Fee │ Dec 17 │
  ├─────────────────────────┼───────────┼────────────────────────┼────────┤
  │ Buckeye Premium Finance │ $1,071.48 │ Rent                   │ Dec 26 │
  ├─────────────────────────┼───────────┼────────────────────────┼────────┤
  │ Extra Space Storage     │ $487.00   │ Storage                │ Dec 2  │
  ├─────────────────────────┼───────────┼────────────────────────┼────────┤
  │ Extra Space Storage     │ $487.00   │ Storage                │ Dec 30 │
  ├─────────────────────────┼───────────┼────────────────────────┼────────┤
  │ Ring Central            │ $170.31   │ Telephone              │ Dec 11 │
  ├─────────────────────────┼───────────┼────────────────────────┼────────┤
  │ Intuit                  │ $123.57   │ Office Subscriptions   │ Dec 24 │
  └─────────────────────────┴───────────┴────────────────────────┴────────┘
  The bulk of December spending was on direct mail operations (~$9,100 combined
  to USPS and CPMI Solutions) and NationBuilder software subscriptions (~$5,600).
```

## Architecture

```
agent-fecfile/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── .mcp.json                # MCP server configuration
├── mcp-server/
│   └── server.py            # MCP server (authenticated FEC API)
└── skills/
    └── fecfile/
        ├── SKILL.md         # Agent Skill instructions
        ├── references/      # Form and schedule documentation
        │   ├── FORMS.md        # Form type reference (F1, F2, F3, F99)
        │   └── SCHEDULES.md    # Schedule field mappings (A, B, C, D, E)
        └── scripts/
            └── fetch_filing.py  # Public FEC filing fetcher (public FEC API)
```

The MCP server:
- Loads the FEC API key from keyring **once at startup**
- Holds the key in memory, never exposing it to the model
- Provides `search_committees` and `get_filings` tools

## Security Notes

- **Network access**: This plugin requires network access to fetch data from the FEC (`docquery.fec.gov`, `api.open.fec.gov`). It will not work in environments where external network access is restricted.

- **Untrusted content**: FEC filings should be considered [untrusted content](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/). A malicious campaign sneaking prompt injections into the memo text field of their F99 is probably unlikely, but not impossible.

- **Keyring access**: The MCP server accesses the keyring at startup. Monitor agent actions that request keyring access.

## Acknowledgments

- Built on the excellent [fecfile](https://github.com/esonderegger/fecfile) library by Evan Sonderegger
- Inspired by Derek Willis's [llm-fecfile](https://github.com/dwillis/llm-fecfile) LLM plugin
- Uses data from the Federal Election Commission

## License

[MIT License](./LICENSE)
