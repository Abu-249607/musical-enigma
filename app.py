"""Census Employment RAG - Web Interface

A simple Streamlit app for recruiters and students to explore
Census employment data with citation-backed insights.
"""

import streamlit as st
from src.census_client import CensusMCPClient
from src.config.settings import get_settings

# Page config
st.set_page_config(
    page_title="Census Employment Explorer",
    page_icon="📊",
    layout="wide"
)

# Initialize client
@st.cache_resource
def get_client():
    settings = get_settings()
    api_key = settings.census_api_key if settings.census_api_key else None
    return CensusMCPClient(api_key=api_key, use_cache=True)

# Header
st.title("📊 Census Employment Explorer")
st.markdown("*Get accurate, citation-backed employment data from the U.S. Census Bureau*")

# Sidebar
st.sidebar.header("Settings")
year = st.sidebar.selectbox("Select Year", [2022, 2021, 2020, 2019], index=0)

# State list
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
    "West Virginia", "Wisconsin", "Wyoming"
]

# Main tabs
tab1, tab2, tab3 = st.tabs(["🎯 Recruiter View", "🎓 Student View", "📈 Compare States"])

# Tab 1: Recruiter View
with tab1:
    st.header("Recruiter Dashboard")
    st.markdown("Find labor market conditions for hiring decisions")

    col1, col2 = st.columns([1, 2])

    with col1:
        selected_state = st.selectbox("Select State", STATES, key="recruiter_state")
        fetch_button = st.button("Get Employment Data", key="recruiter_fetch")

    with col2:
        if fetch_button:
            with st.spinner(f"Fetching data for {selected_state}..."):
                try:
                    client = get_client()
                    record, citation = client.get_employment_data(selected_state, year=year)

                    # Metrics
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Unemployment Rate", f"{record.unemployment_rate:.1f}%")
                    m2.metric("Labor Force", f"{record.labor_force:,}")
                    m3.metric("Employed", f"{record.employed:,}")

                    # Details
                    st.subheader("Detailed Statistics")
                    st.write(f"**Population 16+:** {record.total_population_16_plus:,}")
                    st.write(f"**Unemployed:** {record.unemployed:,}")
                    st.write(f"**Labor Force Participation:** {record.labor_force_participation_rate:.1f}%")

                    # Citation
                    st.subheader("📚 Citation")
                    st.info(citation.to_reference_string())
                    st.caption(f"API Endpoint: {citation.api_endpoint}")

                except Exception as e:
                    st.error(f"Error fetching data: {str(e)}")

# Tab 2: Student View
with tab2:
    st.header("Student Career Explorer")
    st.markdown("Discover job market trends by industry")

    col1, col2 = st.columns([1, 2])

    with col1:
        selected_state = st.selectbox("Select State", STATES, key="student_state")
        fetch_button = st.button("Get Industry Data", key="student_fetch")

    with col2:
        if fetch_button:
            with st.spinner(f"Fetching industry data for {selected_state}..."):
                try:
                    client = get_client()
                    industry_data, citation = client.get_industry_employment(selected_state, year=year)

                    # Display as bar chart
                    st.subheader(f"Employment by Industry in {selected_state}")

                    # Remove total for chart
                    chart_data = {k: v for k, v in industry_data.items() if k != "Total civilian employed"}
                    st.bar_chart(chart_data)

                    # Table view
                    st.subheader("Detailed Breakdown")
                    total = industry_data.get("Total civilian employed", 1)
                    for industry, count in sorted(chart_data.items(), key=lambda x: x[1], reverse=True):
                        pct = (count / total) * 100 if total > 0 else 0
                        st.write(f"**{industry}:** {count:,} ({pct:.1f}%)")

                    # Citation
                    st.subheader("📚 Citation")
                    st.info(citation.to_reference_string())

                except Exception as e:
                    st.error(f"Error fetching data: {str(e)}")

# Tab 3: Compare States
with tab3:
    st.header("State Comparison")
    st.markdown("Compare employment metrics across multiple states")

    selected_states = st.multiselect(
        "Select States to Compare",
        STATES,
        default=["California", "Texas", "New York"]
    )

    if st.button("Compare States", key="compare_fetch"):
        if len(selected_states) < 2:
            st.warning("Please select at least 2 states to compare")
        else:
            with st.spinner("Fetching comparison data..."):
                try:
                    client = get_client()
                    results = []

                    for state in selected_states:
                        record, citation = client.get_employment_data(state, year=year)
                        results.append({
                            "State": state,
                            "Unemployment Rate (%)": record.unemployment_rate,
                            "Labor Force": record.labor_force,
                            "Employed": record.employed,
                            "Participation Rate (%)": record.labor_force_participation_rate
                        })

                    # Display comparison table
                    import pandas as pd
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)

                    # Chart
                    st.subheader("Unemployment Rate Comparison")
                    chart_df = df.set_index("State")["Unemployment Rate (%)"]
                    st.bar_chart(chart_df)

                    # Citation note
                    st.caption(f"Source: U.S. Census Bureau, American Community Survey 5-Year Estimates ({year})")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "*Data sourced from the U.S. Census Bureau American Community Survey. "
    "All statistics include margin of error from sampling.*"
)
