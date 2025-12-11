"""
CPS Basic Monthly data models

Reference: https://www.census.gov/data/developers/data-sets/census-microdata-api/cps/basic.html
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import date


class CPSLaborStats(BaseModel):
    """CPS labor force statistics for a given time/geography

    Based on CPS Basic Monthly variables:
    - PEMLR: Monthly labor force recode
    - PREMPNOT: Employment status
    - PEHRUSL1: Hours usually worked per week
    """
    year: int
    month: int
    state_fips: Optional[str] = None
    state_name: Optional[str] = None

    # Core metrics
    labor_force: int = Field(description="Total in labor force")
    employed: int = Field(description="Total employed")
    unemployed: int = Field(description="Total unemployed")
    not_in_labor_force: int = Field(description="Not in labor force")

    # Computed rates
    unemployment_rate: float = Field(description="Unemployment rate (%)")
    labor_force_participation_rate: float = Field(description="LFPR (%)")
    employment_population_ratio: float = Field(description="Emp-pop ratio (%)")

    # Hours worked
    avg_hours_worked: Optional[float] = Field(None, description="Avg hours/week")

    # Sample size
    sample_size: int = Field(description="Number of observations")


class CPSEducationEmployment(BaseModel):
    """CPS education-employment cross-tabulation

    Variables:
    - PEEDUCA: Educational attainment
    - PEMLR: Labor force status
    - PTDTRACE: Race/ethnicity
    """
    year: int
    month: int
    education_level: str  # e.g., "Bachelor's degree", "High school graduate"
    state_fips: Optional[str] = None

    total_population: int
    employed: int
    unemployed: int
    not_in_labor_force: int

    employment_rate: float
    unemployment_rate: float

    # Demographics
    median_age: Optional[float] = None
    pct_female: Optional[float] = None


class CPSOccupationStats(BaseModel):
    """CPS occupation statistics (for STEM tracking)

    Variables:
    - PRDTOCC1: Detailed occupation recode (2010+ codes)
    - PRMJOCC1: Major occupation recode
    """
    year: int
    month: int
    occupation_code: str
    occupation_name: str
    is_stem: bool = Field(description="Classified as STEM occupation")

    total_employed: int
    avg_hours: Optional[float] = None
    pct_full_time: Optional[float] = None

    # Education breakdown
    pct_bachelors_plus: Optional[float] = None

    # Demographics
    pct_female: Optional[float] = None
    median_age: Optional[float] = None


class CPSGigEconomyStats(BaseModel):
    """Gig economy / non-traditional work indicators

    Variables:
    - PRSJMJ: Multiple jobs
    - PEIO1COW: Class of worker (self-employed, etc.)
    - PEHRFTPT: Full-time/part-time status
    - PEHRRSN1: Reason for part-time work
    """
    year: int
    month: int
    state_fips: Optional[str] = None

    # Gig indicators
    self_employed: int
    multiple_job_holders: int
    part_time_economic_reasons: int  # Want full-time but working part-time

    total_employed: int

    # Computed metrics
    pct_self_employed: float
    pct_multiple_jobs: float
    pct_part_time_economic: float
    gig_economy_estimate: float = Field(description="Estimated gig workers %")


class CPSTalentDistribution(BaseModel):
    """Geographic distribution of talent/skills"""
    state_fips: str
    state_name: str
    year: int
    month: int

    # Talent metrics
    talent_category: str  # e.g., "STEM", "Recent Graduates"
    total_workers: int
    concentration_index: float = Field(description="Relative concentration vs national avg")

    # Supporting metrics
    pct_of_state_workforce: float
    avg_age: Optional[float] = None
    pct_female: Optional[float] = None
