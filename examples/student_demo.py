"""Student Use Case Demo

Demonstrates how students can use the tool to:
- Explore career pathways
- Compare employment outcomes by field of study
- Identify growing industries
- Plan career decisions based on data
"""

import os
from dotenv import load_dotenv

from src.census_client import CensusMCPClient
from src.analytics import STEMIntelligenceHub
from src.retrieval import ConversationalRAGPipeline

load_dotenv()
api_key = os.getenv("CENSUS_API_KEY")


def demo_career_exploration():
    """Demo: Explore STEM career options."""
    print("=" * 80)
    print("DEMO 1: STEM Career Exploration")
    print("=" * 80)

    stem_hub = STEMIntelligenceHub(api_key=api_key)

    state = "California"
    print(f"\nExploring STEM careers in {state}:\n")

    try:
        stem_occupations = stem_hub.get_stem_occupations(state, year=2024)

        print("Occupation                              Workers      Growth Potential")
        print("-" * 75)

        for occ in sorted(stem_occupations, key=lambda x: x.total_count, reverse=True):
            # Simple growth indicator based on size
            if occ.total_count > 100000:
                growth = "🚀 High demand"
            elif occ.total_count > 50000:
                growth = "📈 Good demand"
            else:
                growth = "💼 Moderate"

            print(f"{occ.occupation_name:40s} {occ.total_count:>8,}  {growth}")

        print("\n🚀 = High demand (100k+ workers)")
        print("📈 = Good demand (50k-100k workers)")
        print("💼 = Moderate demand (<50k workers)")

    except Exception as e:
        print(f"Error: {e}")

    stem_hub.close()


def demo_field_of_study_outcomes():
    """Demo: Compare employment outcomes by degree field."""
    print("\n" + "=" * 80)
    print("DEMO 2: Field of Study Employment Outcomes")
    print("=" * 80)

    stem_hub = STEMIntelligenceHub(api_key=api_key)

    state = "California"
    print(f"\nEmployment outcomes for STEM degrees in {state}:\n")

    try:
        field_outcomes = stem_hub.get_stem_field_outcomes(state, year=2024)

        print("Degree Field                      Graduates    Employment Rate")
        print("-" * 65)

        for field in field_outcomes:
            # Emoji based on employment rate
            if field.employment_rate >= 90:
                emoji = "✅"
            elif field.employment_rate >= 80:
                emoji = "👍"
            else:
                emoji = "⚠️"

            print(f"{emoji} {field.field_name:32s} {field.total_with_degree:>10,}  "
                  f"{field.employment_rate:>5.1f}%")

        print("\n✅ = Excellent employment (≥90%)")
        print("👍 = Good employment (80-90%)")
        print("⚠️ = Lower employment (<80%)")

    except Exception as e:
        print(f"Error: {e}")

    stem_hub.close()


def demo_career_questions():
    """Demo: Ask conversational career questions."""
    print("\n" + "=" * 80)
    print("DEMO 3: Ask Career Questions")
    print("=" * 80)

    rag = ConversationalRAGPipeline(api_key=api_key)

    # Pre-load data
    print("\nLoading employment data...")
    rag.ingest_geography("California", years=[2024])
    rag.ingest_geography("New York", years=[2024])

    conv_id = rag.start_conversation()

    questions = [
        "What are the best tech jobs for recent graduates?",
        "Which state has more opportunities: California or New York?",
        "What industries are growing?",
        "Should I consider a career in healthcare?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n[Student Question {i}]: {question}")
        print("-" * 60)

        response = rag.chat(question, conversation_id=conv_id)

        print(f"Answer preview: {response['context'][:400]}...")
        print(f"Based on {len(response['citations'])} Census Bureau sources")

    rag.close()


def demo_state_comparison_for_career():
    """Demo: Compare states for career planning."""
    print("\n" + "=" * 80)
    print("DEMO 4: Compare States for Your Career")
    print("=" * 80)

    client = CensusMCPClient(api_key=api_key)

    states = ["California", "Texas", "Washington"]
    print(f"\nComparing states for career planning: {', '.join(states)}\n")

    comparison = []

    for state in states:
        try:
            record, citation = client.get_employment_data(state, year=2024)

            comparison.append({
                "state": state,
                "unemployment": record.unemployment_rate,
                "labor_force": record.labor_force,
                "participation": record.labor_force_participation_rate,
            })

        except Exception as e:
            print(f"{state}: Error - {e}")

    # Print comparison table
    print("State              Unemployment    Labor Force    Participation")
    print("-" * 70)

    for data in sorted(comparison, key=lambda x: x["unemployment"]):
        print(f"{data['state']:15s}    {data['unemployment']:>5.1f}%      "
              f"{data['labor_force']:>11,}      {data['participation']:>5.1f}%")

    print("\n💡 Lower unemployment = easier to find jobs")
    print("💡 Higher labor force = more opportunities")
    print("💡 Higher participation = active job market")

    client.close()


def demo_stem_career_report():
    """Demo: Generate comprehensive STEM career report."""
    print("\n" + "=" * 80)
    print("DEMO 5: Your Personalized STEM Career Report")
    print("=" * 80)

    stem_hub = STEMIntelligenceHub(api_key=api_key)

    state = "California"
    print(f"\nGenerating STEM career report for {state}...\n")

    try:
        report = stem_hub.generate_stem_report(state, year=2024)

        print("=" * 60)
        print(f"STEM CAREER REPORT - {report['geography']}")
        print(f"Data Year: {report['year']}")
        print("=" * 60)

        print("\n📊 SUMMARY")
        print("-" * 60)
        summary = report['summary']
        print(f"Total STEM Workers: {summary['total_stem_workers']:,}")
        print(f"Female in STEM: {summary['female_stem_workers']:,} ({summary['overall_female_percentage']:.1f}%)")
        print(f"Male in STEM: {summary['male_stem_workers']:,}")

        print("\n💼 TOP STEM OCCUPATIONS")
        print("-" * 60)
        for occ in report['occupations'][:5]:
            print(f"{occ['name']:45s} {occ['total']:>10,} workers")

        print("\n⚖️ DIVERSITY INSIGHTS")
        print("-" * 60)
        gender = report['gender_analysis']
        print(f"Most Balanced: {gender['most_balanced_occupation']} "
              f"({gender['most_balanced_percentage']:.1f}% female)")
        print(f"Least Balanced: {gender['least_balanced_occupation']} "
              f"({gender['least_balanced_percentage']:.1f}% female)")

        print("\n🎓 DEGREE FIELD OUTCOMES")
        print("-" * 60)
        for field in report['degree_fields']:
            print(f"{field['field']:35s} {field['employment_rate']:>5.1f}% employed")

        print("\n" + "=" * 60)
        print("Use this data to make informed career decisions!")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")

    stem_hub.close()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CENSUS EMPLOYMENT RAG - STUDENT USE CASES")
    print("=" * 80)
    print("\nMake data-driven career decisions with Census Bureau data\n")

    demo_career_exploration()
    demo_field_of_study_outcomes()
    demo_career_questions()
    demo_state_comparison_for_career()
    demo_stem_career_report()

    print("\n" + "=" * 80)
    print("DEMO COMPLETE - Plan Your Career with Confidence")
    print("=" * 80)
    print("\nAll data from the U.S. Census Bureau")
    print("Make informed decisions about your future!\n")
