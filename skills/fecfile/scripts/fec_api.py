#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "requests>=2.28.0",
# ]
# ///
"""
FEC API client with secure credential handling.

This module uses the authenticated FEC API at api.open.fec.gov.
API keys are retrieved securely via credential helper (macOS Keychain by default).

Setup (macOS):
    # Store your FEC API key in the Keychain:
    security add-generic-password -s "fec-api" -a "api-key" -w "YOUR_API_KEY_HERE"

    # To update an existing key:
    security add-generic-password -U -s "fec-api" -a "api-key" -w "NEW_API_KEY"

Usage:
    uv run fec_api.py search-committees "Biden"
    uv run fec_api.py search-committees "ActBlue" --limit 5

Get an API key at: https://api.data.gov/signup/
"""

import argparse
import json
import subprocess
import sys
from typing import Optional

import requests

FEC_API_BASE = "https://api.open.fec.gov/v1"
KEYCHAIN_SERVICE = "fec-api"
KEYCHAIN_ACCOUNT = "api-key"


class CredentialError(Exception):
    """Raised when credentials cannot be retrieved."""

    pass


def get_api_key_from_keychain(
    service: str = KEYCHAIN_SERVICE, account: str = KEYCHAIN_ACCOUNT
) -> str:
    """
    Retrieve the FEC API key from macOS Keychain.

    This uses the macOS `security` command to access the Keychain.
    The user may be prompted to allow access if the keychain item
    requires authorization.

    Args:
        service: Keychain service name (default: "fec-api")
        account: Keychain account name (default: "api-key")

    Returns:
        The API key string

    Raises:
        CredentialError: If the key cannot be retrieved
    """
    try:
        result = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-s",
                service,
                "-a",
                account,
                "-w",  # Output only the password
            ],
            capture_output=True,
            text=True,
            timeout=30,  # Allow time for user interaction
        )

        if result.returncode != 0:
            stderr = result.stderr.strip()
            if "could not be found" in stderr or "SecKeychainSearchCopyNext" in stderr:
                raise CredentialError(
                    f"FEC API key not found in Keychain.\n"
                    f"Add it with:\n"
                    f'  security add-generic-password -s "{service}" -a "{account}" -w "YOUR_API_KEY"'
                )
            raise CredentialError(f"Keychain access failed: {stderr}")

        api_key = result.stdout.strip()
        if not api_key:
            raise CredentialError("Retrieved empty API key from Keychain")

        return api_key

    except subprocess.TimeoutExpired:
        raise CredentialError("Keychain access timed out (user interaction required?)")
    except FileNotFoundError:
        raise CredentialError(
            "macOS 'security' command not found. "
            "This credential helper only works on macOS."
        )


def get_api_key(credential_cmd: Optional[str] = None) -> str:
    """
    Get the FEC API key using the credential helper pattern.

    Resolution order:
    1. Custom credential command (if provided)
    2. macOS Keychain (default)

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

    return get_api_key_from_keychain()


def search_committees(
    query: str,
    api_key: str,
    limit: int = 20,
) -> list[dict]:
    """
    Search for FEC committees by name.

    Args:
        query: Search term (committee name or partial name)
        api_key: FEC API key
        limit: Maximum number of results (default: 20, max: 100)

    Returns:
        List of committee records, each containing:
        - committee_id: The FEC committee ID (e.g., "C00401224")
        - name: Committee name
        - treasurer_name: Name of the treasurer
        - committee_type: Type code (e.g., "P" for Presidential)
        - committee_type_full: Full type description
        - designation: Designation code
        - designation_full: Full designation description
        - party: Party affiliation code
        - party_full: Full party name
        - state: State code
        - cycles: List of election cycles

    Raises:
        requests.RequestException: On API errors
    """
    params = {
        "api_key": api_key,
        "q": query,
        "per_page": min(limit, 100),
        "sort": "-last_file_date",
    }

    response = requests.get(
        f"{FEC_API_BASE}/committees/",
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
Setup (macOS Keychain):
  security add-generic-password -s "fec-api" -a "api-key" -w "YOUR_API_KEY"

Get an API key at: https://api.data.gov/signup/
""",
    )

    parser.add_argument(
        "--credential-cmd",
        type=str,
        metavar="CMD",
        help="Shell command to retrieve API key (default: macOS Keychain)",
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

            # Output simplified view for CLI, full JSON available via module import
            output = []
            for r in results:
                output.append(
                    {
                        "committee_id": r.get("committee_id"),
                        "name": r.get("name"),
                        "committee_type_full": r.get("committee_type_full"),
                        "designation_full": r.get("designation_full"),
                        "party_full": r.get("party_full"),
                        "state": r.get("state"),
                        "treasurer_name": r.get("treasurer_name"),
                    }
                )
            print(json.dumps(output, indent=2))

    except requests.RequestException as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
