"""
Geographic Talent Mapper using CPS Basic Monthly data

Maps talent distribution across states and regions, showing where
different skill segments are concentrated.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

from ..census_client.cps_client import CPSClient
from ..models.cps_models import CPSTalentDistribution, CPSEducationEmployment


@dataclass
class TalentHotspot:
    """Talent concentration hotspot"""
    state_fips: str
    state_name: str
    talent_count: int
    concentration_index: float
    rank: int


class GeographicTalentMapper:
    """Map geographic distribution of talent using CPS data"""

    def __init__(self, cps_client: CPSClient):
        """Initialize with CPS client"""
        self.client = cps_client

    def get_talent_distribution(
        self,
        year: int,
        month: int,
        education_level: str,
        state_fips_list: List[str]
    ) -> List[CPSTalentDistribution]:
        """Get talent distribution across multiple states

        Args:
            year: Year
            month: Month
            education_level: Education level code (e.g., "43" for Bachelor's)
            state_fips_list: List of state FIPS codes

        Returns:
            List of CPSTalentDistribution objects
        """
        results = []

        # Get national baseline
        national_stats = self.client.get_cps_education_employment(
            year=year,
            month=month,
            education_level=education_level,
            state_fips=None
        )

        national_labor_force = self.client.get_cps_labor_stats(year, month, state_fips=None)
        national_pct = (national_stats.employed / national_labor_force.employed * 100) if national_labor_force.employed > 0 else 0

        # Get state-level data
        for fips in state_fips_list:
            try:
                state_stats = self.client.get_cps_education_employment(
                    year=year,
                    month=month,
                    education_level=education_level,
                    state_fips=fips
                )

                state_labor_force = self.client.get_cps_labor_stats(year, month, state_fips=fips)
                state_pct = (state_stats.employed / state_labor_force.employed * 100) if state_labor_force.employed > 0 else 0

                # Concentration index: state % / national %
                concentration = (state_pct / national_pct) if national_pct > 0 else 1.0

                results.append(CPSTalentDistribution(
                    state_fips=fips,
                    state_name=self.client._get_state_name(fips),
                    year=year,
                    month=month,
                    talent_category=state_stats.education_level,
                    total_workers=state_stats.employed,
                    concentration_index=round(concentration, 2),
                    pct_of_state_workforce=round(state_pct, 2),
                    avg_age=state_stats.median_age,
                    pct_female=state_stats.pct_female
                ))
            except Exception as e:
                print(f"Error fetching data for {fips}: {e}")
                continue

        # Sort by concentration index (descending)
        results.sort(key=lambda x: x.concentration_index, reverse=True)

        return results

    def identify_talent_hotspots(
        self,
        year: int,
        month: int,
        education_level: str,
        state_fips_list: List[str],
        top_n: int = 10
    ) -> List[TalentHotspot]:
        """Identify top talent concentration hotspots

        Args:
            year: Year
            month: Month
            education_level: Education level code
            state_fips_list: List of state FIPS codes to analyze
            top_n: Number of top hotspots to return

        Returns:
            List of TalentHotspot objects, ranked by concentration
        """
        distribution = self.get_talent_distribution(
            year, month, education_level, state_fips_list
        )

        hotspots = []
        for rank, talent in enumerate(distribution[:top_n], start=1):
            hotspots.append(TalentHotspot(
                state_fips=talent.state_fips,
                state_name=talent.state_name,
                talent_count=talent.total_workers,
                concentration_index=talent.concentration_index,
                rank=rank
            ))

        return hotspots

    def compare_talent_segments(
        self,
        year: int,
        month: int,
        education_levels: List[str],
        state_fips: str
    ) -> Dict[str, CPSTalentDistribution]:
        """Compare different talent segments in a single state

        Args:
            year: Year
            month: Month
            education_levels: List of education level codes
            state_fips: State FIPS code

        Returns:
            Dictionary mapping education level to talent distribution
        """
        results = {}

        for edu_level in education_levels:
            try:
                distribution = self.get_talent_distribution(
                    year, month, edu_level, [state_fips]
                )
                if distribution:
                    results[distribution[0].talent_category] = distribution[0]
            except Exception as e:
                print(f"Error fetching data for level {edu_level}: {e}")
                continue

        return results

    def generate_talent_map_data(
        self,
        year: int,
        month: int,
        education_level: str,
        state_fips_list: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """Generate data suitable for map visualization

        Returns data in a format that can be used by frontend mapping libraries
        (e.g., Plotly, Folium)

        Args:
            year: Year
            month: Month
            education_level: Education level code
            state_fips_list: List of state FIPS codes (None = all states)

        Returns:
            Dictionary with map-ready data
        """
        # If no states specified, use major states
        if state_fips_list is None:
            state_fips_list = [
                "06", "48", "36", "12", "17",  # CA, TX, NY, FL, IL
                "42", "39", "26", "13", "37",  # PA, OH, MI, GA, NC
                "04", "25", "47", "08", "53",  # AZ, MA, TN, CO, WA
            ]

        distribution = self.get_talent_distribution(
            year, month, education_level, state_fips_list
        )

        # Format for choropleth maps
        map_data = {
            "fips_codes": [d.state_fips for d in distribution],
            "state_names": [d.state_name for d in distribution],
            "values": [d.concentration_index for d in distribution],
            "hover_text": [
                f"{d.state_name}<br>"
                f"Workers: {d.total_workers:,}<br>"
                f"Concentration: {d.concentration_index:.2f}x<br>"
                f"% of Workforce: {d.pct_of_state_workforce:.1f}%"
                for d in distribution
            ],
            "metadata": {
                "year": year,
                "month": month,
                "talent_category": distribution[0].talent_category if distribution else "",
                "min_concentration": min([d.concentration_index for d in distribution]) if distribution else 0,
                "max_concentration": max([d.concentration_index for d in distribution]) if distribution else 0,
            }
        }

        return map_data

    def generate_talent_report(
        self,
        year: int,
        month: int,
        education_levels: List[str],
        state_fips_list: List[str]
    ) -> Dict[str, any]:
        """Generate comprehensive talent mapping report

        Args:
            year: Year
            month: Month
            education_levels: List of education level codes
            state_fips_list: List of state FIPS codes

        Returns:
            Dictionary with talent mapping analytics
        """
        report = {
            "year": year,
            "month": month,
            "talent_segments_analyzed": len(education_levels),
            "states_analyzed": len(state_fips_list),
            "segments": {}
        }

        for edu_level in education_levels:
            distribution = self.get_talent_distribution(
                year, month, edu_level, state_fips_list
            )

            if distribution:
                hotspots = self.identify_talent_hotspots(
                    year, month, edu_level, state_fips_list, top_n=5
                )

                report["segments"][distribution[0].talent_category] = {
                    "distribution": distribution,
                    "top_5_hotspots": hotspots,
                    "total_workers_analyzed": sum([d.total_workers for d in distribution]),
                    "highest_concentration": hotspots[0] if hotspots else None
                }

        return report
