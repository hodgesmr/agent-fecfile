# FEC Schedule Field Mappings

## Schedule A - Individual Contributions

Itemized contributions received ($200+ threshold for itemization).

### Key Fields

| Field | Description |
|-------|-------------|
| `contributor_organization_name` | Organization name (if applicable) |
| `contributor_last_name` | Individual's last name |
| `contributor_first_name` | Individual's first name |
| `contributor_middle_name` | Individual's middle name |
| `contributor_suffix` | Name suffix (Jr., Sr., etc.) |
| `contributor_city` | City |
| `contributor_state` | Two-letter state code |
| `contributor_zip_code` | ZIP code |
| `contribution_amount` | Dollar amount of contribution |
| `contribution_date` | Date of contribution |
| `contribution_aggregate` | Year-to-date aggregate from this contributor |
| `contributor_employer` | Employer name |
| `contributor_occupation` | Occupation |
| `memo_code` | Memo indicator |
| `memo_text_description` | Memo text |

### Name Resolution

To get contributor name:
1. First check `contributor_organization_name`
2. If empty, construct from `contributor_last_name, contributor_first_name`

### Common Queries

- **Top contributors**: Sort by `contribution_amount` descending
- **State filtering**: Use exact match on `contributor_state`
- **Large contributions**: Filter where `contribution_amount` > threshold

---

## Schedule B - Disbursements/Expenditures

Itemized expenditures made ($200+ threshold for itemization).

### Key Fields

| Field | Description |
|-------|-------------|
| `payee_organization_name` | Organization/vendor name |
| `payee_last_name` | Individual payee's last name |
| `payee_first_name` | Individual payee's first name |
| `payee_city` | City |
| `payee_state` | Two-letter state code |
| `payee_zip_code` | ZIP code |
| `expenditure_amount` | Dollar amount spent |
| `expenditure_date` | Date of expenditure |
| `expenditure_purpose_descrip` | Purpose/category of spending |
| `category_code` | FEC category code |
| `memo_code` | Memo indicator |
| `memo_text_description` | Memo text |

### Name Resolution

To get payee/recipient name:
1. First check `payee_organization_name`
2. If empty, construct from `payee_last_name, payee_first_name`

### Common Queries

- **Largest expenditures**: Sort by `expenditure_amount` descending
- **Spending by category**: Group by `expenditure_purpose_descrip`
- **Vendor analysis**: Group by `payee_organization_name`

---

## Schedule C - Loans

Loans received by the committee.

### Key Fields

| Field | Description |
|-------|-------------|
| `lender_organization_name` | Lending organization |
| `lender_last_name` | Individual lender's last name |
| `lender_first_name` | Individual lender's first name |
| `loan_amount` | Original loan amount |
| `loan_balance` | Outstanding balance |
| `loan_incurred_date` | Date loan was received |
| `loan_due_date` | Repayment due date |
| `loan_interest_rate` | Interest rate |

---

## Schedule D - Debts and Obligations

Debts owed by or to the committee.

### Key Fields

| Field | Description |
|-------|-------------|
| `creditor_organization_name` | Creditor organization |
| `creditor_last_name` | Individual creditor's last name |
| `creditor_first_name` | Individual creditor's first name |
| `debt_amount` | Amount of debt |
| `debt_incurred_date` | Date debt was incurred |
| `debt_purpose` | Purpose of debt |
| `outstanding_balance_beginning` | Balance at start of period |
| `outstanding_balance_close` | Balance at end of period |

---

## Schedule E - Independent Expenditures

Independent expenditures (not coordinated with campaigns).

### Key Fields

| Field | Description |
|-------|-------------|
| `payee_organization_name` | Payee organization |
| `payee_last_name` | Individual payee's last name |
| `payee_first_name` | Individual payee's first name |
| `expenditure_amount` | Amount spent |
| `expenditure_date` | Date of expenditure |
| `expenditure_purpose_descrip` | Purpose of expenditure |
| `support_oppose_code` | 'S' for support, 'O' for oppose |
| `candidate_name` | Candidate supported/opposed |
| `candidate_office` | Office sought by candidate |
| `candidate_state` | Candidate's state |
| `candidate_district` | Candidate's district |

---

## Data Quality Notes

- **Itemization Threshold**: Only contributions/expenditures of $200+ are required to be itemized
- **Smaller Amounts**: May appear in summary totals but not in schedule itemizations
- **Missing Fields**: Some fields may be empty - handle gracefully
- **Date Formats**: Usually YYYY-MM-DD, may include timezone info (ignore time portion)
- **Amount Formats**: Numeric values, may need formatting for display
