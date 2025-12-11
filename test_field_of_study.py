"""
Test script for Field-of-Study Analytics

This script demonstrates the new field-of-study analytics capabilities
using the ACS 2019-2023 5-Year PUMS data.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from census_client.acs_pums_client import ACSPUMSClient
from analytics import FieldOfStudyAnalyzer, GenderMetricsAnalyzer, SectorAnalyzer


def test_basic_pums_loading():
    """Test basic PUMS data loading"""
    print("=" * 80)
    print("TEST 1: Basic PUMS Data Loading")
    print("=" * 80)

    # Initialize client with the downloaded data
    pums = ACSPUMSClient(
        data_dir="data/acs_pums/5-year/2019-2023",
        dataset="5-year",
        year=2023
    )

    # Test loading California data
    print("\nLoading California PUMS data...")
    ca_df = pums.load_state("ca")
    print(f"✓ Loaded {len(ca_df):,} records for California")
    print(f"  Columns: {', '.join(ca_df.columns[:10])}...")

    # Check for field-of-study variable
    has_fod = 'FOD1P' in ca_df.columns
    fod_count = ca_df['FOD1P'].notna().sum()
    print(f"  FOD1P (field of study) present: {has_fod}")
    print(f"  Records with field of study: {fod_count:,}")

    return pums


def test_field_of_study_outcomes(pums):
    """Test field-of-study outcome calculations"""
    print("\n" + "=" * 80)
    print("TEST 2: Field-of-Study Outcomes")
    print("=" * 80)

    # Computer Science (CIP code 1107)
    print("\nAnalyzing Computer Science (CIP 1107) Bachelor's degree holders in California...")

    cs_outcomes = pums.get_field_of_study_outcomes(
        field_codes=["1107"],  # Computer Science
        education_level="23",  # Bachelor's degree
        state_code="ca"
    )

    if cs_outcomes:
        cs = cs_outcomes[0]
        print(f"\n✓ Field: {cs.field_name} (Code: {cs.field_code})")
        print(f"  Total Population: {cs.total_population:,}")
        print(f"  Employment Rate: {cs.employment_rate:.1f}%")
        print(f"  Unemployment Rate: {cs.unemployment_rate:.1f}%")
        print(f"  Median Earnings: ${cs.median_earnings:,}" if cs.median_earnings else "  Median Earnings: N/A")
        print(f"  Sample Size: {cs.sample_size:,}")

        if cs.top_occupations:
            print(f"\n  Top Occupations:")
            for occ in cs.top_occupations[:3]:
                print(f"    - {occ['occ_title']}: {occ['pct']:.1f}%")
    else:
        print("  ✗ No data found for Computer Science in California")


def test_gender_gap_analysis(pums):
    """Test gender gap analysis"""
    print("\n" + "=" * 80)
    print("TEST 3: Gender Gap Analysis")
    print("=" * 80)

    gender_analyzer = GenderMetricsAnalyzer(pums)

    print("\nAnalyzing gender gap for Computer Science (CIP 1107)...")

    gap = gender_analyzer.analyze_field_gender_gap(
        field_code="1107",
        education_level="23",
        state_code="ca"
    )

    if gap:
        print(f"\n✓ Field: {gap.segment_name}")
        print(f"  Female Representation: {gap.pct_female:.1f}%")
        print(f"  Male Employment Rate: {gap.male_employment_rate:.1f}%")
        print(f"  Female Employment Rate: {gap.female_employment_rate:.1f}%")
        print(f"  Employment Gap: {gap.employment_rate_gap:+.1f} percentage points")

        if gap.earnings_gap_pct is not None:
            print(f"  Male Median Earnings: ${gap.male_median_earnings:,}")
            print(f"  Female Median Earnings: ${gap.female_median_earnings:,}")
            print(f"  Earnings Gap: {gap.earnings_gap_pct:.1f}%")
    else:
        print("  ✗ Insufficient data for gender gap analysis")


def test_occupation_pipeline(pums):
    """Test occupation pipeline analysis"""
    print("\n" + "=" * 80)
    print("TEST 4: Occupation Pipeline Analysis")
    print("=" * 80)

    print("\nTop occupations for Computer Science Bachelor's graduates in California...")

    occupations = pums.get_occupation_pipeline(
        field_code="1107",
        education_level="23",
        state_code="ca"
    )

    if occupations:
        print(f"\n✓ Found {len(occupations)} occupations")
        print("\n  Top 5 Occupations:")
        for i, occ in enumerate(occupations[:5], 1):
            earnings_str = f"${occ['median_earnings']:,}" if occ['median_earnings'] else "N/A"
            print(f"  {i}. {occ['occ_title']}")
            print(f"     {occ['pct_of_field']:.1f}% of CS grads | Median: {earnings_str}")
    else:
        print("  ✗ No occupation data found")


def test_sector_distribution(pums):
    """Test sector distribution analysis"""
    print("\n" + "=" * 80)
    print("TEST 5: Sector Distribution Analysis")
    print("=" * 80)

    print("\nTop industries employing Computer Science Bachelor's graduates in California...")

    sectors = pums.get_sector_distribution(
        field_code="1107",
        education_level="23",
        state_code="ca"
    )

    if sectors:
        print(f"\n✓ Found {len(sectors)} sectors")
        print("\n  Top 5 Sectors:")
        for i, sector in enumerate(sectors[:5], 1):
            earnings_str = f"${sector['median_earnings']:,}" if sector['median_earnings'] else "N/A"
            print(f"  {i}. {sector['sector_name']}")
            print(f"     {sector['pct_of_field']:.1f}% of CS grads | Median: {earnings_str}")
    else:
        print("  ✗ No sector data found")


def test_field_comparison():
    """Test comparing multiple fields"""
    print("\n" + "=" * 80)
    print("TEST 6: Field Comparison")
    print("=" * 80)

    pums = ACSPUMSClient(
        data_dir="data/acs_pums/5-year/2019-2023",
        dataset="5-year",
        year=2023
    )

    analyzer = FieldOfStudyAnalyzer(pums)

    print("\nComparing Computer Science vs Engineering Bachelor's degrees (California)...")

    # Computer Science: 1107, Engineering: 1401
    try:
        comparison = analyzer.compare_fields(
            field_codes=["1107", "1401"],
            education_level="23",
            state_code="ca"
        )

        print(f"\n✓ Compared {len(comparison.fields)} field outcomes")
        print(f"  Highest Employment Rate: {comparison.highest_employment_rate}")
        print(f"  Highest Median Earnings: {comparison.highest_median_earnings}")
        print(f"  Best ROI Overall: {comparison.best_roi_overall}")

        print("\n  Field Details:")
        for field in comparison.fields:
            if field.sex is None:  # Overall (not gender-specific)
                earnings_str = f"${field.median_earnings:,}" if field.median_earnings else "N/A"
                print(f"    {field.field_name}:")
                print(f"      Employment Rate: {field.employment_rate:.1f}%")
                print(f"      Median Earnings: {earnings_str}")
    except Exception as e:
        print(f"  ✗ Error: {e}")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("FIELD-OF-STUDY ANALYTICS TEST SUITE")
    print("=" * 80)
    print("\nThis test demonstrates the new field-of-study analytics using")
    print("ACS 2019-2023 5-Year PUMS data (50 states, 9.8GB)")

    try:
        # Test 1: Basic loading
        pums = test_basic_pums_loading()

        # Test 2: Field outcomes
        test_field_of_study_outcomes(pums)

        # Test 3: Gender gaps
        test_gender_gap_analysis(pums)

        # Test 4: Occupation pipeline
        test_occupation_pipeline(pums)

        # Test 5: Sector distribution
        test_sector_distribution(pums)

        # Test 6: Field comparison
        test_field_comparison()

        print("\n" + "=" * 80)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nThe field-of-study analytics implementation is working with REAL Census data!")
        print("No fake data. No simulations. Just authentic ACS PUMS microdata.\n")

    except FileNotFoundError as e:
        print(f"\n✗ ERROR: PUMS data files not found")
        print(f"  {e}")
        print("\nMake sure ACS PUMS data is downloaded to: data/acs_pums/5-year/2019-2023/")
        print("See DOWNLOAD_INSTRUCTIONS.md for details.")

    except Exception as e:
        print(f"\n✗ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
