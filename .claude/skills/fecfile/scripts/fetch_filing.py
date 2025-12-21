#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "fecfile>=0.9.1",
#     "pandas>=2.3.0",
# ]
# ///
"""
Fetch and display FEC filing data.

Usage:
    uv run fetch_filing.py <filing_id> [options]

Examples:
    uv run fetch_filing.py 1896830                    # Full filing
    uv run fetch_filing.py 1896830 --summary-only     # Summary only (no itemizations)
    uv run fetch_filing.py 1896830 --schedule A       # Only Schedule A (contributions)
    uv run fetch_filing.py 1896830 --schedule B       # Only Schedule B (disbursements)
    uv run fetch_filing.py 1896830 --schedules A,B,C  # Multiple schedules
    uv run fetch_filing.py 1896830 --stream           # Stream as JSONL (low memory)

Dependencies are automatically installed by uv.
"""

import argparse
import json
import sys

import fecfile


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch and display FEC filing data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 1896830                    # Full filing
  %(prog)s 1896830 --summary-only     # Summary only (no itemizations)
  %(prog)s 1896830 --schedule A       # Only Schedule A (contributions)
  %(prog)s 1896830 --schedule B       # Only Schedule B (disbursements)
  %(prog)s 1896830 --schedules A,B,C  # Multiple schedules
  %(prog)s 1896830 --stream           # Stream as JSONL (low memory)
  %(prog)s 1896830 --stream --schedule A  # Stream only Schedule A

Schedule codes:
  A  - Contributions (Schedule A)
  B  - Disbursements (Schedule B)
  C  - Loans (Schedule C)
  D  - Debts (Schedule D)
  E  - Independent Expenditures (Schedule E)

Streaming mode (--stream):
  Outputs JSONL (one JSON object per line) instead of a single JSON document.
  Each line has: {"data_type": "...", "data": {...}}
  Uses constant memory regardless of filing size.
""",
    )
    parser.add_argument(
        "filing_id",
        type=int,
        help="FEC filing ID (positive integer)",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only fetch filing summary (no itemizations)",
    )
    parser.add_argument(
        "--schedule",
        type=str,
        metavar="X",
        help="Only fetch a single schedule (e.g., A, B, C, D, E)",
    )
    parser.add_argument(
        "--schedules",
        type=str,
        metavar="X,Y",
        help="Only fetch multiple schedules (comma-separated, e.g., A,B)",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream output as JSONL (one JSON object per line, low memory usage)",
    )
    return parser.parse_args()


def build_options(args):
    """Build the fecfile options dict based on CLI arguments."""
    options = {}

    if args.summary_only:
        options["filter_itemizations"] = []
    elif args.schedule:
        # Single schedule: A -> SA, B -> SB, etc.
        schedule_code = f"S{args.schedule.upper()}"
        options["filter_itemizations"] = [schedule_code]
    elif args.schedules:
        # Multiple schedules: A,B -> ['SA', 'SB']
        codes = [f"S{s.strip().upper()}" for s in args.schedules.split(",")]
        options["filter_itemizations"] = codes

    return options


def stream_filing(filing_id, options):
    """Stream filing data as JSONL using iter_http."""
    for item in fecfile.iter_http(filing_id, options=options):
        record = {
            "data_type": item.data_type,
            "data": item.data,
        }
        print(json.dumps(record, default=str))


def fetch_filing(filing_id, options):
    """Fetch complete filing data using from_http."""
    filing_data = fecfile.from_http(filing_id, options=options)
    print(json.dumps(filing_data, indent=2, default=str))


def main():
    args = parse_args()

    if args.filing_id <= 0:
        print("Error: Filing ID must be a positive integer.", file=sys.stderr)
        sys.exit(1)

    # Check for conflicting options
    if args.summary_only and (args.schedule or args.schedules):
        print(
            "Error: --summary-only cannot be combined with --schedule or --schedules.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.schedule and args.schedules:
        print(
            "Error: Use either --schedule or --schedules, not both.", file=sys.stderr
        )
        sys.exit(1)

    if args.summary_only and args.stream:
        print(
            "Error: --summary-only cannot be combined with --stream.",
            file=sys.stderr,
        )
        sys.exit(1)

    options = build_options(args)

    try:
        if args.stream:
            stream_filing(args.filing_id, options)
        else:
            fetch_filing(args.filing_id, options)
    except Exception as e:
        print(f"Error fetching filing {args.filing_id}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
