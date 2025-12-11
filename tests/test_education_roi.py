"""
Unit tests for Education ROI Calculator

Run with: pytest tests/test_education_roi.py -v
"""

import pytest
from unittest.mock import Mock
from src.analytics.education_roi import EducationROICalculator, EducationROI
from src.models.cps_models import CPSEducationEmployment


class TestEducationROICalculator:
    """Test Education ROI calculation logic"""

    @pytest.fixture
    def mock_cps_client(self):
        """Create mock CPS client"""
        return Mock()

    @pytest.fixture
    def roi_calculator(self, mock_cps_client):
        """Create ROI calculator with mocked client"""
        return EducationROICalculator(mock_cps_client)

    def test_calculate_roi_basic(self, roi_calculator, mock_cps_client):
        """Test basic ROI calculation"""
        # Mock responses for high school and bachelor's
        mock_cps_client.get_cps_education_employment.side_effect = [
            # High school (baseline)
            CPSEducationEmployment(
                year=2024,
                month=11,
                education_level="High school graduate",
                state_fips="06",
                total_population=10000,
                employed=7000,
                unemployed=1000,
                not_in_labor_force=2000,
                employment_rate=70.0,
                unemployment_rate=12.5
            ),
            # Bachelor's degree
            CPSEducationEmployment(
                year=2024,
                month=11,
                education_level="Bachelor's degree",
                state_fips="06",
                total_population=8000,
                employed=7200,
                unemployed=400,
                not_in_labor_force=400,
                employment_rate=90.0,
                unemployment_rate=5.0
            ),
        ]

        results = roi_calculator.calculate_roi(
            year=2024,
            month=11,
            education_levels=["43"],  # Bachelor's
            state_fips="06"
        )

        assert len(results) == 1
        roi = results[0]

        assert roi.education_level == "Bachelor's degree"
        assert roi.employment_rate == 90.0
        assert roi.employment_advantage == 20.0  # 90 - 70
        assert roi.roi_score > 50  # Should be reasonably high

    def test_roi_score_calculation(self, roi_calculator, mock_cps_client):
        """Test ROI score formula"""
        mock_cps_client.get_cps_education_employment.side_effect = [
            # Baseline (high school)
            CPSEducationEmployment(
                year=2024, month=11,
                education_level="High school graduate",
                state_fips=None,
                total_population=10000,
                employed=6000, unemployed=1000, not_in_labor_force=3000,
                employment_rate=60.0, unemployment_rate=14.3
            ),
            # Test case: perfect employment
            CPSEducationEmployment(
                year=2024, month=11,
                education_level="Doctoral degree",
                state_fips=None,
                total_population=1000,
                employed=1000, unemployed=0, not_in_labor_force=0,
                employment_rate=100.0, unemployment_rate=0.0
            ),
        ]

        results = roi_calculator.calculate_roi(
            year=2024,
            month=11,
            education_levels=["46"]  # Doctoral
        )

        roi = results[0]

        # ROI score formula: emp_rate * 0.6 + max(0, advantage) * 0.3 - unemp_rate * 0.1
        # = 100 * 0.6 + 40 * 0.3 - 0 * 0.1 = 60 + 12 - 0 = 72
        assert 70 < roi.roi_score < 75

    def test_multiple_education_levels_sorted(self, roi_calculator, mock_cps_client):
        """Test that results are sorted by ROI score"""
        mock_cps_client.get_cps_education_employment.side_effect = [
            # Baseline
            CPSEducationEmployment(
                year=2024, month=11, education_level="High school graduate",
                state_fips=None, total_population=10000,
                employed=6000, unemployed=1000, not_in_labor_force=3000,
                employment_rate=60.0, unemployment_rate=14.3
            ),
            # Some college (worse than bachelor's)
            CPSEducationEmployment(
                year=2024, month=11, education_level="Some college or Associate degree",
                state_fips=None, total_population=5000,
                employed=3500, unemployed=500, not_in_labor_force=1000,
                employment_rate=70.0, unemployment_rate=12.5
            ),
            # Bachelor's (best)
            CPSEducationEmployment(
                year=2024, month=11, education_level="Bachelor's degree",
                state_fips=None, total_population=8000,
                employed=7200, unemployed=400, not_in_labor_force=400,
                employment_rate=90.0, unemployment_rate=5.0
            ),
        ]

        results = roi_calculator.calculate_roi(
            year=2024,
            month=11,
            education_levels=["40", "43"]  # Some college, Bachelor's
        )

        assert len(results) == 2
        # Results should be sorted by ROI score (descending)
        assert results[0].roi_score >= results[1].roi_score
        assert results[0].education_level == "Bachelor's degree"

    def test_summary_report_generation(self, roi_calculator, mock_cps_client):
        """Test summary report generation"""
        # Mock all education levels
        mock_responses = []

        # Baseline (high school)
        mock_responses.append(CPSEducationEmployment(
            year=2024, month=11,
            education_level="High school graduate",
            state_fips=None,
            total_population=10000,
            employed=6000, unemployed=1000, not_in_labor_force=3000,
            employment_rate=60.0, unemployment_rate=14.3
        ))

        # All other levels
        for level, rate in [("40", 70.0), ("43", 90.0), ("44", 92.0), ("45", 95.0), ("46", 96.0)]:
            mock_responses.append(CPSEducationEmployment(
                year=2024, month=11,
                education_level=f"Level {level}",
                state_fips=None,
                total_population=5000,
                employed=int(5000 * rate / 100), unemployed=100, not_in_labor_force=100,
                employment_rate=rate, unemployment_rate=5.0
            ))

        mock_cps_client.get_cps_education_employment.side_effect = mock_responses

        report = roi_calculator.get_summary_report(2024, 11, state_fips=None)

        assert report["year"] == 2024
        assert report["month"] == 11
        assert report["geography"] == "United States"
        assert len(report["education_roi"]) == 6
        assert report["highest_roi"] is not None
        assert len(report["key_insights"]) > 0
