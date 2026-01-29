# FEC Filing Agent Skill

An [Agent Skill](https://agentskills.io) for analyzing Federal Election Commission (FEC) campaign finance filings.

This skill enables AI agents to fetch, parse, and analyze FEC filings directly within agent sessions. Parsing and filtering happen outside the model context, allowing agents to programmatically reduce large filings before analysis, saving tokens and enabling efficient queries against filings of any size. The skill includes detailed field mappings for common form types and schedules, helping agents accurately interpret campaign finance data like contributions, disbursements, and committee information. You can read more about how this skill was built [here](https://matthodges.com/posts/2025-12-19-ai-agent-fec/).

> [!NOTE]
> This Skill requires network access to fetch data from the FEC (`docquery.fec.gov`). It will not work in environments where external network access is restricted.

## Features

- Fetch and analyze FEC filings by filing ID
- Support for major form types (F1, F2, F3, F99)
- Detailed field mappings for contributions, disbursements, and schedules
- Auto-installing dependencies via uv

## Requirements

- An agent runtime that supports Agent Skills (e.g., [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) or [Codex CLI](https://developers.openai.com/codex/cli/))
- [uv](https://docs.astral.sh/uv/) (This skill uses `uv` to manage its own dependencies in isolation)
- Python 3.9+

> [!TIP]
> For best results, use the most capable models available in your agent runtime (e.g., Claude Opus 4.5 or comparable frontier models). More capable models produce better analysis and more accurate field interpretations.

## Installation (Global)

Clone the repository to a permanent location and symlink the skill into your runtime's skills directory.

```bash
git clone --branch latest git@github.com:hodgesmr/agent-fecfile.git ~/agent-fecfile
```

**Symlink to your agent's skills directory:**
```bash
# Claude Code CLI
ln -sfn ~/agent-fecfile/skills/fecfile ~/.claude/skills/fecfile

# Codex CLI
ln -sfn ~/agent-fecfile/skills/fecfile ~/.codex/skills/fecfile
```

Replace the target path with your agent runtime's skill directory as needed.

## Updating

```bash
cd ~/agent-fecfile && git fetch --tags --force && git checkout latest
```

Or pin a specific version:
```bash
cd ~/agent-fecfile && git fetch && git checkout 1.0.0
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
3. **FEC API**: Use `fec_api.py` to search for committees (requires API key setup below)

## FEC API Setup (Optional)

The skill includes `fec_api.py` for searching committees via the authenticated FEC API. This is optional—the core filing analysis works without it.

### 1. Get an API Key

1. Visit https://api.open.fec.gov/developers/
2. Click "Get an API Key" and fill out the form
3. You'll receive your API key via email

### 2. Store Your API Key

API keys are stored in your system keyring. **Important:** Create the key manually (not via Python) so that the OS prompts for approval when scripts access it.

#### macOS

**Option A: Using Keychain Access (GUI)**
1. Open Keychain Access (Applications → Utilities → Keychain Access)
2. Click File → New Password Item (or press ⌘N)
3. Fill in:
   - Keychain Item Name: `fec-api`
   - Account Name: `api-key`
   - Password: *your API key*
4. Click Add

**Option B: Using Terminal**
```bash
security add-generic-password -s "fec-api" -a "api-key" -w "YOUR_API_KEY_HERE"
```

The first time the script accesses the key, macOS will prompt you to allow access.

#### Windows

1. Open Credential Manager (search "Credential Manager" in Start)
2. Click "Windows Credentials"
3. Click "Add a generic credential"
4. Fill in:
   - Internet or network address: `fec-api`
   - User name: `api-key`
   - Password: *your API key*

#### Linux

Use your distribution's secret manager (GNOME Keyring, KWallet) or `--credential-cmd` with your preferred secret store.

#### Verify your key is stored

```bash
# macOS
security find-generic-password -s "fec-api" -a "api-key" -w
```

### Alternative Secret Stores

If you use a secret manager like HashiCorp Vault, 1Password, or AWS Secrets Manager, you can use `--credential-cmd` to retrieve your API key:

```bash
# HashiCorp Vault
uv run scripts/fec_api.py --credential-cmd "vault kv get -field=api_key secret/fec" search-committees "Biden"

# 1Password CLI
uv run scripts/fec_api.py --credential-cmd "op read 'op://Private/FEC API/credential'" search-committees "Biden"

# AWS Secrets Manager
uv run scripts/fec_api.py --credential-cmd "aws secretsmanager get-secret-value --secret-id fec-api --query SecretString --output text" search-committees "Biden"

# pass (Unix password manager)
uv run scripts/fec_api.py --credential-cmd "pass show fec/api-key" search-committees "Biden"

# Bitwarden CLI
uv run scripts/fec_api.py --credential-cmd "bw get password fec-api-key" search-committees "Biden"
```

### Linux Notes

On Linux systems without a graphical environment, the keyring library may not find a Secret Service provider. Options:

1. **Install a Secret Service provider**: `gnome-keyring` or `kwallet`
2. **Use the encrypted file backend**: `PYTHON_KEYRING_BACKEND=keyrings.alt.file.EncryptedKeyring` (prompts for master password)
3. **Use `--credential-cmd`**: Point to your preferred secret store

### Troubleshooting

| Error | Solution |
|-------|----------|
| "FEC API key not found in system keyring" | Re-add your key using the setup instructions above |
| "Failed to initialize keyring backend" (Linux) | Install a Secret Service provider or use `--credential-cmd` |
| API returns 403 Forbidden | Your API key may be invalid—request a new one |

## Skill Structure

```
skills/fecfile/
├── SKILL.md            # Main skill instructions
├── references/
│   ├── FORMS.md        # Form type reference (F1, F2, F3, F99)
│   └── SCHEDULES.md    # Schedule field mappings (A, B, C, D, E)
└── scripts/
    ├── fetch_filing.py # Fetches FEC filing data (public API)
    └── fec_api.py      # Committee search (authenticated API)
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

[MIT License](./LICENSE)
