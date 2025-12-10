"""
STEM Intelligence Dashboard using CPS Basic Monthly data

Analyzes STEM employment trends, demographics, and outcomes using
CPS occupation and education data.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

from ..census_client.cps_client import CPSClient
from ..models.cps_models import CPSEducationEmployment, CPSOccupationStats


@dataclass
class STEMDashboardMetrics:
    """STEM workforce metrics"""
    year: int
    month: int
    state_fips: Optional[str]

    # STEM workforce size
    total_stem_workers: int
    stem_pct_of_workforce: float

    # Education levels in STEM
    bachelors_plus_pct: Optional[float] = None

    # Demographics
    female_pct: Optional[float] = None
    median_age: Optional[float] = None

    # Employment metrics
    avg_hours_worked: Optional[float] = None
    full_time_pct: Optional[float] = None


class STEMDashboardCPS:
    """STEM Intelligence Dashboard using CPS data"""

    def __init__(self, cps_client: CPSClient):
        """Initialize with CPS client"""
        self.client = cps_client

    def get_stem_overview(
        self,
        year: int,
        month: int,
        state_fips: Optional[str] = None
    ) -> STEMDashboardMetrics:
        """Get STEM workforce overview

        Note: CPS Basic Monthly has limited occupation detail.
        For comprehensive STEM analysis, use ACS PUMS or the existing
        STEMIntelligenceHub which provides more granular occupation data.

        Args:
            year: Year
            month: Month
            state_fips: State FIPS

        Returns:
            STEMDashboardMetrics object
        """
        # This is a simplified implementation
        # Full implementation would need CPS ASEC supplement or ACS data
        # for detailed occupation codes

        # For now, we can estimate STEM workers using education as a proxy
        # Get Bachelor's+ in computer/engineering fields
        bachelors_stats = self.client.get_cps_education_employment(
            year=year,
            month=month,
            education_level="43",  # Bachelor's
            state_fips=state_fips
        )

        masters_stats = self.client.get_cps_education_employment(
            year=year,
            month=month,
            education_level="44",  # Master's
            state_fips=state_fips
        )

        # Rough estimate: 20% of Bachelor's+ are in STEM fields
        # (This would be more accurate with field-of-study data from ACS)
        stem_estimate = int((bachelors_stats.employed + masters_stats.employed) * 0.20)

        # Get total workforce
        labor_stats = self.client.get_cps_labor_stats(
            year=year,
            month=month,
            state_fips=state_fips
        )

        stem_pct = (stem_estimate / labor_stats.employed * 100) if labor_stats.employed > 0 else 0

        return STEMDashboardMetrics(
            year=year,
            month=month,
            state_fips=state_fips,
            total_stem_workers=stem_estimate,
            stem_pct_of_workforce=round(stem_pct, 2),
            bachelors_plus_pct=100.0,  # By definition
            female_pct=bachelors_stats.pct_female,  # Proxy
            median_age=bachelors_stats.median_age,  # Proxy
            avg_hours_worked=labor_stats.avg_hours_worked,
            full_time_pct=None  # Not available in Basic Monthly
        )

    def compare_stem_across_states(
        self,
        year: int,
        month: int,
        state_fips_list: List[str]
    ) -> List[STEMDashboardMetrics]:
        """Compare STEM metrics across multiple states

        Args:
            year: Year
            month: Month
            state_fips_list: List of state FIPS codes

        Returns:
            List of STEMDashboardMetrics, one per state
        """
        results = []

        for fips in state_fips_list:
            try:
                metrics = self.get_stem_overview(year, month, state_fips=fips)
                results.append(metrics)
            except Exception as e:
                print(f"Error fetching data for {fips}: {e}")
                continue

        # Sort by STEM percentage (descending)
        results.sort(key=lambda x: x.stem_pct_of_workforce, reverse=True)

        return results

    def get_stem_education_pathway(
        self,
        year: int,
        month: int,
        state_fips: Optional[str] = None
    ) -> Dict[str, CPSEducationEmployment]:
        """Analyze STEM education pathway

        Compare employment outcomes for different STEM-relevant education levels

        Args:
            year: Year
            month: Month
            state_fips: State FIPS

        Returns:
            Dictionary mapping education level to stats
        """
        education_levels = ["43", "44", "45", "46"]  # BA, MA, Professional, PhD

        results = {}

        for level in education_levels:
            try:
                stats = self.client.get_cps_education_employment(
                    year=year,
                    month=month,
                    education_level=level,
                    state_fips=state_fips
                )
                results[stats.education_level] = stats
            except Exception as e:
                print(f"Error fetching data for level {level}: {e}")
                continue

        return results

    def generate_stem_report(
        self,
        year: int,
        month: int,
        state_fips: Optional[str] = None
    ) -> Dict[str, any]:
        """Generate comprehensive STEM report

        Args:
            year: Year
            month: Month
            state_fips: State FIPS

        Returns:
            Dictionary with STEM analytics
        """
        overview = self.get_stem_overview(year, month, state_fips)
        education_pathway = self.get_stem_education_pathway(year, month, state_fips)

        return {
            "year": year,
            "month": month,
            "geography": self.client._get_state_name(state_fips) if state_fips else "United States",
            "stem_overview": overview,
            "education_pathway": education_pathway,
            "key_metrics": {
                "stem_workers": overview.total_stem_workers,
                "stem_percentage": overview.stem_pct_of_workforce,
                "female_representation": overview.female_pct,
                "median_age": overview.median_age
            },
            "note": "For more detailed STEM occupation analysis, use the existing STEMIntelligenceHub with ACS data."
        }
