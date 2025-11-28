"""Recruiter Use Case Demo

Demonstrates how recruiters can use the Census Employment RAG tool to:
- Assess talent pools by geography
- Compare labor markets
- Identify hiring hotspots
- Analyze industry concentrations
"""

import os
from dotenv import load_dotenv

from src.census_client import CensusMCPClient
from src.analytics import STEMIntelligenceHub, GeographicVisualizer
from src.retrieval import ConversationalRAGPipeline

# Load environment variables
load_dotenv()
api_key = os.getenv("CENSUS_API_KEY")


def demo_talent_pool_assessment():
    """Demo: Assess tech talent pool in multiple states."""
    print("=" * 80)
    print("DEMO 1: Tech Talent Pool Assessment")
    print("=" * 80)

    client = CensusMCPClient(api_key=api_key)
    stem_hub = STEMIntelligenceHub(census_client=client)

    # States to compare
    states = ["California", "Texas", "Washington", "New York"]

    print(f"\nComparing tech talent across: {', '.join(states)}\n")

    # Get STEM data for each state
    for state in states:
        print(f"\n{state}:")
        print("-" * 40)

        try:
            stem_occupations = stem_hub.get_stem_occupations(state, year=2024)

            for occ in stem_occupations:
                if "Computer" in occ.occupation_name:
                    print(f"  {occ.occupation_name}:")
                    print(f"    Total workers: {occ.total_count:,}")
                    print(f"    Female: {occ.female_count:,} ({occ.female_percentage:.1f}%)")
                    print(f"    Male: {occ.male_count:,}")
                    print(f"    Citation: {occ.citation.citation_id}")

        except Exception as e:
            print(f"  Error: {e}")

    client.close()


def demo_labor_market_comparison():
    """Demo: Compare overall labor market conditions."""
    print("\n" + "=" * 80)
    print("DEMO 2: Labor Market Comparison")
    print("=" * 80)

    client = CensusMCPClient(api_key=api_key)

    states = ["California", "Texas", "Florida"]
    print(f"\nComparing labor markets: {', '.join(states)}\n")

    comparison_data = []

    for state in states:
        try:
            record, citation = client.get_employment_data(state, year=2024)

            comparison_data.append({
                "State": state,
                "Labor Force": record.labor_force,
                "Unemployment Rate": record.unemployment_rate,
                "Participation Rate": record.labor_force_participation_rate,
            })

            print(f"{state}:")
            print(f"  Labor Force: {record.labor_force:,}")
            print(f"  Unemployment Rate: {record.unemployment_rate:.1f}%")
            print(f"  Participation Rate: {record.labor_force_participation_rate:.1f}%")
            print(f"  Citation: {citation.citation_id}\n")

        except Exception as e:
            print(f"{state}: Error - {e}\n")

    client.close()

    # Generate visualization
    viz = GeographicVisualizer()

    unemployment_map = {d["State"]: d["Unemployment Rate"] for d in comparison_data}
    fig = viz.create_unemployment_heatmap(unemployment_map)

    print("\nGenerating choropleth map...")
    fig.write_html("recruiter_unemployment_map.html")
    print("Map saved to: recruiter_unemployment_map.html")


def demo_industry_concentration():
    """Demo: Analyze industry concentration in a region."""
    print("\n" + "=" * 80)
    print("DEMO 3: Industry Concentration Analysis")
    print("=" * 80)

    client = CensusMCPClient(api_key=api_key)

    state = "California"
    print(f"\nIndustry breakdown for {state}:\n")

    try:
        industry_data, citation = client.get_industry_employment(state, year=2024)

        # Sort by worker count
        sorted_industries = sorted(
            industry_data.items(),
            key=lambda x: x[1],
            reverse=True
        )

        total = industry_data.get("Total civilian employed", 1)

        for industry, count in sorted_industries[:10]:
            if industry != "Total civilian employed":
                percentage = (count / total * 100) if total > 0 else 0
                print(f"{industry:60s} {count:>10,} ({percentage:>5.1f}%)")

        print(f"\nCitation: {citation.to_reference_string()}")

    except Exception as e:
        print(f"Error: {e}")

    client.close()


def demo_conversational_hiring_insights():
    """Demo: Use conversational RAG for hiring insights."""
    print("\n" + "=" * 80)
    print("DEMO 4: Conversational Hiring Insights")
    print("=" * 80)

    rag = ConversationalRAGPipeline(api_key=api_key)

    # Ingest data for analysis
    print("\nLoading employment data...")
    rag.ingest_geography("California", years=[2024])
    rag.ingest_geography("Texas", years=[2024])

    # Start conversation
    conv_id = rag.start_conversation()

    # Ask questions
    questions = [
        "Where should I recruit software engineers: California or Texas?",
        "What's the tech talent pool like in California?",
        "How does the unemployment rate compare between these states?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n[Question {i}]: {question}")
        print("-" * 60)

        response = rag.chat(question, conversation_id=conv_id)

        print(f"Context: {response['context'][:500]}...")
        print(f"\nCitations: {len(response['citations'])} sources")

        for citation in response['citations'][:3]:
            print(f"  - {citation['dataset']} ({citation['year']}) - {citation['geography']}")

    rag.close()


def demo_stem_gender_gap_analysis():
    """Demo: Analyze STEM gender gaps for diversity hiring."""
    print("\n" + "=" * 80)
    print("DEMO 5: STEM Gender Gap Analysis for Diversity Hiring")
    print("=" * 80)

    stem_hub = STEMIntelligenceHub(api_key=api_key)

    state = "California"
    print(f"\nSTEM Gender Gap Analysis - {state}\n")

    try:
        gaps = stem_hub.analyze_stem_gender_gap(state, year=2024)

        print("Occupation                           Total      Female    Male    Female%  Gap")
        print("-" * 85)

        for gap in gaps:
            gap_indicator = "⚖️" if 40 <= gap.female_percentage <= 60 else "⚠️"
            print(f"{gap.occupation_name:35s} {gap.total_workers:>8,}  "
                  f"{gap.female_count:>8,}  {gap.male_count:>7,}  "
                  f"{gap.female_percentage:>6.1f}%  {gap_indicator}")

        print("\n⚖️ = Balanced (40-60%)  |  ⚠️ = Imbalanced (<40% or >60%)")

    except Exception as e:
        print(f"Error: {e}")

    stem_hub.close()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CENSUS EMPLOYMENT RAG - RECRUITER USE CASES")
    print("=" * 80)
    print("\nDemonstrating how recruiters can leverage Census data for hiring decisions")

    # Run demos
    demo_talent_pool_assessment()
    demo_labor_market_comparison()
    demo_industry_concentration()
    demo_conversational_hiring_insights()
    demo_stem_gender_gap_analysis()

    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nAll data sourced from U.S. Census Bureau with full citation tracking.")
    print("Use these insights to make data-driven hiring decisions.\n")
