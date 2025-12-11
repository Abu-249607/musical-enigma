"""Census Employment Assistant - Main interface for users."""

from typing import Any
from datetime import datetime

from ..retrieval.rag_pipeline import CensusRAGPipeline
from ..census_client import CensusMCPClient
from ..retrieval.vector_store import CensusVectorStore
from .providers import LLMProvider, get_llm_provider


class CensusEmploymentAssistant:
    """High-level assistant for Census employment queries.

    This class provides a simple interface for:
    - Recruiters researching job markets
    - Students exploring employment data
    - Researchers analyzing labor statistics

    All responses include citations for accuracy and transparency.
    """

    SYSTEM_PROMPT = """You are an expert employment data analyst with access to official U.S. Census Bureau statistics.

Your role is to help users understand employment data accurately and provide actionable insights.

CRITICAL REQUIREMENTS:
1. ONLY use information from the provided Census data context
2. ALWAYS include citation references [CITATION-ID] when stating specific numbers or facts
3. Clearly distinguish between:
   - Exact counts (Decennial Census)
   - Estimates (ACS data - note margins of error exist)
4. If data is insufficient, clearly state what's missing
5. Provide context for numbers (e.g., "This is higher/lower than the national average")

TARGET AUDIENCES:
- Recruiters: Focus on labor market conditions, talent availability, industry composition
- Students: Explain metrics clearly, provide career insights
- Researchers: Be precise about data sources and limitations

Always end responses with a Sources section listing citations used."""

    def __init__(
        self,
        census_api_key: str | None = None,
        llm_provider: LLMProvider | None = None,
        llm_provider_name: str = "anthropic",
        llm_api_key: str | None = None,
    ):
        """Initialize the assistant.

        Args:
            census_api_key: Census Bureau API key
            llm_provider: Pre-configured LLM provider
            llm_provider_name: Name of LLM provider to use
            llm_api_key: API key for LLM provider
        """
        # Initialize Census client
        self.census_client = CensusMCPClient(api_key=census_api_key)

        # Initialize vector store
        self.vector_store = CensusVectorStore()

        # Initialize RAG pipeline
        self.rag_pipeline = CensusRAGPipeline(
            census_client=self.census_client,
            vector_store=self.vector_store,
        )

        # Initialize LLM provider
        self.llm = llm_provider or get_llm_provider(
            provider_name=llm_provider_name,
            api_key=llm_api_key,
        )

        # Track conversation for context
        self._conversation_history: list[dict[str, str]] = []

    def setup_geographies(
        self,
        geographies: list[str],
        years: list[int] | None = None,
    ) -> dict[str, int]:
        """Pre-load employment data for specified geographies.

        Call this before querying to ensure data is available.

        Args:
            geographies: List of state/county names
            years: Years to load (default: [2022])

        Returns:
            Dict mapping geography to chunks loaded
        """
        return self.rag_pipeline.ingest_multiple_geographies(geographies, years)

    def ask(
        self,
        question: str,
        include_raw_data: bool = False,
    ) -> dict[str, Any]:
        """Ask a question about employment data.

        Args:
            question: Natural language question
            include_raw_data: Include structured data in response

        Returns:
            Dict with answer, citations, and metadata
        """
        # Get RAG context
        prompt_data = self.rag_pipeline.query_with_prompt(question)

        # Generate response
        if self.llm.is_available():
            answer = self.llm.generate(
                prompt=prompt_data["user_prompt"],
                system_prompt=self.SYSTEM_PROMPT,
                max_tokens=1500,
                temperature=0.3,  # Lower temperature for factual accuracy
            )
        else:
            # Fallback if no LLM configured
            answer = self._generate_fallback_response(prompt_data)

        # Build response
        response = {
            "question": question,
            "answer": answer,
            "citations": prompt_data["citations"],
            "citation_ids": prompt_data["citation_ids"],
            "generated_at": datetime.utcnow().isoformat(),
        }

        if include_raw_data:
            response["raw_context"] = prompt_data["raw_context"]

        # Store in conversation history
        self._conversation_history.append({
            "question": question,
            "answer": answer,
        })

        return response

    def _generate_fallback_response(self, prompt_data: dict[str, Any]) -> str:
        """Generate a simple response when no LLM is available."""
        context = prompt_data.get("raw_context", "")
        citation_ids = prompt_data.get("citation_ids", [])

        response_parts = [
            "Based on the Census Bureau data:\n",
            context[:1000],
            "\n\nSources:",
        ]

        for cid in citation_ids:
            response_parts.append(f"\n- {cid}")

        return "".join(response_parts)

    def compare_markets(
        self,
        geographies: list[str],
        year: int = 2022,
        focus: str = "general",
    ) -> dict[str, Any]:
        """Compare employment markets across geographies.

        Useful for recruiters comparing talent markets.

        Args:
            geographies: States/counties to compare
            year: Data year
            focus: 'general', 'unemployment', 'industry', or 'growth'

        Returns:
            Comparison analysis with citations
        """
        # Get comparison data
        comparison = self.rag_pipeline.compare_geographies(
            geographies, metric=focus, year=year
        )

        # Build comparison question
        geo_list = ", ".join(geographies)
        question = f"Compare the employment markets in {geo_list} for {year}. "

        focus_additions = {
            "unemployment": "Focus on unemployment rates and job availability.",
            "industry": "Focus on industry composition and major employers.",
            "growth": "Focus on employment growth trends and emerging sectors.",
            "general": "Provide a comprehensive overview.",
        }
        question += focus_additions.get(focus, focus_additions["general"])

        # Generate analysis
        analysis = self.ask(question)

        return {
            "comparison_data": comparison,
            "analysis": analysis["answer"],
            "citations": analysis["citations"],
        }

    def get_recruiter_insights(
        self,
        geography: str,
        industry: str | None = None,
        year: int = 2022,
    ) -> dict[str, Any]:
        """Get recruiting-focused insights for a geography.

        Args:
            geography: Target location
            industry: Specific industry focus (optional)
            year: Data year

        Returns:
            Recruiter-focused analysis
        """
        question = f"""As a recruiter, what should I know about the employment market in {geography}?

Include:
1. Overall labor market health (unemployment rate, labor force size)
2. Competition for talent (employment-population ratio)
3. {'Specifically for the ' + industry + ' industry: talent availability and concentration' if industry else 'Major industries and their employment shares'}
4. Key considerations for recruiting in this area"""

        return self.ask(question)

    def get_student_career_info(
        self,
        geography: str,
        field_of_interest: str | None = None,
        year: int = 2022,
    ) -> dict[str, Any]:
        """Get career-focused insights for students.

        Args:
            geography: Location of interest
            field_of_interest: Career field (optional)
            year: Data year

        Returns:
            Student-friendly career analysis
        """
        question = f"""I'm a student interested in the job market in {geography}.

Please explain in simple terms:
1. What's the overall employment situation? Is it easy to find jobs?
2. {'What are the opportunities in ' + field_of_interest + '?' if field_of_interest else 'What are the major industries with the most jobs?'}
3. How does this compare to national averages?
4. What should I know before job searching here?"""

        return self.ask(question)

    def get_data_summary(
        self,
        geography: str,
        year: int = 2022,
    ) -> dict[str, Any]:
        """Get a quick data summary for a geography.

        Returns structured data without LLM processing.
        """
        try:
            record, citation = self.census_client.get_employment_data(
                geography, year=year
            )

            industry_data, industry_citation = self.census_client.get_industry_employment(
                geography, year=year
            )

            return {
                "geography": geography,
                "year": year,
                "employment_summary": {
                    "total_population_16_plus": record.total_population_16_plus,
                    "labor_force": record.labor_force,
                    "employed": record.employed,
                    "unemployed": record.unemployed,
                    "not_in_labor_force": record.not_in_labor_force,
                    "unemployment_rate": record.unemployment_rate,
                    "labor_force_participation_rate": record.labor_force_participation_rate,
                    "employment_population_ratio": record.employment_population_ratio,
                },
                "industry_breakdown": industry_data,
                "citations": [
                    citation.to_reference_string(),
                    industry_citation.to_reference_string(),
                ],
            }

        except Exception as e:
            return {"error": str(e), "geography": geography, "year": year}

    def clear_history(self):
        """Clear conversation history."""
        self._conversation_history = []

    def close(self):
        """Close all connections."""
        self.census_client.close()
