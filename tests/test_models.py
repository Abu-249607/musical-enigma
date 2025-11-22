"""Tests for data models."""

import pytest
from datetime import datetime

from src.models.citation import Citation, CitedDataPoint, CitedResponse
from src.models.employment import (
    EmploymentRecord,
    GeographyLevel,
    EMPLOYMENT_VARIABLES,
    get_moe_variable,
)


class TestCitation:
    """Tests for Citation model."""

    def test_citation_creation(self):
        """Test creating a citation."""
        citation = Citation(
            citation_id="ACS-ACS5-2022-001",
            dataset_name="acs/acs5",
            dataset_year=2022,
            variables=["B23025_001E", "B23025_004E"],
            geography="state",
            geography_name="California",
            fips_code="06",
            api_endpoint="https://api.census.gov/data/2022/acs/acs5",
        )

        assert citation.citation_id == "ACS-ACS5-2022-001"
        assert citation.dataset_year == 2022
        assert citation.geography_name == "California"

    def test_citation_reference_string(self):
        """Test generating reference string."""
        citation = Citation(
            citation_id="TEST-001",
            dataset_name="acs/acs5",
            dataset_year=2022,
            variables=["B23025_001E"],
            geography="state",
            geography_name="California",
            api_endpoint="https://api.census.gov/data/2022/acs/acs5",
        )

        ref = citation.to_reference_string()
        assert "TEST-001" in ref
        assert "Census Bureau" in ref
        assert "California" in ref
        assert "2022" in ref


class TestEmploymentRecord:
    """Tests for EmploymentRecord model."""

    def test_unemployment_rate_calculation(self):
        """Test unemployment rate calculation."""
        record = EmploymentRecord(
            geography_name="California",
            geography_level=GeographyLevel.STATE,
            year=2022,
            labor_force=20000000,
            employed=19000000,
            unemployed=1000000,
        )

        assert record.unemployment_rate == 5.0

    def test_labor_force_participation_rate(self):
        """Test labor force participation rate calculation."""
        record = EmploymentRecord(
            geography_name="California",
            geography_level=GeographyLevel.STATE,
            year=2022,
            total_population_16_plus=30000000,
            labor_force=20000000,
        )

        rate = record.labor_force_participation_rate
        assert rate == pytest.approx(66.67, rel=0.01)

    def test_missing_data_returns_none(self):
        """Test that missing data returns None for rates."""
        record = EmploymentRecord(
            geography_name="Unknown",
            geography_level=GeographyLevel.STATE,
            year=2022,
        )

        assert record.unemployment_rate is None
        assert record.labor_force_participation_rate is None


class TestEmploymentVariables:
    """Tests for employment variable mappings."""

    def test_variables_exist(self):
        """Test that expected variables are defined."""
        assert "B23025_001E" in EMPLOYMENT_VARIABLES
        assert "B23025_004E" in EMPLOYMENT_VARIABLES
        assert "B23025_005E" in EMPLOYMENT_VARIABLES

    def test_moe_variable_conversion(self):
        """Test converting estimate to MOE variable."""
        assert get_moe_variable("B23025_001E") == "B23025_001M"
        assert get_moe_variable("C24050_001E") == "C24050_001M"


class TestCitedDataPoint:
    """Tests for CitedDataPoint model."""

    def test_cited_data_point_creation(self):
        """Test creating a cited data point."""
        citation = Citation(
            citation_id="TEST-001",
            dataset_name="acs/acs5",
            dataset_year=2022,
            variables=["B23025_005E"],
            geography="state",
            geography_name="California",
            api_endpoint="https://api.census.gov/data/2022/acs/acs5",
        )

        data_point = CitedDataPoint(
            value=5.2,
            label="Unemployment rate in California",
            variable_code="B23025_005E/B23025_002E",
            citation=citation,
            is_estimate=True,
            confidence_note="ACS 5-year estimate",
        )

        assert data_point.value == 5.2
        assert data_point.is_estimate is True
        assert data_point.citation.citation_id == "TEST-001"
