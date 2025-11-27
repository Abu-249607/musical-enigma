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
from src.retrieval.conversational_rag import ConversationalRAGPipeline
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
    }
    .user-message {
        background-color: #e0f2fe;
        border-left: 4px solid #0ea5e9;
    }
    .assistant-message {
        background-color: #f1f5f9;
        border-left: 4px solid #64748b;
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
def get_rag_pipeline():
    settings = get_settings()
    api_key = settings.census_api_key if settings.census_api_key else None
    return ConversationalRAGPipeline(api_key=api_key, enable_memory=True)

# Initialize session state
if 'conversation_id' not in st.session_state:
    rag_pipeline = get_rag_pipeline()
    st.session_state.conversation_id = rag_pipeline.start_conversation()

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
        rag_pipeline = get_rag_pipeline()
        rag_pipeline.clear_conversation(st.session_state.conversation_id)
        st.session_state.chat_history = []
        st.session_state.conversation_id = rag_pipeline.start_conversation()
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
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Chat Assistant",
    "🎯 Employment Dashboard",
    "📈 State Comparison",
    "🔬 Advanced Analytics"
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
        with st.spinner("Thinking..."):
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_query
            })

            # Get RAG response
            rag_pipeline = get_rag_pipeline()
            response = rag_pipeline.chat(
                user_query,
                conversation_id=st.session_state.conversation_id,
                n_results=5
            )

            # Generate assistant response
            assistant_response = f"""Based on Census Bureau data:

**Context:** {response['context'][:500]}...

**Geography Context:** {response.get('geography_context', 'Not specified')}

*This response is based on {len(response['citations'])} Census data sources.*
"""

            # Add assistant message to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": assistant_response,
                "citations": [f"{c['dataset']} - {c['year']} - {c['geography']}" for c in response['citations']]
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
            with st.spinner("Fetching comparison data..."):
                try:
                    rag_pipeline = get_rag_pipeline()
                    comparison = rag_pipeline.compare_geographies_conversational(
                        geographies=selected_states,
                        metric=metric_to_compare.lower(),
                        year=year,
                        conversation_id=st.session_state.conversation_id
                    )

                    # Build comparison DataFrame
                    comparison_data = []
                    for state, data in comparison['geographies'].items():
                        if 'error' not in data:
                            comparison_data.append({
                                'State': state,
                                'Unemployment Rate (%)': data['unemployment_rate'],
                                'Labor Force': data['labor_force'],
                                'Employed': data['employed'],
                                'Participation Rate (%)': data['labor_force_participation']
                            })

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
    st.header("Advanced Employment Analytics")
    st.markdown("*Coming soon: STEM career pathways, education ROI, and talent flow mapping*")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎓 STEM Career Intelligence")
        st.info("Track STEM employment trends, gender gaps, and geographic concentration")
        st.caption("• Field-to-job pipeline mapping")
        st.caption("• Gender representation analysis")
        st.caption("• Hot job alerts by region")

    with col2:
        st.subheader("💼 Gig Economy Tracker")
        st.info("Analyze self-employment and future of work trends")
        st.caption("• Class of worker analysis")
        st.caption("• Independent contractor growth")
        st.caption("• Industry-specific trends")

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🗺️ Geographic Talent Mapper")
        st.info("Visualize where talent concentrates and flows")
        st.caption("• Occupation concentration heat maps")
        st.caption("• Brain drain/gain analysis")
        st.caption("• Recruiting hotspot identification")

    with col4:
        st.subheader("📊 Education ROI Calculator")
        st.info("Connect degrees to employment outcomes")
        st.caption("• Degree field → job outcomes")
        st.caption("• Earnings by field of study")
        st.caption("• Employment rates by major")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem 0;'>
    <p><strong>Data Source:</strong> U.S. Census Bureau American Community Survey</p>
    <p><em>All statistics are estimates with margins of error from sampling.</em></p>
    <p style='font-size: 0.85rem;'>Powered by RAG with citation tracking | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
