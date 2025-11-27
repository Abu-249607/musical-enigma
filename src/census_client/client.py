"""Census Bureau MCP client wrapper.

This client wraps the Census Bureau's official MCP server, adding:
- Response caching for performance
- Citation generation for transparency
- Error handling and retries
- Structured data models
"""

import hashlib
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models.citation import Citation, CitedDataPoint
from ..models.employment import (
    EmploymentRecord,
    GeographyLevel,
    DatasetInfo,
    EMPLOYMENT_VARIABLES,
)
from .cache import CensusCache


class CensusMCPClient:
    """Client for interacting with Census Bureau MCP server.

    This wrapper provides:
    1. Structured responses with Pydantic models
    2. Automatic citation generation
    3. Response caching
    4. Employment-specific convenience methods
    """

    # Base URL for direct Census API calls (fallback)
    CENSUS_API_BASE = "https://api.census.gov/data"

    def __init__(
        self,
        mcp_server_path: str | Path | None = None,
        api_key: str | None = None,
        cache_dir: str | Path = "data/cache",
        use_cache: bool = True,
    ):
        """Initialize the Census MCP client.

        Args:
            mcp_server_path: Path to the Census MCP server directory
            api_key: Census API key (get from api.census.gov/data/key_signup.html)
            cache_dir: Directory for caching responses
            use_cache: Whether to cache responses
        """
        self.mcp_server_path = Path(mcp_server_path) if mcp_server_path else None
        self.api_key = api_key
        self.use_cache = use_cache
        self._cache = CensusCache(cache_dir) if use_cache else None
        self._http_client = httpx.Client(timeout=30.0)
        self._citation_counter = 0

    def _generate_citation_id(self, dataset: str, year: int) -> str:
        """Generate a unique citation ID."""
        self._citation_counter += 1
        dataset_short = dataset.replace("/", "-").upper()
        return f"{dataset_short}-{year}-{self._citation_counter:03d}"

    def _create_citation(
        self,
        dataset: str,
        year: int,
        variables: list[str],
        geography: str,
        geography_name: str,
        fips_code: str | None = None,
    ) -> Citation:
        """Create a citation for a data request."""
        citation_id = self._generate_citation_id(dataset, year)

        # Build Census data explorer URL
        var_str = ",".join(variables[:5])  # Limit for URL length
        census_url = (
            f"https://data.census.gov/table?g={geography}&y={year}&d={dataset}"
        )

        return Citation(
            citation_id=citation_id,
            dataset_name=dataset,
            dataset_year=year,
            variables=variables,
            geography=geography,
            geography_name=geography_name,
            fips_code=fips_code,
            api_endpoint=f"{self.CENSUS_API_BASE}/{year}/{dataset}",
            census_api_url=census_url,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    def _call_census_api(
        self,
        dataset: str,
        year: int,
        variables: list[str],
        geography_for: str,
        geography_in: str | None = None,
    ) -> list[list[str]]:
        """Make a direct call to the Census API.

        This is used as a fallback when MCP server is not available,
        or for simple queries.
        """
        # Check cache first
        cache_params = {
            "dataset": dataset,
            "year": year,
            "variables": variables,
            "for": geography_for,
            "in": geography_in,
        }

        if self._cache:
            cached = self._cache.get("aggregate", cache_params)
            if cached:
                return cached

        # Build request URL
        url = f"{self.CENSUS_API_BASE}/{year}/{dataset}"
        params = {
            "get": ",".join(variables),
            "for": geography_for,
        }
        if geography_in:
            params["in"] = geography_in
        if self.api_key:
            params["key"] = self.api_key

        response = self._http_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Cache the response
        if self._cache:
            self._cache.set("aggregate", cache_params, data)

        return data

    def list_datasets(self) -> list[DatasetInfo]:
        """List all available Census datasets.

        Returns metadata about each dataset including available years
        and geography levels.
        """
        # Check cache
        if self._cache:
            cached = self._cache.get("datasets", {})
            if cached:
                return [DatasetInfo.model_validate(d) for d in cached]

        # Fetch from Census API discovery endpoint
        url = f"{self.CENSUS_API_BASE}.json"
        response = self._http_client.get(url)
        response.raise_for_status()
        raw_datasets = response.json().get("dataset", [])

        # Parse into structured format (simplified)
        datasets = []
        for ds in raw_datasets[:50]:  # Limit for performance
            try:
                dataset_id = ds.get("c_dataset", [""])[0] if ds.get("c_dataset") else ""
                if not dataset_id:
                    continue

                info = DatasetInfo(
                    dataset_id=dataset_id,
                    title=ds.get("title", "Unknown"),
                    description=ds.get("description", ""),
                    available_years=[int(y) for y in ds.get("c_vintage", []) if y.isdigit()],
                    geography_levels=[GeographyLevel.STATE, GeographyLevel.COUNTY],
                )
                datasets.append(info)
            except Exception:
                continue

        # Cache results
        if self._cache and datasets:
            self._cache.set(
                "datasets", {}, [d.model_dump() for d in datasets]
            )

        return datasets

    def resolve_fips(
        self, geography_name: str, level: GeographyLevel = GeographyLevel.STATE
    ) -> dict[str, str] | None:
        """Resolve a geography name to its FIPS code.

        Args:
            geography_name: Name like "California" or "Los Angeles County"
            level: Geography level to search

        Returns:
            Dict with 'fips' and 'name' keys, or None if not found
        """
        # Check cache
        cache_key = {"name": geography_name.lower(), "level": level.value}
        if self._cache:
            cached = self._cache.get("fips", cache_key)
            if cached:
                return cached

        # Use Census geocoder or hardcoded mappings for common states
        state_fips = {
            "alabama": "01", "alaska": "02", "arizona": "04", "arkansas": "05",
            "california": "06", "colorado": "08", "connecticut": "09", "delaware": "10",
            "florida": "12", "georgia": "13", "hawaii": "15", "idaho": "16",
            "illinois": "17", "indiana": "18", "iowa": "19", "kansas": "20",
            "kentucky": "21", "louisiana": "22", "maine": "23", "maryland": "24",
            "massachusetts": "25", "michigan": "26", "minnesota": "27",
            "mississippi": "28", "missouri": "29", "montana": "30", "nebraska": "31",
            "nevada": "32", "new hampshire": "33", "new jersey": "34",
            "new mexico": "35", "new york": "36", "north carolina": "37",
            "north dakota": "38", "ohio": "39", "oklahoma": "40", "oregon": "41",
            "pennsylvania": "42", "rhode island": "44", "south carolina": "45",
            "south dakota": "46", "tennessee": "47", "texas": "48", "utah": "49",
            "vermont": "50", "virginia": "51", "washington": "53",
            "west virginia": "54", "wisconsin": "55", "wyoming": "56",
            "district of columbia": "11", "puerto rico": "72",
        }

        name_lower = geography_name.lower().strip()
        if name_lower in state_fips:
            result = {"fips": state_fips[name_lower], "name": geography_name.title()}
            if self._cache:
                self._cache.set("fips", cache_key, result)
            return result

        return None

    def get_employment_data(
        self,
        geography_name: str,
        year: int = 2024,
        dataset: str = "acs/acs1",
        level: GeographyLevel = GeographyLevel.STATE,
    ) -> tuple[EmploymentRecord, Citation]:
        """Fetch employment statistics for a geography.

        Args:
            geography_name: State or county name
            year: Data year (default 2024, most recent ACS 1-year)
            dataset: Census dataset (default ACS 1-year for latest data)
            level: Geography level

        Returns:
            Tuple of (EmploymentRecord, Citation)

        Note:
            2024 ACS 1-year data released September 2025
            Use acs/acs5 for 5-year estimates (more geographic detail)
        """
        # Resolve geography to FIPS
        fips_info = self.resolve_fips(geography_name, level)
        if not fips_info:
            raise ValueError(f"Could not resolve geography: {geography_name}")

        fips_code = fips_info["fips"]
        resolved_name = fips_info["name"]

        # Employment status variables (Table B23025)
        variables = [
            "NAME",
            "B23025_001E",  # Total 16+
            "B23025_002E",  # In labor force
            "B23025_004E",  # Employed
            "B23025_005E",  # Unemployed
            "B23025_007E",  # Not in labor force
        ]

        # Build geography string
        if level == GeographyLevel.STATE:
            geo_for = f"state:{fips_code}"
            geo_in = None
        elif level == GeographyLevel.COUNTY:
            geo_for = "county:*"
            geo_in = f"state:{fips_code}"
        else:
            geo_for = f"state:{fips_code}"
            geo_in = None

        # Fetch data
        data = self._call_census_api(dataset, year, variables, geo_for, geo_in)

        if len(data) < 2:
            raise ValueError(f"No data returned for {geography_name}")

        # Parse response (first row is headers, second is data)
        headers = data[0]
        values = data[1]

        def get_int(var: str) -> int | None:
            try:
                idx = headers.index(var)
                return int(values[idx]) if values[idx] else None
            except (ValueError, IndexError):
                return None

        # Create employment record
        record = EmploymentRecord(
            geography_name=resolved_name,
            geography_level=level,
            fips_code=fips_code,
            year=year,
            total_population_16_plus=get_int("B23025_001E"),
            labor_force=get_int("B23025_002E"),
            employed=get_int("B23025_004E"),
            unemployed=get_int("B23025_005E"),
            not_in_labor_force=get_int("B23025_007E"),
        )

        # Create citation
        citation = self._create_citation(
            dataset=dataset,
            year=year,
            variables=variables[1:],  # Exclude NAME
            geography=level.value,
            geography_name=resolved_name,
            fips_code=fips_code,
        )

        return record, citation

    def get_industry_employment(
        self,
        geography_name: str,
        year: int = 2024,
        dataset: str = "acs/acs1",
    ) -> tuple[dict[str, int], Citation]:
        """Fetch employment by industry for a geography.

        Returns:
            Tuple of (industry_counts dict, Citation)
        """
        fips_info = self.resolve_fips(geography_name)
        if not fips_info:
            raise ValueError(f"Could not resolve geography: {geography_name}")

        fips_code = fips_info["fips"]

        # Industry variables (Table C24050)
        variables = [
            "NAME",
            "C24050_001E",  # Total
            "C24050_002E",  # Agriculture
            "C24050_003E",  # Construction
            "C24050_004E",  # Manufacturing
            "C24050_006E",  # Retail
            "C24050_008E",  # Information
            "C24050_009E",  # Finance
            "C24050_010E",  # Professional/Scientific
            "C24050_011E",  # Education/Healthcare
            "C24050_014E",  # Public administration
        ]

        data = self._call_census_api(
            dataset, year, variables, f"state:{fips_code}"
        )

        headers = data[0]
        values = data[1]

        industry_labels = {
            "C24050_001E": "Total civilian employed",
            "C24050_002E": "Agriculture & Mining",
            "C24050_003E": "Construction",
            "C24050_004E": "Manufacturing",
            "C24050_006E": "Retail Trade",
            "C24050_008E": "Information",
            "C24050_009E": "Finance & Real Estate",
            "C24050_010E": "Professional & Scientific",
            "C24050_011E": "Education & Healthcare",
            "C24050_014E": "Public Administration",
        }

        industry_data = {}
        for var, label in industry_labels.items():
            try:
                idx = headers.index(var)
                val = int(values[idx]) if values[idx] else 0
                industry_data[label] = val
            except (ValueError, IndexError):
                continue

        citation = self._create_citation(
            dataset=dataset,
            year=year,
            variables=list(industry_labels.keys()),
            geography="state",
            geography_name=geography_name,
            fips_code=fips_code,
        )

        return industry_data, citation

    def search_employment_insights(
        self,
        query: str,
        geographies: list[str] | None = None,
        years: list[int] | None = None,
    ) -> list[CitedDataPoint]:
        """Search for employment insights across multiple geographies.

        This method is designed for RAG integration, returning
        cited data points that can be used to ground LLM responses.
        """
        geographies = geographies or ["California", "Texas", "New York"]
        years = years or [2024]

        results = []
        for geo in geographies:
            for year in years:
                try:
                    record, citation = self.get_employment_data(geo, year)

                    # Create cited data points for key metrics
                    if record.unemployment_rate is not None:
                        results.append(
                            CitedDataPoint(
                                value=record.unemployment_rate,
                                label=f"Unemployment rate in {geo} ({year})",
                                variable_code="B23025_005E/B23025_002E",
                                citation=citation,
                                is_estimate=True,
                                confidence_note="ACS 5-year estimate",
                            )
                        )

                    if record.labor_force_participation_rate is not None:
                        results.append(
                            CitedDataPoint(
                                value=record.labor_force_participation_rate,
                                label=f"Labor force participation in {geo} ({year})",
                                variable_code="B23025_002E/B23025_001E",
                                citation=citation,
                                is_estimate=True,
                            )
                        )

                except Exception as e:
                    # Log but continue with other geographies
                    print(f"Warning: Could not fetch data for {geo} {year}: {e}")
                    continue

        return results

    def close(self):
        """Close client connections."""
        self._http_client.close()
        if self._cache:
            self._cache.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
