"""Intelligent Census Assistant - No Hallucinations

An assistant that:
1. Understands what the user is asking
2. Fetches fresh, accurate data from Census API
3. Returns structured, verified responses
4. Never hallucinates or makes up data
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ..census_client import CensusMCPClient
from ..models.employment import EmploymentRecord
from ..models.citation import Citation


@dataclass
class QueryIntent:
    """Parsed user query intent"""
    geography: Optional[str] = None
    metric: Optional[str] = None  # unemployment, labor_force, industry, etc.
    comparison: bool = False
    multiple_geographies: List[str] = None
    year: int = 2024

    def __post_init__(self):
        if self.multiple_geographies is None:
            self.multiple_geographies = []


class IntelligentCensusAssistant:
    """An assistant that accurately answers Census employment questions"""

    # US States and territories
    STATES = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
        "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
        "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
        "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
        "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
        "New Hampshire", "New Jersey", "New Mexico", "New York",
        "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
        "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
        "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
        "West Virginia", "Wisconsin", "Wyoming", "District of Columbia",
        "Puerto Rico"
    ]

    # Common city → state mappings (for better UX)
    CITY_TO_STATE = {
        "chicago": "Illinois",
        "new york": "New York",
        "los angeles": "California",
        "houston": "Texas",
        "phoenix": "Arizona",
        "philadelphia": "Pennsylvania",
        "san antonio": "Texas",
        "san diego": "California",
        "dallas": "Texas",
        "austin": "Texas",
        "san jose": "California",
        "jacksonville": "Florida",
        "fort worth": "Texas",
        "columbus": "Ohio",
        "charlotte": "North Carolina",
        "san francisco": "California",
        "indianapolis": "Indiana",
        "seattle": "Washington",
        "denver": "Colorado",
        "boston": "Massachusetts",
        "detroit": "Michigan",
        "nashville": "Tennessee",
        "portland": "Oregon",
        "las vegas": "Nevada",
        "miami": "Florida",
        "atlanta": "Georgia",
    }

    # Metric keywords
    METRIC_KEYWORDS = {
        "unemployment": ["unemployment", "jobless", "unemployed"],
        "labor_force": ["labor force", "workforce", "workers"],
        "employment": ["employment", "employed", "jobs"],
        "participation": ["participation rate", "lfpr"],
        "industry": ["industry", "industries", "sector", "sectors"],
        "occupation": ["occupation", "job type", "career"],
    }

    def __init__(self, census_client: Optional[CensusMCPClient] = None):
        """Initialize the intelligent assistant

        Args:
            census_client: Optional Census client (will create one if not provided)
        """
        self.client = census_client or CensusMCPClient(use_cache=True)

    def parse_query(self, query: str) -> QueryIntent:
        """Parse user query to understand intent

        Args:
            query: User's natural language query

        Returns:
            QueryIntent with extracted information
        """
        query_lower = query.lower()
        intent = QueryIntent()

        # Extract year
        year_match = re.search(r'\b(20\d{2})\b', query)
        if year_match:
            intent.year = int(year_match.group(1))

        # Check for comparison keywords
        if any(word in query_lower for word in ["compare", "versus", "vs", "versus", "between"]):
            intent.comparison = True

        # Extract geographies (states or cities)
        found_geographies = []

        # First check for cities
        for city, state in self.CITY_TO_STATE.items():
            if city in query_lower:
                found_geographies.append(state)
                intent.geography = state  # Set primary geography

        # Then check for states
        for state in self.STATES:
            if state.lower() in query_lower:
                if state not in found_geographies:
                    found_geographies.append(state)
                if not intent.geography:
                    intent.geography = state

        if len(found_geographies) > 1:
            intent.comparison = True
            intent.multiple_geographies = found_geographies

        # Extract metric
        for metric, keywords in self.METRIC_KEYWORDS.items():
            if any(keyword in query_lower for keyword in keywords):
                intent.metric = metric
                break

        # Default metric if none found
        if not intent.metric:
            intent.metric = "employment"

        return intent

    def answer_question(self, query: str) -> Dict:
        """Answer user's question with accurate Census data

        Args:
            query: User's natural language query

        Returns:
            Dictionary with answer, data, and citations
        """
        # Parse the query
        intent = self.parse_query(query)

        # If no geography found, return helpful message
        if not intent.geography and not intent.multiple_geographies:
            return {
                "answer": "I couldn't identify a specific state or city in your question. Could you please specify a state? For example: 'What is the unemployment rate in California?' or 'Compare unemployment in Texas and Florida.'",
                "data": None,
                "citations": [],
                "success": False
            }

        # Handle comparison queries
        if intent.comparison and len(intent.multiple_geographies) > 1:
            return self._handle_comparison(intent)

        # Handle single geography query
        return self._handle_single_geography(intent)

    def _handle_single_geography(self, intent: QueryIntent) -> Dict:
        """Handle query for a single geography

        Args:
            intent: Parsed query intent

        Returns:
            Response dictionary
        """
        try:
            # Fetch fresh data from Census API
            record, citation = self.client.get_employment_data(
                geography_name=intent.geography,
                year=intent.year
            )

            # Build response based on metric
            if intent.metric == "unemployment":
                answer = self._format_unemployment_response(record, citation)
            elif intent.metric == "labor_force":
                answer = self._format_labor_force_response(record, citation)
            elif intent.metric == "industry":
                # Fetch industry data
                industry_data, ind_citation = self.client.get_industry_employment(
                    geography_name=intent.geography,
                    year=intent.year
                )
                answer = self._format_industry_response(industry_data, intent.geography, ind_citation)
                citation = ind_citation
            else:
                # General employment overview
                answer = self._format_employment_overview(record, citation)

            return {
                "answer": answer,
                "data": record,
                "citations": [citation],
                "success": True,
                "geography": intent.geography,
                "year": intent.year
            }

        except Exception as e:
            return {
                "answer": f"I encountered an error fetching data for {intent.geography}: {str(e)}",
                "data": None,
                "citations": [],
                "success": False,
                "error": str(e)
            }

    def _handle_comparison(self, intent: QueryIntent) -> Dict:
        """Handle comparison query for multiple geographies

        Args:
            intent: Parsed query intent

        Returns:
            Response dictionary
        """
        results = []
        citations = []

        for geography in intent.multiple_geographies:
            try:
                record, citation = self.client.get_employment_data(
                    geography_name=geography,
                    year=intent.year
                )
                results.append({
                    "geography": geography,
                    "record": record,
                    "citation": citation
                })
                citations.append(citation)
            except Exception as e:
                results.append({
                    "geography": geography,
                    "error": str(e)
                })

        # Format comparison response
        answer = self._format_comparison_response(results, intent.metric)

        return {
            "answer": answer,
            "data": results,
            "citations": citations,
            "success": True,
            "comparison": True,
            "geographies": intent.multiple_geographies,
            "year": intent.year
        }

    def _format_unemployment_response(self, record: EmploymentRecord, citation: Citation) -> str:
        """Format unemployment rate response"""
        response = f"**{record.geography_name} Unemployment ({record.year})**\n\n"

        if record.unemployment_rate is not None:
            response += f"• **Unemployment Rate:** {record.unemployment_rate:.1f}%\n"

        if record.unemployed is not None:
            response += f"• **Unemployed:** {record.unemployed:,} people\n"

        if record.labor_force is not None:
            response += f"• **Labor Force:** {record.labor_force:,} people\n"

        response += f"\n*Source: {citation.to_reference_string()}*"
        return response

    def _format_labor_force_response(self, record: EmploymentRecord, citation: Citation) -> str:
        """Format labor force response"""
        response = f"**{record.geography_name} Labor Force ({record.year})**\n\n"

        if record.labor_force is not None:
            response += f"• **Labor Force:** {record.labor_force:,} people\n"

        if record.employed is not None:
            response += f"• **Employed:** {record.employed:,} people\n"

        if record.labor_force_participation_rate is not None:
            response += f"• **Participation Rate:** {record.labor_force_participation_rate:.1f}%\n"

        response += f"\n*Source: {citation.to_reference_string()}*"
        return response

    def _format_employment_overview(self, record: EmploymentRecord, citation: Citation) -> str:
        """Format general employment overview"""
        response = f"**{record.geography_name} Employment Overview ({record.year})**\n\n"

        if record.unemployment_rate is not None:
            response += f"• **Unemployment Rate:** {record.unemployment_rate:.1f}%\n"

        if record.labor_force is not None:
            response += f"• **Labor Force:** {record.labor_force:,} people\n"

        if record.employed is not None:
            response += f"• **Employed:** {record.employed:,} people\n"

        if record.labor_force_participation_rate is not None:
            response += f"• **Participation Rate:** {record.labor_force_participation_rate:.1f}%\n"

        if record.employment_population_ratio is not None:
            response += f"• **Employment-Population Ratio:** {record.employment_population_ratio:.1f}%\n"

        response += f"\n*Source: {citation.to_reference_string()}*"
        return response

    def _format_industry_response(self, industry_data: Dict[str, int], geography: str, citation: Citation) -> str:
        """Format industry breakdown response"""
        response = f"**{geography} Top Industries**\n\n"

        # Remove total and sort by size
        industries = {k: v for k, v in industry_data.items() if k != "Total civilian employed"}
        sorted_industries = sorted(industries.items(), key=lambda x: x[1], reverse=True)

        # Show top 5
        for industry, count in sorted_industries[:5]:
            response += f"• **{industry}:** {count:,} workers\n"

        response += f"\n*Source: {citation.to_reference_string()}*"
        return response

    def _format_comparison_response(self, results: List[Dict], metric: str) -> str:
        """Format comparison response"""
        response = f"**Comparison: {metric.replace('_', ' ').title()}**\n\n"

        for result in results:
            if "error" in result:
                response += f"• **{result['geography']}:** Error - {result['error']}\n"
                continue

            geography = result["geography"]
            record = result["record"]

            if metric == "unemployment" and record.unemployment_rate is not None:
                response += f"• **{geography}:** {record.unemployment_rate:.1f}% unemployment\n"
            elif metric == "labor_force" and record.labor_force is not None:
                response += f"• **{geography}:** {record.labor_force:,} workers\n"
            else:
                # General comparison
                if record.unemployment_rate is not None:
                    response += f"• **{geography}:** {record.unemployment_rate:.1f}% unemployment, "
                if record.labor_force is not None:
                    response += f"{record.labor_force:,} labor force\n"

        response += f"\n*Source: U.S. Census Bureau ACS {results[0]['record'].year if results else 2024}*"
        return response
