"""
Unit tests for Data Validator

Run with: pytest tests/test_data_validator.py -v
"""

import pytest
from unittest.mock import Mock
from src.validation.data_validator import DataValidator, ValidationResult
from src.models.cps_models import CPSLaborStats, CPSEducationEmployment


class TestDataValidator:
    """Test data validation logic"""

    @pytest.fixture
    def mock_cps_client(self):
        """Create mock CPS client"""
        return Mock()

    @pytest.fixture
    def validator(self, mock_cps_client):
        """Create validator with mocked client"""
        return DataValidator(mock_cps_client)

    def test_validate_labor_stats_exact_match(self, validator, mock_cps_client):
        """Test validation with exact match (should pass)"""
        app_stats = CPSLaborStats(
            year=2024, month=11, state_fips="06", state_name="California",
            labor_force=10000, employed=9500, unemployed=500, not_in_labor_force=2000,
            unemployment_rate=5.0, labor_force_participation_rate=65.0,
            employment_population_ratio=61.75,
            avg_hours_worked=40.0, sample_size=1000
        )

        # Mock re-query to return same values
        mock_cps_client.get_cps_labor_stats.return_value = app_stats

        results = validator.validate_labor_stats(app_stats)

        # All validations should pass
        assert all(r.is_valid for r in results)
        assert len(results) == 6  # 6 metrics validated

    def test_validate_labor_stats_small_difference(self, validator, mock_cps_client):
        """Test validation with small acceptable difference"""
        app_stats = CPSLaborStats(
            year=2024, month=11, state_fips="06", state_name="California",
            labor_force=10000, employed=9500, unemployed=500, not_in_labor_force=2000,
            unemployment_rate=5.0, labor_force_participation_rate=65.0,
            employment_population_ratio=61.75,
            avg_hours_worked=40.0, sample_size=1000
        )

        # Mock re-query with slightly different values (within threshold)
        census_stats = CPSLaborStats(
            year=2024, month=11, state_fips="06", state_name="California",
            labor_force=10001, employed=9501, unemployed=500, not_in_labor_force=2000,
            unemployment_rate=4.99, labor_force_participation_rate=65.01,
            employment_population_ratio=61.76,
            avg_hours_worked=40.0, sample_size=1000
        )

        mock_cps_client.get_cps_labor_stats.return_value = census_stats

        results = validator.validate_labor_stats(app_stats)

        # Should still pass (differences are tiny)
        assert all(r.is_valid for r in results)

    def test_validate_labor_stats_large_difference(self, validator, mock_cps_client):
        """Test validation with large unacceptable difference"""
        app_stats = CPSLaborStats(
            year=2024, month=11, state_fips="06", state_name="California",
            labor_force=10000, employed=9500, unemployed=500, not_in_labor_force=2000,
            unemployment_rate=5.0, labor_force_participation_rate=65.0,
            employment_population_ratio=61.75,
            avg_hours_worked=40.0, sample_size=1000
        )

        # Mock re-query with significantly different values
        census_stats = CPSLaborStats(
            year=2024, month=11, state_fips="06", state_name="California",
            labor_force=10000, employed=9500, unemployed=500, not_in_labor_force=2000,
            unemployment_rate=10.0,  # Very different!
            labor_force_participation_rate=65.0,
            employment_population_ratio=61.75,
            avg_hours_worked=40.0, sample_size=1000
        )

        mock_cps_client.get_cps_labor_stats.return_value = census_stats

        results = validator.validate_labor_stats(app_stats)

        # Unemployment rate should fail
        failed = [r for r in results if not r.is_valid]
        assert len(failed) > 0
        assert any(r.metric_name == "unemployment_rate" for r in failed)

    def test_assert_valid_passes(self, validator, mock_cps_client):
        """Test assert_valid with all passing results"""
        app_stats = CPSLaborStats(
            year=2024, month=11, state_fips="06", state_name="California",
            labor_force=10000, employed=9500, unemployed=500, not_in_labor_force=2000,
            unemployment_rate=5.0, labor_force_participation_rate=65.0,
            employment_population_ratio=61.75,
            avg_hours_worked=40.0, sample_size=1000
        )

        mock_cps_client.get_cps_labor_stats.return_value = app_stats

        results = validator.validate_labor_stats(app_stats)

        # Should not raise assertion error
        validator.assert_valid(results)

    def test_assert_valid_fails(self, validator, mock_cps_client):
        """Test assert_valid with failing results"""
        app_stats = CPSLaborStats(
            year=2024, month=11, state_fips="06", state_name="California",
            labor_force=10000, employed=9500, unemployed=500, not_in_labor_force=2000,
            unemployment_rate=5.0, labor_force_participation_rate=65.0,
            employment_population_ratio=61.75,
            avg_hours_worked=40.0, sample_size=1000
        )

        census_stats = CPSLaborStats(
            year=2024, month=11, state_fips="06", state_name="California",
            labor_force=10000, employed=9500, unemployed=500, not_in_labor_force=2000,
            unemployment_rate=10.0,  # Significantly different
            labor_force_participation_rate=65.0,
            employment_population_ratio=61.75,
            avg_hours_worked=40.0, sample_size=1000
        )

        mock_cps_client.get_cps_labor_stats.return_value = census_stats

        results = validator.validate_labor_stats(app_stats)

        # Should raise assertion error
        with pytest.raises(AssertionError, match="Data validation failed"):
            validator.assert_valid(results)

    def test_validation_report_generation(self, validator, mock_cps_client):
        """Test validation report generation"""
        app_stats = CPSLaborStats(
            year=2024, month=11, state_fips="06", state_name="California",
            labor_force=10000, employed=9500, unemployed=500, not_in_labor_force=2000,
            unemployment_rate=5.0, labor_force_participation_rate=65.0,
            employment_population_ratio=61.75,
            avg_hours_worked=40.0, sample_size=1000
        )

        mock_cps_client.get_cps_labor_stats.return_value = app_stats

        results = validator.validate_labor_stats(app_stats)

        report = validator.generate_validation_report(results)

        assert report["total_validations"] == 6
        assert report["passed"] == 6
        assert report["failed"] == 0
        assert report["pass_rate"] == 100.0
        assert report["max_difference"] >= 0
        assert report["avg_difference"] >= 0

    def test_custom_threshold(self, validator, mock_cps_client):
        """Test validation with custom threshold"""
        app_stats = CPSLaborStats(
            year=2024, month=11, state_fips="06", state_name="California",
            labor_force=10000, employed=9500, unemployed=500, not_in_labor_force=2000,
            unemployment_rate=5.0, labor_force_participation_rate=65.0,
            employment_population_ratio=61.75,
            avg_hours_worked=40.0, sample_size=1000
        )

        census_stats = CPSLaborStats(
            year=2024, month=11, state_fips="06", state_name="California",
            labor_force=10050, employed=9500, unemployed=500, not_in_labor_force=2000,
            unemployment_rate=5.0, labor_force_participation_rate=65.0,
            employment_population_ratio=61.75,
            avg_hours_worked=40.0, sample_size=1000
        )

        mock_cps_client.get_cps_labor_stats.return_value = census_stats

        # With very strict threshold (0.1%), should fail
        results_strict = validator.validate_labor_stats(app_stats, threshold=0.1)
        failed_strict = [r for r in results_strict if not r.is_valid]
        assert len(failed_strict) > 0

        # With relaxed threshold (1.0%), should pass
        results_relaxed = validator.validate_labor_stats(app_stats, threshold=1.0)
        failed_relaxed = [r for r in results_relaxed if not r.is_valid and r.metric_name == "labor_force"]
        assert len(failed_relaxed) == 0
