# FEC Form Types

## F1 / F1A - Statement of Organization

**Purpose**: Committee registration/organization details (not financial)

**Key Fields**:
- `committee_name`
- `committee_type`
- `committee_designation`
- `fec_committee_id_number`
- `treasurer_name`
- `treasurer_email`
- `custodian_name`
- `custodian_email`
- `committee_email`
- `committee_url` / `committee_website`
- `street_1`, `street_2`, `city`, `state`, `zip_code`
- `filing_frequency`

**F1 vs F1A**:
- **F1**: Original Statement of Organization - filed when a committee first registers with the FEC
- **F1A**: Amended Statement of Organization - filed when committee details change (address, treasurer, etc.)

**Notes**:
- Must be filed before a committee can raise or spend money
- Amendments must be filed within 10 days of changes

---

## F2 / F2A - Statement of Candidacy

**Purpose**: Candidate declaration (not financial)

**Key Fields**:
- `candidate_name`
- `office` - Office sought (House, Senate, President)
- `state`
- `district` - Congressional district (N/A for Senate/President)
- `party`
- `election_year`
- `election_type`
- `candidate_email` / `email`
- `candidate_url` / `candidate_website` / `website`
- `street_1`, `street_2`, `city`, `candidate_state`, `zip_code`

**F2 vs F2A**:
- **F2**: Original Statement of Candidacy - declares intent to run for federal office
- **F2A**: Amended Statement of Candidacy - updates candidate information

**Notes**:
- Filed by individuals seeking House, Senate, or Presidential office
- Must be filed within 15 days of becoming a candidate
- Amendments must be filed within 15 days of changes

---

## F3 / F3P / F3X - Financial Reports

**Purpose**: Financial report showing money raised and spent

### Form Variants
- **F3**: Report of Receipts and Disbursements (House/Senate campaigns)
- **F3P**: Report of Receipts and Disbursements (Presidential campaigns)
- **F3X**: Report of Receipts and Disbursements (PACs, party committees)

**Key Summary Fields**:
- `col_a_total_receipts` - Total money received
- `col_a_total_disbursements` - Total money spent
- `col_a_cash_on_hand_close_of_period` - Ending cash balance
- `col_a_debts_to` - Money owed to the committee
- `col_a_debts_by` - Money the committee owes

**Coverage Period Fields**:
- `coverage_from_date` - Start of reporting period
- `coverage_through_date` - End of reporting period

**Amendment Fields**:
- `amendment_indicator` - 'A' for amendment, 'T' for termination, empty for original
- `previous_report_amendment_indicator` - Original filing ID if this is an amendment

**Itemizations**:
Financial reports include detailed itemizations in schedules:
- Schedule A: Contributions received
- Schedule B: Disbursements made
- Schedule C: Loans
- Schedule D: Debts
- Schedule E: Independent expenditures

See [SCHEDULES.md](SCHEDULES.md) for field mappings.

---

## F99 - Miscellaneous Text

**Purpose**: Miscellaneous text communications to the FEC

**Key Fields**:
- `fec_committee_id_number`
- `committee_name`
- `date_signed`
- `text` - The substantive content of the filing

**Common Uses**:
- Debt settlement notifications
- Schedule change requests
- Explanations of discrepancies
- General correspondence with the FEC

**Notes**:
- The `text` field contains the important information
- No financial data - focus on the written explanation
- Text content may be a string or list of text blocks
