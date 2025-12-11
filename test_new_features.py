"""Test script for new features.

Quick test to verify all new components work correctly.
Run this after installation to verify everything is set up properly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()
api_key = os.getenv("CENSUS_API_KEY")

if not api_key:
    print("⚠️  WARNING: CENSUS_API_KEY not found in .env file")
    print("The Census API works without a key but is rate-limited to 500 calls/day")
    print("Get a free key at: https://api.census.gov/data/key_signup.html\n")


def test_basic_client():
    """Test basic census client functionality."""
    print("=" * 80)
    print("TEST 1: Basic Census Client (2024 Data)")
    print("=" * 80)

    try:
        from src.census_client import CensusMCPClient

        client = CensusMCPClient(api_key=api_key)

        # Test 2024 data fetch
        record, citation = client.get_employment_data("California", year=2024, dataset="acs/acs1")

        print(f"✅ Successfully fetched 2024 data for California")
        print(f"   Unemployment Rate: {record.unemployment_rate:.1f}%")
        print(f"   Labor Force: {record.labor_force:,}")
        print(f"   Citation: {citation.citation_id}")

        client.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_stem_intelligence():
    """Test STEM Intelligence Hub."""
    print("\n" + "=" * 80)
    print("TEST 2: STEM Intelligence Hub")
    print("=" * 80)

    try:
        from src.analytics import STEMIntelligenceHub

        stem_hub = STEMIntelligenceHub(api_key=api_key)

        # Get STEM occupations
        stem_data = stem_hub.get_stem_occupations("California", year=2024)

        print(f"✅ STEM data retrieved successfully")
        print(f"   Found {len(stem_data)} STEM occupation categories")

        for occ in stem_data:
            print(f"   - {occ.occupation_name}: {occ.total_count:,} workers")

        stem_hub.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversational_rag():
    """Test conversational RAG pipeline."""
    print("\n" + "=" * 80)
    print("TEST 3: Conversational RAG Pipeline")
    print("=" * 80)

    try:
        from src.retrieval import ConversationalRAGPipeline

        rag = ConversationalRAGPipeline(api_key=api_key, enable_memory=True)

        # Start conversation
        conv_id = rag.start_conversation()
        print(f"✅ Started conversation: {conv_id}")

        # Ingest data
        print("   Loading employment data...")
        chunks = rag.ingest_geography("California", years=[2024])
        print(f"   Ingested {chunks} data chunks")

        # Query
        response = rag.chat(
            "What's the unemployment rate in California?",
            conversation_id=conv_id
        )

        print(f"✅ Query successful")
        print(f"   Retrieved {len(response['citations'])} citations")
        print(f"   Context length: {len(response['context'])} characters")

        rag.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualizations():
    """Test geographic visualizations."""
    print("\n" + "=" * 80)
    print("TEST 4: Geographic Visualizations")
    print("=" * 80)

    try:
        from src.analytics import GeographicVisualizer

        viz = GeographicVisualizer()

        # Create test data
        test_data = {
            "California": 5.2,
            "Texas": 4.1,
            "New York": 4.8,
        }

        # Create choropleth
        fig = viz.create_choropleth_map(
            state_data=test_data,
            metric_name="Unemployment Rate (%)",
            title="Test Unemployment Map"
        )

        print("✅ Created choropleth map")
        print(f"   Data points: {len(test_data)}")

        # Save to file
        fig.write_html("test_map.html")
        print("   Saved to: test_map.html")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_employment_datasets():
    """Test employment dataset catalog."""
    print("\n" + "=" * 80)
    print("TEST 5: Employment Dataset Catalog")
    print("=" * 80)

    try:
        from src.models.employment_datasets import (
            ALL_EMPLOYMENT_TABLES,
            get_stem_tables,
            get_gig_economy_tables,
            DatasetCategory
        )

        print(f"✅ Loaded {len(ALL_EMPLOYMENT_TABLES)} employment tables")

        stem_tables = get_stem_tables()
        print(f"   STEM tables: {len(stem_tables)}")
        for table in stem_tables:
            print(f"     - {table.table_id}: {table.title}")

        gig_tables = get_gig_economy_tables()
        print(f"   Gig economy tables: {len(gig_tables)}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """Test that all dependencies are installed."""
    print("\n" + "=" * 80)
    print("TEST 6: Dependencies Check")
    print("=" * 80)

    required = [
        "httpx",
        "pydantic",
        "chromadb",
        "sentence_transformers",
        "diskcache",
        "tenacity",
        "streamlit",
        "pandas",
        "plotly",
    ]

    optional = [
        "folium",
        "mcp",
    ]

    all_ok = True

    print("Required dependencies:")
    for pkg in required:
        try:
            __import__(pkg)
            print(f"   ✅ {pkg}")
        except ImportError:
            print(f"   ❌ {pkg} - MISSING")
            all_ok = False

    print("\nOptional dependencies:")
    for pkg in optional:
        try:
            __import__(pkg)
            print(f"   ✅ {pkg}")
        except ImportError:
            print(f"   ⚠️  {pkg} - Not installed (optional)")

    return all_ok


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("CENSUS EMPLOYMENT RAG - FEATURE TESTS")
    print("=" * 80)
    print("\nTesting new features: 2024 data, STEM analytics, visualizations, RAG")
    print()

    results = {
        "Dependencies": test_dependencies(),
        "Basic Client (2024)": test_basic_client(),
        "Employment Datasets": test_employment_datasets(),
        "STEM Intelligence": test_stem_intelligence(),
        "Conversational RAG": test_conversational_rag(),
        "Visualizations": test_visualizations(),
    }

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Run demo: python examples/recruiter_demo.py")
        print("  2. Try Streamlit app: streamlit run app_enhanced.py")
        print("  3. Explore examples in the examples/ directory")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("Make sure all dependencies are installed:")
        print("  pip install -e \".[web]\"")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
