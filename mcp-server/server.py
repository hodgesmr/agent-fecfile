#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "mcp>=1.0.0",
#     "requests>=2.28.0",
#     "keyring>=24.0.0",
# ]
# ///
"""
FEC API MCP Server

An MCP server that provides secure access to the FEC API. The API key is loaded
from the system keyring at startup and held in memory, preventing the LLM from
ever seeing or accessing the credential.

Tools:
    - search_committees: Search for FEC committees by name
    - get_filings: Get filings for a specific committee

The server uses stdio transport for communication with Claude Code.
"""

import json
import re
import sys
from typing import Optional

import keyring
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Constants
FEC_API_BASE = "https://api.open.fec.gov/v1"
KEYRING_SERVICE = "fec-api"
KEYRING_USERNAME = "api-key"


def sanitize_api_key(text: str) -> str:
    """Remove API key from text to prevent accidental exposure."""
    return re.sub(r"api_key=[^&\s]+", "api_key=REDACTED", text)


class FECAPIServer:
    """MCP server for FEC API access with secure credential handling."""

    def __init__(self):
        self.server = Server("fec-api")
        self.api_key: Optional[str] = None
        self._setup_handlers()

    def _load_api_key(self) -> Optional[str]:
        """
        Load the FEC API key from the system keyring.

        Returns None if the key is not found or cannot be retrieved,
        allowing the server to start without a key (for public-only access).
        """
        try:
            api_key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
            if api_key:
                return api_key
        except Exception:
            pass
        return None

    def _setup_handlers(self):
        """Configure MCP server handlers."""

        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="search_committees",
                    description=(
                        "Search for FEC committees by name. Returns committee IDs "
                        "that can be used with get_filings. Requires FEC API key "
                        "to be configured in system keyring."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Committee name or partial name to search for",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 20)",
                                "default": 20,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="get_filings",
                    description=(
                        "Get FEC filings for a committee. Returns filing IDs, dates, "
                        "and financial summaries. Use search_committees first to find "
                        "the committee ID. Requires FEC API key to be configured."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "committee_id": {
                                "type": "string",
                                "description": "FEC committee ID (e.g., C00089482)",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10,
                            },
                            "form_type": {
                                "type": "string",
                                "description": "Filter by form type (F3, F3P, F3X)",
                            },
                            "cycle": {
                                "type": "integer",
                                "description": "Filter by two-year election cycle (e.g., 2024)",
                            },
                            "report_type": {
                                "type": "string",
                                "description": "Filter by report type (Q1, Q2, Q3, YE, MY, 12G, 30G)",
                            },
                            "sort": {
                                "type": "string",
                                "description": "Sort field with optional '-' prefix for descending (default: -receipt_date)",
                                "default": "-receipt_date",
                            },
                            "include_amended": {
                                "type": "boolean",
                                "description": "Include superseded amendments (default: false)",
                                "default": False,
                            },
                        },
                        "required": ["committee_id"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "search_committees":
                return await self._search_committees(arguments)
            elif name == "get_filings":
                return await self._get_filings(arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async def _search_committees(self, arguments: dict):
        """Search for committees by name."""
        if not self.api_key:
            return [
                TextContent(
                    type="text",
                    text=(
                        "FEC API key not configured. Please add your API key to the "
                        "system keyring with service 'fec-api' and username 'api-key'. "
                        "See README for setup instructions."
                    ),
                )
            ]

        query = arguments.get("query", "")
        limit = arguments.get("limit", 20)

        try:
            params = {
                "api_key": self.api_key,
                "q": query,
            }

            response = requests.get(
                f"{FEC_API_BASE}/names/committees/",
                params=params,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])[:limit]

            if not results:
                return [
                    TextContent(
                        type="text",
                        text=f"No committees found matching '{query}'",
                    )
                ]

            return [
                TextContent(
                    type="text",
                    text=json.dumps(results, indent=2),
                )
            ]

        except requests.RequestException as e:
            return [
                TextContent(
                    type="text",
                    text=f"API error: {sanitize_api_key(str(e))}",
                )
            ]

    async def _get_filings(self, arguments: dict):
        """Get filings for a committee."""
        if not self.api_key:
            return [
                TextContent(
                    type="text",
                    text=(
                        "FEC API key not configured. Please add your API key to the "
                        "system keyring with service 'fec-api' and username 'api-key'. "
                        "See README for setup instructions."
                    ),
                )
            ]

        committee_id = arguments.get("committee_id", "")
        limit = arguments.get("limit", 10)
        form_type = arguments.get("form_type")
        cycle = arguments.get("cycle")
        report_type = arguments.get("report_type")
        sort = arguments.get("sort", "-receipt_date")
        include_amended = arguments.get("include_amended", False)

        try:
            params = {
                "api_key": self.api_key,
                "per_page": min(limit, 100),
                "sort": sort,
                "most_recent": not include_amended,
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
            results = data.get("results", [])

            if not results:
                return [
                    TextContent(
                        type="text",
                        text=f"No filings found for committee '{committee_id}'",
                    )
                ]

            # Extract key fields for each filing
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

            return [
                TextContent(
                    type="text",
                    text=json.dumps(output, indent=2),
                )
            ]

        except requests.RequestException as e:
            return [
                TextContent(
                    type="text",
                    text=f"API error: {sanitize_api_key(str(e))}",
                )
            ]

    async def run(self):
        """Start the MCP server."""
        # Load API key at startup - only once
        self.api_key = self._load_api_key()

        if self.api_key:
            print("FEC API key loaded from keyring", file=sys.stderr)
        else:
            print(
                "Warning: FEC API key not found in keyring. "
                "Committee search and filing lookup will be unavailable.",
                file=sys.stderr,
            )

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main():
    server = FECAPIServer()
    await server.run()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
