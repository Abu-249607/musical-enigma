"""Enhanced Census Employment RAG - Web Interface with Chat

A conversational Streamlit app for exploring Census employment data
with RAG-powered insights, interactive visualizations, and citation tracking.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from src.census_client import CensusMCPClient
from src.census_client.cps_client import CPSClient
from src.assistants import IntelligentCensusAssistant
from src.analytics.education_roi import EducationROICalculator
from src.analytics.gig_economy_tracker import GigEconomyTracker
from src.analytics.talent_mapper import GeographicTalentMapper
from src.config.settings import get_settings

# Page config
st.set_page_config(
    page_title="Census Employment Intelligence",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: #0f172a;
    }
    .user-message {
        background-color: #e0f2fe;
        border-left: 4px solid #0ea5e9;
        color: #0c4a6e;
    }
    .assistant-message {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        color: #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize clients
@st.cache_resource
def get_census_client():
    settings = get_settings()
    api_key = settings.census_api_key if settings.census_api_key else None
    return CensusMCPClient(api_key=api_key, use_cache=True)

@st.cache_resource
def get_intelligent_assistant():
    """Get the intelligent Census assistant"""
    census_client = get_census_client()
    return IntelligentCensusAssistant(census_client=census_client)

@st.cache_resource
def get_cps_client():
    """Get CPS Basic Monthly client

    Note: CPS API may not be available for all years/months.
    Demo mode automatically activates if API fails.
    """
    settings = get_settings()
    api_key = settings.census_api_key if settings.census_api_key else None
    # Start with demo_mode=False to try real API first, will fall back to demo if API fails
    return CPSClient(api_key=api_key, use_cache=True, demo_mode=False)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Header
st.markdown('<h1 class="main-header">💼 Census Employment Intelligence</h1>', unsafe_allow_html=True)
st.markdown("*Conversational AI for Census Bureau employment data with 2024 insights*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    year = st.selectbox(
        "Data Year",
        [2024, 2023, 2022, 2021, 2020],
        index=0,
        help="2024 data is the most recent (ACS 1-year estimates)"
    )

    dataset = st.selectbox(
        "Dataset",
        ["acs/acs1", "acs/acs5"],
        index=0 if year == 2024 else 1,
        help="ACS 1-year for recent data, 5-year for smaller geographies"
    )

    st.divider()

    st.subheader("📊 Data Source")
    st.caption(f"U.S. Census Bureau")
    st.caption(f"American Community Survey")
    st.caption(f"{year} Estimates")

    st.divider()

    if st.button("🔄 Clear Chat History"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")

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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Chat Assistant",
    "🎯 Employment Dashboard",
    "📈 State Comparison",
    "🔬 Advanced Analytics",
    "🎓 Student Analytics (CPS)"
])

# Tab 1: Chat Assistant
with tab1:
    st.header("Ask Questions About Employment Data")
    st.markdown("Chat with our AI assistant to get insights about employment trends, industry data, and more.")

    # Chat display
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.chat_history:
            role = message["role"]
            content = message["content"]

            if role == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong><br>{content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message"><strong>Assistant:</strong><br>{content}</div>', unsafe_allow_html=True)

                if "citations" in message and message["citations"]:
                    with st.expander("📚 View Citations"):
                        for citation in message["citations"]:
                            st.caption(f"• {citation}")

    # Chat input
    user_query = st.text_input(
        "Ask a question:",
        placeholder="e.g., What's the unemployment rate in California? How does it compare to Texas?",
        key="chat_input"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        send_button = st.button("Send", type="primary", use_container_width=True)

    if send_button and user_query:
        with st.spinner(f"Fetching {year} Census data..."):
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_query
            })

            # Get intelligent assistant response (no hallucinations!)
            assistant = get_intelligent_assistant()
            response = assistant.answer_question(user_query, year=year, dataset=dataset)

            if response["success"]:
                # Format citations
                citations_formatted = []
                if response.get("citations"):
                    citations_formatted = [cit.to_reference_string() for cit in response["citations"]]

                # Add assistant message to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "citations": citations_formatted
                })
            else:
                # Handle errors or missing geography
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "citations": []
                })

            st.rerun()

# Tab 2: Employment Dashboard
with tab2:
    st.header("Employment Dashboard")

    col1, col2 = st.columns([1, 2])

    with col1:
        selected_state = st.selectbox("Select State", STATES, key="dashboard_state")
        show_industry = st.checkbox("Show Industry Breakdown", value=True)

        if st.button("🔍 Get Employment Data", use_container_width=True, type="primary"):
            with st.spinner(f"Fetching {year} data for {selected_state}..."):
                try:
                    client = get_census_client()
                    record, citation = client.get_employment_data(selected_state, year=year, dataset=dataset)

                    # Store in session state
                    st.session_state.current_record = record
                    st.session_state.current_citation = citation

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.session_state.current_record = None

    with col2:
        if 'current_record' in st.session_state and st.session_state.current_record:
            record = st.session_state.current_record
            citation = st.session_state.current_citation

            # Metrics cards
            st.subheader(f"📊 {selected_state} Employment Statistics ({year})")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric(
                "Unemployment Rate",
                f"{record.unemployment_rate:.1f}%" if record.unemployment_rate else "N/A",
                help="Percentage of labor force that is unemployed"
            )
            m2.metric(
                "Labor Force",
                f"{record.labor_force:,}" if record.labor_force else "N/A",
                help="Total number in labor force"
            )
            m3.metric(
                "Employed",
                f"{record.employed:,}" if record.employed else "N/A",
                help="Total employed population"
            )
            m4.metric(
                "Participation Rate",
                f"{record.labor_force_participation_rate:.1f}%" if record.labor_force_participation_rate else "N/A",
                help="% of population 16+ in labor force"
            )

            # Employment breakdown pie chart
            st.subheader("Employment Status Breakdown")

            if record.employed and record.unemployed and record.not_in_labor_force:
                fig = go.Figure(data=[go.Pie(
                    labels=['Employed', 'Unemployed', 'Not in Labor Force'],
                    values=[record.employed, record.unemployed, record.not_in_labor_force],
                    hole=.3,
                    marker_colors=['#10b981', '#ef4444', '#94a3b8']
                )])

                fig.update_layout(
                    title=f"Population 16+ Distribution ({record.total_population_16_plus:,} total)",
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

            # Citation
            with st.expander("📚 Data Citation"):
                st.info(citation.to_reference_string())
                st.caption(f"API Endpoint: {citation.api_endpoint}")

        # Industry breakdown
        if show_industry and 'current_record' in st.session_state and st.session_state.current_record:
            st.divider()
            st.subheader("🏭 Employment by Industry")

            if st.button("Load Industry Data", use_container_width=True):
                with st.spinner("Fetching industry breakdown..."):
                    try:
                        client = get_census_client()
                        industry_data, ind_citation = client.get_industry_employment(selected_state, year=year)

                        # Create bar chart
                        chart_data = {k: v for k, v in industry_data.items() if k != "Total civilian employed"}

                        df_industry = pd.DataFrame({
                            'Industry': list(chart_data.keys()),
                            'Employed': list(chart_data.values())
                        }).sort_values('Employed', ascending=False)

                        fig = px.bar(
                            df_industry,
                            x='Employed',
                            y='Industry',
                            orientation='h',
                            title=f"Employment by Industry in {selected_state}",
                            color='Employed',
                            color_continuous_scale='Blues'
                        )

                        fig.update_layout(height=500, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)

                    except Exception as e:
                        st.error(f"Error loading industry data: {str(e)}")

# Tab 3: State Comparison
with tab3:
    st.header("Compare States")

    selected_states = st.multiselect(
        "Select States to Compare",
        STATES,
        default=["California", "Texas", "New York", "Florida"]
    )

    metric_to_compare = st.selectbox(
        "Metric to Compare",
        ["Unemployment Rate", "Labor Force Participation", "Employment-Population Ratio"],
        index=0
    )

    if st.button("📊 Compare States", use_container_width=True, type="primary"):
        if len(selected_states) < 2:
            st.warning("Please select at least 2 states to compare")
        else:
            with st.spinner("Fetching fresh Census data for comparison..."):
                try:
                    client = get_census_client()

                    # Fetch data for each state
                    comparison_data = []
                    for state in selected_states:
                        try:
                            record, citation = client.get_employment_data(state, year=year, dataset=dataset)
                            comparison_data.append({
                                'State': state,
                                'Unemployment Rate (%)': record.unemployment_rate,
                                'Labor Force': record.labor_force,
                                'Employed': record.employed,
                                'Participation Rate (%)': record.labor_force_participation_rate
                            })
                        except Exception as e:
                            st.warning(f"Could not fetch data for {state}: {str(e)}")

                    df = pd.DataFrame(comparison_data)

                    # Display table
                    st.dataframe(
                        df.style.format({
                            'Unemployment Rate (%)': '{:.1f}',
                            'Labor Force': '{:,}',
                            'Employed': '{:,}',
                            'Participation Rate (%)': '{:.1f}'
                        }).background_gradient(subset=['Unemployment Rate (%)'], cmap='RdYlGn_r'),
                        use_container_width=True,
                        height=300
                    )

                    # Visualization
                    col1, col2 = st.columns(2)

                    with col1:
                        # Unemployment comparison
                        fig1 = px.bar(
                            df.sort_values('Unemployment Rate (%)'),
                            x='State',
                            y='Unemployment Rate (%)',
                            title='Unemployment Rate Comparison',
                            color='Unemployment Rate (%)',
                            color_continuous_scale='RdYlGn_r'
                        )
                        fig1.update_layout(showlegend=False)
                        st.plotly_chart(fig1, use_container_width=True)

                    with col2:
                        # Labor force comparison
                        fig2 = px.bar(
                            df.sort_values('Labor Force', ascending=False),
                            x='State',
                            y='Labor Force',
                            title='Labor Force Size Comparison',
                            color='Labor Force',
                            color_continuous_scale='Blues'
                        )
                        fig2.update_layout(showlegend=False)
                        st.plotly_chart(fig2, use_container_width=True)

                    st.caption(f"Source: U.S. Census Bureau, {dataset.upper()} {year} Estimates")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Tab 4: Advanced Analytics
with tab4:
    st.header("🎓 Field-of-Study Analytics")
    st.markdown("*Analyze employment outcomes by field of study with gender and sector breakdowns*")

    # Sub-tabs for different analytics
    analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs([
        "📊 Field Comparison",
        "⚖️ Gender Gap Analysis",
        "🗺️ Geographic Insights"
    ])

    # Analysis Tab 1: Field Comparison
    with analysis_tab1:
        st.subheader("Compare Fields of Study")
        st.markdown("Compare employment outcomes across different academic fields")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.caption("**Select Fields to Compare:**")

            # Popular comparisons quick-select
            comparison_sets = {
                "STEM Fields": ["Computer Science", "Engineering", "Biology", "Mathematics"],
                "Health Professions": ["Nursing", "Public Health", "Health Administration"],
                "Business & Social Sciences": ["Business", "Psychology", "Economics"]
            }

            selected_set = st.selectbox(
                "Quick Select:",
                ["Custom"] + list(comparison_sets.keys()),
                key="field_comparison_set"
            )

            if selected_set != "Custom":
                st.info(f"Comparing: {', '.join(comparison_sets[selected_set])}")
                selected_fields = comparison_sets[selected_set]
            else:
                selected_fields = st.multiselect(
                    "Select fields:",
                    [
                        "Computer Science",
                        "Engineering",
                        "Biology",
                        "Mathematics",
                        "Nursing",
                        "Business",
                        "Psychology",
                        "Education",
                        "Communications"
                    ],
                    default=["Computer Science", "Engineering"]
                )

            compare_button = st.button("Compare Fields", type="primary", use_container_width=True)

        with col2:
            if compare_button and selected_fields:
                st.markdown("### 📈 Comparison Results")

                # Note about data source
                st.info("💡 **Note**: Field-of-study analytics use ACS PUMS microdata. "
                       "Full analytics available when PUMS data is loaded. Currently showing demonstration mode.")

                # Create sample comparison data
                comparison_data = []
                for field in selected_fields:
                    # Simulated data for demonstration
                    comparison_data.append({
                        "Field": field,
                        "Employment Rate": 92.5 + hash(field) % 8,
                        "Median Earnings": 50000 + (hash(field) % 50) * 1000,
                        "% Female": 30 + hash(field) % 40
                    })

                comparison_df = pd.DataFrame(comparison_data)

                # Employment Rate Chart
                st.markdown("#### Employment Rates by Field")
                fig1 = px.bar(
                    comparison_df,
                    x="Field",
                    y="Employment Rate",
                    color="Field",
                    title="Employment Rate Comparison"
                )
                st.plotly_chart(fig1, use_container_width=True)

                # Median Earnings Chart
                st.markdown("#### Median Earnings by Field")
                fig2 = px.bar(
                    comparison_df,
                    x="Field",
                    y="Median Earnings",
                    color="Field",
                    title="Median Earnings Comparison"
                )
                fig2.update_traces(marker_color='lightseagreen')
                st.plotly_chart(fig2, use_container_width=True)

                # Gender representation
                st.markdown("#### Female Representation by Field")
                fig3 = px.bar(
                    comparison_df,
                    x="Field",
                    y="% Female",
                    color="Field",
                    title="Female Representation (%)"
                )
                fig3.update_traces(marker_color='mediumpurple')
                st.plotly_chart(fig3, use_container_width=True)

                # Summary table
                st.markdown("#### Summary Table")
                st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    # Analysis Tab 2: Gender Gap Analysis
    with analysis_tab2:
        st.subheader("Gender Gap Analysis")
        st.markdown("Analyze employment and earnings gaps between male and female graduates")

        col1, col2 = st.columns([1, 2])

        with col1:
            selected_field = st.selectbox(
                "Select Field:",
                [
                    "Computer Science",
                    "Engineering",
                    "Business",
                    "Nursing",
                    "Education",
                    "Psychology"
                ],
                key="gender_field"
            )

            education_level = st.selectbox(
                "Education Level:",
                ["Bachelor's degree", "Master's degree", "Doctoral degree"],
                key="gender_edu"
            )

            analyze_gender = st.button("Analyze Gender Gap", type="primary", use_container_width=True)

        with col2:
            if analyze_gender:
                st.markdown(f"### ⚖️ Gender Gap Analysis: {selected_field}")

                st.info("💡 **Note**: Gender gap analytics use ACS PUMS microdata with person-level records. "
                       "Full analytics available when PUMS data is loaded. Currently showing demonstration mode.")

                # Simulated gender gap data
                male_employment = 95.2
                female_employment = 93.8
                male_earnings = 85000
                female_earnings = 72000

                # Metrics
                col_m1, col_m2, col_m3 = st.columns(3)

                with col_m1:
                    st.metric(
                        "Employment Gap",
                        f"{male_employment - female_employment:.1f}%",
                        delta=f"Male: {male_employment:.1f}% | Female: {female_employment:.1f}%",
                        delta_color="off"
                    )

                with col_m2:
                    earnings_gap_pct = ((male_earnings - female_earnings) / male_earnings) * 100
                    st.metric(
                        "Earnings Gap",
                        f"{earnings_gap_pct:.1f}%",
                        delta=f"${male_earnings - female_earnings:,} difference",
                        delta_color="inverse"
                    )

                with col_m3:
                    female_pct = 38.5
                    st.metric(
                        "Female Representation",
                        f"{female_pct:.1f}%",
                        delta="of total graduates",
                        delta_color="off"
                    )

                # Gender comparison charts
                st.markdown("#### Employment & Earnings Comparison")

                gender_data = pd.DataFrame({
                    "Metric": ["Employment Rate", "Median Earnings"],
                    "Male": [male_employment, male_earnings],
                    "Female": [female_employment, female_earnings]
                })

                fig = go.Figure(data=[
                    go.Bar(name='Male', x=gender_data["Metric"], y=gender_data["Male"], marker_color='steelblue'),
                    go.Bar(name='Female', x=gender_data["Metric"], y=gender_data["Female"], marker_color='coral')
                ])
                fig.update_layout(barmode='group', title="Gender Comparison")
                st.plotly_chart(fig, use_container_width=True)

                # Insights
                st.markdown("#### 💡 Key Insights")
                st.success(f"✓ **Employment**: {'Male' if male_employment > female_employment else 'Female'} graduates have {abs(male_employment - female_employment):.1f}% higher employment rate")
                st.success(f"✓ **Earnings**: Women earn ${male_earnings - female_earnings:,} less on average ({earnings_gap_pct:.1f}% gap)")
                st.success(f"✓ **Representation**: Women make up {female_pct:.1f}% of {selected_field} graduates")

    # Analysis Tab 3: Geographic Insights
    with analysis_tab3:
        st.subheader("Geographic Talent Distribution")
        st.markdown("Explore where field graduates work and geographic concentration patterns")

        col1, col2 = st.columns([1, 2])

        with col1:
            selected_field_geo = st.selectbox(
                "Select Field:",
                [
                    "Computer Science",
                    "Engineering",
                    "Business",
                    "Healthcare"
                ],
                key="geo_field"
            )

            metric_type = st.radio(
                "View:",
                ["Employment Concentration", "Median Earnings", "Gender Distribution"],
                key="geo_metric"
            )

            show_geo = st.button("Show Geographic Distribution", type="primary", use_container_width=True)

        with col2:
            if show_geo:
                st.markdown(f"### 🗺️ {selected_field_geo}: {metric_type}")

                st.info("💡 **Note**: Geographic analytics use state-level ACS PUMS data. "
                       "Full analytics available when PUMS data is loaded. Currently showing demonstration mode.")

                # Sample state data
                states_sample = ["California", "Texas", "New York", "Florida", "Illinois", "Pennsylvania"]
                values = [45000 + i * 5000 for i in range(len(states_sample))]

                geo_df = pd.DataFrame({
                    "State": states_sample,
                    "Value": values
                })

                # Bar chart
                fig = px.bar(
                    geo_df,
                    x="State",
                    y="Value",
                    title=f"{metric_type} by State",
                    color="Value",
                    color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Top states table
                st.markdown("#### Top States")
                st.dataframe(geo_df.sort_values("Value", ascending=False), use_container_width=True, hide_index=True)

# Tab 5: Student Analytics (CPS)
with tab5:
    st.header("🎓 Student Analytics - CPS Basic Monthly Data")
    st.markdown("*Real-time labor market data from Current Population Survey for students and career planners*")

    # Sub-tabs for different CPS features
    subtab1, subtab2, subtab3 = st.tabs([
        "📊 Education ROI",
        "💼 Gig Economy",
        "🗺️ Talent Mapping"
    ])

    # Subtab 1: Education ROI
    with subtab1:
        st.subheader("Education Return on Investment Calculator")
        st.markdown("Compare employment outcomes across education levels using CPS data")

        col1, col2 = st.columns([1, 2])

        with col1:
            cps_year = st.selectbox("Year", [2024, 2023, 2022], index=0, key="cps_year")
            cps_month = st.selectbox("Month", list(range(1, 13)), index=10, key="cps_month")
            cps_state = st.selectbox(
                "Geography",
                ["National"] + STATES,
                index=0,
                key="cps_state"
            )

            education_levels = st.multiselect(
                "Education Levels to Compare",
                [
                    "High school graduate",
                    "Some college or Associate degree",
                    "Bachelor's degree",
                    "Master's degree",
                    "Professional degree",
                    "Doctoral degree"
                ],
                default=["Bachelor's degree", "Master's degree"]
            )

            calculate_roi = st.button("Calculate ROI", type="primary", use_container_width=True)

        with col2:
            if calculate_roi and education_levels:
                with st.spinner("Fetching CPS data..."):
                    try:
                        # Map education level names to codes
                        edu_code_map = {
                            "High school graduate": "39",
                            "Some college or Associate degree": "40",
                            "Bachelor's degree": "43",
                            "Master's degree": "44",
                            "Professional degree": "45",
                            "Doctoral degree": "46"
                        }

                        edu_codes = [edu_code_map[level] for level in education_levels]
                        state_fips = None if cps_state == "National" else \
                                     [fips for fips, name in CPSClient.STATE_FIPS.items() if name == cps_state][0]

                        # Get CPS client and calculator
                        cps_client = get_cps_client()
                        roi_calc = EducationROICalculator(cps_client)

                        # Calculate ROI
                        roi_results = roi_calc.calculate_roi(
                            year=cps_year,
                            month=cps_month,
                            education_levels=edu_codes,
                            state_fips=state_fips
                        )

                        # Display results
                        st.success(f"✅ Analyzed {len(roi_results)} education levels")

                        # Create comparison table
                        df_roi = pd.DataFrame([{
                            "Education Level": r.education_level,
                            "Employment Rate": f"{r.employment_rate:.1f}%",
                            "Unemployment Rate": f"{r.unemployment_rate:.1f}%",
                            "Advantage vs. HS": f"+{r.employment_advantage:.1f}%",
                            "ROI Score": f"{r.roi_score:.1f}"
                        } for r in roi_results])

                        st.dataframe(df_roi, use_container_width=True, hide_index=True)

                        # Bar chart
                        fig_roi = px.bar(
                            x=[r.education_level for r in roi_results],
                            y=[r.roi_score for r in roi_results],
                            title="Education ROI Score Comparison",
                            labels={"x": "Education Level", "y": "ROI Score (0-100)"},
                            color=[r.roi_score for r in roi_results],
                            color_continuous_scale="Viridis"
                        )
                        st.plotly_chart(fig_roi, use_container_width=True)

                        # Key insights
                        st.info(f"🏆 Highest ROI: **{roi_results[0].education_level}** ({roi_results[0].roi_score:.1f})")

                    except Exception as e:
                        st.error(f"Error calculating ROI: {str(e)}")

    # Subtab 2: Gig Economy
    with subtab2:
        st.subheader("Gig Economy Tracker")
        st.markdown("Track non-traditional work arrangements using CPS data")

        col1, col2 = st.columns([1, 2])

        with col1:
            gig_year = st.selectbox("Year", [2024, 2023, 2022], index=0, key="gig_year")
            gig_month = st.selectbox("Month", list(range(1, 13)), index=10, key="gig_month")
            gig_state = st.selectbox(
                "Geography",
                ["National"] + STATES,
                index=0,
                key="gig_state"
            )

            analyze_gig = st.button("Analyze Gig Economy", type="primary", use_container_width=True)

        with col2:
            if analyze_gig:
                with st.spinner("Fetching CPS gig economy data..."):
                    try:
                        state_fips = None if gig_state == "National" else \
                                     [fips for fips, name in CPSClient.STATE_FIPS.items() if name == gig_state][0]

                        cps_client = get_cps_client()
                        gig_tracker = GigEconomyTracker(cps_client)

                        stats = gig_tracker.get_current_gig_stats(gig_year, gig_month, state_fips)

                        # Display metrics
                        st.success("✅ Gig Economy Analysis Complete")

                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Gig Economy Est.", f"{stats.gig_economy_estimate:.1f}%")
                        m2.metric("Self-Employed", f"{stats.pct_self_employed:.1f}%")
                        m3.metric("Multiple Jobs", f"{stats.pct_multiple_jobs:.1f}%")
                        m4.metric("Part-Time Econ.", f"{stats.pct_part_time_economic:.1f}%")

                        # Pie chart
                        fig_gig = go.Figure(data=[go.Pie(
                            labels=['Self-Employed', 'Multiple Jobs', 'Part-Time Economic', 'Traditional'],
                            values=[
                                stats.self_employed,
                                stats.multiple_job_holders,
                                stats.part_time_economic_reasons,
                                stats.total_employed - stats.self_employed - stats.multiple_job_holders
                            ],
                            hole=.3
                        )])
                        fig_gig.update_layout(title="Gig Economy Breakdown")
                        st.plotly_chart(fig_gig, use_container_width=True)

                        st.info(f"📊 Total Employed: {stats.total_employed:,} workers")

                    except Exception as e:
                        st.error(f"Error analyzing gig economy: {str(e)}")

    # Subtab 3: Talent Mapping
    with subtab3:
        st.subheader("Geographic Talent Mapper")
        st.markdown("Map talent distribution across states")

        col1, col2 = st.columns([1, 2])

        with col1:
            map_year = st.selectbox("Year", [2024, 2023, 2022], index=0, key="map_year")
            map_month = st.selectbox("Month", list(range(1, 13)), index=10, key="map_month")

            talent_segment = st.selectbox(
                "Talent Segment",
                [
                    "Bachelor's degree",
                    "Master's degree",
                    "Doctoral degree",
                    "High school graduate"
                ]
            )

            states_to_map = st.multiselect(
                "States to Analyze",
                STATES,
                default=["California", "Texas", "New York", "Florida", "Illinois"]
            )

            map_talent = st.button("Generate Talent Map", type="primary", use_container_width=True)

        with col2:
            if map_talent and states_to_map:
                with st.spinner("Mapping talent distribution..."):
                    try:
                        edu_code_map = {
                            "High school graduate": "39",
                            "Bachelor's degree": "43",
                            "Master's degree": "44",
                            "Doctoral degree": "46"
                        }

                        edu_code = edu_code_map[talent_segment]
                        state_fips_list = [
                            fips for fips, name in CPSClient.STATE_FIPS.items()
                            if name in states_to_map
                        ]

                        cps_client = get_cps_client()
                        mapper = GeographicTalentMapper(cps_client)

                        distribution = mapper.get_talent_distribution(
                            map_year, map_month, edu_code, state_fips_list
                        )

                        # Display results
                        st.success(f"✅ Mapped {len(distribution)} states")

                        # Top hotspots
                        hotspots = mapper.identify_talent_hotspots(
                            map_year, map_month, edu_code, state_fips_list, top_n=5
                        )

                        st.subheader("🔥 Top 5 Talent Hotspots")
                        for hotspot in hotspots:
                            st.write(f"**#{hotspot.rank} {hotspot.state_name}** - "
                                   f"{hotspot.talent_count:,} workers "
                                   f"(Concentration: {hotspot.concentration_index:.2f}x)")

                        # Bar chart
                        df_dist = pd.DataFrame([{
                            "State": d.state_name,
                            "Workers": d.total_workers,
                            "Concentration Index": d.concentration_index
                        } for d in distribution])

                        fig_map = px.bar(
                            df_dist,
                            x="State",
                            y="Concentration Index",
                            title=f"{talent_segment} Concentration by State",
                            color="Concentration Index",
                            color_continuous_scale="RdYlGn"
                        )
                        st.plotly_chart(fig_map, use_container_width=True)

                    except Exception as e:
                        st.error(f"Error mapping talent: {str(e)}")

    # CPS Data Source Info
    st.divider()
    st.caption("**Data Source:** U.S. Census Bureau Current Population Survey (CPS) Basic Monthly")
    st.caption("*CPS is the primary source of labor force statistics in the United States*")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem 0;'>
    <p><strong>Data Source:</strong> U.S. Census Bureau American Community Survey</p>
    <p><em>All statistics are estimates with margins of error from sampling.</em></p>
    <p style='font-size: 0.85rem;'>Powered by RAG with citation tracking | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
