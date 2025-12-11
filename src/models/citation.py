"""Citation models for tracking data provenance."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Tracks the source of a data point for transparency."""

    citation_id: str = Field(description="Unique identifier for this citation")
    dataset_name: str = Field(description="Census dataset name (e.g., 'acs/acs5')")
    dataset_year: int = Field(description="Year of the dataset")
    variables: list[str] = Field(description="Census API variables queried")
    geography: str = Field(description="Geographic level (state, county, etc.)")
    geography_name: str = Field(description="Human-readable geography name")
    fips_code: str | None = Field(default=None, description="FIPS code if applicable")
    api_endpoint: str = Field(description="Census API endpoint used")
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    census_api_url: str | None = Field(
        default=None, description="Direct URL to Census data explorer"
    )

    def to_reference_string(self) -> str:
        """Generate a human-readable citation string."""
        return (
            f"[{self.citation_id}] U.S. Census Bureau, {self.dataset_name} "
            f"({self.dataset_year}), {self.geography_name}. "
            f"Retrieved {self.retrieved_at.strftime('%Y-%m-%d')}."
        )

    def to_markdown_link(self) -> str:
        """Generate a markdown citation with link if available."""
        if self.census_api_url:
            return f"[{self.citation_id}]({self.census_api_url})"
        return f"[{self.citation_id}]"


class CitedDataPoint(BaseModel):
    """A single data point with its citation."""

    value: Any = Field(description="The data value")
    label: str = Field(description="Human-readable label for the value")
    variable_code: str = Field(description="Census variable code (e.g., 'B23025_004E')")
    citation: Citation = Field(description="Source citation for this data point")
    margin_of_error: float | None = Field(
        default=None, description="Margin of error if available"
    )
    is_estimate: bool = Field(
        default=True, description="Whether this is an estimate vs exact count"
    )
    confidence_note: str | None = Field(
        default=None, description="Notes about data reliability"
    )


class CitedResponse(BaseModel):
    """A complete response with multiple cited data points."""

    query: str = Field(description="Original user query")
    summary: str = Field(description="Natural language summary of findings")
    data_points: list[CitedDataPoint] = Field(description="All retrieved data points")
    citations: list[Citation] = Field(description="All citations used in response")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    def get_citation_block(self) -> str:
        """Generate a formatted citation block for the response."""
        lines = ["\n---", "**Sources:**"]
        for citation in self.citations:
            lines.append(f"- {citation.to_reference_string()}")
        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Generate full markdown response with citations."""
        return f"{self.summary}\n{self.get_citation_block()}"
