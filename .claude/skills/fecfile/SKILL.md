---
name: fecfile
description: Analyze FEC (Federal Election Commission) campaign finance filings. Use when working with FEC filing IDs, campaign finance data, contributions, disbursements, or political committee financial reports.
---

# FEC Filing Analysis

This skill enables analysis of Federal Election Commission campaign finance filings.

## Requirements

- [uv](https://docs.astral.sh/uv/) must be installed
- Python 3.9+

Dependencies are automatically installed when running the script with `uv run`.

## Quick Start

To analyze an FEC filing, use the helper script:

```bash
uv run .claude/skills/fecfile/scripts/fetch_filing.py <FILING_ID>
```

Example:
```bash
uv run .claude/skills/fecfile/scripts/fetch_filing.py 1896830
```

The `fecfile` and `pandas` libraries are installed automatically by uv.

## Handling Large Filings

FEC filings vary widely in size. Small filings (a few hundred lines) can be used directly, but large filings (thousands of itemizations) should be filtered before analysis to avoid overwhelming the context window.

**Check the size first:**
```bash
uv run .claude/skills/fecfile/scripts/fetch_filing.py <ID> 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
for sched, items in data.get('itemizations', {}).items():
    print(f'{sched}: {len(items)} items')
"
```

### Simple Filtering (stdlib)

For basic filtering, pipe to `python3`:

```bash
# Filing summary only (no itemizations)
uv run .claude/skills/fecfile/scripts/fetch_filing.py <ID> 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(json.dumps(data.get('filing', {}), indent=2, default=str))
"
```

### Pandas Filtering

For aggregations and complex analysis, write a temp script with inline dependencies:

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
# Your analysis here...
print(df.groupby('contributor_state')['contribution_amount'].agg(['count', 'sum']).sort_values('sum', ascending=False).to_string())
EOF

uv run .claude/skills/fecfile/scripts/fetch_filing.py <ID> 2>&1 | uv run /tmp/analysis.py
```

### Guidelines

1. **Check size first** - Count itemizations before deciding to filter
2. **Filter early** - Use pandas to select only relevant columns/rows
3. **Aggregate** - Use groupby, sum, count to reduce data volume
4. **Limit output** - Use `.head()`, `.nlargest()`, `.nsmallest()` to cap results

## Finding Filing IDs

Filing IDs can be found via:
1. **FEC Website**: Visit [fec.gov](https://www.fec.gov) and search for a committee
2. **Direct URLs**: Filing IDs appear in URLs like `https://docquery.fec.gov/dcdev/posted/1690664.fec`
3. **FEC API**: Use the [FEC API](https://api.open.fec.gov/developers/) to search for filings

## Response Style

When analyzing FEC filings:
- Start with your best judgment about whether this filing has unusual aspects (no activity is not unusual)
- Write in a simple, direct style
- Group related information together in coherent sections
- Avoid excessive formatting or bold text

## Form Types

See [FORMS.md](FORMS.md) for detailed guidance on:
- **F1/F1A**: Committee registration/organization
- **F2/F2A**: Candidate declarations
- **F3/F3P/F3X**: Financial reports
- **F99**: Miscellaneous text filings

## Schedules & Field Mappings

See [SCHEDULES.md](SCHEDULES.md) for detailed field mappings for:
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
