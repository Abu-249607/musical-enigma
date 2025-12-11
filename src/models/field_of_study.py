"""
Data models for field-of-study analytics

These models support field-of-study × employment × gender × sector analysis
using ACS PUMS and CPS ASEC data.
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import date


class FieldOfStudyOutcome(BaseModel):
    """Employment outcomes by field of study

    Represents employment statistics for graduates of a specific field,
    with optional gender and sector breakdowns.
    """

    # Identifiers
    field_code: str = Field(description="CIP code (e.g., '1107' for Computer Science)")
    field_name: str = Field(description="Field title")
    degree_level: str = Field(description="Bachelor's, Master's, Doctoral, Professional")

    # Demographics (optional filters)
    year: int
    geography_level: str = Field(description="national, state, puma")
    geography_name: str
    sex: Optional[str] = Field(None, description="Male, Female, or None for all")
    age_group: Optional[str] = Field(None, description="e.g., '22-27' or None for all")

    # Employment metrics
    total_population: int = Field(description="Total with this degree/field")
    in_labor_force: int
    employed: int
    unemployed: int
    not_in_labor_force: int

    # Rates
    employment_rate: float = Field(description="employed / in_labor_force * 100")
    unemployment_rate: float = Field(description="unemployed / in_labor_force * 100")
    labor_force_participation_rate: float = Field(description="in_labor_force / total * 100")

    # Work characteristics
    median_hours_worked: Optional[float] = None
    pct_full_time: Optional[float] = Field(None, description="% working 35+ hours/week")

    # Earnings (if available from dataset)
    median_earnings: Optional[int] = Field(None, description="Median annual earnings")
    mean_earnings: Optional[int] = None
    earnings_25th_percentile: Optional[int] = None
    earnings_75th_percentile: Optional[int] = None

    # Occupation alignment (top occupations for this field)
    top_occupations: Optional[List[Dict]] = Field(
        None,
        description="List of {occ_code, occ_title, pct, median_earnings}"
    )

    # Sample metadata
    sample_size: int = Field(description="Unweighted sample size")
    margin_of_error: Optional[float] = Field(None, description="90% MOE for rates")

    # Data source
    data_source: str = Field(description="e.g., 'ACS_PUMS_2024', 'CPS_ASEC_2024'")
    citation: str = Field(description="Full citation string")

    class Config:
        json_schema_extra = {
            "example": {
                "field_code": "1107",
                "field_name": "Computer Science",
                "degree_level": "Bachelor's degree",
                "year": 2024,
                "geography_level": "national",
                "geography_name": "United States",
                "sex": "Female",
                "total_population": 125000,
                "in_labor_force": 118000,
                "employed": 112000,
                "unemployed": 6000,
                "not_in_labor_force": 7000,
                "employment_rate": 94.9,
                "unemployment_rate": 5.1,
                "labor_force_participation_rate": 94.4,
                "median_earnings": 85000,
                "sample_size": 1250,
                "data_source": "ACS_PUMS_2024",
                "citation": "U.S. Census Bureau, 2024 ACS 1-Year PUMS"
            }
        }


class OccupationEducationCrosstab(BaseModel):
    """Cross-tabulation of occupation × education × field

    Shows what occupations field graduates work in,
    and what education/fields workers in each occupation have.
    """

    occupation_code: str = Field(description="SOC 2018 code (e.g., '15-1252')")
    occupation_title: str

    field_code: Optional[str] = Field(None, description="CIP code if filtering by field")
    field_name: Optional[str] = None

    education_level: str

    # Employment counts
    total_employed: int = Field(description="Workers in this occ × edu × field combo")
    pct_of_occupation: float = Field(description="% of occupation with this education/field")
    pct_of_field: Optional[float] = Field(None, description="% of field grads in this occupation")

    # Demographics
    median_age: Optional[float] = None
    pct_female: Optional[float] = None

    # Compensation
    median_earnings: Optional[int] = None

    # Metadata
    year: int
    geography: str
    sample_size: int
    data_source: str


class SectorEmploymentByEducation(BaseModel):
    """Industry/sector employment by education and field

    Shows employment in industries/sectors broken down by
    education level and optional field of study.
    """

    industry_code: str = Field(description="NAICS code")
    industry_name: str
    sector: str = Field(description="Broad sector grouping")

    education_level: str
    field_code: Optional[str] = None
    field_name: Optional[str] = None

    # Employment
    total_employed: int
    pct_of_sector: float = Field(description="% of sector with this education/field")
    growth_rate: Optional[float] = Field(None, description="Year-over-year % change")

    # Demographics
    pct_female: Optional[float] = None
    median_age: Optional[float] = None

    # Compensation
    median_earnings: Optional[int] = None

    # Metadata
    year: int
    geography: str
    sample_size: int
    data_source: str


class GenderGap(BaseModel):
    """Gender gap metrics for a field/occupation/sector

    Compares employment and earnings outcomes between male and female workers.
    """

    segment_type: str = Field(description="field, occupation, or sector")
    segment_code: str
    segment_name: str

    year: int
    geography: str

    # Male metrics
    male_employment_rate: float
    male_unemployment_rate: float
    male_median_earnings: Optional[int] = None
    male_sample_size: int

    # Female metrics
    female_employment_rate: float
    female_unemployment_rate: float
    female_median_earnings: Optional[int] = None
    female_sample_size: int

    # Gap calculations
    employment_rate_gap: float = Field(description="male - female (percentage points)")
    unemployment_rate_gap: float = Field(description="male - female (percentage points)")
    earnings_gap_pct: Optional[float] = Field(
        None,
        description="(male - female) / male * 100"
    )

    # Representation
    pct_female: float = Field(description="% of workforce that is female")

    data_source: str


class LongitudinalTrend(BaseModel):
    """Time series data for trend analysis and forecasting

    Tracks a metric over time for a specific segment (field, occupation, etc).
    """

    metric_name: str = Field(description="employment_rate, median_earnings, etc.")
    segment: str = Field(description="CS_Bachelors_Female, All_Masters, etc.")

    # Time series data
    time_series: List[Dict] = Field(
        description="List of {year, month, value, moe, sample_size}"
    )

    # Trend statistics
    start_year: int
    end_year: int
    start_value: float
    end_value: float
    percent_change: float = Field(description="(end - start) / start * 100")
    annual_growth_rate: Optional[float] = Field(None, description="CAGR if applicable")

    # Statistical significance
    trend_direction: str = Field(description="increasing, decreasing, stable")
    is_significant: bool = Field(description="Is trend statistically significant?")

    # Forecast (optional)
    forecast_years: Optional[List[int]] = None
    forecast_values: Optional[List[float]] = None
    forecast_confidence_intervals: Optional[List[Dict]] = Field(
        None,
        description="List of {year, lower, upper} for confidence bands"
    )

    data_source: str


class FieldROIComparison(BaseModel):
    """ROI comparison across multiple fields of study

    Compares return on investment (employment + earnings outcomes)
    across different fields at the same degree level.
    """

    degree_level: str
    year: int
    geography: str

    fields: List[FieldOfStudyOutcome]

    # Rankings
    highest_employment_rate: str = Field(description="Field code with highest employment")
    highest_median_earnings: Optional[str] = Field(None, description="Field code with highest earnings")
    best_roi_overall: str = Field(description="Field code with best composite ROI score")

    # Statistics
    employment_rate_range: tuple = Field(description="(min, max) employment rates across fields")
    earnings_range: Optional[tuple] = Field(None, description="(min, max) median earnings")

    data_source: str
