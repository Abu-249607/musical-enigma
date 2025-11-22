"""Data chunking for RAG retrieval."""

from typing import Any
from datetime import datetime
import hashlib

from ..models.citation import Citation, CitedDataPoint
from ..models.employment import EmploymentRecord, EMPLOYMENT_VARIABLES


class DataChunker:
    """Chunks Census data into retrievable units for RAG.

    Creates semantic chunks that:
    1. Maintain context (geography, time period)
    2. Include citation metadata
    3. Are appropriately sized for embedding
    """

    def __init__(self, chunk_size: int = 500):
        """Initialize chunker.

        Args:
            chunk_size: Target characters per chunk (for text chunks)
        """
        self.chunk_size = chunk_size

    def chunk_employment_record(
        self,
        record: EmploymentRecord,
        citation: Citation,
    ) -> list[dict[str, Any]]:
        """Create retrievable chunks from an employment record.

        Each chunk contains:
        - Semantic text representation
        - Structured data
        - Citation metadata
        - Embedding-ready content
        """
        chunks = []

        # Chunk 1: Overview statistics
        overview_text = self._create_overview_text(record)
        chunks.append(
            self._create_chunk(
                chunk_type="employment_overview",
                content=overview_text,
                record=record,
                citation=citation,
                metrics=["labor_force", "employed", "unemployed"],
            )
        )

        # Chunk 2: Rate calculations
        rates_text = self._create_rates_text(record)
        if rates_text:
            chunks.append(
                self._create_chunk(
                    chunk_type="employment_rates",
                    content=rates_text,
                    record=record,
                    citation=citation,
                    metrics=["unemployment_rate", "participation_rate"],
                )
            )

        return chunks

    def _create_overview_text(self, record: EmploymentRecord) -> str:
        """Create natural language overview of employment data."""
        parts = [
            f"Employment statistics for {record.geography_name} ({record.year}):"
        ]

        if record.total_population_16_plus:
            parts.append(
                f"The total population aged 16 and over is {record.total_population_16_plus:,}."
            )

        if record.labor_force:
            parts.append(f"The labor force consists of {record.labor_force:,} people.")

        if record.employed:
            parts.append(f"There are {record.employed:,} employed individuals.")

        if record.unemployed:
            parts.append(f"There are {record.unemployed:,} unemployed individuals.")

        if record.not_in_labor_force:
            parts.append(
                f"{record.not_in_labor_force:,} people are not in the labor force."
            )

        return " ".join(parts)

    def _create_rates_text(self, record: EmploymentRecord) -> str | None:
        """Create text about employment rates."""
        parts = [f"Employment rates for {record.geography_name} ({record.year}):"]

        has_data = False

        if record.unemployment_rate is not None:
            parts.append(f"The unemployment rate is {record.unemployment_rate}%.")
            has_data = True

        if record.labor_force_participation_rate is not None:
            parts.append(
                f"The labor force participation rate is "
                f"{record.labor_force_participation_rate}%."
            )
            has_data = True

        if record.employment_population_ratio is not None:
            parts.append(
                f"The employment-population ratio is "
                f"{record.employment_population_ratio}%."
            )
            has_data = True

        return " ".join(parts) if has_data else None

    def _create_chunk(
        self,
        chunk_type: str,
        content: str,
        record: EmploymentRecord,
        citation: Citation,
        metrics: list[str],
    ) -> dict[str, Any]:
        """Create a standardized chunk structure."""
        # Generate chunk ID
        chunk_id = hashlib.sha256(
            f"{citation.citation_id}:{chunk_type}:{content[:50]}".encode()
        ).hexdigest()[:12]

        return {
            "id": chunk_id,
            "type": chunk_type,
            "content": content,
            "embedding_text": self._create_embedding_text(content, record),
            "metadata": {
                "geography_name": record.geography_name,
                "geography_level": record.geography_level.value,
                "fips_code": record.fips_code,
                "year": record.year,
                "metrics": metrics,
                "citation_id": citation.citation_id,
                "dataset": citation.dataset_name,
                "retrieved_at": citation.retrieved_at.isoformat(),
            },
            "citation": citation.model_dump(mode="json"),
            "structured_data": {
                "labor_force": record.labor_force,
                "employed": record.employed,
                "unemployed": record.unemployed,
                "unemployment_rate": record.unemployment_rate,
                "participation_rate": record.labor_force_participation_rate,
            },
        }

    def _create_embedding_text(self, content: str, record: EmploymentRecord) -> str:
        """Create optimized text for embedding.

        Includes semantic keywords to improve retrieval.
        """
        keywords = [
            record.geography_name,
            str(record.year),
            "employment",
            "labor force",
            "unemployment",
            "jobs",
            "workforce",
            record.geography_level.value,
        ]

        return f"{' '.join(keywords)}. {content}"

    def chunk_industry_data(
        self,
        industry_data: dict[str, int],
        geography_name: str,
        year: int,
        citation: Citation,
    ) -> list[dict[str, Any]]:
        """Create chunks from industry employment data."""
        chunks = []

        # Create overview chunk
        total = industry_data.get("Total civilian employed", 0)
        overview_parts = [
            f"Industry employment breakdown for {geography_name} ({year}):",
            f"Total civilian employed population: {total:,}.",
        ]

        # Add top industries
        sorted_industries = sorted(
            [(k, v) for k, v in industry_data.items() if k != "Total civilian employed"],
            key=lambda x: x[1],
            reverse=True,
        )

        for industry, count in sorted_industries[:5]:
            pct = (count / total * 100) if total else 0
            overview_parts.append(f"{industry}: {count:,} ({pct:.1f}%)")

        chunks.append({
            "id": hashlib.sha256(
                f"{citation.citation_id}:industry:{geography_name}".encode()
            ).hexdigest()[:12],
            "type": "industry_employment",
            "content": " ".join(overview_parts),
            "embedding_text": f"{geography_name} {year} industry jobs sectors employment " + " ".join(overview_parts),
            "metadata": {
                "geography_name": geography_name,
                "year": year,
                "citation_id": citation.citation_id,
            },
            "citation": citation.model_dump(mode="json"),
            "structured_data": industry_data,
        })

        return chunks
