"""Hybrid search combining vector and structured queries."""

import re
from typing import Any
from .vector_store import CensusVectorStore


class HybridSearcher:
    """Combines semantic vector search with structured filtering.

    Implements a hybrid search strategy:
    1. Parse query for structured constraints (geography, year, metrics)
    2. Execute vector search with filters
    3. Re-rank results based on relevance signals
    4. Return results with citation metadata
    """

    # Patterns for extracting structured info from queries
    YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")
    RATE_KEYWORDS = ["rate", "percentage", "percent", "%"]
    COMPARISON_KEYWORDS = ["compare", "versus", "vs", "between", "difference"]

    # Known metrics for keyword matching
    METRIC_KEYWORDS = {
        "unemployment": ["unemployment", "unemployed", "jobless", "out of work"],
        "employment": ["employment", "employed", "jobs", "working"],
        "labor_force": ["labor force", "workforce", "participation"],
        "industry": ["industry", "sector", "field", "occupation"],
    }

    def __init__(self, vector_store: CensusVectorStore):
        """Initialize with a vector store."""
        self.vector_store = vector_store

    def search(
        self,
        query: str,
        n_results: int = 5,
    ) -> list[dict[str, Any]]:
        """Execute hybrid search on the query.

        Args:
            query: Natural language query
            n_results: Maximum results to return

        Returns:
            Ranked list of relevant chunks with metadata
        """
        # Parse query for structured constraints
        parsed = self._parse_query(query)

        # Execute vector search with any extracted filters
        results = self.vector_store.search(
            query=query,
            n_results=n_results * 2,  # Over-fetch for re-ranking
            filter_year=parsed.get("year"),
            filter_geography=parsed.get("geography"),
        )

        # Re-rank based on relevance signals
        ranked = self._rerank_results(results, parsed)

        return ranked[:n_results]

    def _parse_query(self, query: str) -> dict[str, Any]:
        """Extract structured information from natural language query."""
        parsed = {
            "original_query": query,
            "query_type": "general",
            "metrics": [],
        }

        query_lower = query.lower()

        # Extract year
        year_match = self.YEAR_PATTERN.search(query)
        if year_match:
            parsed["year"] = int(year_match.group(1))

        # Detect comparison queries
        if any(kw in query_lower for kw in self.COMPARISON_KEYWORDS):
            parsed["query_type"] = "comparison"

        # Detect rate/percentage queries
        if any(kw in query_lower for kw in self.RATE_KEYWORDS):
            parsed["wants_rates"] = True

        # Extract metrics of interest
        for metric, keywords in self.METRIC_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                parsed["metrics"].append(metric)

        # Try to extract geography names (simplified - would use NER in production)
        # For now, just mark if specific states are mentioned
        us_states = [
            "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
            "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
            "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
            "maine", "maryland", "massachusetts", "michigan", "minnesota",
            "mississippi", "missouri", "montana", "nebraska", "nevada",
            "new hampshire", "new jersey", "new mexico", "new york",
            "north carolina", "north dakota", "ohio", "oklahoma", "oregon",
            "pennsylvania", "rhode island", "south carolina", "south dakota",
            "tennessee", "texas", "utah", "vermont", "virginia", "washington",
            "west virginia", "wisconsin", "wyoming"
        ]

        mentioned_states = [s for s in us_states if s in query_lower]
        if len(mentioned_states) == 1:
            parsed["geography"] = mentioned_states[0].title()
        elif mentioned_states:
            parsed["mentioned_geographies"] = [s.title() for s in mentioned_states]

        return parsed

    def _rerank_results(
        self,
        results: list[dict[str, Any]],
        parsed_query: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Re-rank results based on relevance signals."""
        for result in results:
            # Start with vector similarity score
            score = result.get("score", 0.5)

            # Boost if year matches
            if parsed_query.get("year"):
                if result["metadata"].get("year") == parsed_query["year"]:
                    score += 0.1

            # Boost if chunk type matches query intent
            chunk_type = result["metadata"].get("type", "")
            if parsed_query.get("wants_rates") and "rates" in chunk_type:
                score += 0.1
            if "industry" in parsed_query.get("metrics", []) and "industry" in chunk_type:
                score += 0.1

            # Boost if geography matches
            if parsed_query.get("geography"):
                if result["metadata"].get("geography_name") == parsed_query["geography"]:
                    score += 0.15

            result["final_score"] = min(score, 1.0)

        # Sort by final score
        return sorted(results, key=lambda x: x.get("final_score", 0), reverse=True)

    def search_for_comparison(
        self,
        geographies: list[str],
        metric: str = "unemployment",
        year: int | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Search for data to compare multiple geographies.

        Returns results grouped by geography for easy comparison.
        """
        results_by_geo = {}

        for geo in geographies:
            results = self.vector_store.search(
                query=f"{metric} employment data for {geo}",
                n_results=3,
                filter_geography=geo,
                filter_year=year,
            )
            results_by_geo[geo] = results

        return results_by_geo

    def get_context_for_llm(
        self,
        query: str,
        max_tokens: int = 2000,
    ) -> tuple[str, list[str]]:
        """Get formatted context string for LLM prompting.

        Args:
            query: User query
            max_tokens: Approximate max tokens for context

        Returns:
            Tuple of (context_string, list_of_citation_ids)
        """
        results = self.search(query, n_results=5)

        context_parts = []
        citation_ids = []
        char_count = 0
        char_limit = max_tokens * 4  # Rough chars-to-tokens conversion

        for result in results:
            content = result.get("content", "")
            citation_id = result["metadata"].get("citation_id", "unknown")

            # Check if we have room
            if char_count + len(content) > char_limit:
                break

            # Format with citation reference
            formatted = f"[{citation_id}] {content}"
            context_parts.append(formatted)
            citation_ids.append(citation_id)
            char_count += len(formatted)

        context = "\n\n".join(context_parts)
        return context, citation_ids
