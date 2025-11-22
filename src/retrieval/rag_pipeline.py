"""RAG pipeline for Census employment queries."""

from typing import Any
from datetime import datetime

from ..models.citation import Citation, CitedResponse, CitedDataPoint
from ..census_client import CensusMCPClient
from ..preprocessing.chunker import DataChunker
from .vector_store import CensusVectorStore
from .search import HybridSearcher


class CensusRAGPipeline:
    """End-to-end RAG pipeline for Census employment data.

    This pipeline:
    1. Ingests data from Census API via MCP client
    2. Chunks and stores in vector database
    3. Retrieves relevant context for queries
    4. Formats responses with citations
    """

    def __init__(
        self,
        census_client: CensusMCPClient | None = None,
        vector_store: CensusVectorStore | None = None,
        api_key: str | None = None,
    ):
        """Initialize the RAG pipeline.

        Args:
            census_client: Pre-configured Census MCP client
            vector_store: Pre-configured vector store
            api_key: Census API key (used if client not provided)
        """
        self.client = census_client or CensusMCPClient(api_key=api_key)
        self.vector_store = vector_store or CensusVectorStore()
        self.chunker = DataChunker()
        self.searcher = HybridSearcher(self.vector_store)

    def ingest_geography(
        self,
        geography_name: str,
        years: list[int] | None = None,
        include_industry: bool = True,
    ) -> int:
        """Ingest employment data for a geography into the vector store.

        Args:
            geography_name: State or county name
            years: Years to ingest (default: [2022])
            include_industry: Whether to include industry breakdown

        Returns:
            Number of chunks ingested
        """
        years = years or [2022]
        total_chunks = 0

        for year in years:
            # Fetch employment data
            try:
                record, citation = self.client.get_employment_data(
                    geography_name, year=year
                )

                # Create chunks
                chunks = self.chunker.chunk_employment_record(record, citation)
                total_chunks += self.vector_store.add_chunks(chunks)

            except Exception as e:
                print(f"Warning: Could not ingest {geography_name} {year}: {e}")

            # Fetch industry data if requested
            if include_industry:
                try:
                    industry_data, industry_citation = self.client.get_industry_employment(
                        geography_name, year=year
                    )

                    industry_chunks = self.chunker.chunk_industry_data(
                        industry_data, geography_name, year, industry_citation
                    )
                    total_chunks += self.vector_store.add_chunks(industry_chunks)

                except Exception as e:
                    print(f"Warning: Could not ingest industry data for {geography_name}: {e}")

        return total_chunks

    def ingest_multiple_geographies(
        self,
        geographies: list[str],
        years: list[int] | None = None,
    ) -> dict[str, int]:
        """Ingest data for multiple geographies.

        Returns dict mapping geography name to chunks ingested.
        """
        results = {}
        for geo in geographies:
            results[geo] = self.ingest_geography(geo, years)
        return results

    def query(
        self,
        question: str,
        n_results: int = 5,
    ) -> dict[str, Any]:
        """Query the RAG system with a natural language question.

        Args:
            question: Natural language question about employment data
            n_results: Number of relevant chunks to retrieve

        Returns:
            Dict with retrieved context, citations, and metadata
        """
        # Search for relevant chunks
        results = self.searcher.search(question, n_results=n_results)

        # Extract citations
        citations = []
        seen_citation_ids = set()
        for result in results:
            citation_id = result["metadata"].get("citation_id")
            if citation_id and citation_id not in seen_citation_ids:
                # Reconstruct citation from metadata
                citations.append({
                    "citation_id": citation_id,
                    "dataset": result["metadata"].get("dataset", "acs/acs5"),
                    "year": result["metadata"].get("year"),
                    "geography": result["metadata"].get("geography_name"),
                })
                seen_citation_ids.add(citation_id)

        # Format context for LLM
        context, citation_ids = self.searcher.get_context_for_llm(question)

        return {
            "question": question,
            "context": context,
            "results": results,
            "citations": citations,
            "citation_ids": citation_ids,
            "retrieved_at": datetime.utcnow().isoformat(),
        }

    def query_with_prompt(
        self,
        question: str,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Query and format for LLM consumption.

        Returns a ready-to-use prompt with context and citation instructions.
        """
        query_result = self.query(question)

        default_system = """You are an expert analyst helping users understand U.S. Census Bureau employment data.

IMPORTANT INSTRUCTIONS:
1. Base your answers ONLY on the provided context from Census Bureau data
2. Include citation references [CITATION-ID] when stating facts
3. If the context doesn't contain enough information, say so
4. Provide specific numbers when available
5. Note that Census ACS data are estimates with margins of error

Always end your response with a "Sources" section listing the citations used."""

        user_prompt = f"""Question: {question}

Census Data Context:
{query_result['context']}

Please answer the question based on the Census data provided above. Include citation references for any facts you state."""

        return {
            "system_prompt": system_prompt or default_system,
            "user_prompt": user_prompt,
            "raw_context": query_result["context"],
            "citations": query_result["citations"],
            "citation_ids": query_result["citation_ids"],
        }

    def compare_geographies(
        self,
        geographies: list[str],
        metric: str = "unemployment",
        year: int = 2022,
    ) -> dict[str, Any]:
        """Compare employment metrics across geographies.

        Returns structured comparison data with citations.
        """
        results = {}

        for geo in geographies:
            try:
                record, citation = self.client.get_employment_data(geo, year=year)

                results[geo] = {
                    "unemployment_rate": record.unemployment_rate,
                    "labor_force_participation": record.labor_force_participation_rate,
                    "employment_population_ratio": record.employment_population_ratio,
                    "labor_force": record.labor_force,
                    "employed": record.employed,
                    "unemployed": record.unemployed,
                    "citation": citation.to_reference_string(),
                    "citation_id": citation.citation_id,
                }
            except Exception as e:
                results[geo] = {"error": str(e)}

        return {
            "comparison_year": year,
            "metric_focus": metric,
            "geographies": results,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_pipeline_stats(self) -> dict[str, Any]:
        """Get statistics about the pipeline state."""
        return {
            "vector_store": self.vector_store.get_stats(),
            "cache": self.client._cache.get_stats() if self.client._cache else None,
        }

    def close(self):
        """Close all connections."""
        self.client.close()
