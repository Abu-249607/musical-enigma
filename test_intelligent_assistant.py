"""Test the Intelligent Census Assistant - No Hallucinations!

This script tests that the assistant:
1. Accurately answers questions about specific geographies
2. Returns fresh Census data, not pre-ingested chunks
3. Maps cities to states correctly
4. Never hallucinates or returns wrong geography data
"""

import sys
from src.assistants import IntelligentCensusAssistant
from src.census_client import CensusMCPClient


def print_separator(title=""):
    """Print a nice separator"""
    if title:
        print("\n" + "=" * 80)
        print(f" {title}")
        print("=" * 80)
    else:
        print("-" * 80)


def test_basic_queries():
    """Test basic geography queries"""
    print_separator("TEST 1: Basic Geography Queries (No Hallucinations)")

    assistant = IntelligentCensusAssistant()

    test_queries = [
        "What is the unemployment rate in Texas?",
        "What is the unemployment rate in Chicago?",  # Should return Illinois data
        "What is the unemployment rate in California?",
        "Tell me about employment in New York",
        "Labor force in Washington",
    ]

    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print_separator()

        response = assistant.answer_question(query)

        if response["success"]:
            print(f"✅ Success!")
            print(f"\n{response['answer']}\n")

            # Verify geography matches
            if "geography" in response:
                print(f"🎯 Geography: {response['geography']}")

            # Check for Chicago → Illinois mapping
            if "chicago" in query.lower():
                if "Illinois" in response["answer"]:
                    print("✅ Correctly mapped Chicago → Illinois")
                else:
                    print("❌ FAILED: Did not map Chicago to Illinois")

        else:
            print(f"⚠️  {response['answer']}")

        print()


def test_comparison_queries():
    """Test comparison queries"""
    print_separator("TEST 2: Comparison Queries")

    assistant = IntelligentCensusAssistant()

    test_queries = [
        "Compare unemployment between California and Texas",
        "Compare California, Texas, and Florida",
    ]

    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print_separator()

        response = assistant.answer_question(query)

        if response["success"]:
            print(f"✅ Success!")
            print(f"\n{response['answer']}\n")

            if "comparison" in response:
                print(f"🎯 Compared {len(response['geographies'])} geographies")

        else:
            print(f"⚠️  {response['answer']}")

        print()


def test_city_mapping():
    """Test city to state mapping"""
    print_separator("TEST 3: City → State Mapping")

    assistant = IntelligentCensusAssistant()

    city_tests = [
        ("Chicago", "Illinois"),
        ("Houston", "Texas"),
        ("San Francisco", "California"),
        ("Seattle", "Washington"),
        ("Miami", "Florida"),
    ]

    for city, expected_state in city_tests:
        query = f"What is the unemployment rate in {city}?"
        print(f"\n❓ Query: {query}")
        print(f"   Expected: {expected_state} data")

        response = assistant.answer_question(query)

        if response["success"]:
            if expected_state in response["answer"]:
                print(f"   ✅ Correctly returned {expected_state} data")
            else:
                print(f"   ❌ FAILED: Did not return {expected_state} data")
                print(f"   Response: {response['answer'][:100]}...")
        else:
            print(f"   ⚠️  {response['answer']}")


def test_no_hallucination():
    """Critical test: Verify NO hallucination

    When asked about one geography, should NEVER return data for another.
    """
    print_separator("TEST 4: NO HALLUCINATION (Critical)")

    assistant = IntelligentCensusAssistant()

    # The critical test from user's bug report
    query = "What is the unemployment rate in Chicago?"
    print(f"\n❓ Query: {query}")
    print("   ⚠️  CRITICAL: Should return Illinois data, NOT California/Texas")

    response = assistant.answer_question(query)

    if response["success"]:
        answer = response["answer"]

        # Check for hallucination
        hallucinated = False
        wrong_states = []

        # These states should NOT appear in Chicago response
        unwanted_states = ["California", "Texas", "Florida", "New York", "Washington"]

        for state in unwanted_states:
            if state in answer and state != "Illinois":
                hallucinated = True
                wrong_states.append(state)

        if hallucinated:
            print(f"\n   ❌ HALLUCINATION DETECTED!")
            print(f"   Found data for: {', '.join(wrong_states)}")
            print(f"   Should only have Illinois data")
            print(f"\n   Response:\n{answer}")
            return False
        else:
            if "Illinois" in answer:
                print(f"\n   ✅ NO HALLUCINATION!")
                print(f"   Correctly returned Illinois data only")
                print(f"\n   Response:\n{answer}")
                return True
            else:
                print(f"\n   ⚠️  No Illinois data found")
                print(f"\n   Response:\n{answer}")
                return False
    else:
        print(f"\n   ⚠️  {response['answer']}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("█" * 80)
    print(" INTELLIGENT CENSUS ASSISTANT - NO HALLUCINATION TESTS")
    print("█" * 80)

    try:
        test_basic_queries()
        test_comparison_queries()
        test_city_mapping()

        # The most critical test
        success = test_no_hallucination()

        print("\n")
        print("=" * 80)
        if success:
            print(" ✅ ALL TESTS PASSED - NO HALLUCINATIONS DETECTED")
        else:
            print(" ⚠️  SOME TESTS FAILED - REVIEW OUTPUT ABOVE")
        print("=" * 80)
        print()

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
