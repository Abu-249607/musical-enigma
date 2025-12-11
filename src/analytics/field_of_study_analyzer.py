"""
Field-of-Study Analytics

Provides high-level analytics for comparing fields of study, analyzing ROI,
gender gaps, occupation pathways, and sector distributions.
"""

from typing import List, Optional, Dict, Tuple
import pandas as pd
import logging

from ..census_client.acs_pums_client import ACSPUMSClient
from ..models.field_of_study import (
    FieldOfStudyOutcome,
    FieldROIComparison,
    GenderGap,
    OccupationEducationCrosstab
)

logger = logging.getLogger(__name__)


class FieldOfStudyAnalyzer:
    """Analyze employment outcomes by field of study with gender and sector breakdowns"""

    def __init__(self, pums_client: Optional[ACSPUMSClient] = None):
        """Initialize analyzer

        Args:
            pums_client: ACS PUMS client. If None, creates default client.
        """
        self.pums = pums_client or ACSPUMSClient()

    def compare_fields(
        self,
        field_codes: List[str],
        education_level: str = "23",
        state_code: Optional[str] = None,
        include_gender_breakdown: bool = False
    ) -> FieldROIComparison:
        """Compare multiple fields of study side-by-side

        Args:
            field_codes: List of CIP codes to compare (e.g., ["1107", "1401"])
            education_level: SCHL code (default "23" = Bachelor's)
            state_code: State filter or None for national
            include_gender_breakdown: Include gender-specific outcomes

        Returns:
            FieldROIComparison with all fields and rankings
        """
        # Get outcomes for all fields
        all_outcomes = self.pums.get_field_of_study_outcomes(
            field_codes=field_codes,
            education_level=education_level,
            state_code=state_code
        )

        if len(all_outcomes) == 0:
            raise ValueError(f"No data found for field codes: {field_codes}")

        # Add gender breakdowns if requested
        if include_gender_breakdown:
            for field_code in field_codes:
                # Male outcomes
                male_outcomes = self.pums.get_field_of_study_outcomes(
                    field_codes=[field_code],
                    education_level=education_level,
                    sex="1",
                    state_code=state_code
                )
                if male_outcomes:
                    all_outcomes.extend(male_outcomes)

                # Female outcomes
                female_outcomes = self.pums.get_field_of_study_outcomes(
                    field_codes=[field_code],
                    education_level=education_level,
                    sex="2",
                    state_code=state_code
                )
                if female_outcomes:
                    all_outcomes.extend(female_outcomes)

        # Find best performers
        overall_outcomes = [o for o in all_outcomes if o.sex is None]

        if len(overall_outcomes) == 0:
            raise ValueError("No overall outcomes found")

        highest_employment = max(overall_outcomes, key=lambda x: x.employment_rate)

        # Highest earnings (only if earnings data available)
        earnings_outcomes = [o for o in overall_outcomes if o.median_earnings is not None]
        highest_earnings = max(earnings_outcomes, key=lambda x: x.median_earnings) if earnings_outcomes else None

        # Calculate composite ROI score (employment rate + earnings percentile)
        if earnings_outcomes:
            earnings_values = [o.median_earnings for o in earnings_outcomes]
            min_earnings = min(earnings_values)
            max_earnings = max(earnings_values)
            earnings_range = max_earnings - min_earnings if max_earnings > min_earnings else 1

            for outcome in earnings_outcomes:
                earnings_pct = ((outcome.median_earnings - min_earnings) / earnings_range) * 50
                employment_pct = outcome.employment_rate / 2  # Scale to 0-50
                outcome.roi_score = earnings_pct + employment_pct

            best_roi = max(earnings_outcomes, key=lambda x: getattr(x, 'roi_score', 0))
        else:
            best_roi = highest_employment

        # Calculate ranges
        employment_rates = [o.employment_rate for o in overall_outcomes]
        employment_range = (min(employment_rates), max(employment_rates))

        if earnings_outcomes:
            earnings_range = (
                min(o.median_earnings for o in earnings_outcomes),
                max(o.median_earnings for o in earnings_outcomes)
            )
        else:
            earnings_range = None

        return FieldROIComparison(
            degree_level=overall_outcomes[0].degree_level,
            year=overall_outcomes[0].year,
            geography=overall_outcomes[0].geography_name,
            fields=all_outcomes,
            highest_employment_rate=highest_employment.field_code,
            highest_median_earnings=highest_earnings.field_code if highest_earnings else None,
            best_roi_overall=best_roi.field_code,
            employment_rate_range=employment_range,
            earnings_range=earnings_range,
            data_source=overall_outcomes[0].data_source
        )

    def analyze_gender_gap(
        self,
        field_code: str,
        education_level: str = "23",
        state_code: Optional[str] = None
    ) -> Optional[GenderGap]:
        """Analyze gender gap for a specific field

        Args:
            field_code: CIP code
            education_level: SCHL code
            state_code: State filter or None for national

        Returns:
            GenderGap object with male vs female metrics, or None if insufficient data
        """
        # Get male outcomes
        male_outcomes = self.pums.get_field_of_study_outcomes(
            field_codes=[field_code],
            education_level=education_level,
            sex="1",
            state_code=state_code
        )

        # Get female outcomes
        female_outcomes = self.pums.get_field_of_study_outcomes(
            field_codes=[field_code],
            education_level=education_level,
            sex="2",
            state_code=state_code
        )

        if not male_outcomes or not female_outcomes:
            logger.warning(f"Insufficient data for gender gap analysis: field {field_code}")
            return None

        male = male_outcomes[0]
        female = female_outcomes[0]

        # Calculate gaps
        employment_gap = male.employment_rate - female.employment_rate
        unemployment_gap = male.unemployment_rate - female.unemployment_rate

        # Earnings gap (only if both have earnings data)
        if male.median_earnings and female.median_earnings:
            earnings_gap_pct = ((male.median_earnings - female.median_earnings) / male.median_earnings) * 100
        else:
            earnings_gap_pct = None

        # Female representation
        total_pop = male.total_population + female.total_population
        pct_female = (female.total_population / total_pop * 100) if total_pop > 0 else 0.0

        return GenderGap(
            segment_type="field",
            segment_code=field_code,
            segment_name=male.field_name,
            year=male.year,
            geography=male.geography_name,
            male_employment_rate=male.employment_rate,
            male_unemployment_rate=male.unemployment_rate,
            male_median_earnings=male.median_earnings,
            male_sample_size=male.sample_size,
            female_employment_rate=female.employment_rate,
            female_unemployment_rate=female.unemployment_rate,
            female_median_earnings=female.median_earnings,
            female_sample_size=female.sample_size,
            employment_rate_gap=round(employment_gap, 2),
            unemployment_rate_gap=round(unemployment_gap, 2),
            earnings_gap_pct=round(earnings_gap_pct, 1) if earnings_gap_pct is not None else None,
            pct_female=round(pct_female, 1),
            data_source=male.data_source
        )

    def get_occupation_pathways(
        self,
        field_code: str,
        education_level: str = "23",
        state_code: Optional[str] = None,
        top_n: int = 10
    ) -> List[Dict]:
        """Get top occupation pathways for field graduates

        Args:
            field_code: CIP code
            education_level: SCHL code
            state_code: State filter or None for national
            top_n: Number of top occupations to return

        Returns:
            List of occupation dictionaries with counts, percentages, earnings
        """
        occupations = self.pums.get_occupation_pipeline(
            field_code=field_code,
            education_level=education_level,
            state_code=state_code
        )

        return occupations[:top_n]

    def get_sector_distribution(
        self,
        field_code: str,
        education_level: str = "23",
        state_code: Optional[str] = None,
        top_n: int = 10
    ) -> List[Dict]:
        """Get top sectors/industries employing field graduates

        Args:
            field_code: CIP code
            education_level: SCHL code
            state_code: State filter or None for national
            top_n: Number of top sectors to return

        Returns:
            List of sector dictionaries with counts, percentages, earnings
        """
        sectors = self.pums.get_sector_distribution(
            field_code=field_code,
            education_level=education_level,
            state_code=state_code
        )

        return sectors[:top_n]

    def get_all_fields(
        self,
        education_level: str = "23",
        state_code: Optional[str] = None,
        min_sample_size: int = 100
    ) -> List[FieldOfStudyOutcome]:
        """Get outcomes for all available fields

        Args:
            education_level: SCHL code
            state_code: State filter or None for national
            min_sample_size: Minimum sample size to include

        Returns:
            List of all field outcomes sorted by employment rate
        """
        return self.pums.get_field_of_study_outcomes(
            field_codes=None,  # All fields
            education_level=education_level,
            state_code=state_code,
            min_sample_size=min_sample_size
        )

    def search_fields_by_stem(
        self,
        education_level: str = "23",
        state_code: Optional[str] = None,
        stem_only: bool = True
    ) -> List[FieldOfStudyOutcome]:
        """Get STEM or non-STEM fields

        Args:
            education_level: SCHL code
            state_code: State filter or None for national
            stem_only: True for STEM fields, False for non-STEM

        Returns:
            List of field outcomes filtered by STEM status
        """
        # Get all fields
        all_fields = self.get_all_fields(
            education_level=education_level,
            state_code=state_code
        )

        # Filter by STEM status
        cip_loader = self.pums.cip_loader
        filtered = []

        for field in all_fields:
            is_stem = cip_loader.is_stem(field.field_code)
            if is_stem == stem_only:
                filtered.append(field)

        return filtered

    def compare_gender_across_fields(
        self,
        field_codes: List[str],
        education_level: str = "23",
        state_code: Optional[str] = None
    ) -> List[GenderGap]:
        """Compare gender gaps across multiple fields

        Args:
            field_codes: List of CIP codes
            education_level: SCHL code
            state_code: State filter or None for national

        Returns:
            List of GenderGap objects, one per field
        """
        gaps = []

        for field_code in field_codes:
            gap = self.analyze_gender_gap(
                field_code=field_code,
                education_level=education_level,
                state_code=state_code
            )
            if gap:
                gaps.append(gap)

        # Sort by female representation (ascending = most male-dominated first)
        gaps.sort(key=lambda x: x.pct_female)

        return gaps
