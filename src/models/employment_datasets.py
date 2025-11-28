"""Comprehensive catalog of Census Bureau employment datasets.

This module defines all employment-related tables available in the
American Community Survey and other Census datasets.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class DatasetCategory(str, Enum):
    """Categories of employment datasets."""
    BASIC_EMPLOYMENT = "basic_employment"
    OCCUPATION = "occupation"
    INDUSTRY = "industry"
    CLASS_OF_WORKER = "class_of_worker"
    EDUCATION = "education"
    EARNINGS = "earnings"
    COMMUTING = "commuting"
    LABOR_FORCE = "labor_force"


@dataclass
class VariableInfo:
    """Information about a Census variable."""
    code: str
    label: str
    concept: Optional[str] = None


@dataclass
class EmploymentTable:
    """Metadata for a Census employment table."""
    table_id: str
    title: str
    category: DatasetCategory
    variables: List[VariableInfo]
    universe: str
    available_in_acs1: bool = True
    available_in_acs5: bool = True
    notes: Optional[str] = None


# ==============================================================================
# BASIC EMPLOYMENT STATUS TABLES
# ==============================================================================

TABLE_B23025 = EmploymentTable(
    table_id="B23025",
    title="Employment Status for the Population 16 Years and Over",
    category=DatasetCategory.BASIC_EMPLOYMENT,
    universe="Population 16 years and over",
    variables=[
        VariableInfo("B23025_001E", "Total population 16+"),
        VariableInfo("B23025_002E", "In labor force"),
        VariableInfo("B23025_003E", "In labor force: Civilian labor force"),
        VariableInfo("B23025_004E", "In labor force: Civilian labor force: Employed"),
        VariableInfo("B23025_005E", "In labor force: Civilian labor force: Unemployed"),
        VariableInfo("B23025_006E", "In labor force: Armed Forces"),
        VariableInfo("B23025_007E", "Not in labor force"),
    ],
    notes="Primary table for unemployment rate calculations"
)

TABLE_C23002 = EmploymentTable(
    table_id="C23002",
    title="Sex by Age by Employment Status for the Population 16+",
    category=DatasetCategory.BASIC_EMPLOYMENT,
    universe="Population 16 years and over",
    variables=[
        VariableInfo("C23002_001E", "Total"),
        VariableInfo("C23002_002E", "Male"),
        VariableInfo("C23002_003E", "Male: 16 to 64 years"),
        VariableInfo("C23002_004E", "Male: 16 to 64 years: In labor force"),
        VariableInfo("C23002_005E", "Male: 16 to 64 years: In labor force: In Armed Forces"),
        VariableInfo("C23002_006E", "Male: 16 to 64 years: In labor force: Civilian: Employed"),
        VariableInfo("C23002_007E", "Male: 16 to 64 years: In labor force: Civilian: Unemployed"),
        VariableInfo("C23002_008E", "Male: 16 to 64 years: Not in labor force"),
        # Add female equivalents...
        VariableInfo("C23002_015E", "Female"),
        VariableInfo("C23002_016E", "Female: 16 to 64 years"),
        VariableInfo("C23002_019E", "Female: 16 to 64 years: In labor force: Civilian: Employed"),
        VariableInfo("C23002_020E", "Female: 16 to 64 years: In labor force: Civilian: Unemployed"),
    ],
    notes="Detailed age and sex breakdowns for labor force analysis"
)

# ==============================================================================
# OCCUPATION TABLES
# ==============================================================================

TABLE_B24010 = EmploymentTable(
    table_id="B24010",
    title="Sex by Occupation for the Civilian Employed Population 16+",
    category=DatasetCategory.OCCUPATION,
    universe="Civilian employed population 16 years and over",
    variables=[
        VariableInfo("B24010_001E", "Total"),
        VariableInfo("B24010_002E", "Male"),
        VariableInfo("B24010_003E", "Male: Management, business, science, and arts occupations"),
        VariableInfo("B24010_004E", "Male: Management, business, and financial occupations"),
        VariableInfo("B24010_011E", "Male: Computer and mathematical occupations"),
        VariableInfo("B24010_015E", "Male: Engineering occupations"),
        VariableInfo("B24010_019E", "Male: Life, physical, and social science occupations"),
        VariableInfo("B24010_027E", "Male: Education, legal, community service, arts, and media occupations"),
        VariableInfo("B24010_035E", "Male: Healthcare practitioners and technical occupations"),
        VariableInfo("B24010_041E", "Male: Service occupations"),
        VariableInfo("B24010_055E", "Male: Sales and office occupations"),
        VariableInfo("B24010_063E", "Male: Natural resources, construction, and maintenance occupations"),
        VariableInfo("B24010_071E", "Male: Production, transportation, and material moving occupations"),
        # Female equivalents
        VariableInfo("B24010_077E", "Female"),
        VariableInfo("B24010_078E", "Female: Management, business, science, and arts occupations"),
    ],
    available_in_acs5=False,
    notes="150+ occupation categories, ACS 1-year only"
)

TABLE_B24020 = EmploymentTable(
    table_id="B24020",
    title="Sex by Occupation for Full-Time, Year-Round Civilian Employed Population 16+",
    category=DatasetCategory.OCCUPATION,
    universe="Full-time, year-round civilian employed population 16 years and over",
    variables=[
        VariableInfo("B24020_001E", "Total"),
        VariableInfo("B24020_002E", "Male"),
        VariableInfo("B24020_003E", "Male: Management, business, science, and arts occupations"),
        # Similar structure to B24010 but for full-time workers
    ],
    available_in_acs5=False,
    notes="Same occupation detail as B24010 but full-time workers only"
)

TABLE_C24010 = EmploymentTable(
    table_id="C24010",
    title="Sex by Occupation for the Civilian Employed Population 16+ (Simplified)",
    category=DatasetCategory.OCCUPATION,
    universe="Civilian employed population 16 years and over",
    variables=[
        VariableInfo("C24010_001E", "Total"),
        VariableInfo("C24010_003E", "Management, business, science, and arts occupations"),
        VariableInfo("C24010_019E", "Service occupations"),
        VariableInfo("C24010_033E", "Sales and office occupations"),
        VariableInfo("C24010_039E", "Natural resources, construction, and maintenance occupations"),
        VariableInfo("C24010_055E", "Production, transportation, and material moving occupations"),
    ],
    notes="Simplified occupation categories, available in both 1-year and 5-year"
)

# ==============================================================================
# INDUSTRY TABLES
# ==============================================================================

TABLE_C24030 = EmploymentTable(
    table_id="C24030",
    title="Sex by Industry for the Civilian Employed Population 16+",
    category=DatasetCategory.INDUSTRY,
    universe="Civilian employed population 16 years and over",
    variables=[
        VariableInfo("C24030_001E", "Total"),
        VariableInfo("C24030_003E", "Agriculture, forestry, fishing and hunting, and mining"),
        VariableInfo("C24030_004E", "Construction"),
        VariableInfo("C24030_005E", "Manufacturing"),
        VariableInfo("C24030_006E", "Wholesale trade"),
        VariableInfo("C24030_007E", "Retail trade"),
        VariableInfo("C24030_008E", "Transportation and warehousing, and utilities"),
        VariableInfo("C24030_009E", "Information"),
        VariableInfo("C24030_010E", "Finance and insurance, and real estate and rental and leasing"),
        VariableInfo("C24030_011E", "Professional, scientific, and management, and administrative and waste management services"),
        VariableInfo("C24030_012E", "Educational services, and health care and social assistance"),
        VariableInfo("C24030_013E", "Arts, entertainment, and recreation, and accommodation and food services"),
        VariableInfo("C24030_014E", "Other services, except public administration"),
        VariableInfo("C24030_015E", "Public administration"),
    ],
    notes="13 major industry categories"
)

TABLE_C24050 = EmploymentTable(
    table_id="C24050",
    title="Industry by Sex for the Civilian Employed Population 16+ (Detailed)",
    category=DatasetCategory.INDUSTRY,
    universe="Civilian employed population 16 years and over",
    variables=[
        VariableInfo("C24050_001E", "Total"),
        VariableInfo("C24050_002E", "Agriculture, forestry, fishing and hunting, and mining"),
        VariableInfo("C24050_003E", "Construction"),
        VariableInfo("C24050_004E", "Manufacturing"),
        VariableInfo("C24050_006E", "Retail trade"),
        VariableInfo("C24050_008E", "Information"),
        VariableInfo("C24050_009E", "Finance and insurance, and real estate and rental and leasing"),
        VariableInfo("C24050_010E", "Professional, scientific, and management, and administrative and waste management services"),
        VariableInfo("C24050_011E", "Educational services, and health care and social assistance"),
        VariableInfo("C24050_014E", "Public administration"),
    ],
    notes="Alternative industry classification with sex breakdown"
)

# ==============================================================================
# CLASS OF WORKER TABLES
# ==============================================================================

TABLE_C24060 = EmploymentTable(
    table_id="C24060",
    title="Sex by Class of Worker for the Civilian Employed Population 16+",
    category=DatasetCategory.CLASS_OF_WORKER,
    universe="Civilian employed population 16 years and over",
    variables=[
        VariableInfo("C24060_001E", "Total"),
        VariableInfo("C24060_002E", "Male"),
        VariableInfo("C24060_003E", "Male: Private for-profit wage and salary workers"),
        VariableInfo("C24060_004E", "Male: Private for-profit wage and salary workers: Employee of private company"),
        VariableInfo("C24060_005E", "Male: Private for-profit wage and salary workers: Self-employed in own incorporated business"),
        VariableInfo("C24060_006E", "Male: Private not-for-profit wage and salary workers"),
        VariableInfo("C24060_007E", "Male: Local government workers"),
        VariableInfo("C24060_008E", "Male: State government workers"),
        VariableInfo("C24060_009E", "Male: Federal government workers"),
        VariableInfo("C24060_010E", "Male: Self-employed in own not incorporated business workers"),
        VariableInfo("C24060_011E", "Male: Unpaid family workers"),
        # Female equivalents
        VariableInfo("C24060_012E", "Female"),
        VariableInfo("C24060_015E", "Female: Self-employed in own incorporated business"),
        VariableInfo("C24060_020E", "Female: Self-employed in own not incorporated business workers"),
    ],
    notes="Essential for gig economy and self-employment analysis"
)

# ==============================================================================
# EDUCATION AND EMPLOYMENT TABLES
# ==============================================================================

TABLE_S1501 = EmploymentTable(
    table_id="S1501",
    title="Educational Attainment (Subject Table)",
    category=DatasetCategory.EDUCATION,
    universe="Population 18 years and over",
    variables=[
        VariableInfo("S1501_C01_001E", "Total population 18+"),
        VariableInfo("S1501_C01_006E", "High school graduate or higher"),
        VariableInfo("S1501_C01_012E", "Bachelor's degree or higher"),
        VariableInfo("S1501_C01_013E", "Bachelor's degree"),
        VariableInfo("S1501_C01_014E", "Graduate or professional degree"),
    ],
    notes="Subject table with employment status by education level"
)

TABLE_S1502 = EmploymentTable(
    table_id="S1502",
    title="Educational Attainment by Field of Bachelor's Degree",
    category=DatasetCategory.EDUCATION,
    universe="Population 25 years and over with a bachelor's degree or higher",
    variables=[
        VariableInfo("S1502_C01_001E", "Total with bachelor's degree or higher"),
        VariableInfo("S1502_C01_002E", "Science and Engineering"),
        VariableInfo("S1502_C01_003E", "Science and Engineering Related Fields"),
        VariableInfo("S1502_C01_004E", "Business"),
        VariableInfo("S1502_C01_005E", "Education"),
        VariableInfo("S1502_C01_006E", "Arts, Humanities and Other"),
        VariableInfo("S1502_C02_001E", "Employment rate - Total"),
        VariableInfo("S1502_C02_002E", "Employment rate - Science and Engineering"),
        VariableInfo("S1502_C02_003E", "Employment rate - Science and Engineering Related"),
    ],
    notes="CRITICAL for STEM career pathway analysis and education ROI"
)

TABLE_B23006 = EmploymentTable(
    table_id="B23006",
    title="Educational Attainment by Employment Status for the Population 25+",
    category=DatasetCategory.EDUCATION,
    universe="Population 25 years and over",
    variables=[
        VariableInfo("B23006_001E", "Total"),
        VariableInfo("B23006_002E", "Less than high school graduate"),
        VariableInfo("B23006_003E", "Less than high school graduate: In labor force"),
        VariableInfo("B23006_004E", "Less than high school graduate: In labor force: Employed"),
        VariableInfo("B23006_009E", "High school graduate (includes equivalency)"),
        VariableInfo("B23006_010E", "High school graduate: In labor force"),
        VariableInfo("B23006_011E", "High school graduate: In labor force: Employed"),
        VariableInfo("B23006_023E", "Bachelor's degree or higher"),
        VariableInfo("B23006_024E", "Bachelor's degree or higher: In labor force"),
        VariableInfo("B23006_025E", "Bachelor's degree or higher: In labor force: Employed"),
    ],
    notes="Employment outcomes by education level"
)

# ==============================================================================
# EARNINGS TABLES
# ==============================================================================

TABLE_B24011 = EmploymentTable(
    table_id="B24011",
    title="Median Earnings by Occupation",
    category=DatasetCategory.EARNINGS,
    universe="Civilian employed population 16+ with earnings",
    variables=[
        VariableInfo("B24011_001E", "Median earnings - Total"),
        VariableInfo("B24011_002E", "Median earnings - Management, business, science, and arts"),
        VariableInfo("B24011_013E", "Median earnings - Service occupations"),
        VariableInfo("B24011_027E", "Median earnings - Sales and office occupations"),
        VariableInfo("B24011_033E", "Median earnings - Natural resources, construction, and maintenance"),
        VariableInfo("B24011_049E", "Median earnings - Production, transportation, and material moving"),
    ],
    available_in_acs5=False,
    notes="Median earnings by occupation category"
)

TABLE_B24031 = EmploymentTable(
    table_id="B24031",
    title="Median Earnings by Industry",
    category=DatasetCategory.EARNINGS,
    universe="Civilian employed population 16+ with earnings",
    variables=[
        VariableInfo("B24031_001E", "Median earnings - Total"),
        VariableInfo("B24031_002E", "Median earnings - Agriculture, forestry, fishing, hunting, mining"),
        VariableInfo("B24031_003E", "Median earnings - Construction"),
        VariableInfo("B24031_004E", "Median earnings - Manufacturing"),
        VariableInfo("B24031_007E", "Median earnings - Information"),
        VariableInfo("B24031_008E", "Median earnings - Finance, insurance, real estate"),
        VariableInfo("B24031_009E", "Median earnings - Professional, scientific, management"),
        VariableInfo("B24031_010E", "Median earnings - Educational services, health care"),
    ],
    notes="Median earnings by industry sector"
)

TABLE_S2001 = EmploymentTable(
    table_id="S2001",
    title="Earnings in the Past 12 Months (Subject Table)",
    category=DatasetCategory.EARNINGS,
    universe="Population 16+ with earnings",
    variables=[
        VariableInfo("S2001_C01_001E", "Total with earnings"),
        VariableInfo("S2001_C01_002E", "Median earnings"),
        VariableInfo("S2001_C01_003E", "Mean earnings"),
    ],
    notes="Comprehensive earnings statistics"
)

# ==============================================================================
# COMMUTING AND WORK PATTERNS TABLES
# ==============================================================================

TABLE_B08006 = EmploymentTable(
    table_id="B08006",
    title="Sex of Workers by Means of Transportation to Work",
    category=DatasetCategory.COMMUTING,
    universe="Workers 16 years and over",
    variables=[
        VariableInfo("B08006_001E", "Total"),
        VariableInfo("B08006_008E", "Drove alone"),
        VariableInfo("B08006_009E", "Carpooled"),
        VariableInfo("B08006_014E", "Public transportation"),
        VariableInfo("B08006_015E", "Walked"),
        VariableInfo("B08006_017E", "Worked from home"),
    ],
    notes="Work from home data useful for remote work analysis"
)

TABLE_B08303 = EmploymentTable(
    table_id="B08303",
    title="Travel Time to Work",
    category=DatasetCategory.COMMUTING,
    universe="Workers 16 years and over who did not work from home",
    variables=[
        VariableInfo("B08303_001E", "Total"),
        VariableInfo("B08303_002E", "Less than 10 minutes"),
        VariableInfo("B08303_008E", "30 to 44 minutes"),
        VariableInfo("B08303_012E", "60 to 89 minutes"),
        VariableInfo("B08303_013E", "90 or more minutes"),
    ],
    notes="Commute time patterns"
)

# ==============================================================================
# LABOR FORCE PARTICIPATION BY DEMOGRAPHICS
# ==============================================================================

TABLE_C23002A = EmploymentTable(
    table_id="C23002A",
    title="Sex by Age by Employment Status (White Alone)",
    category=DatasetCategory.LABOR_FORCE,
    universe="White alone population 16 years and over",
    variables=[
        VariableInfo("C23002A_001E", "Total"),
        VariableInfo("C23002A_006E", "Male: 16 to 64: In labor force: Employed"),
        VariableInfo("C23002A_007E", "Male: 16 to 64: In labor force: Unemployed"),
        VariableInfo("C23002A_019E", "Female: 16 to 64: In labor force: Employed"),
        VariableInfo("C23002A_020E", "Female: 16 to 64: In labor force: Unemployed"),
    ],
    notes="Employment by race (White alone). Similar tables exist for other races: B, C, D, E, F, G, H, I"
)

# ==============================================================================
# DATASET REGISTRY
# ==============================================================================

ALL_EMPLOYMENT_TABLES: Dict[str, EmploymentTable] = {
    # Basic Employment
    "B23025": TABLE_B23025,
    "C23002": TABLE_C23002,

    # Occupation
    "B24010": TABLE_B24010,
    "B24020": TABLE_B24020,
    "C24010": TABLE_C24010,

    # Industry
    "C24030": TABLE_C24030,
    "C24050": TABLE_C24050,

    # Class of Worker
    "C24060": TABLE_C24060,

    # Education & Employment
    "S1501": TABLE_S1501,
    "S1502": TABLE_S1502,
    "B23006": TABLE_B23006,

    # Earnings
    "B24011": TABLE_B24011,
    "B24031": TABLE_B24031,
    "S2001": TABLE_S2001,

    # Commuting
    "B08006": TABLE_B08006,
    "B08303": TABLE_B08303,

    # Demographics
    "C23002A": TABLE_C23002A,
}


def get_tables_by_category(category: DatasetCategory) -> List[EmploymentTable]:
    """Get all tables in a specific category."""
    return [
        table for table in ALL_EMPLOYMENT_TABLES.values()
        if table.category == category
    ]


def get_stem_tables() -> List[EmploymentTable]:
    """Get tables relevant for STEM career analysis."""
    return [
        TABLE_B24010,  # Occupation detail (includes computer, engineering, science)
        TABLE_B24020,  # Full-time occupation
        TABLE_S1502,   # Field of degree to employment
        TABLE_B24011,  # Earnings by occupation
        TABLE_C24010,  # Simplified occupation
    ]


def get_gig_economy_tables() -> List[EmploymentTable]:
    """Get tables relevant for gig economy analysis."""
    return [
        TABLE_C24060,  # Class of worker (self-employed)
        TABLE_B08006,  # Work from home
        TABLE_C24030,  # Industry (gig sectors)
    ]


def get_education_roi_tables() -> List[EmploymentTable]:
    """Get tables relevant for education ROI analysis."""
    return [
        TABLE_S1502,   # Field of degree
        TABLE_B23006,  # Education by employment status
        TABLE_B24011,  # Earnings by occupation
        TABLE_B24031,  # Earnings by industry
        TABLE_S2001,   # Overall earnings
    ]


def get_geography_talent_tables() -> List[EmploymentTable]:
    """Get tables relevant for geographic talent mapping."""
    return [
        TABLE_B24010,  # Occupation distribution
        TABLE_C24030,  # Industry distribution
        TABLE_B23025,  # Basic employment
        TABLE_C24060,  # Class of worker
    ]


# STEM-specific occupation codes (subset of B24010)
STEM_OCCUPATION_CODES = {
    "B24010_011E": "Computer and mathematical occupations",
    "B24010_015E": "Architecture and engineering occupations",
    "B24010_019E": "Life, physical, and social science occupations",
    "B24010_086E": "Computer and mathematical occupations (Female)",
    "B24010_090E": "Architecture and engineering occupations (Female)",
    "B24010_094E": "Life, physical, and social science occupations (Female)",
}

# High-growth industries for talent mapping
HIGH_GROWTH_INDUSTRIES = {
    "C24030_009E": "Information",
    "C24030_010E": "Finance and insurance, and real estate",
    "C24030_011E": "Professional, scientific, and management services",
    "C24030_012E": "Educational services, and health care",
}
