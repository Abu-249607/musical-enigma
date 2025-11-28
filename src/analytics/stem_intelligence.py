"""STEM Career Intelligence Hub.

Analyzes STEM employment trends, gender gaps, education pathways,
and geographic concentrations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..census_client import CensusMCPClient
from ..models.citation import Citation
from ..models.employment_datasets import (
    STEM_OCCUPATION_CODES,
    TABLE_B24010,
    TABLE_S1502,
    TABLE_B24011,
)


@dataclass
class STEMOccupationData:
    """Data for a specific STEM occupation."""
    occupation_name: str
    variable_code: str
    male_count: int
    female_count: int
    total_count: int
    female_percentage: float
    geography_name: str
    year: int
    citation: Citation


@dataclass
class STEMFieldData:
    """Data for STEM degree fields."""
    field_name: str
    total_with_degree: int
    employment_rate: float
    median_earnings: Optional[int]
    geography_name: str
    year: int
    citation: Citation


@dataclass
class STEMGenderGap:
    """Gender gap analysis for STEM occupations."""
    occupation_name: str
    total_workers: int
    female_count: int
    male_count: int
    female_percentage: float
    gender_gap_score: float  # 50% = parity, higher = more female, lower = more male
    geography_name: str
    year: int


@dataclass
class STEMCareerPathway:
    """Maps education field to occupation outcomes."""
    degree_field: str
    total_graduates: int
    employment_rate: float
    top_occupations: List[Dict[str, any]]
    median_earnings: Optional[int]
    geography_name: str
    year: int


class STEMIntelligenceHub:
    """Comprehensive STEM career and employment intelligence.

    Features:
    - STEM occupation trends and gender gaps
    - Field-to-job pipeline analysis
    - Geographic STEM talent concentration
    - STEM earnings and growth projections
    """

    def __init__(self, census_client: Optional[CensusMCPClient] = None, api_key: Optional[str] = None):
        """Initialize STEM intelligence hub.

        Args:
            census_client: Pre-configured Census client
            api_key: Census API key (if client not provided)
        """
        self.client = census_client or CensusMCPClient(api_key=api_key)

    def get_stem_occupations(
        self,
        geography_name: str,
        year: int = 2024,
        dataset: str = "acs/acs1",
    ) -> List[STEMOccupationData]:
        """Get detailed STEM occupation employment data.

        Args:
            geography_name: State or region name
            year: Data year
            dataset: ACS dataset

        Returns:
            List of STEM occupation data with gender breakdowns
        """
        # Resolve geography
        fips_info = self.client.resolve_fips(geography_name)
        if not fips_info:
            raise ValueError(f"Could not resolve geography: {geography_name}")

        fips_code = fips_info["fips"]
        resolved_name = fips_info["name"]

        # Build variable list for STEM occupations
        variables = ["NAME"] + list(STEM_OCCUPATION_CODES.keys())

        # Fetch data
        try:
            data = self.client._call_census_api(
                dataset=dataset,
                year=year,
                variables=variables,
                geography_for=f"state:{fips_code}",
            )
        except Exception as e:
            raise RuntimeError(f"Failed to fetch STEM occupation data: {e}")

        headers = data[0]
        values = data[1]

        # Parse STEM occupations
        stem_occupations = []

        # Group by occupation type (male and female versions)
        occupation_pairs = {
            "Computer and mathematical": ("B24010_011E", "B24010_086E"),
            "Architecture and engineering": ("B24010_015E", "B24010_090E"),
            "Life, physical, and social science": ("B24010_019E", "B24010_094E"),
        }

        for occ_name, (male_code, female_code) in occupation_pairs.items():
            try:
                male_idx = headers.index(male_code)
                female_idx = headers.index(female_code)

                male_count = int(values[male_idx]) if values[male_idx] else 0
                female_count = int(values[female_idx]) if values[female_idx] else 0
                total = male_count + female_count

                female_pct = (female_count / total * 100) if total > 0 else 0

                # Create citation
                citation = self.client._create_citation(
                    dataset=dataset,
                    year=year,
                    variables=[male_code, female_code],
                    geography="state",
                    geography_name=resolved_name,
                    fips_code=fips_code,
                )

                stem_occupations.append(STEMOccupationData(
                    occupation_name=occ_name,
                    variable_code=male_code,
                    male_count=male_count,
                    female_count=female_count,
                    total_count=total,
                    female_percentage=female_pct,
                    geography_name=resolved_name,
                    year=year,
                    citation=citation,
                ))

            except (ValueError, IndexError) as e:
                print(f"Warning: Could not parse {occ_name}: {e}")
                continue

        return stem_occupations

    def analyze_stem_gender_gap(
        self,
        geography_name: str,
        year: int = 2024,
    ) -> List[STEMGenderGap]:
        """Analyze gender gaps in STEM occupations.

        Args:
            geography_name: State or region
            year: Data year

        Returns:
            List of gender gap analyses
        """
        stem_data = self.get_stem_occupations(geography_name, year)

        gaps = []
        for occ in stem_data:
            # Calculate gender gap score (50 = parity)
            gap_score = occ.female_percentage

            gaps.append(STEMGenderGap(
                occupation_name=occ.occupation_name,
                total_workers=occ.total_count,
                female_count=occ.female_count,
                male_count=occ.male_count,
                female_percentage=occ.female_percentage,
                gender_gap_score=gap_score,
                geography_name=occ.geography_name,
                year=occ.year,
            ))

        # Sort by gender gap (most imbalanced first)
        gaps.sort(key=lambda x: abs(50 - x.gender_gap_score), reverse=True)

        return gaps

    def get_stem_field_outcomes(
        self,
        geography_name: str,
        year: int = 2024,
    ) -> List[STEMFieldData]:
        """Get employment outcomes for STEM degree fields.

        Uses Table S1502 (Field of Bachelor's Degree).

        Args:
            geography_name: State or region
            year: Data year

        Returns:
            List of STEM field employment outcomes
        """
        fips_info = self.client.resolve_fips(geography_name)
        if not fips_info:
            raise ValueError(f"Could not resolve geography: {geography_name}")

        fips_code = fips_info["fips"]
        resolved_name = fips_info["name"]

        # S1502 variables for STEM fields
        variables = [
            "NAME",
            "S1502_C01_002E",  # Science and Engineering - total
            "S1502_C02_002E",  # Science and Engineering - employment rate
            "S1502_C01_003E",  # Science and Engineering Related - total
            "S1502_C02_003E",  # Science and Engineering Related - employment rate
        ]

        try:
            data = self.client._call_census_api(
                dataset="acs/acs1",
                year=year,
                variables=variables,
                geography_for=f"state:{fips_code}",
            )
        except Exception as e:
            # Try 5-year if 1-year fails
            data = self.client._call_census_api(
                dataset="acs/acs5",
                year=year,
                variables=variables,
                geography_for=f"state:{fips_code}",
            )

        headers = data[0]
        values = data[1]

        # Create citation
        citation = self.client._create_citation(
            dataset="acs/acs1",
            year=year,
            variables=variables[1:],
            geography="state",
            geography_name=resolved_name,
            fips_code=fips_code,
        )

        stem_fields = []

        # Parse Science and Engineering
        try:
            se_total_idx = headers.index("S1502_C01_002E")
            se_emp_idx = headers.index("S1502_C02_002E")

            se_total = int(values[se_total_idx]) if values[se_total_idx] else 0
            se_emp_rate = float(values[se_emp_idx]) if values[se_emp_idx] else 0.0

            stem_fields.append(STEMFieldData(
                field_name="Science and Engineering",
                total_with_degree=se_total,
                employment_rate=se_emp_rate,
                median_earnings=None,  # Would need to fetch from earnings table
                geography_name=resolved_name,
                year=year,
                citation=citation,
            ))
        except (ValueError, IndexError):
            pass

        # Parse Science and Engineering Related
        try:
            ser_total_idx = headers.index("S1502_C01_003E")
            ser_emp_idx = headers.index("S1502_C02_003E")

            ser_total = int(values[ser_total_idx]) if values[ser_total_idx] else 0
            ser_emp_rate = float(values[ser_emp_idx]) if values[ser_emp_idx] else 0.0

            stem_fields.append(STEMFieldData(
                field_name="Science and Engineering Related",
                total_with_degree=ser_total,
                employment_rate=ser_emp_rate,
                median_earnings=None,
                geography_name=resolved_name,
                year=year,
                citation=citation,
            ))
        except (ValueError, IndexError):
            pass

        return stem_fields

    def compare_stem_across_states(
        self,
        states: List[str],
        year: int = 2024,
    ) -> Dict[str, List[STEMOccupationData]]:
        """Compare STEM employment across multiple states.

        Args:
            states: List of state names
            year: Data year

        Returns:
            Dictionary mapping state names to STEM occupation data
        """
        results = {}

        for state in states:
            try:
                stem_data = self.get_stem_occupations(state, year)
                results[state] = stem_data
            except Exception as e:
                print(f"Warning: Could not fetch STEM data for {state}: {e}")
                results[state] = []

        return results

    def get_stem_concentration_ranking(
        self,
        states: List[str],
        occupation_name: str,
        year: int = 2024,
    ) -> List[Tuple[str, int, float]]:
        """Rank states by STEM occupation concentration.

        Args:
            states: List of state names
            occupation_name: STEM occupation to analyze
            year: Data year

        Returns:
            List of (state_name, worker_count, percentage) tuples, sorted by count
        """
        comparison = self.compare_stem_across_states(states, year)

        rankings = []
        for state, stem_data in comparison.items():
            for occ in stem_data:
                if occupation_name.lower() in occ.occupation_name.lower():
                    rankings.append((
                        state,
                        occ.total_count,
                        occ.female_percentage,
                    ))
                    break

        # Sort by worker count descending
        rankings.sort(key=lambda x: x[1], reverse=True)

        return rankings

    def get_stem_hot_jobs(
        self,
        geography_name: str,
        year: int = 2024,
        min_workers: int = 1000,
    ) -> List[Dict[str, any]]:
        """Identify hot STEM jobs in a geography.

        Args:
            geography_name: State or region
            year: Data year
            min_workers: Minimum worker count threshold

        Returns:
            List of hot STEM jobs with metadata
        """
        stem_data = self.get_stem_occupations(geography_name, year)

        hot_jobs = []
        for occ in stem_data:
            if occ.total_count >= min_workers:
                hot_jobs.append({
                    "occupation": occ.occupation_name,
                    "total_workers": occ.total_count,
                    "female_percentage": occ.female_percentage,
                    "male_workers": occ.male_count,
                    "female_workers": occ.female_count,
                    "geography": occ.geography_name,
                    "year": occ.year,
                    "citation_id": occ.citation.citation_id,
                })

        # Sort by total workers
        hot_jobs.sort(key=lambda x: x["total_workers"], reverse=True)

        return hot_jobs

    def generate_stem_report(
        self,
        geography_name: str,
        year: int = 2024,
    ) -> Dict[str, any]:
        """Generate comprehensive STEM employment report.

        Args:
            geography_name: State or region
            year: Data year

        Returns:
            Comprehensive report dictionary
        """
        # Get all STEM data
        stem_occupations = self.get_stem_occupations(geography_name, year)
        gender_gaps = self.analyze_stem_gender_gap(geography_name, year)
        field_outcomes = self.get_stem_field_outcomes(geography_name, year)

        # Calculate summary statistics
        total_stem_workers = sum(occ.total_count for occ in stem_occupations)
        total_female_stem = sum(occ.female_count for occ in stem_occupations)
        overall_female_pct = (total_female_stem / total_stem_workers * 100) if total_stem_workers > 0 else 0

        # Find most/least balanced occupations
        most_balanced = min(gender_gaps, key=lambda x: abs(50 - x.gender_gap_score)) if gender_gaps else None
        least_balanced = max(gender_gaps, key=lambda x: abs(50 - x.gender_gap_score)) if gender_gaps else None

        return {
            "geography": geography_name,
            "year": year,
            "generated_at": datetime.utcnow().isoformat(),

            "summary": {
                "total_stem_workers": total_stem_workers,
                "female_stem_workers": total_female_stem,
                "male_stem_workers": total_stem_workers - total_female_stem,
                "overall_female_percentage": overall_female_pct,
            },

            "occupations": [
                {
                    "name": occ.occupation_name,
                    "total": occ.total_count,
                    "female": occ.female_count,
                    "male": occ.male_count,
                    "female_pct": occ.female_percentage,
                    "citation_id": occ.citation.citation_id,
                }
                for occ in stem_occupations
            ],

            "gender_analysis": {
                "most_balanced_occupation": most_balanced.occupation_name if most_balanced else None,
                "most_balanced_percentage": most_balanced.female_percentage if most_balanced else None,
                "least_balanced_occupation": least_balanced.occupation_name if least_balanced else None,
                "least_balanced_percentage": least_balanced.female_percentage if least_balanced else None,
                "all_gaps": [
                    {
                        "occupation": gap.occupation_name,
                        "female_pct": gap.female_percentage,
                        "gap_score": gap.gender_gap_score,
                    }
                    for gap in gender_gaps
                ],
            },

            "degree_fields": [
                {
                    "field": field.field_name,
                    "graduates": field.total_with_degree,
                    "employment_rate": field.employment_rate,
                    "citation_id": field.citation.citation_id,
                }
                for field in field_outcomes
            ],
        }

    def close(self):
        """Close client connections."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
