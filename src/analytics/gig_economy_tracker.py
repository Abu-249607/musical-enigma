"""
Gig Economy Tracker using CPS Basic Monthly data

Tracks non-traditional work arrangements including self-employment,
multiple jobs, and part-time for economic reasons.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

from ..census_client.cps_client import CPSClient
from ..models.cps_models import CPSGigEconomyStats


@dataclass
class GigEconomyTrend:
    """Gig economy trend over time"""
    time_period: str
    gig_estimate: float
    self_employed_pct: float
    multiple_jobs_pct: float
    part_time_economic_pct: float


class GigEconomyTracker:
    """Track gig economy trends using CPS data"""

    def __init__(self, cps_client: CPSClient):
        """Initialize with CPS client"""
        self.client = cps_client

    def get_current_gig_stats(
        self,
        year: int,
        month: int,
        state_fips: Optional[str] = None
    ) -> CPSGigEconomyStats:
        """Get current gig economy statistics

        Args:
            year: Year
            month: Month
            state_fips: State FIPS

        Returns:
            CPSGigEconomyStats object
        """
        return self.client.get_cps_gig_economy_stats(
            year=year,
            month=month,
            state_fips=state_fips
        )

    def track_trends(
        self,
        year_month_pairs: List[tuple],
        state_fips: Optional[str] = None
    ) -> List[GigEconomyTrend]:
        """Track gig economy trends over time

        Args:
            year_month_pairs: List of (year, month) tuples
            state_fips: State FIPS

        Returns:
            List of GigEconomyTrend objects
        """
        trends = []

        for year, month in year_month_pairs:
            try:
                stats = self.get_current_gig_stats(year, month, state_fips)

                trends.append(GigEconomyTrend(
                    time_period=f"{year}-{month:02d}",
                    gig_estimate=stats.gig_economy_estimate,
                    self_employed_pct=stats.pct_self_employed,
                    multiple_jobs_pct=stats.pct_multiple_jobs,
                    part_time_economic_pct=stats.pct_part_time_economic
                ))
            except Exception as e:
                print(f"Error fetching data for {year}-{month}: {e}")
                continue

        return trends

    def compare_states(
        self,
        year: int,
        month: int,
        state_fips_list: List[str]
    ) -> List[CPSGigEconomyStats]:
        """Compare gig economy across states

        Args:
            year: Year
            month: Month
            state_fips_list: List of state FIPS codes

        Returns:
            List of CPSGigEconomyStats, sorted by gig economy estimate
        """
        results = []

        for fips in state_fips_list:
            try:
                stats = self.get_current_gig_stats(year, month, state_fips=fips)
                results.append(stats)
            except Exception as e:
                print(f"Error fetching data for {fips}: {e}")
                continue

        # Sort by gig economy estimate (descending)
        results.sort(key=lambda x: x.gig_economy_estimate, reverse=True)

        return results

    def analyze_by_demographics(
        self,
        year: int,
        month: int,
        state_fips: Optional[str] = None
    ) -> Dict[str, any]:
        """Analyze gig economy by demographics

        Note: Detailed demographic breakdowns require CPS ASEC supplement
        or custom tabulations. This provides basic state-level analysis.

        Args:
            year: Year
            month: Month
            state_fips: State FIPS

        Returns:
            Dictionary with demographic analysis
        """
        stats = self.get_current_gig_stats(year, month, state_fips)

        return {
            "year": year,
            "month": month,
            "geography": self.client._get_state_name(state_fips) if state_fips else "United States",
            "gig_economy_estimate": stats.gig_economy_estimate,
            "total_employed": stats.total_employed,
            "self_employed": stats.self_employed,
            "multiple_jobs": stats.multiple_job_holders,
            "part_time_economic": stats.part_time_economic_reasons,
            "insights": [
                f"{stats.pct_self_employed:.1f}% of workers are self-employed",
                f"{stats.pct_multiple_jobs:.1f}% hold multiple jobs",
                f"{stats.pct_part_time_economic:.1f}% work part-time for economic reasons",
                f"Estimated gig economy: {stats.gig_economy_estimate:.1f}% of workforce"
            ],
            "note": "For age/education breakdowns, use CPS ASEC supplement or custom tabulations"
        }

    def generate_gig_report(
        self,
        year: int,
        month: int,
        state_fips: Optional[str] = None,
        include_trends: bool = False,
        trend_months: int = 12
    ) -> Dict[str, any]:
        """Generate comprehensive gig economy report

        Args:
            year: Year
            month: Month
            state_fips: State FIPS
            include_trends: Include historical trends
            trend_months: Number of months to include in trends

        Returns:
            Dictionary with gig economy report
        """
        current_stats = self.get_current_gig_stats(year, month, state_fips)

        report = {
            "year": year,
            "month": month,
            "geography": self.client._get_state_name(state_fips) if state_fips else "United States",
            "current_stats": current_stats,
            "summary": {
                "gig_workers_estimate": current_stats.gig_economy_estimate,
                "self_employed_count": current_stats.self_employed,
                "multiple_job_holders": current_stats.multiple_job_holders,
                "part_time_economic": current_stats.part_time_economic_reasons
            }
        }

        if include_trends:
            # Generate last N months
            year_month_pairs = []
            for i in range(trend_months):
                m = month - i
                y = year
                while m < 1:
                    m += 12
                    y -= 1
                year_month_pairs.append((y, m))

            trends = self.track_trends(year_month_pairs, state_fips)
            report["trends"] = trends

        return report
