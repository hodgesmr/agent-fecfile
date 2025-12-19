#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "fecfile>=0.6.0",
# ]
# ///
"""
Fetch and display FEC filing data.

Usage:
    uv run fetch_filing.py <filing_id>

Example:
    uv run fetch_filing.py 1896830

Dependencies are automatically installed by uv.
"""

import sys
import json
import fecfile


def fetch_filing(filing_id: int) -> dict:
    """Fetch an FEC filing by ID."""
    return fecfile.from_http(filing_id)


def main():
    if len(sys.argv) != 2:
        print("Usage: python fetch_filing.py <filing_id>", file=sys.stderr)
        print("Example: python fetch_filing.py 1896830", file=sys.stderr)
        sys.exit(1)

    try:
        filing_id = int(sys.argv[1])
        if filing_id <= 0:
            raise ValueError("Filing ID must be a positive number")
    except ValueError as e:
        print(f"Error: Invalid filing ID '{sys.argv[1]}'. Must be a positive integer.", file=sys.stderr)
        sys.exit(1)

    try:
        filing_data = fetch_filing(filing_id)
        print(json.dumps(filing_data, indent=2, default=str))
    except Exception as e:
        print(f"Error fetching filing {filing_id}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
