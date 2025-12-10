"""
Education ROI Calculator using CPS Basic Monthly data

Estimates return on investment for different education levels and fields
by comparing employment outcomes.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import date

from ..census_client.cps_client import CPSClient
from ..models.cps_models import CPSEducationEmployment


@dataclass
class EducationROI:
    """Education ROI comparison"""
    education_level: str
    field_of_study: Optional[str] = None

    # Employment outcomes
    employment_rate: float
    unemployment_rate: float
    avg_hours_worked: Optional[float] = None

    # Relative metrics
    employment_advantage: float  # vs. high school
    roi_score: float  # Composite score (0-100)

    # Sample info
    sample_size: int
    time_period: str


class EducationROICalculator:
    """Calculate education ROI using CPS data"""

    # Education level ordering (for comparison)
    EDUCATION_HIERARCHY = [
        "39",  # High school
        "40",  # Some college
        "43",  # Bachelor's
        "44",  # Master's
        "45",  # Professional
        "46",  # Doctoral
    ]

    def __init__(self, cps_client: CPSClient):
        """Initialize with CPS client"""
        self.client = cps_client

    def calculate_roi(
        self,
        year: int,
        month: int,
        education_levels: List[str],
        state_fips: Optional[str] = None,
        age_range: Optional[tuple] = None
    ) -> List[EducationROI]:
        """Calculate ROI for multiple education levels

        Args:
            year: Year to analyze
            month: Month to analyze
            education_levels: List of education level codes
            state_fips: State FIPS (optional)
            age_range: (min_age, max_age) for filtering (future enhancement)

        Returns:
            List of EducationROI objects sorted by ROI score

        Example:
            >>> calc = EducationROICalculator(cps_client)
            >>> roi = calc.calculate_roi(
            ...     year=2024,
            ...     month=11,
            ...     education_levels=["39", "43", "44"],  # HS, BA, MA
            ...     state_fips="06"  # California
            ... )
            >>> for r in roi:
            ...     print(f"{r.education_level}: {r.roi_score:.1f}")
        """
        results = []

        # Get baseline (high school) for comparison
        baseline = self.client.get_cps_education_employment(
            year=year,
            month=month,
            education_level="39",  # High school
            state_fips=state_fips
        )

        for edu_level in education_levels:
            stats = self.client.get_cps_education_employment(
                year=year,
                month=month,
                education_level=edu_level,
                state_fips=state_fips
            )

            # Calculate employment advantage over high school
            emp_advantage = stats.employment_rate - baseline.employment_rate

            # Calculate ROI score (0-100)
            # Factors: employment rate (60%), employment advantage (30%), unemployment (10%)
            roi_score = (
                stats.employment_rate * 0.6 +
                max(0, emp_advantage) * 0.3 -
                stats.unemployment_rate * 0.1
            )
            roi_score = max(0, min(100, roi_score))  # Clamp to 0-100

            results.append(EducationROI(
                education_level=stats.education_level,
                employment_rate=stats.employment_rate,
                unemployment_rate=stats.unemployment_rate,
                employment_advantage=round(emp_advantage, 2),
                roi_score=round(roi_score, 2),
                sample_size=stats.total_population,
                time_period=f"{year}-{month:02d}"
            ))

        # Sort by ROI score (descending)
        results.sort(key=lambda x: x.roi_score, reverse=True)

        return results

    def compare_timeline(
        self,
        education_level: str,
        year_month_pairs: List[tuple],
        state_fips: Optional[str] = None
    ) -> List[EducationROI]:
        """Compare ROI over time for a single education level

        Args:
            education_level: Education level code
            year_month_pairs: List of (year, month) tuples
            state_fips: State FIPS

        Returns:
            List of EducationROI objects over time
        """
        results = []

        for year, month in year_month_pairs:
            roi_list = self.calculate_roi(
                year=year,
                month=month,
                education_levels=[education_level],
                state_fips=state_fips
            )
            if roi_list:
                results.extend(roi_list)

        return results

    def compare_fields(
        self,
        year: int,
        month: int,
        bachelor_fields: List[str],
        state_fips: Optional[str] = None
    ) -> Dict[str, EducationROI]:
        """Compare ROI across fields of study (for bachelor's degree holders)

        Note: CPS Basic Monthly has limited field-of-study data.
        For detailed field data, would need to use ACS PUMS or CPS Supplements.

        Args:
            year: Year
            month: Month
            bachelor_fields: List of field codes
            state_fips: State FIPS

        Returns:
            Dictionary mapping field to ROI
        """
        # This is a placeholder for future implementation
        # Full implementation would query field-specific supplements
        # or cross-reference with ACS Table S1502 (Field of Bachelor's Degree)

        raise NotImplementedError(
            "Field-of-study analysis requires CPS Supplements or ACS PUMS data. "
            "Use ACS Table S1502 for field-specific outcomes, which is already "
            "available in the existing STEMIntelligenceHub."
        )

    def get_summary_report(
        self,
        year: int,
        month: int,
        state_fips: Optional[str] = None
    ) -> Dict[str, any]:
        """Generate a comprehensive summary report

        Args:
            year: Year
            month: Month
            state_fips: State FIPS

        Returns:
            Dictionary with summary statistics and rankings
        """
        # Calculate ROI for all major education levels
        all_levels = ["39", "40", "43", "44", "45", "46"]
        roi_results = self.calculate_roi(
            year=year,
            month=month,
            education_levels=all_levels,
            state_fips=state_fips
        )

        # Create summary
        return {
            "year": year,
            "month": month,
            "geography": self.client._get_state_name(state_fips) if state_fips else "United States",
            "education_roi": roi_results,
            "highest_roi": roi_results[0] if roi_results else None,
            "total_levels_analyzed": len(roi_results),
            "key_insights": self._generate_insights(roi_results)
        }

    def _generate_insights(self, roi_results: List[EducationROI]) -> List[str]:
        """Generate key insights from ROI results"""
        insights = []

        if not roi_results:
            return insights

        # Best ROI
        best = roi_results[0]
        insights.append(f"{best.education_level} has the highest ROI score ({best.roi_score:.1f})")

        # Employment rate leaders
        high_emp = [r for r in roi_results if r.employment_rate >= 90.0]
        if high_emp:
            insights.append(f"{len(high_emp)} education level(s) have 90%+ employment rates")

        # Employment advantage
        high_advantage = [r for r in roi_results if r.employment_advantage >= 20.0]
        if high_advantage:
            levels = ", ".join([r.education_level for r in high_advantage])
            insights.append(f"{levels} show 20%+ employment advantage over high school")

        return insights
