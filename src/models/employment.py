"""Employment-specific data models."""

from enum import Enum
from pydantic import BaseModel, Field


class GeographyLevel(str, Enum):
    """Census geography hierarchy levels."""

    NATION = "nation"
    STATE = "state"
    COUNTY = "county"
    PLACE = "place"  # Cities, towns
    TRACT = "tract"
    BLOCK_GROUP = "block group"
    MSA = "metropolitan statistical area"


class DatasetInfo(BaseModel):
    """Metadata about a Census dataset."""

    dataset_id: str = Field(description="Dataset identifier (e.g., 'acs/acs5')")
    title: str = Field(description="Human-readable title")
    description: str = Field(description="Dataset description")
    available_years: list[int] = Field(description="Years with available data")
    geography_levels: list[GeographyLevel] = Field(
        description="Supported geography levels"
    )
    update_frequency: str | None = Field(
        default=None, description="How often dataset is updated"
    )


class EmploymentRecord(BaseModel):
    """Structured employment data from Census."""

    geography_name: str
    geography_level: GeographyLevel
    fips_code: str | None = None
    year: int

    # Core employment metrics
    total_population_16_plus: int | None = Field(
        default=None, description="Population 16 years and over"
    )
    labor_force: int | None = Field(
        default=None, description="Total in labor force"
    )
    employed: int | None = Field(default=None, description="Employed population")
    unemployed: int | None = Field(default=None, description="Unemployed population")
    not_in_labor_force: int | None = Field(
        default=None, description="Not in labor force"
    )

    # Calculated metrics
    @property
    def unemployment_rate(self) -> float | None:
        """Calculate unemployment rate."""
        if self.labor_force and self.unemployed:
            return round((self.unemployed / self.labor_force) * 100, 2)
        return None

    @property
    def labor_force_participation_rate(self) -> float | None:
        """Calculate labor force participation rate."""
        if self.total_population_16_plus and self.labor_force:
            return round((self.labor_force / self.total_population_16_plus) * 100, 2)
        return None

    @property
    def employment_population_ratio(self) -> float | None:
        """Calculate employment-population ratio."""
        if self.total_population_16_plus and self.employed:
            return round((self.employed / self.total_population_16_plus) * 100, 2)
        return None


# Common ACS employment variables for reference
EMPLOYMENT_VARIABLES = {
    # Employment Status (Table B23025)
    "B23025_001E": "Total population 16 years and over",
    "B23025_002E": "In labor force",
    "B23025_003E": "In labor force: Civilian labor force",
    "B23025_004E": "In labor force: Civilian labor force: Employed",
    "B23025_005E": "In labor force: Civilian labor force: Unemployed",
    "B23025_006E": "In labor force: Armed Forces",
    "B23025_007E": "Not in labor force",
    # Industry (Table C24050)
    "C24050_001E": "Total civilian employed population 16+",
    "C24050_002E": "Agriculture, forestry, fishing, hunting, mining",
    "C24050_003E": "Construction",
    "C24050_004E": "Manufacturing",
    "C24050_005E": "Wholesale trade",
    "C24050_006E": "Retail trade",
    "C24050_007E": "Transportation and warehousing, and utilities",
    "C24050_008E": "Information",
    "C24050_009E": "Finance and insurance, real estate",
    "C24050_010E": "Professional, scientific, management, administrative",
    "C24050_011E": "Educational services, health care, social assistance",
    "C24050_012E": "Arts, entertainment, recreation, accommodation, food",
    "C24050_013E": "Other services, except public administration",
    "C24050_014E": "Public administration",
}

# Margin of error variables (append 'M' instead of 'E')
def get_moe_variable(estimate_var: str) -> str:
    """Convert estimate variable to margin of error variable."""
    return estimate_var.replace("E", "M")
