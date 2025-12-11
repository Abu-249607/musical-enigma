"""
Sector Analytics

Analyzes employment distribution across industries/sectors with
education and field-of-study filters.
"""

from typing import List, Optional, Dict
import pandas as pd
import logging

from ..census_client.acs_pums_client import ACSPUMSClient
from ..models.field_of_study import SectorEmploymentByEducation

logger = logging.getLogger(__name__)


class SectorAnalyzer:
    """Analyze employment by industry/sector with education and field filters"""

    def __init__(self, pums_client: Optional[ACSPUMSClient] = None):
        """Initialize analyzer

        Args:
            pums_client: ACS PUMS client. If None, creates default client.
        """
        self.pums = pums_client or ACSPUMSClient()

    def get_sector_employment_by_field(
        self,
        field_code: str,
        education_level: str = "23",
        state_code: Optional[str] = None,
        top_n: int = 10
    ) -> List[Dict]:
        """Get top sectors employing graduates from a specific field

        Args:
            field_code: CIP code
            education_level: SCHL code (default "23" = Bachelor's)
            state_code: State filter or None for national
            top_n: Number of top sectors to return

        Returns:
            List of sector dictionaries with employment counts and percentages
        """
        sectors = self.pums.get_sector_distribution(
            field_code=field_code,
            education_level=education_level,
            state_code=state_code
        )

        return sectors[:top_n]

    def get_tech_sector_education_breakdown(
        self,
        state_code: Optional[str] = None
    ) -> List[Dict]:
        """Analyze education levels in technology sector

        Args:
            state_code: State filter or None for national

        Returns:
            List of education level breakdowns for tech sector
        """
        # Load data
        df = self.pums.load_state(state_code) if state_code else self.pums.load_national()

        # Filter to employed workers only
        df = df[df['ESR'].isin([1, 2])]

        # Filter to tech sectors (using NAICS loader)
        df = df[df['NAICSP'].notna()]

        # Check which industries are tech
        tech_industries = []
        for naics_code in df['NAICSP'].unique():
            if pd.notna(naics_code):
                naics_str = str(int(naics_code))
                if self.pums.naics_loader.is_tech_sector(naics_str):
                    tech_industries.append(naics_code)

        # Filter to tech industries
        df_tech = df[df['NAICSP'].isin(tech_industries)]

        if len(df_tech) == 0:
            return []

        # Group by education level
        results = []
        total_tech = df_tech['PWGTP'].sum()

        for schl_code, group in df_tech.groupby('SCHL'):
            if pd.notna(schl_code):
                count = group['PWGTP'].sum()
                pct = count / total_tech * 100

                schl_str = str(int(schl_code))
                edu_level = self.pums.EDUCATION_LEVELS.get(schl_str, f"SCHL {schl_str}")

                # Median earnings
                earnings_data = group[group['WAGP'] > 0]['WAGP']
                median_earnings = int(earnings_data.median()) if len(earnings_data) > 0 else None

                results.append({
                    'education_level': edu_level,
                    'education_code': schl_str,
                    'count': int(count),
                    'pct_of_tech_sector': round(pct, 1),
                    'median_earnings': median_earnings,
                    'sample_size': len(group)
                })

        # Sort by count descending
        results.sort(key=lambda x: x['count'], reverse=True)

        return results

    def get_field_distribution_in_sector(
        self,
        sector_code: str,
        education_level: str = "23",
        state_code: Optional[str] = None,
        top_n: int = 10
    ) -> List[Dict]:
        """Analyze which fields of study work in a specific sector

        Args:
            sector_code: NAICS code (e.g., "5112" for Software Publishers)
            education_level: SCHL code
            state_code: State filter or None for national
            top_n: Number of top fields to return

        Returns:
            List of field distributions in the sector
        """
        # Load data
        df = self.pums.load_state(state_code) if state_code else self.pums.load_national()

        # Filter to employed workers in this sector and education level
        df = df[df['ESR'].isin([1, 2])]
        df = df[df['SCHL'] == int(education_level)]
        df = df[df['NAICSP'] == int(sector_code)]
        df = df[df['FOD1P'].notna()]

        if len(df) == 0:
            logger.warning(f"No data found for sector {sector_code}")
            return []

        # Group by field of study
        total_in_sector = df['PWGTP'].sum()

        results = []
        for fod_code, group in df.groupby('FOD1P'):
            count = group['PWGTP'].sum()
            pct = count / total_in_sector * 100

            fod_str = str(int(fod_code))
            field_name = self.pums.cip_loader.get_title(fod_str) or f"Field {fod_str}"

            # Median earnings
            earnings_data = group[group['WAGP'] > 0]['WAGP']
            median_earnings = int(earnings_data.median()) if len(earnings_data) > 0 else None

            results.append({
                'field_code': fod_str,
                'field_name': field_name,
                'count': int(count),
                'pct_of_sector': round(pct, 1),
                'median_earnings': median_earnings,
                'sample_size': len(group)
            })

        # Sort by count descending
        results.sort(key=lambda x: x['count'], reverse=True)

        return results[:top_n]

    def compare_sectors_by_field(
        self,
        field_codes: List[str],
        education_level: str = "23",
        state_code: Optional[str] = None
    ) -> Dict[str, List[Dict]]:
        """Compare sector distributions across multiple fields

        Args:
            field_codes: List of CIP codes to compare
            education_level: SCHL code
            state_code: State filter or None for national

        Returns:
            Dict mapping field_code to list of sector distributions
        """
        results = {}

        for field_code in field_codes:
            sectors = self.get_sector_employment_by_field(
                field_code=field_code,
                education_level=education_level,
                state_code=state_code,
                top_n=10
            )
            results[field_code] = sectors

        return results

    def get_gender_breakdown_by_sector(
        self,
        sector_code: str,
        education_level: str = "23",
        state_code: Optional[str] = None
    ) -> Dict:
        """Analyze gender distribution in a specific sector

        Args:
            sector_code: NAICS code
            education_level: SCHL code
            state_code: State filter or None for national

        Returns:
            Dict with male/female counts, percentages, and earnings
        """
        # Load data
        df = self.pums.load_state(state_code) if state_code else self.pums.load_national()

        # Filter to employed workers in this sector and education level
        df = df[df['ESR'].isin([1, 2])]
        df = df[df['SCHL'] == int(education_level)]
        df = df[df['NAICSP'] == int(sector_code)]

        if len(df) == 0:
            return {}

        total_count = df['PWGTP'].sum()

        # Male statistics
        male_df = df[df['SEX'] == 1]
        male_count = male_df['PWGTP'].sum()
        male_pct = (male_count / total_count * 100) if total_count > 0 else 0

        male_earnings_data = male_df[male_df['WAGP'] > 0]['WAGP']
        male_median_earnings = int(male_earnings_data.median()) if len(male_earnings_data) > 0 else None

        # Female statistics
        female_df = df[df['SEX'] == 2]
        female_count = female_df['PWGTP'].sum()
        female_pct = (female_count / total_count * 100) if total_count > 0 else 0

        female_earnings_data = female_df[female_df['WAGP'] > 0]['WAGP']
        female_median_earnings = int(female_earnings_data.median()) if len(female_earnings_data) > 0 else None

        # Calculate gap
        if male_median_earnings and female_median_earnings:
            earnings_gap_pct = (
                (male_median_earnings - female_median_earnings) / male_median_earnings * 100
            )
        else:
            earnings_gap_pct = None

        sector_name = self.pums.naics_loader.get_title(sector_code) or f"Sector {sector_code}"

        return {
            'sector_code': sector_code,
            'sector_name': sector_name,
            'total_count': int(total_count),
            'male_count': int(male_count),
            'male_pct': round(male_pct, 1),
            'male_median_earnings': male_median_earnings,
            'female_count': int(female_count),
            'female_pct': round(female_pct, 1),
            'female_median_earnings': female_median_earnings,
            'earnings_gap_pct': round(earnings_gap_pct, 1) if earnings_gap_pct else None,
            'sample_size': len(df)
        }
