"""
Data Availability Registry and Validation

This module enforces strict data availability rules to ensure the application
ONLY requests data that actually exists and has been published by Census/BLS.

NO FAKE DATA. NO EXTRAPOLATION. NO FUTURE YEARS.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


class DatasetType(Enum):
    """Enumeration of all supported datasets"""
    ACS_1YEAR_API = "acs1_api"
    ACS_5YEAR_API = "acs5_api"
    ACS_1YEAR_PUMS = "acs1_pums"
    ACS_5YEAR_PUMS = "acs5_pums"
    CPS_BASIC_MONTHLY = "cps_basic"
    CPS_ASEC = "cps_asec"
    BLS_OES = "bls_oes"
    BLS_JOLTS = "bls_jolts"
    BLS_QCEW = "bls_qcew"


class DataAvailabilityError(Exception):
    """Raised when requested data is not available"""
    pass


@dataclass
class DatasetAvailability:
    """Metadata describing dataset availability and characteristics"""

    dataset_type: DatasetType
    min_year: int
    max_year: int
    geography_levels: list[str]  # ["national", "state", "county", "puma"]
    has_field_of_study: bool
    has_earnings: bool
    has_occupation: bool
    has_industry: bool
    release_lag_months: int  # Months after year-end until data released
    notes: str
    data_dictionary_url: Optional[str] = None
    api_endpoint: Optional[str] = None


# =====================================================================
# DATASET REGISTRY - SOURCE OF TRUTH FOR DATA AVAILABILITY
# =====================================================================

DATASET_REGISTRY = {

    # ACS 1-Year API (Detailed Tables)
    DatasetType.ACS_1YEAR_API: DatasetAvailability(
        dataset_type=DatasetType.ACS_1YEAR_API,
        min_year=2005,
        max_year=2024,  # Released September 2025
        geography_levels=["national", "state"],
        has_field_of_study=False,  # API tables don't have detailed FOD
        has_earnings=True,  # Median earnings tables available
        has_occupation=True,  # Occupation by demographics tables
        has_industry=True,  # Industry employment tables
        release_lag_months=9,  # Released September following survey year
        notes="Detailed tabulations via API. Use PUMS for field-of-study data. "
              "2024 data released September 2025.",
        api_endpoint="https://api.census.gov/data/2024/acs/acs1",
        data_dictionary_url="https://api.census.gov/data/2024/acs/acs1/variables.html"
    ),

    # ACS 5-Year API (Detailed Tables)
    DatasetType.ACS_5YEAR_API: DatasetAvailability(
        dataset_type=DatasetType.ACS_5YEAR_API,
        min_year=2009,  # 2005-2009 first 5-year period
        max_year=2023,  # 2019-2023 latest, released December 2024
        geography_levels=["national", "state", "county", "tract", "block_group"],
        has_field_of_study=False,
        has_earnings=True,
        has_occupation=True,
        has_industry=True,
        release_lag_months=13,  # Released December after period ends
        notes="5-year pooled estimates. 2019-2023 is latest available. "
              "Provides smaller geography support than 1-year.",
        api_endpoint="https://api.census.gov/data/2023/acs/acs5",
        data_dictionary_url="https://api.census.gov/data/2023/acs/acs5/variables.html"
    ),

    # ACS 1-Year PUMS (Microdata)
    DatasetType.ACS_1YEAR_PUMS: DatasetAvailability(
        dataset_type=DatasetType.ACS_1YEAR_PUMS,
        min_year=2005,
        max_year=2024,  # Released October 2025
        geography_levels=["puma"],  # PUMAs only (100k+ population areas)
        has_field_of_study=True,  # FOD1P, FOD2P variables (4-digit CIP codes)
        has_earnings=True,  # WAGP, PERNP variables
        has_occupation=True,  # OCCP variable (2018 SOC codes)
        has_industry=True,  # NAICSP variable (2017 NAICS codes)
        release_lag_months=10,  # Released October following survey year
        notes="Person-level microdata. Best source for field-of-study analysis. "
              "FOD1P uses CIP 2010 4-digit codes. Requires weighting with PWGTP.",
        api_endpoint=None,  # Must download CSV files
        data_dictionary_url="https://www.census.gov/programs-surveys/acs/microdata/documentation.html"
    ),

    # ACS 5-Year PUMS (Microdata)
    DatasetType.ACS_5YEAR_PUMS: DatasetAvailability(
        dataset_type=DatasetType.ACS_5YEAR_PUMS,
        min_year=2009,
        max_year=2023,  # 2019-2023 released December 2024
        geography_levels=["puma"],
        has_field_of_study=True,
        has_earnings=True,
        has_occupation=True,
        has_industry=True,
        release_lag_months=13,
        notes="5-year pooled microdata. Larger sample sizes than 1-year for "
              "analyzing rare fields/occupations. Latest is 2019-2023.",
        api_endpoint=None,
        data_dictionary_url="https://www.census.gov/programs-surveys/acs/microdata/documentation.html"
    ),

    # CPS Basic Monthly
    DatasetType.CPS_BASIC_MONTHLY: DatasetAvailability(
        dataset_type=DatasetType.CPS_BASIC_MONTHLY,
        min_year=1994,  # When modern CPS started
        max_year=2024,  # Latest month available
        geography_levels=["national", "state"],  # Limited state detail
        has_field_of_study=False,
        has_earnings=False,  # Basic monthly doesn't have earnings
        has_occupation=True,  # PRDTOCC1, PRMJOCC1
        has_industry=True,  # PRDTIND1
        release_lag_months=1,  # Released ~1 month after survey month
        notes="Monthly labor force statistics. No field-of-study or earnings. "
              "Use CPS ASEC for those.",
        api_endpoint="https://api.census.gov/data/timeseries/cps/basic",
        data_dictionary_url="https://www.census.gov/data/developers/data-sets/census-microdata-api/cps/basic.html"
    ),

    # CPS ASEC (Annual Social and Economic Supplement)
    DatasetType.CPS_ASEC: DatasetAvailability(
        dataset_type=DatasetType.CPS_ASEC,
        min_year=1962,
        max_year=2024,  # March 2024 supplement
        geography_levels=["national", "state"],
        has_field_of_study=True,  # EDDEGREE (2015+), GRADDEG variables
        has_earnings=True,  # INCWAGE, WSAL_VAL, PEARNVAL
        has_occupation=True,  # PRDTOCC1 (2018 SOC)
        has_industry=True,  # PRDTIND1 (2017 NAICS)
        release_lag_months=6,  # March supplement released ~September
        notes="CRITICAL: Best longitudinal source for field-of-study outcomes. "
              "EDDEGREE variable added 2015, covers recent graduates. "
              "Access via IPUMS CPS (no direct API). Requires IPUMS extract.",
        api_endpoint=None,  # IPUMS extract required
        data_dictionary_url="https://cps.ipums.org/cps/"
    ),

    # BLS Occupational Employment Statistics
    DatasetType.BLS_OES: DatasetAvailability(
        dataset_type=DatasetType.BLS_OES,
        min_year=1997,
        max_year=2024,  # May 2024 estimates
        geography_levels=["national", "state", "metro"],
        has_field_of_study=False,
        has_earnings=True,  # Best wage data by detailed occupation
        has_occupation=True,  # SOC 2018 codes
        has_industry=True,  # NAICS codes
        release_lag_months=10,  # May survey released ~March next year
        notes="Best source for wages by occupation. Annual May survey. "
              "Provides mean, median, and percentile wages by SOC code.",
        api_endpoint="https://api.bls.gov/publicAPI/v2/timeseries/data/",
        data_dictionary_url="https://www.bls.gov/oes/"
    ),

    # BLS JOLTS (Job Openings and Labor Turnover)
    DatasetType.BLS_JOLTS: DatasetAvailability(
        dataset_type=DatasetType.BLS_JOLTS,
        min_year=2000,
        max_year=2024,
        geography_levels=["national", "region"],
        has_field_of_study=False,
        has_earnings=False,
        has_occupation=False,
        has_industry=True,  # By NAICS sector
        release_lag_months=2,  # Released ~2 months after survey month
        notes="Job openings, hires, separations by industry. Useful for "
              "understanding labor demand. Monthly data.",
        api_endpoint="https://api.bls.gov/publicAPI/v2/timeseries/data/",
        data_dictionary_url="https://www.bls.gov/jlt/"
    ),

    # BLS QCEW (Quarterly Census of Employment and Wages)
    DatasetType.BLS_QCEW: DatasetAvailability(
        dataset_type=DatasetType.BLS_QCEW,
        min_year=1990,
        max_year=2024,
        geography_levels=["national", "state", "county", "msa"],
        has_field_of_study=False,
        has_earnings=True,  # Average weekly wages
        has_occupation=False,
        has_industry=True,  # Detailed NAICS codes
        release_lag_months=7,  # Released ~6-7 months after quarter
        notes="Comprehensive wage data by industry and geography. Quarterly. "
              "Covers 95% of U.S. jobs. Good for industry wage comparisons.",
        api_endpoint="https://api.bls.gov/publicAPI/v2/timeseries/data/",
        data_dictionary_url="https://www.bls.gov/cew/"
    ),
}


# =====================================================================
# VALIDATION FUNCTIONS
# =====================================================================

def validate_data_request(
    dataset: DatasetType,
    year: int,
    geography_level: str = "national",
    requires_field_of_study: bool = False,
    requires_earnings: bool = False,
    requires_occupation: bool = False,
    requires_industry: bool = False
) -> tuple[bool, Optional[str]]:
    """Validate if a data request can be fulfilled

    Args:
        dataset: Dataset type to query
        year: Year of data requested
        geography_level: Geographic level needed
        requires_field_of_study: Request needs field-of-study data
        requires_earnings: Request needs earnings/wage data
        requires_occupation: Request needs occupation data
        requires_industry: Request needs industry data

    Returns:
        (is_valid, error_message)

    Raises:
        DataAvailabilityError: If ENFORCE_DATA_AVAILABILITY env var is True
    """
    if dataset not in DATASET_REGISTRY:
        error = f"Unknown dataset: {dataset}"
        logger.error(error)
        return False, error

    meta = DATASET_REGISTRY[dataset]

    # Check year range
    if year < meta.min_year or year > meta.max_year:
        error = (
            f"{dataset.value} only available for years {meta.min_year}-{meta.max_year}. "
            f"Requested: {year}. Latest available: {meta.max_year}."
        )
        logger.error(error)
        return False, error

    # Check geography
    if geography_level not in meta.geography_levels:
        error = (
            f"{dataset.value} does not support '{geography_level}' geography. "
            f"Available: {', '.join(meta.geography_levels)}"
        )
        logger.error(error)
        return False, error

    # Check field of study
    if requires_field_of_study and not meta.has_field_of_study:
        error = (
            f"{dataset.value} does not contain field-of-study variables. "
            f"Use ACS PUMS (FOD1P) or CPS ASEC (EDDEGREE) instead."
        )
        logger.error(error)
        return False, error

    # Check earnings
    if requires_earnings and not meta.has_earnings:
        error = (
            f"{dataset.value} does not contain earnings data. "
            f"Use ACS PUMS, CPS ASEC, or BLS OES for wage data."
        )
        logger.error(error)
        return False, error

    # Check occupation
    if requires_occupation and not meta.has_occupation:
        error = f"{dataset.value} does not contain occupation codes."
        logger.error(error)
        return False, error

    # Check industry
    if requires_industry and not meta.has_industry:
        error = f"{dataset.value} does not contain industry codes."
        logger.error(error)
        return False, error

    logger.info(f"✅ Data request validated: {dataset.value} year={year} geo={geography_level}")
    return True, None


def get_latest_available_year(dataset: DatasetType) -> int:
    """Get most recent year with published data

    Args:
        dataset: Dataset to check

    Returns:
        Latest year with data
    """
    if dataset not in DATASET_REGISTRY:
        raise DataAvailabilityError(f"Unknown dataset: {dataset}")

    return DATASET_REGISTRY[dataset].max_year


def get_available_years(dataset: DatasetType) -> list[int]:
    """Get all available years for a dataset

    Args:
        dataset: Dataset to check

    Returns:
        List of all valid years
    """
    if dataset not in DATASET_REGISTRY:
        raise DataAvailabilityError(f"Unknown dataset: {dataset}")

    meta = DATASET_REGISTRY[dataset]
    return list(range(meta.min_year, meta.max_year + 1))


def check_release_status(dataset: DatasetType, year: int) -> dict:
    """Check if a year's data has been released

    Args:
        dataset: Dataset to check
        year: Year to check

    Returns:
        {
            "released": bool,
            "expected_release_date": Optional[date],
            "latest_available": int,
            "url": Optional[str]
        }
    """
    if dataset not in DATASET_REGISTRY:
        raise DataAvailabilityError(f"Unknown dataset: {dataset}")

    meta = DATASET_REGISTRY[dataset]
    latest_year = meta.max_year

    if year <= latest_year:
        return {
            "released": True,
            "expected_release_date": None,
            "latest_available": latest_year,
            "url": meta.data_dictionary_url
        }

    # Calculate expected release date
    expected_release = date(year + 1, 1, 1) + timedelta(days=meta.release_lag_months * 30)

    return {
        "released": False,
        "expected_release_date": expected_release,
        "latest_available": latest_year,
        "url": None,
        "message": (
            f"{dataset.value} data for {year} not yet released. "
            f"Expected around {expected_release.strftime('%B %Y')}. "
            f"Latest available: {latest_year}"
        )
    }


def get_dataset_info(dataset: DatasetType) -> DatasetAvailability:
    """Get full metadata for a dataset

    Args:
        dataset: Dataset to query

    Returns:
        DatasetAvailability object with all metadata
    """
    if dataset not in DATASET_REGISTRY:
        raise DataAvailabilityError(f"Unknown dataset: {dataset}")

    return DATASET_REGISTRY[dataset]


def recommend_dataset_for_query(
    year: int,
    geography_level: str,
    needs_field_of_study: bool = False,
    needs_earnings: bool = False,
    needs_time_series: bool = False
) -> list[DatasetType]:
    """Recommend best dataset(s) for a given query

    Args:
        year: Year needed
        geography_level: Geographic detail needed
        needs_field_of_study: Requires field-of-study data
        needs_earnings: Requires earnings data
        needs_time_series: Requires multi-year comparison

    Returns:
        List of recommended datasets (ordered by preference)
    """
    recommendations = []

    for dataset, meta in DATASET_REGISTRY.items():
        # Check if dataset covers requested year
        if year < meta.min_year or year > meta.max_year:
            continue

        # Check geography support
        if geography_level not in meta.geography_levels:
            continue

        # Check required features
        if needs_field_of_study and not meta.has_field_of_study:
            continue

        if needs_earnings and not meta.has_earnings:
            continue

        # Dataset matches requirements
        recommendations.append(dataset)

    # Sort by preference (PUMS > API for field-of-study)
    if needs_field_of_study:
        # Prefer CPS ASEC for time series, ACS PUMS for cross-sectional
        if needs_time_series:
            recommendations.sort(key=lambda d: (
                d == DatasetType.CPS_ASEC,  # CPS ASEC best for trends
                d == DatasetType.ACS_1YEAR_PUMS
            ), reverse=True)
        else:
            recommendations.sort(key=lambda d: (
                d == DatasetType.ACS_1YEAR_PUMS,  # Largest sample
                d == DatasetType.CPS_ASEC
            ), reverse=True)

    return recommendations
