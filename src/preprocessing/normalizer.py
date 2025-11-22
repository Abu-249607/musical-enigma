"""Data normalization for Census employment data."""

from typing import Any
from ..models.employment import EmploymentRecord, GeographyLevel, EMPLOYMENT_VARIABLES


class EmploymentDataNormalizer:
    """Normalizes raw Census API responses into structured formats.

    Handles:
    - Variable code to human-readable label mapping
    - Missing value handling
    - Data type conversions
    - Geographic identifier standardization
    """

    def __init__(self):
        self.variable_labels = EMPLOYMENT_VARIABLES.copy()

    def normalize_api_response(
        self,
        raw_response: list[list[str]],
        dataset: str,
        year: int,
    ) -> list[dict[str, Any]]:
        """Convert raw Census API response to normalized records.

        Args:
            raw_response: Raw API response (list of lists with header row)
            dataset: Dataset identifier
            year: Data year

        Returns:
            List of normalized dictionaries
        """
        if not raw_response or len(raw_response) < 2:
            return []

        headers = raw_response[0]
        records = []

        for row in raw_response[1:]:
            record = self._normalize_row(headers, row, dataset, year)
            if record:
                records.append(record)

        return records

    def _normalize_row(
        self,
        headers: list[str],
        values: list[str],
        dataset: str,
        year: int,
    ) -> dict[str, Any]:
        """Normalize a single data row."""
        record = {
            "_metadata": {
                "dataset": dataset,
                "year": year,
                "raw_variables": {},
            }
        }

        for i, header in enumerate(headers):
            value = values[i] if i < len(values) else None

            # Store raw value
            record["_metadata"]["raw_variables"][header] = value

            # Handle NAME field
            if header == "NAME":
                record["geography_name"] = value
                continue

            # Handle state/county FIPS
            if header == "state":
                record["state_fips"] = value
                continue
            if header == "county":
                record["county_fips"] = value
                continue

            # Handle numeric variables
            if header in self.variable_labels:
                label = self.variable_labels[header]
                normalized_value = self._parse_numeric(value)
                record[self._to_snake_case(label)] = normalized_value

                # Check for margin of error companion
                moe_var = header.replace("E", "M")
                if moe_var in headers:
                    moe_idx = headers.index(moe_var)
                    moe_value = values[moe_idx] if moe_idx < len(values) else None
                    record[f"{self._to_snake_case(label)}_moe"] = self._parse_numeric(moe_value)

        return record

    def _parse_numeric(self, value: str | None) -> int | float | None:
        """Parse numeric value, handling Census null indicators."""
        if value is None:
            return None

        # Census uses various null indicators
        null_indicators = ["-", "N", "(X)", "**", "***", "-888888888", "-666666666"]
        if value in null_indicators:
            return None

        try:
            # Try integer first
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None

    def _to_snake_case(self, label: str) -> str:
        """Convert label to snake_case key."""
        return (
            label.lower()
            .replace(" ", "_")
            .replace(",", "")
            .replace(":", "")
            .replace("-", "_")
            .replace("(", "")
            .replace(")", "")
        )

    def to_employment_record(
        self,
        normalized: dict[str, Any],
        level: GeographyLevel = GeographyLevel.STATE,
    ) -> EmploymentRecord:
        """Convert normalized dict to EmploymentRecord model."""
        # Build FIPS code
        fips = normalized.get("state_fips", "")
        if normalized.get("county_fips"):
            fips = f"{fips}{normalized['county_fips']}"

        return EmploymentRecord(
            geography_name=normalized.get("geography_name", "Unknown"),
            geography_level=level,
            fips_code=fips if fips else None,
            year=normalized.get("_metadata", {}).get("year", 0),
            total_population_16_plus=normalized.get("total_population_16_years_and_over"),
            labor_force=normalized.get("in_labor_force"),
            employed=normalized.get("in_labor_force_civilian_labor_force_employed"),
            unemployed=normalized.get("in_labor_force_civilian_labor_force_unemployed"),
            not_in_labor_force=normalized.get("not_in_labor_force"),
        )

    def validate_record(self, record: EmploymentRecord) -> list[str]:
        """Validate an employment record for data quality issues.

        Returns list of warning messages for any issues found.
        """
        warnings = []

        # Check for missing critical fields
        if record.labor_force is None:
            warnings.append("Missing labor force data")

        # Sanity checks
        if record.labor_force and record.employed and record.unemployed:
            expected_lf = record.employed + record.unemployed
            # Allow for rounding in some edge cases
            if abs(record.labor_force - expected_lf) > 100:
                warnings.append(
                    f"Labor force ({record.labor_force}) doesn't match "
                    f"employed ({record.employed}) + unemployed ({record.unemployed})"
                )

        if record.unemployment_rate and record.unemployment_rate > 50:
            warnings.append(
                f"Unusually high unemployment rate: {record.unemployment_rate}%"
            )

        return warnings
