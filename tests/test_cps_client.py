"""
Unit tests for CPS Client

Run with: pytest tests/test_cps_client.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.census_client.cps_client import CPSClient
from src.models.cps_models import CPSLaborStats, CPSEducationEmployment, CPSGigEconomyStats


class TestCPSClient:
    """Test CPS data access layer"""

    @pytest.fixture
    def mock_cps_labor_response(self):
        """Mock CPS API response for labor stats"""
        return [
            ["PEMLR", "PREMPNOT", "PEHRUSL1", "PWSSWGT", "state"],  # Headers
            ["1", "1", "40", "1000.5", "06"],  # Employed, 40 hours, weight 1000.5
            ["1", "1", "35", "950.2", "06"],   # Employed, 35 hours
            ["3", "3", "0", "100.8", "06"],    # Unemployed
            ["5", "5", "0", "500.0", "06"],    # Not in labor force
        ]

    @pytest.fixture
    def mock_cps_education_response(self):
        """Mock CPS API response for education-employment"""
        return [
            ["PEEDUCA", "PEMLR", "PWSSWGT", "PRTAGE", "PESEX", "state"],
            ["43", "1", "500.0", "28", "1", "06"],  # BA, employed, male, age 28
            ["43", "1", "450.0", "32", "2", "06"],  # BA, employed, female, age 32
            ["43", "3", "50.0", "25", "1", "06"],   # BA, unemployed, male
        ]

    @pytest.fixture
    def mock_cps_gig_response(self):
        """Mock CPS API response for gig economy"""
        return [
            ["PEIO1COW", "PRSJMJ", "PEHRRSN1", "PEMLR", "PWSSWGT", "state"],
            ["6", "0", "0", "1", "100.0", "06"],  # Self-employed
            ["1", "1", "0", "1", "50.0", "06"],   # Multiple jobs
            ["1", "0", "1", "1", "75.0", "06"],   # Part-time economic
            ["1", "0", "0", "1", "300.0", "06"],  # Regular employed
        ]

    @pytest.fixture
    def cps_client(self):
        """Create CPS client with cache disabled for testing"""
        return CPSClient(api_key="test_key", use_cache=False)

    def test_get_labor_stats_success(self, cps_client, mock_cps_labor_response):
        """Test successful labor stats retrieval"""
        with patch.object(cps_client, '_make_request', return_value=mock_cps_labor_response):
            stats = cps_client.get_cps_labor_stats(
                year=2024,
                month=11,
                state_fips="06"
            )

            assert isinstance(stats, CPSLaborStats)
            assert stats.year == 2024
            assert stats.month == 11
            assert stats.state_fips == "06"

            # Check computed values
            # Total employed = 1000.5 + 950.2 = 1950.7
            # Total unemployed = 100.8
            # Labor force = 1950.7 + 100.8 = 2051.5
            # Unemployment rate = 100.8 / 2051.5 * 100 ≈ 4.91%

            assert stats.employed == 1951  # Rounded
            assert stats.unemployed == 101  # Rounded
            assert stats.labor_force == 2052  # Rounded
            assert 4.5 < stats.unemployment_rate < 5.5  # Approximate

    def test_get_labor_stats_national(self, cps_client, mock_cps_labor_response):
        """Test national-level query (no state filter)"""
        with patch.object(cps_client, '_make_request', return_value=mock_cps_labor_response):
            stats = cps_client.get_cps_labor_stats(
                year=2024,
                month=11,
                state_fips=None  # National
            )

            assert stats.state_fips is None
            assert stats.state_name == "United States"

    def test_get_labor_stats_zero_labor_force(self, cps_client):
        """Test edge case: zero labor force"""
        # All not in labor force
        empty_response = [
            ["PEMLR", "PWSSWGT", "state"],
            ["5", "1000", "06"],  # Not in LF
            ["7", "500", "06"],   # Not in LF
        ]

        with patch.object(cps_client, '_make_request', return_value=empty_response):
            stats = cps_client.get_cps_labor_stats(2024, 11, "06")

            assert stats.labor_force == 0
            assert stats.unemployment_rate == 0  # Avoid division by zero
            assert stats.not_in_labor_force == 1500

    def test_get_education_employment(self, cps_client, mock_cps_education_response):
        """Test education-employment statistics"""
        with patch.object(cps_client, '_make_request', return_value=mock_cps_education_response):
            stats = cps_client.get_cps_education_employment(
                year=2024,
                month=11,
                education_level="43",  # Bachelor's
                state_fips="06"
            )

            assert isinstance(stats, CPSEducationEmployment)
            assert stats.education_level == "Bachelor's degree"
            assert stats.total_population == 1000  # 500 + 450 + 50
            assert stats.employed == 950  # 500 + 450
            assert stats.unemployed == 50

            # Employment rate = 950/1000 * 100 = 95%
            assert stats.employment_rate == 95.0

    def test_get_gig_economy_stats(self, cps_client, mock_cps_gig_response):
        """Test gig economy statistics"""
        with patch.object(cps_client, '_make_request', return_value=mock_cps_gig_response):
            stats = cps_client.get_cps_gig_economy_stats(
                year=2024,
                month=11,
                state_fips="06"
            )

            assert isinstance(stats, CPSGigEconomyStats)
            assert stats.self_employed == 100
            assert stats.multiple_job_holders == 50
            assert stats.part_time_economic_reasons == 75
            assert stats.total_employed == 525  # All rows are employed

            # Check percentages
            assert stats.pct_self_employed == round(100/525 * 100, 2)
            assert stats.pct_multiple_jobs == round(50/525 * 100, 2)

    def test_api_retry_on_failure(self, cps_client):
        """Test retry logic on API failure"""
        mock_client = Mock()
        cps_client.client = mock_client

        # Simulate failures then success
        mock_response_error = Mock()
        mock_response_error.raise_for_status.side_effect = Exception("Network error")

        mock_response_success = Mock()
        mock_response_success.json.return_value = [["PEMLR"], ["1"]]
        mock_response_success.raise_for_status.return_value = None

        mock_client.get.side_effect = [
            mock_response_error,  # First attempt fails
            mock_response_error,  # Second attempt fails
            mock_response_success  # Third attempt succeeds
        ]

        # Should retry and eventually succeed
        result = cps_client._make_request("jun", {"get": "PEMLR"})
        assert result == [["PEMLR"], ["1"]]
        assert mock_client.get.call_count == 3

    def test_caching(self):
        """Test response caching"""
        import tempfile
        import os

        # Create temporary cache directory
        with tempfile.TemporaryDirectory() as tmpdir:
            client_with_cache = CPSClient(api_key="test", use_cache=True, cache_dir=tmpdir)

            mock_response = [["VAR"], ["value"]]

            with patch.object(client_with_cache.client, 'get') as mock_get:
                mock_get.return_value.json.return_value = mock_response
                mock_get.return_value.raise_for_status.return_value = None

                # First call - cache miss
                result1 = client_with_cache._make_request("jun", {"get": "TEST"}, cache_key="test_key")

                # Second call - cache hit (should not call API)
                result2 = client_with_cache._make_request("jun", {"get": "TEST"}, cache_key="test_key")

                assert result1 == result2
                assert mock_get.call_count == 1  # Only called once

    def test_invalid_row_handling(self, cps_client):
        """Test handling of invalid data rows"""
        invalid_response = [
            ["PEMLR", "PWSSWGT", "state"],
            ["1", "abc", "06"],    # Invalid weight (non-numeric)
            ["1", "500.0", "06"],  # Valid row
            ["invalid", "100", "06"],  # Invalid PEMLR code
        ]

        with patch.object(cps_client, '_make_request', return_value=invalid_response):
            # Should skip invalid rows and process valid ones
            stats = cps_client.get_cps_labor_stats(2024, 11, "06")

            # Should only count the valid row
            assert stats.employed == 500
            assert stats.sample_size == 3  # All rows counted

    def test_month_to_endpoint_mapping(self, cps_client):
        """Test correct month-to-endpoint mapping"""
        with patch.object(cps_client, '_make_request', return_value=[["PEMLR"], ["1"]]) as mock_request:
            # Test January (month 1)
            cps_client.get_cps_labor_stats(2024, 1, "06")
            assert "jan" in mock_request.call_args[0][0]

            # Test December (month 12)
            cps_client.get_cps_labor_stats(2024, 12, "06")
            assert "dec" in mock_request.call_args[0][0]

            # Test June (month 6)
            cps_client.get_cps_labor_stats(2024, 6, "06")
            assert "jun" in mock_request.call_args[0][0]

    def test_state_fips_lookup(self, cps_client):
        """Test state FIPS code to name mapping"""
        assert cps_client._get_state_name("06") == "California"
        assert cps_client._get_state_name("48") == "Texas"
        assert cps_client._get_state_name("36") == "New York"
        assert cps_client._get_state_name("99") == "State 99"  # Unknown

    def test_education_level_lookup(self, cps_client):
        """Test education level code to name mapping"""
        assert cps_client._education_level_name("43") == "Bachelor's degree"
        assert cps_client._education_level_name("44") == "Master's degree"
        assert cps_client._education_level_name("99") == "Education level 99"  # Unknown
