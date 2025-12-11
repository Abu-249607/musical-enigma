"""
Gender Metrics Analytics

Analyzes gender gaps across fields, occupations, and sectors with
employment rates, earnings gaps, and representation metrics.
"""

from typing import List, Optional, Dict
import pandas as pd
import logging

from ..census_client.acs_pums_client import ACSPUMSClient
from ..models.field_of_study import GenderGap

logger = logging.getLogger(__name__)


class GenderMetricsAnalyzer:
    """Analyze gender gaps and representation across fields, occupations, and sectors"""

    def __init__(self, pums_client: Optional[ACSPUMSClient] = None):
        """Initialize analyzer

        Args:
            pums_client: ACS PUMS client. If None, creates default client.
        """
        self.pums = pums_client or ACSPUMSClient()

    def analyze_field_gender_gap(
        self,
        field_code: str,
        education_level: str = "23",
        state_code: Optional[str] = None
    ) -> Optional[GenderGap]:
        """Analyze gender gap for a specific field of study

        Args:
            field_code: CIP code
            education_level: SCHL code (default "23" = Bachelor's)
            state_code: State filter or None for national

        Returns:
            GenderGap object or None if insufficient data
        """
        # Get male outcomes
        male_outcomes = self.pums.get_field_of_study_outcomes(
            field_codes=[field_code],
            education_level=education_level,
            sex="1",
            state_code=state_code,
            min_sample_size=50
        )

        # Get female outcomes
        female_outcomes = self.pums.get_field_of_study_outcomes(
            field_codes=[field_code],
            education_level=education_level,
            sex="2",
            state_code=state_code,
            min_sample_size=50
        )

        if not male_outcomes or not female_outcomes:
            logger.warning(f"Insufficient data for gender gap analysis: field {field_code}")
            return None

        male = male_outcomes[0]
        female = female_outcomes[0]

        return self._create_gender_gap(
            segment_type="field",
            segment_code=field_code,
            segment_name=male.field_name,
            male_outcome=male,
            female_outcome=female
        )

    def compare_stem_vs_non_stem_gaps(
        self,
        education_level: str = "23",
        state_code: Optional[str] = None
    ) -> Dict[str, List[GenderGap]]:
        """Compare gender gaps in STEM vs non-STEM fields

        Args:
            education_level: SCHL code
            state_code: State filter or None for national

        Returns:
            Dict with 'stem' and 'non_stem' keys containing lists of GenderGap objects
        """
        # Get all fields
        all_fields = self.pums.get_field_of_study_outcomes(
            field_codes=None,
            education_level=education_level,
            state_code=state_code,
            min_sample_size=100
        )

        stem_gaps = []
        non_stem_gaps = []

        for field in all_fields:
            gap = self.analyze_field_gender_gap(
                field_code=field.field_code,
                education_level=education_level,
                state_code=state_code
            )

            if gap:
                if self.pums.cip_loader.is_stem(field.field_code):
                    stem_gaps.append(gap)
                else:
                    non_stem_gaps.append(gap)

        return {
            'stem': sorted(stem_gaps, key=lambda x: x.pct_female),
            'non_stem': sorted(non_stem_gaps, key=lambda x: x.pct_female)
        }

    def find_most_gender_balanced_fields(
        self,
        education_level: str = "23",
        state_code: Optional[str] = None,
        top_n: int = 10
    ) -> List[GenderGap]:
        """Find fields with most balanced gender representation

        Args:
            education_level: SCHL code
            state_code: State filter or None for national
            top_n: Number of fields to return

        Returns:
            List of GenderGap objects sorted by proximity to 50% female
        """
        # Get all fields
        all_fields = self.pums.get_field_of_study_outcomes(
            field_codes=None,
            education_level=education_level,
            state_code=state_code,
            min_sample_size=100
        )

        gaps = []
        for field in all_fields:
            gap = self.analyze_field_gender_gap(
                field_code=field.field_code,
                education_level=education_level,
                state_code=state_code
            )
            if gap:
                # Calculate distance from 50%
                gap.balance_score = abs(50 - gap.pct_female)
                gaps.append(gap)

        # Sort by balance score (closest to 50% first)
        gaps.sort(key=lambda x: x.balance_score)

        return gaps[:top_n]

    def find_largest_earnings_gaps(
        self,
        education_level: str = "23",
        state_code: Optional[str] = None,
        top_n: int = 10
    ) -> List[GenderGap]:
        """Find fields with largest gender pay gaps

        Args:
            education_level: SCHL code
            state_code: State filter or None for national
            top_n: Number of fields to return

        Returns:
            List of GenderGap objects sorted by earnings gap (largest first)
        """
        # Get all fields
        all_fields = self.pums.get_field_of_study_outcomes(
            field_codes=None,
            education_level=education_level,
            state_code=state_code,
            min_sample_size=100
        )

        gaps = []
        for field in all_fields:
            gap = self.analyze_field_gender_gap(
                field_code=field.field_code,
                education_level=education_level,
                state_code=state_code
            )
            if gap and gap.earnings_gap_pct is not None:
                gaps.append(gap)

        # Sort by earnings gap percentage (largest gap first)
        gaps.sort(key=lambda x: x.earnings_gap_pct, reverse=True)

        return gaps[:top_n]

    def find_most_female_dominated_fields(
        self,
        education_level: str = "23",
        state_code: Optional[str] = None,
        top_n: int = 10
    ) -> List[GenderGap]:
        """Find fields with highest female representation

        Args:
            education_level: SCHL code
            state_code: State filter or None for national
            top_n: Number of fields to return

        Returns:
            List of GenderGap objects sorted by % female (highest first)
        """
        # Get all fields
        all_fields = self.pums.get_field_of_study_outcomes(
            field_codes=None,
            education_level=education_level,
            state_code=state_code,
            min_sample_size=100
        )

        gaps = []
        for field in all_fields:
            gap = self.analyze_field_gender_gap(
                field_code=field.field_code,
                education_level=education_level,
                state_code=state_code
            )
            if gap:
                gaps.append(gap)

        # Sort by pct_female descending
        gaps.sort(key=lambda x: x.pct_female, reverse=True)

        return gaps[:top_n]

    def find_most_male_dominated_fields(
        self,
        education_level: str = "23",
        state_code: Optional[str] = None,
        top_n: int = 10
    ) -> List[GenderGap]:
        """Find fields with highest male representation

        Args:
            education_level: SCHL code
            state_code: State filter or None for national
            top_n: Number of fields to return

        Returns:
            List of GenderGap objects sorted by % female (lowest first)
        """
        # Get all fields
        all_fields = self.pums.get_field_of_study_outcomes(
            field_codes=None,
            education_level=education_level,
            state_code=state_code,
            min_sample_size=100
        )

        gaps = []
        for field in all_fields:
            gap = self.analyze_field_gender_gap(
                field_code=field.field_code,
                education_level=education_level,
                state_code=state_code
            )
            if gap:
                gaps.append(gap)

        # Sort by pct_female ascending
        gaps.sort(key=lambda x: x.pct_female)

        return gaps[:top_n]

    def _create_gender_gap(
        self,
        segment_type: str,
        segment_code: str,
        segment_name: str,
        male_outcome,
        female_outcome
    ) -> GenderGap:
        """Create GenderGap object from male and female outcomes

        Args:
            segment_type: "field", "occupation", or "sector"
            segment_code: Code identifier
            segment_name: Display name
            male_outcome: Male FieldOfStudyOutcome
            female_outcome: Female FieldOfStudyOutcome

        Returns:
            GenderGap object
        """
        # Calculate gaps
        employment_gap = male_outcome.employment_rate - female_outcome.employment_rate
        unemployment_gap = male_outcome.unemployment_rate - female_outcome.unemployment_rate

        # Earnings gap
        if male_outcome.median_earnings and female_outcome.median_earnings:
            earnings_gap_pct = (
                (male_outcome.median_earnings - female_outcome.median_earnings)
                / male_outcome.median_earnings * 100
            )
        else:
            earnings_gap_pct = None

        # Female representation
        total_pop = male_outcome.total_population + female_outcome.total_population
        pct_female = (female_outcome.total_population / total_pop * 100) if total_pop > 0 else 0.0

        return GenderGap(
            segment_type=segment_type,
            segment_code=segment_code,
            segment_name=segment_name,
            year=male_outcome.year,
            geography=male_outcome.geography_name,
            male_employment_rate=male_outcome.employment_rate,
            male_unemployment_rate=male_outcome.unemployment_rate,
            male_median_earnings=male_outcome.median_earnings,
            male_sample_size=male_outcome.sample_size,
            female_employment_rate=female_outcome.employment_rate,
            female_unemployment_rate=female_outcome.unemployment_rate,
            female_median_earnings=female_outcome.median_earnings,
            female_sample_size=female_outcome.sample_size,
            employment_rate_gap=round(employment_gap, 2),
            unemployment_rate_gap=round(unemployment_gap, 2),
            earnings_gap_pct=round(earnings_gap_pct, 1) if earnings_gap_pct is not None else None,
            pct_female=round(pct_female, 1),
            data_source=male_outcome.data_source
        )
