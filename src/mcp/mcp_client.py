"""Python client for the official Census Bureau MCP server.

This client communicates with the Census Bureau's MCP server to access
enhanced Census data with metadata enrichment.
"""

import json
import subprocess
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from pydantic import BaseModel


class MCPToolCall(BaseModel):
    """MCP tool call request."""
    method: str = "tools/call"
    params: Dict[str, Any]


class MCPResponse(BaseModel):
    """MCP response structure."""
    content: List[Dict[str, Any]]
    isError: Optional[bool] = False


@dataclass
class DatasetInfo:
    """Information about a Census dataset."""
    identifier: str
    title: str
    description: Optional[str] = None
    vintage: Optional[int] = None
    geography_levels: Optional[List[str]] = None


class CensusMCPClient:
    """Client for interacting with the official Census Bureau MCP server.

    This client provides:
    - Communication with the Census MCP server via stdio
    - Access to enhanced metadata from the server's PostgreSQL database
    - Geography resolution with fuzzy matching
    - Structured data retrieval with proper typing
    """

    def __init__(
        self,
        mcp_server_path: str | Path,
        api_key: str,
        node_path: str = "node",
    ):
        """Initialize the MCP client.

        Args:
            mcp_server_path: Path to the us-census-bureau-data-api-mcp directory
            api_key: Census API key
            node_path: Path to node executable (default: "node")
        """
        self.mcp_server_path = Path(mcp_server_path)
        self.api_key = api_key
        self.node_path = node_path
        self._process: Optional[subprocess.Popen] = None

    def _start_server(self) -> subprocess.Popen:
        """Start the MCP server process."""
        server_script = self.mcp_server_path / "mcp-server" / "dist" / "index.js"

        if not server_script.exists():
            raise FileNotFoundError(
                f"MCP server not found at {server_script}. "
                f"Make sure to run 'npm run build' in the mcp-server directory."
            )

        env = {"CENSUS_API_KEY": self.api_key}

        process = subprocess.Popen(
            [self.node_path, str(server_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1,
        )

        return process

    def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool and get the response.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool response data
        """
        if not self._process:
            self._process = self._start_server()

        # Build JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        # Send request
        request_json = json.dumps(request) + "\n"
        self._process.stdin.write(request_json)
        self._process.stdin.flush()

        # Read response
        response_line = self._process.stdout.readline()
        response = json.loads(response_line)

        if "error" in response:
            raise RuntimeError(f"MCP error: {response['error']}")

        return response.get("result", {})

    def list_datasets(self) -> List[DatasetInfo]:
        """List all available Census datasets.

        Uses the MCP server's list-datasets tool which includes
        metadata from the server's database.

        Returns:
            List of DatasetInfo objects
        """
        result = self._call_tool("list-datasets", {})

        datasets = []
        for item in result.get("content", []):
            if item.get("type") == "text":
                # Parse the text response
                data = json.loads(item["text"])
                for ds in data:
                    datasets.append(DatasetInfo(
                        identifier=ds.get("identifier", ""),
                        title=ds.get("title", ""),
                        description=ds.get("description"),
                        vintage=ds.get("vintage"),
                        geography_levels=ds.get("geography_levels", []),
                    ))

        return datasets

    def resolve_geography_fips(
        self,
        geography_name: str,
        summary_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Resolve a geography name to FIPS codes.

        This uses the MCP server's fuzzy matching across all Census
        Bureau geographies.

        Args:
            geography_name: Name of the geography (e.g., "Philadelphia")
            summary_level: Optional summary level filter (e.g., "Place", "160")

        Returns:
            List of matching geographies with FIPS codes
        """
        arguments = {"geography_name": geography_name}
        if summary_level:
            arguments["summary_level"] = summary_level

        result = self._call_tool("resolve-geography-fips", arguments)

        matches = []
        for item in result.get("content", []):
            if item.get("type") == "text":
                data = json.loads(item["text"])
                matches.extend(data)

        return matches

    def fetch_dataset_geography(
        self,
        dataset: str,
        year: Optional[int] = None
    ) -> List[str]:
        """Fetch available geography levels for a dataset.

        Args:
            dataset: Dataset identifier (e.g., "acs/acs1")
            year: Optional dataset vintage

        Returns:
            List of available geography levels
        """
        arguments = {"dataset": dataset}
        if year:
            arguments["year"] = year

        result = self._call_tool("fetch-dataset-geography", arguments)

        geographies = []
        for item in result.get("content", []):
            if item.get("type") == "text":
                data = json.loads(item["text"])
                geographies.extend(data)

        return geographies

    def fetch_aggregate_data(
        self,
        dataset: str,
        year: int,
        variables: Optional[List[str]] = None,
        group: Optional[str] = None,
        geography_for: Optional[str] = None,
        geography_in: Optional[str] = None,
        ucgid: Optional[str] = None,
        predicates: Optional[Dict[str, str]] = None,
        descriptive: bool = False,
    ) -> List[List[str]]:
        """Fetch aggregate data from the Census API via MCP server.

        Args:
            dataset: Dataset identifier (e.g., "acs/acs5")
            year: Dataset vintage
            variables: List of variable codes (e.g., ["NAME", "B01001_001E"])
            group: Variable group code (alternative to variables)
            geography_for: Geography level (e.g., "state:06")
            geography_in: Parent geography (e.g., "state:06")
            ucgid: Uniform Census Geography Identifier
            predicates: Additional filter predicates
            descriptive: Include variable labels in response

        Returns:
            Census data as list of lists (first row is headers)
        """
        arguments: Dict[str, Any] = {
            "dataset": dataset,
            "year": year,
            "get": {},
        }

        if variables:
            arguments["get"]["variables"] = variables
        if group:
            arguments["get"]["group"] = group
        if geography_for:
            arguments["for"] = geography_for
        if geography_in:
            arguments["in"] = geography_in
        if ucgid:
            arguments["ucgid"] = ucgid
        if predicates:
            arguments["predicates"] = predicates
        if descriptive:
            arguments["descriptive"] = True

        result = self._call_tool("fetch-aggregate-data", arguments)

        data = []
        for item in result.get("content", []):
            if item.get("type") == "text":
                data = json.loads(item["text"])
                break

        return data

    def get_employment_data_2024(
        self,
        geography_name: str,
        dataset: str = "acs/acs1",
        year: int = 2024,
    ) -> Dict[str, Any]:
        """Fetch 2024 employment data for a geography.

        This is a convenience method that:
        1. Resolves the geography name to FIPS
        2. Fetches employment data from Table B23025
        3. Returns structured data

        Args:
            geography_name: State or place name
            dataset: ACS dataset (default: acs1 for 2024 data)
            year: Data year (default: 2024)

        Returns:
            Dictionary with employment data and metadata
        """
        # Resolve geography
        matches = self.resolve_geography_fips(geography_name)

        if not matches:
            raise ValueError(f"Could not resolve geography: {geography_name}")

        # Use first match
        geo_match = matches[0]
        fips_code = geo_match.get("fips")
        geo_name = geo_match.get("name", geography_name)

        # Fetch employment data (Table B23025)
        variables = [
            "NAME",
            "B23025_001E",  # Total 16+
            "B23025_002E",  # In labor force
            "B23025_004E",  # Employed
            "B23025_005E",  # Unemployed
            "B23025_007E",  # Not in labor force
        ]

        data = self.fetch_aggregate_data(
            dataset=dataset,
            year=year,
            variables=variables,
            geography_for=f"state:{fips_code}",
        )

        if len(data) < 2:
            raise ValueError(f"No data returned for {geography_name}")

        # Parse response
        headers = data[0]
        values = data[1]

        def get_value(var: str) -> Optional[int]:
            try:
                idx = headers.index(var)
                return int(values[idx]) if values[idx] else None
            except (ValueError, IndexError):
                return None

        total = get_value("B23025_001E") or 0
        labor_force = get_value("B23025_002E") or 0
        employed = get_value("B23025_004E") or 0
        unemployed = get_value("B23025_005E") or 0
        not_in_lf = get_value("B23025_007E") or 0

        # Calculate rates
        unemployment_rate = (unemployed / labor_force * 100) if labor_force > 0 else None
        lfpr = (labor_force / total * 100) if total > 0 else None
        emp_pop_ratio = (employed / total * 100) if total > 0 else None

        return {
            "geography_name": geo_name,
            "fips_code": fips_code,
            "year": year,
            "dataset": dataset,
            "total_population_16_plus": total,
            "labor_force": labor_force,
            "employed": employed,
            "unemployed": unemployed,
            "not_in_labor_force": not_in_lf,
            "unemployment_rate": unemployment_rate,
            "labor_force_participation_rate": lfpr,
            "employment_population_ratio": emp_pop_ratio,
            "raw_data": data,
        }

    def close(self):
        """Close the MCP server process."""
        if self._process:
            self._process.terminate()
            self._process.wait(timeout=5)
            self._process = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
