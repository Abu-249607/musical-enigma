#!/usr/bin/env python3
"""Basic usage examples for Census Employment RAG tool.

This script demonstrates how to use the tool for common tasks.
Run with: python examples/basic_usage.py
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.census_client import CensusMCPClient
from src.retrieval import CensusRAGPipeline


def example_direct_data_access():
    """Example: Directly accessing Census employment data."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Direct Data Access (No LLM Required)")
    print("=" * 60)

    # Initialize client (use environment variable or pass directly)
    api_key = os.getenv("CENSUS_API_KEY", "")

    with CensusMCPClient(api_key=api_key) as client:
        # Fetch employment data for California
        record, citation = client.get_employment_data("California", year=2022)

        print(f"\nEmployment Data for {record.geography_name} ({record.year})")
        print("-" * 40)
        print(f"Total Population 16+:  {record.total_population_16_plus:,}")
        print(f"Labor Force:           {record.labor_force:,}")
        print(f"Employed:              {record.employed:,}")
        print(f"Unemployed:            {record.unemployed:,}")
        print(f"Not in Labor Force:    {record.not_in_labor_force:,}")
        print()
        print(f"Unemployment Rate:     {record.unemployment_rate}%")
        print(f"Participation Rate:    {record.labor_force_participation_rate}%")
        print(f"Employment Ratio:      {record.employment_population_ratio}%")

        print(f"\nCitation: {citation.to_reference_string()}")


def example_industry_breakdown():
    """Example: Getting industry employment breakdown."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Industry Employment Breakdown")
    print("=" * 60)

    api_key = os.getenv("CENSUS_API_KEY", "")

    with CensusMCPClient(api_key=api_key) as client:
        industry_data, citation = client.get_industry_employment("Texas", year=2022)

        total = industry_data.get("Total civilian employed", 0)
        print(f"\nIndustry Employment in Texas (2022)")
        print(f"Total Employed: {total:,}")
        print("-" * 40)

        # Sort by employment count
        sorted_industries = sorted(
            [(k, v) for k, v in industry_data.items() if k != "Total civilian employed"],
            key=lambda x: x[1],
            reverse=True,
        )

        for industry, count in sorted_industries:
            pct = (count / total * 100) if total else 0
            print(f"{industry:30s} {count:>12,}  ({pct:>5.1f}%)")

        print(f"\nCitation: {citation.to_reference_string()}")


def example_rag_pipeline():
    """Example: Using the RAG pipeline for semantic search."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: RAG Pipeline (Semantic Search)")
    print("=" * 60)

    api_key = os.getenv("CENSUS_API_KEY", "")

    pipeline = CensusRAGPipeline(api_key=api_key)

    # Ingest data for a few states
    print("\nIngesting employment data...")
    results = pipeline.ingest_multiple_geographies(
        ["California", "Texas", "Florida"],
        years=[2022],
    )

    for geo, chunks in results.items():
        print(f"  {geo}: {chunks} chunks ingested")

    # Query the pipeline
    print("\nQuerying: 'Which state has the highest unemployment?'")
    query_result = pipeline.query("Which state has the highest unemployment?")

    print(f"\nRetrieved {len(query_result['results'])} relevant chunks:")
    for r in query_result["results"][:3]:
        print(f"  - [{r['metadata']['citation_id']}] {r['content'][:100]}...")

    print("\nCitations used:")
    for cit in query_result["citations"]:
        print(f"  - {cit['citation_id']}: {cit['geography']} ({cit['year']})")


def example_comparison():
    """Example: Comparing employment across states."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: State Comparison")
    print("=" * 60)

    api_key = os.getenv("CENSUS_API_KEY", "")

    pipeline = CensusRAGPipeline(api_key=api_key)

    states = ["California", "Texas", "New York", "Florida"]
    comparison = pipeline.compare_geographies(states, year=2022)

    print(f"\nEmployment Comparison ({comparison['comparison_year']})")
    print("-" * 70)
    print(f"{'State':<15} {'Unemp. Rate':>12} {'Participation':>14} {'Labor Force':>15}")
    print("-" * 70)

    for state, data in comparison["geographies"].items():
        if "error" in data:
            print(f"{state:<15} Error: {data['error']}")
        else:
            print(
                f"{state:<15} "
                f"{data['unemployment_rate']:>11.1f}% "
                f"{data['labor_force_participation']:>13.1f}% "
                f"{data['labor_force']:>15,}"
            )

    print("-" * 70)


def example_with_llm():
    """Example: Full assistant with LLM (requires API key)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Full Assistant with LLM")
    print("=" * 60)

    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    census_key = os.getenv("CENSUS_API_KEY", "")

    if not anthropic_key:
        print("\nSkipping LLM example (ANTHROPIC_API_KEY not set)")
        print("Set the environment variable to enable this example.")
        return

    from src.llm import CensusEmploymentAssistant

    assistant = CensusEmploymentAssistant(
        census_api_key=census_key,
        llm_provider_name="anthropic",
        llm_api_key=anthropic_key,
    )

    # Setup data
    print("\nSetting up data for California...")
    assistant.setup_geographies(["California"])

    # Ask a question
    print("\nAsking: 'What is the employment situation in California?'")
    result = assistant.ask("What is the employment situation in California?")

    print("\nAssistant Response:")
    print("-" * 40)
    print(result["answer"])

    print("\nCitations:")
    for cit in result["citations"]:
        print(f"  - {cit}")


def main():
    """Run all examples."""
    print("Census Employment RAG Tool - Examples")
    print("=" * 60)

    try:
        example_direct_data_access()
    except Exception as e:
        print(f"Example 1 failed: {e}")

    try:
        example_industry_breakdown()
    except Exception as e:
        print(f"Example 2 failed: {e}")

    try:
        example_rag_pipeline()
    except Exception as e:
        print(f"Example 3 failed: {e}")

    try:
        example_comparison()
    except Exception as e:
        print(f"Example 4 failed: {e}")

    try:
        example_with_llm()
    except Exception as e:
        print(f"Example 5 failed: {e}")

    print("\n" + "=" * 60)
    print("Examples complete!")


if __name__ == "__main__":
    main()
