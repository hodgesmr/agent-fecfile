---
name: fecfile
description: Analyze FEC (Federal Election Commission) campaign finance filings. Use when working with FEC filing IDs, campaign finance data, contributions, disbursements, or political committee financial reports.
compatibility: Requires uv and access to the internet
license: MIT
metadata:
  author: Matt Hodges
  version: "1.0.5"
---

# FEC Filing Analysis

This skill enables analysis of Federal Election Commission campaign finance filings.

## Requirements

- [uv](https://docs.astral.sh/uv/) must be installed
- Python 3.9+

Dependencies are automatically installed when running the script with `uv run`.

## First-Time Check

The first time this skill is invoked in a session, verify that `uv` is installed by running:

```bash
uv --version
```

If this command fails or `uv` is not found, do not proceed. Instead, inform the user that `uv` is required but not installed, and direct them to the installation guide: https://docs.astral.sh/uv/getting-started/installation/

## Quick Start

**Always start by checking the filing size:**
```bash
uv run scripts/fetch_filing.py <FILING_ID> --summary-only
```

Based on the summary, decide how to proceed—see **Handling Large Filings** below for filtering and streaming strategies. Small filings can be fetched directly; large filings require pre-filtering or streaming.

**Fetching data:**
```bash
uv run scripts/fetch_filing.py <FILING_ID>                   # Full filing (small filings only)
uv run scripts/fetch_filing.py <FILING_ID> --schedule A      # Only contributions
uv run scripts/fetch_filing.py <FILING_ID> --schedule B      # Only disbursements
uv run scripts/fetch_filing.py <FILING_ID> --schedules A,B   # Multiple schedules
```

The `fecfile` library is installed automatically by uv.

## Field Name Policy

**IMPORTANT**: Do not guess at field names. Before referencing any field names in responses:

1. For form-level fields (summary data, cash flow, totals): Read `references/FORMS.md`
2. For itemization fields (contributors, payees, expenditures): Read `references/SCHEDULES.md`

These files contain the authoritative field mappings. If a field name isn't documented there, verify it exists in the actual JSON output before using it.

## Handling Large Filings

FEC filings vary enormously in size. Small filings (like state party monthly reports) may have only a few dozen itemizations and can be used directly. However, major committees like ActBlue, WinRed, and presidential campaigns can have hundreds of thousands of itemizations in a single filing. **Do not dump large filing data directly into the context window.**

### Checking Size

Before pulling full schedules, use `--summary-only` to assess the filing:

```bash
uv run scripts/fetch_filing.py <ID> --summary-only
```

The summary includes financial totals that help gauge filing size without parsing itemizations:

| Field | Description |
|-------|-------------|
| `col_a_individuals_itemized` | Itemized individual contributions (this period) |
| `col_a_total_contributions` | Total contributions (this period) |
| `col_a_total_disbursements` | Total disbursements (this period) |
| `col_b_individuals_itemized` | Itemized individual contributions (year-to-date) |
| `col_b_total_contributions` | Total contributions (year-to-date) |
| `col_b_total_disbursements` | Total disbursements (year-to-date) |

These are dollar totals, not item counts, but combined with the committee name they help you decide:
- **Small state/local party with modest totals**: Probably safe to pull full schedules
- **ActBlue, WinRed, or presidential campaign with millions in totals**: Use streaming or post-filter

If you need to verify exact counts before processing, stream with an early cutoff:

```bash
uv run scripts/fetch_filing.py <ID> --stream --schedule A | python3 -c "
import sys
count = 0
limit = 256
for line in sys.stdin:
    count += 1
    if count >= limit:
        print(f'Schedule A: {limit}+ items (stopped counting)')
        sys.exit(0)
print(f'Schedule A: {count} items')
"
```

If itemization counts are in the hundreds or more, you must post-filter before presenting results. Even smaller filings may benefit from post-filtering to aggregate or focus the output.

### Pre-Filtering at Parse Time

Use CLI flags to filter before data is loaded into memory:

| Flag | Effect |
|------|--------|
| `--summary-only` | Only filing summary (no itemizations) |
| `--schedule A` | Only Schedule A (contributions) |
| `--schedule B` | Only Schedule B (disbursements) |
| `--schedule C` | Only Schedule C (loans) |
| `--schedule D` | Only Schedule D (debts) |
| `--schedule E` | Only Schedule E (independent expenditures) |
| `--schedules A,B` | Multiple schedules (comma-separated) |

Schedules you don't request are never parsed.

### Post-Filtering with Pandas

Use Python/pandas to aggregate, filter, and limit results:

```bash
cat > /tmp/analysis.py << 'EOF'
# /// script
# requires-python = ">=3.9"
# dependencies = ["pandas>=2.3.0"]
# ///
import json, sys
import pandas as pd

data = json.load(sys.stdin)
df = pd.DataFrame(data.get('itemizations', {}).get('Schedule A', []))
# Aggregate and limit output
print(df.groupby('contributor_state')['contribution_amount'].agg(['count', 'sum']).sort_values('sum', ascending=False).to_string())
EOF

uv run scripts/fetch_filing.py <ID> --schedule A 2>&1 | uv run /tmp/analysis.py
```

### Streaming Mode (Producer/Consumer Model)

For truly massive filings where even a single schedule is too large to hold in memory, use `--stream` to output JSONL (one JSON object per line):

```bash
uv run scripts/fetch_filing.py <ID> --stream --schedule A
```

Each line has the format: `{"data_type": "...", "data": {...}}`

**How streaming works:**

The producer (fetch_filing.py) outputs one record at a time without loading the full filing. A consumer script reads one line at a time and aggregates incrementally. Neither side ever holds all records in memory.

Example streaming aggregation:

```bash
uv run scripts/fetch_filing.py <ID> --stream --schedule A | python3 -c "
import json, sys
from collections import defaultdict
totals = defaultdict(float)
counts = defaultdict(int)
for line in sys.stdin:
    rec = json.loads(line)
    if rec['data_type'] == 'itemization':
        state = rec['data'].get('contributor_state', 'Unknown')
        amt = float(rec['data'].get('contribution_amount', 0))
        totals[state] += amt
        counts[state] += 1
for state in sorted(totals, key=lambda s: -totals[s]):
    print(f'{state}: {counts[state]} contributions, \${totals[state]:,.2f}')
"
```

This processes hundreds of thousands of records using constant memory.

### Guidelines

1. **Small filings** - Can be used directly without filtering
2. **Large filings** - Pre-filter with `--summary-only` or `--schedule X`, then check size
3. **Massive results** - Post-filter with pandas to aggregate, filter, and limit output
4. **Streaming mode** - Use `--stream` with inline Python consumers for constant-memory processing
5. **Limit output** - Use `.head()`, `.nlargest()`, `.nsmallest()` to cap results

## Finding Filing IDs

Filing IDs can be found via:
1. **FEC Website**: Visit [fec.gov](https://www.fec.gov) and search for a committee
2. **Direct URLs**: Filing IDs appear in URLs like `https://docquery.fec.gov/dcdev/posted/1690664.fec`
3. **FEC API**: Use `fec_api.py` to search for committees (see below), or the [FEC API directly](https://api.open.fec.gov/developers/)

## FEC API (Authenticated)

The `fec_api.py` script provides access to the authenticated FEC API at `api.open.fec.gov`. This API requires an API key and provides additional search capabilities beyond what's available through public filing data.

### Getting an API Key

1. Visit https://api.data.gov/signup/
2. Fill out the form to receive your API key via email
3. Store the key securely using one of the methods below

### Credential Setup

API keys are retrieved securely via the system keyring. This prevents secrets from being exposed in environment variables or files that could be read inadvertently.

**Supported platforms:**
- **macOS**: Keychain
- **Windows**: Credential Manager
- **Linux**: Secret Service (GNOME Keyring, KWallet)

#### Store your API key (one-time setup)

Using Python (cross-platform):
```bash
python -c "import keyring; keyring.set_password('fec-api', 'api-key', input('API Key: '))"
```

Using the keyring CLI (if installed):
```bash
keyring set fec-api api-key
```

Using macOS Keychain directly:
```bash
security add-generic-password -s "fec-api" -a "api-key" -w "YOUR_API_KEY_HERE"
```

#### Verify your key is stored

```bash
python -c "import keyring; print('Key found' if keyring.get_password('fec-api', 'api-key') else 'Not found')"
```

### Usage

**Search for committees by name:**
```bash
uv run scripts/fec_api.py search-committees "ActBlue"
uv run scripts/fec_api.py search-committees "Biden" --limit 5
```

**Output format:**
```json
[
  {
    "committee_id": "C00401224",
    "name": "ACTBLUE",
    "committee_type_full": "Independent Expenditor (Person or Group)",
    "designation_full": "Unauthorized",
    "party_full": null,
    "state": "MA",
    "treasurer_name": "ERIN HILL"
  }
]
```

### Alternative Secret Stores

For users with existing secret management infrastructure (HashiCorp Vault, 1Password, AWS Secrets Manager, etc.), use `--credential-cmd` to specify a shell command that outputs the API key:

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
2. **Use the encrypted file backend**: Set `PYTHON_KEYRING_BACKEND=keyrings.alt.file.EncryptedKeyring` (will prompt for a master password)
3. **Use `--credential-cmd`**: Point to your preferred secret store

### Troubleshooting

**"FEC API key not found in system keyring"**
- Verify the key is stored: `python -c "import keyring; print(keyring.get_password('fec-api', 'api-key'))"`
- Re-add the key using the setup instructions above

**"Failed to initialize keyring backend" (Linux)**
- Ensure a Secret Service provider is running, or use `--credential-cmd`

**API returns 403 Forbidden**
- Your API key may be invalid or expired
- Request a new key at https://api.data.gov/signup/

## Response Style

When analyzing FEC filings:
- Start with your best judgment about whether this filing has unusual aspects (no activity is not unusual)
- Write in a simple, direct style
- Group related information together in coherent sections
- Avoid excessive formatting or bold text

## Form Types

See [FORMS.md](references/FORMS.md) for detailed guidance on:
- **F1/F1A**: Committee registration/organization
- **F2/F2A**: Candidate declarations
- **F3/F3P/F3X**: Financial reports
- **F99**: Miscellaneous text filings

## Schedules & Field Mappings

See [SCHEDULES.md](references/SCHEDULES.md) for detailed field mappings for:
- **Schedule A**: Individual contributions
- **Schedule B**: Disbursements/expenditures
- **Schedule C**: Loans
- **Schedule D**: Debts
- **Schedule E**: Independent expenditures

## Amendment Detection

Check the `amendment_indicator` field:
- `A` = Standard Amendment
- `T` = Termination Amendment
- Empty/None = Original Filing

If it's an amendment, look for `previous_report_amendment_indicator` for the original filing ID.

## Coverage Periods

Use `coverage_from_date` and `coverage_through_date` fields.
- Format: Usually YYYY-MM-DD
- Calculate days covered: (end_date - start_date) + 1
- Context: Quarterly reports ~90 days, Monthly ~30 days, Pre-election varies

## Financial Summary Fields

For financial filings (F3, F3P, F3X):
- **Receipts**: `col_a_total_receipts`
- **Disbursements**: `col_a_total_disbursements`
- **Cash on Hand**: `col_a_cash_on_hand_close_of_period`
- **Debts**: `col_a_debts_to` and `col_a_debts_by`

## Data Quality Notes

- Contributions/expenditures $200+ must be itemized with details
- Smaller amounts may appear in summary totals but not itemized
- FEC Committee ID format is usually C########

## Example Queries

Once you have filing data, you can answer questions like:
- "What are the total receipts and disbursements?"
- "Who are the top 10 contributors?"
- "What are the largest expenditures?"
- "What contributions came from California?"
- "How much was spent on advertising?"
