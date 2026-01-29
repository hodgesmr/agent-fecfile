#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "requests>=2.28.0",
#     "keyring>=24.0.0",
# ]
# ///
"""
FEC API client with secure credential handling.

This module uses the authenticated FEC API at api.open.fec.gov.
API keys are retrieved securely via the system keyring (cross-platform).

Supported backends:
    - macOS: Keychain
    - Windows: Credential Manager
    - Linux: Secret Service (GNOME Keyring, KWallet) or encrypted file

Setup:
    # Store your FEC API key (interactive prompt):
    python -c "import keyring; keyring.set_password('fec-api', 'api-key', input('API Key: '))"

    # Or via CLI (if keyring CLI is installed):
    keyring set fec-api api-key

Usage:
    uv run fec_api.py search-committees "Harris"
    uv run fec_api.py get-filings C00703975 --limit 5

Get an API key at: https://api.open.fec.gov/developers/
"""

import argparse
import json
import subprocess
import sys
from typing import Optional

import keyring
import requests

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
                f"Add it with:\n"
                f"  python -c \"import keyring; keyring.set_password('{service}', '{username}', input('API Key: '))\"\n"
                f"Or:\n"
                f"  keyring set {service} {username}"
            )

        if not api_key:
            raise CredentialError("Retrieved empty API key from keyring")

        return api_key

    except keyring.errors.KeyringError as e:
        raise CredentialError(f"Keyring access failed: {e}")
    except keyring.errors.InitError as e:
        raise CredentialError(
            f"Failed to initialize keyring backend: {e}\n"
            "On Linux, ensure a Secret Service provider is running "
            "(e.g., gnome-keyring-daemon or kwallet)."
        )


def get_api_key(credential_cmd: Optional[str] = None) -> str:
    """
    Get the FEC API key using the credential helper pattern.

    Resolution order:
    1. Custom credential command (if provided)
    2. System keyring (default)

    Args:
        credential_cmd: Optional shell command that outputs the API key

    Returns:
        The API key string

    Raises:
        CredentialError: If credentials cannot be retrieved
    """
    if credential_cmd:
        try:
            result = subprocess.run(
                credential_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                raise CredentialError(
                    f"Credential command failed: {result.stderr.strip()}"
                )
            api_key = result.stdout.strip()
            if not api_key:
                raise CredentialError("Credential command returned empty output")
            return api_key
        except subprocess.TimeoutExpired:
            raise CredentialError("Credential command timed out")

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
) -> list[dict]:
    """
    Get filings for a committee.

    Args:
        committee_id: FEC committee ID (e.g., "C00703975")
        api_key: FEC API key
        limit: Maximum number of results (default: 10)
        form_type: Filter by form type (e.g., "F3P", "F3X", "F3")

    Returns:
        List of filing records, sorted by most recent first

    Raises:
        requests.RequestException: On API errors
    """
    params = {
        "api_key": api_key,
        "per_page": min(limit, 100),
        "sort": "-receipt_date",
    }

    if form_type:
        params["form_type"] = form_type

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
Setup (cross-platform):
  python -c "import keyring; keyring.set_password('fec-api', 'api-key', input('API Key: '))"

Or with keyring CLI:
  keyring set fec-api api-key

Get an API key at: https://api.open.fec.gov/developers/
""",
    )

    parser.add_argument(
        "--credential-cmd",
        type=str,
        metavar="CMD",
        help="Shell command to retrieve API key (default: system keyring)",
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
        help="FEC committee ID (e.g., C00703975)",
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

    args = parser.parse_args()

    try:
        api_key = get_api_key(args.credential_cmd)
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
                args.limit,
                args.form_type,
            )

            if not results:
                print(f"No filings found for committee '{args.committee_id}'", file=sys.stderr)
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
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
