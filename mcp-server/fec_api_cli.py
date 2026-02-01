#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "requests>=2.28.0",
#     "keyring>=24.0.0",
# ]
# ///
"""
FEC API CLI client with secure credential handling.

This is a standalone CLI for agent runtimes that don't support MCP (like Codex).
The API key is retrieved from the system keyring on each invocation.

For Claude Code users, prefer the MCP server which loads the key once at startup
and keeps it hidden from the conversation.

Usage:
    uv run fec_api_cli.py search-committees "Utah Republican Party"
    uv run fec_api_cli.py get-filings C00089482 --limit 5

Get an API key at: https://api.open.fec.gov/developers/
"""

import argparse
import json
import re
import sys
from typing import Optional

import keyring
import requests


def sanitize_api_key(text: str) -> str:
    """Remove API key from text to prevent accidental exposure in logs/errors."""
    return re.sub(r"api_key=[^&\s]+", "api_key=REDACTED", text)


FEC_API_BASE = "https://api.open.fec.gov/v1"
KEYRING_SERVICE = "fec-api"
KEYRING_USERNAME = "api-key"


class CredentialError(Exception):
    """Raised when credentials cannot be retrieved."""

    pass


def get_api_key_from_keyring(
    service: str = KEYRING_SERVICE, username: str = KEYRING_USERNAME
) -> str:
    """
    Retrieve the FEC API key from the system keyring.

    Uses the `keyring` library which provides cross-platform access to:
    - macOS Keychain
    - Windows Credential Manager
    - Linux Secret Service (GNOME Keyring, KWallet)
    - Encrypted file fallback

    The user may be prompted to unlock the keyring if it's locked.

    Args:
        service: Keyring service name (default: "fec-api")
        username: Keyring username/account (default: "api-key")

    Returns:
        The API key string

    Raises:
        CredentialError: If the key cannot be retrieved
    """
    try:
        api_key = keyring.get_password(service, username)

        if api_key is None:
            raise CredentialError(
                f"FEC API key not found in system keyring.\n"
                f"Attempted at Service: {service}, Username: {username}"
            )

        if not api_key:
            raise CredentialError("Retrieved empty FEC API key from keyring")

        return api_key

    except keyring.errors.KeyringError as e:
        raise CredentialError(f"Keyring access failed: {e}")
    except keyring.errors.InitError as e:
        raise CredentialError(f"Failed to initialize keyring backend: {e}")


def get_api_key() -> str:
    """
    Get the FEC API key from the system keyring.

    Returns:
        The API key string

    Raises:
        CredentialError: If credentials cannot be retrieved
    """
    return get_api_key_from_keyring()


def search_committees(
    query: str,
    api_key: str,
    limit: int = 20,
) -> list[dict]:
    """
    Search for FEC committees by name using the typeahead endpoint.

    Args:
        query: Search term (committee name or partial name)
        api_key: FEC API key
        limit: Maximum number of results (default: 20)

    Returns:
        List of committee records from /v1/names/committees/

    Raises:
        requests.RequestException: On API errors
    """
    params = {
        "api_key": api_key,
        "q": query,
    }

    response = requests.get(
        f"{FEC_API_BASE}/names/committees/",
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])
    return results[:limit]


def get_filings(
    committee_id: str,
    api_key: str,
    limit: int = 10,
    form_type: Optional[str] = None,
    most_recent: bool = True,
    cycle: Optional[int] = None,
    report_type: Optional[str] = None,
    sort: str = "-receipt_date",
) -> list[dict]:
    """
    Get filings for a committee.

    Args:
        committee_id: FEC committee ID (e.g., "C00089482")
        api_key: FEC API key
        limit: Maximum number of results (default: 10)
        form_type: Filter by form type (e.g., "F3P", "F3X", "F3")
        most_recent: Only return current versions, not superseded amendments (default: True)
        cycle: Filter by two-year election cycle (e.g., 2024)
        report_type: Filter by report type (e.g., "Q1", "Q2", "MY", "YE", "12G", "30G")
        sort: Sort field with optional "-" prefix for descending (default: "-receipt_date").
              Valid fields: receipt_date, coverage_start_date, coverage_end_date,
                  total_receipts, total_disbursements, report_year, cycle

    Returns:
        List of filing records

    Raises:
        requests.RequestException: On API errors
    """
    params = {
        "api_key": api_key,
        "per_page": min(limit, 100),
        "sort": sort,
        "most_recent": most_recent,
    }

    if form_type:
        params["form_type"] = form_type
    if cycle:
        params["cycle"] = cycle
    if report_type:
        params["report_type"] = report_type

    response = requests.get(
        f"{FEC_API_BASE}/committee/{committee_id}/filings/",
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    return data.get("results", [])


def main():
    parser = argparse.ArgumentParser(
        description="Query the FEC API with secure credential handling.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Setup:
  See README.md for secure API key storage instructions.
  Get an API key at: https://api.open.fec.gov/developers/

macOS quick setup:
  security add-generic-password -s "fec-api" -a "api-key" -w"
""",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # search-committees subcommand
    search_parser = subparsers.add_parser(
        "search-committees",
        help="Search for committees by name",
    )
    search_parser.add_argument(
        "query",
        type=str,
        help="Committee name or search term",
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum results to return (default: 20)",
    )

    # get-filings subcommand
    filings_parser = subparsers.add_parser(
        "get-filings",
        help="Get filings for a committee",
    )
    filings_parser.add_argument(
        "committee_id",
        type=str,
        help="FEC committee ID (e.g., C00089482)",
    )
    filings_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum results to return (default: 10)",
    )
    filings_parser.add_argument(
        "--form-type",
        type=str,
        metavar="TYPE",
        help="Filter by form type (e.g., F3P, F3X, F3)",
    )
    filings_parser.add_argument(
        "--cycle",
        type=int,
        metavar="YEAR",
        help="Filter by two-year election cycle (e.g., 2024)",
    )
    filings_parser.add_argument(
        "--report-type",
        type=str,
        metavar="TYPE",
        help="Filter by report type (e.g., Q1, Q2, MY, YE, 12G, 30G)",
    )
    filings_parser.add_argument(
        "--sort",
        type=str,
        default="-receipt_date",
        metavar="FIELD",
        help="Sort field, use '-' prefix for descending (default: -receipt_date)",
    )
    filings_parser.add_argument(
        "--include-amended",
        action="store_true",
        help="Include superseded amendments (default: only most recent versions)",
    )

    args = parser.parse_args()

    try:
        api_key = get_api_key()
    except CredentialError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.command == "search-committees":
            results = search_committees(args.query, api_key, args.limit)

            if not results:
                print(f"No committees found matching '{args.query}'", file=sys.stderr)
                sys.exit(0)

            print(json.dumps(results, indent=2))

        elif args.command == "get-filings":
            results = get_filings(
                args.committee_id,
                api_key,
                limit=args.limit,
                form_type=args.form_type,
                most_recent=not args.include_amended,
                cycle=args.cycle,
                report_type=args.report_type,
                sort=args.sort,
            )

            if not results:
                print(
                    f"No filings found for committee '{args.committee_id}'",
                    file=sys.stderr,
                )
                sys.exit(0)

            # Output key fields for each filing
            output = []
            for r in results:
                output.append(
                    {
                        "filing_id": r.get("file_number"),
                        "form_type": r.get("form_type"),
                        "receipt_date": r.get("receipt_date"),
                        "coverage_start_date": r.get("coverage_start_date"),
                        "coverage_end_date": r.get("coverage_end_date"),
                        "total_receipts": r.get("total_receipts"),
                        "total_disbursements": r.get("total_disbursements"),
                        "amendment_indicator": r.get("amendment_indicator"),
                    }
                )
            print(json.dumps(output, indent=2))

    except requests.RequestException as e:
        print(f"API error: {sanitize_api_key(str(e))}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
