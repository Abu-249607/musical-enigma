"""Geographic visualization tools for employment data.

Creates interactive maps, heat maps, and geographic comparisons
using Plotly and Folium.
"""

from typing import Dict, List, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

try:
    import folium
    from folium.plugins import HeatMap
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False


# State FIPS codes and coordinates for mapping
STATE_COORDINATES = {
    "Alabama": ("AL", "01", 32.806671, -86.791130),
    "Alaska": ("AK", "02", 61.370716, -152.404419),
    "Arizona": ("AZ", "04", 33.729759, -111.431221),
    "Arkansas": ("AR", "05", 34.969704, -92.373123),
    "California": ("CA", "06", 36.116203, -119.681564),
    "Colorado": ("CO", "08", 39.059811, -105.311104),
    "Connecticut": ("CT", "09", 41.597782, -72.755371),
    "Delaware": ("DE", "10", 39.318523, -75.507141),
    "Florida": ("FL", "12", 27.766279, -81.686783),
    "Georgia": ("GA", "13", 33.040619, -83.643074),
    "Hawaii": ("HI", "15", 21.094318, -157.498337),
    "Idaho": ("ID", "16", 44.240459, -114.478828),
    "Illinois": ("IL", "17", 40.349457, -88.986137),
    "Indiana": ("IN", "18", 39.849426, -86.258278),
    "Iowa": ("IA", "19", 42.011539, -93.210526),
    "Kansas": ("KS", "20", 38.526600, -96.726486),
    "Kentucky": ("KY", "21", 37.668140, -84.670067),
    "Louisiana": ("LA", "22", 31.169546, -91.867805),
    "Maine": ("ME", "23", 44.693947, -69.381927),
    "Maryland": ("MD", "24", 39.063946, -76.802101),
    "Massachusetts": ("MA", "25", 42.230171, -71.530106),
    "Michigan": ("MI", "26", 43.326618, -84.536095),
    "Minnesota": ("MN", "27", 45.694454, -93.900192),
    "Mississippi": ("MS", "28", 32.741646, -89.678696),
    "Missouri": ("MO", "29", 38.456085, -92.288368),
    "Montana": ("MT", "30", 46.921925, -110.454353),
    "Nebraska": ("NE", "31", 41.125370, -98.268082),
    "Nevada": ("NV", "32", 38.313515, -117.055374),
    "New Hampshire": ("NH", "33", 43.452492, -71.563896),
    "New Jersey": ("NJ", "34", 40.298904, -74.521011),
    "New Mexico": ("NM", "35", 34.840515, -106.248482),
    "New York": ("NY", "36", 42.165726, -74.948051),
    "North Carolina": ("NC", "37", 35.630066, -79.806419),
    "North Dakota": ("ND", "38", 47.528912, -99.784012),
    "Ohio": ("OH", "39", 40.388783, -82.764915),
    "Oklahoma": ("OK", "40", 35.565342, -96.928917),
    "Oregon": ("OR", "41", 44.572021, -122.070938),
    "Pennsylvania": ("PA", "42", 40.590752, -77.209755),
    "Rhode Island": ("RI", "44", 41.680893, -71.511780),
    "South Carolina": ("SC", "45", 33.856892, -80.945007),
    "South Dakota": ("SD", "46", 44.299782, -99.438828),
    "Tennessee": ("TN", "47", 35.747845, -86.692345),
    "Texas": ("TX", "48", 31.054487, -97.563461),
    "Utah": ("UT", "49", 40.150032, -111.862434),
    "Vermont": ("VT", "50", 44.045876, -72.710686),
    "Virginia": ("VA", "51", 37.769337, -78.169968),
    "Washington": ("WA", "53", 47.400902, -121.490494),
    "West Virginia": ("WV", "54", 38.491226, -80.954453),
    "Wisconsin": ("WI", "55", 44.268543, -89.616508),
    "Wyoming": ("WY", "56", 42.755966, -107.302490),
}


class GeographicVisualizer:
    """Creates interactive geographic visualizations for employment data."""

    @staticmethod
    def create_choropleth_map(
        state_data: Dict[str, float],
        metric_name: str,
        title: str,
        color_scale: str = "Blues",
        reverse_scale: bool = False,
    ) -> go.Figure:
        """Create a choropleth map of US states.

        Args:
            state_data: Dictionary mapping state names to metric values
            metric_name: Name of the metric being displayed
            title: Map title
            color_scale: Plotly color scale name
            reverse_scale: Whether to reverse the color scale

        Returns:
            Plotly Figure object
        """
        # Convert state names to abbreviations
        state_abbrevs = []
        values = []

        for state, value in state_data.items():
            if state in STATE_COORDINATES:
                abbrev, fips, lat, lon = STATE_COORDINATES[state]
                state_abbrevs.append(abbrev)
                values.append(value)

        # Create choropleth
        fig = go.Figure(data=go.Choropleth(
            locations=state_abbrevs,
            z=values,
            locationmode='USA-states',
            colorscale=color_scale,
            reversescale=reverse_scale,
            text=[f"{abbrev}: {val:.1f}" for abbrev, val in zip(state_abbrevs, values)],
            colorbar_title=metric_name,
        ))

        fig.update_layout(
            title_text=title,
            geo_scope='usa',
            height=600,
            template='plotly_white',
        )

        return fig

    @staticmethod
    def create_unemployment_heatmap(
        state_unemployment: Dict[str, float],
        title: str = "Unemployment Rate by State"
    ) -> go.Figure:
        """Create unemployment rate heat map.

        Args:
            state_unemployment: State name -> unemployment rate mapping
            title: Map title

        Returns:
            Plotly choropleth figure
        """
        return GeographicVisualizer.create_choropleth_map(
            state_data=state_unemployment,
            metric_name="Unemployment Rate (%)",
            title=title,
            color_scale="RdYlGn",
            reverse_scale=True,  # Red = high unemployment (bad)
        )

    @staticmethod
    def create_stem_concentration_map(
        state_stem_workers: Dict[str, int],
        title: str = "STEM Worker Concentration by State"
    ) -> go.Figure:
        """Create STEM worker concentration heat map.

        Args:
            state_stem_workers: State name -> STEM worker count mapping
            title: Map title

        Returns:
            Plotly choropleth figure
        """
        return GeographicVisualizer.create_choropleth_map(
            state_data=state_stem_workers,
            metric_name="STEM Workers",
            title=title,
            color_scale="Viridis",
        )

    @staticmethod
    def create_bubble_map(
        state_data: List[Dict[str, any]],
        size_metric: str,
        color_metric: str,
        title: str,
    ) -> go.Figure:
        """Create bubble map with sized markers.

        Args:
            state_data: List of dictionaries with 'state', size_metric, color_metric keys
            size_metric: Metric name for bubble size
            color_metric: Metric name for bubble color
            title: Map title

        Returns:
            Plotly scatter geo figure
        """
        lats = []
        lons = []
        sizes = []
        colors = []
        texts = []
        state_names = []

        for data in state_data:
            state = data['state']
            if state in STATE_COORDINATES:
                abbrev, fips, lat, lon = STATE_COORDINATES[state]
                lats.append(lat)
                lons.append(lon)
                sizes.append(data[size_metric])
                colors.append(data[color_metric])
                state_names.append(state)
                texts.append(
                    f"{state}<br>"
                    f"{size_metric}: {data[size_metric]:,}<br>"
                    f"{color_metric}: {data[color_metric]:.1f}"
                )

        fig = go.Figure(data=go.Scattergeo(
            lon=lons,
            lat=lats,
            text=texts,
            mode='markers',
            marker=dict(
                size=[s/1000 for s in sizes],  # Scale down for display
                color=colors,
                colorscale='Viridis',
                showscale=True,
                colorbar_title=color_metric,
                sizemode='area',
                sizeref=2.*max(sizes)/(100.**2),
                sizemin=4,
                line_width=1,
                line_color='white',
            ),
        ))

        fig.update_layout(
            title=title,
            geo_scope='usa',
            height=600,
            template='plotly_white',
        )

        return fig

    @staticmethod
    def create_comparison_bars(
        states: List[str],
        metrics: Dict[str, List[float]],
        title: str,
    ) -> go.Figure:
        """Create grouped bar chart comparing states.

        Args:
            states: List of state names
            metrics: Dictionary mapping metric names to lists of values
            title: Chart title

        Returns:
            Plotly bar chart figure
        """
        fig = go.Figure()

        for metric_name, values in metrics.items():
            fig.add_trace(go.Bar(
                name=metric_name,
                x=states,
                y=values,
                text=[f"{v:.1f}" for v in values],
                textposition='auto',
            ))

        fig.update_layout(
            title=title,
            xaxis_title="State",
            barmode='group',
            height=500,
            template='plotly_white',
        )

        return fig

    @staticmethod
    def create_talent_flow_sankey(
        flows: List[Dict[str, any]],
        title: str = "Talent Flow Between States"
    ) -> go.Figure:
        """Create Sankey diagram showing talent flows.

        Args:
            flows: List of dicts with 'source', 'target', 'value' keys
            title: Diagram title

        Returns:
            Plotly Sankey figure
        """
        # Extract unique states
        all_states = set()
        for flow in flows:
            all_states.add(flow['source'])
            all_states.add(flow['target'])

        state_list = sorted(all_states)
        state_to_idx = {state: idx for idx, state in enumerate(state_list)}

        # Build Sankey data
        sources = [state_to_idx[f['source']] for f in flows]
        targets = [state_to_idx[f['target']] for f in flows]
        values = [f['value'] for f in flows]

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=state_list,
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
            )
        )])

        fig.update_layout(
            title=title,
            height=600,
            font_size=10,
        )

        return fig

    @staticmethod
    def create_folium_heatmap(
        state_data: Dict[str, float],
        metric_name: str,
        zoom_start: int = 4,
    ):
        """Create Folium heat map (if folium is available).

        Args:
            state_data: State name -> metric value mapping
            metric_name: Name of metric
            zoom_start: Initial zoom level

        Returns:
            Folium Map object or None if folium not available
        """
        if not FOLIUM_AVAILABLE:
            return None

        # Create base map centered on US
        m = folium.Map(
            location=[37.0902, -95.7129],
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )

        # Add markers for each state
        for state, value in state_data.items():
            if state in STATE_COORDINATES:
                abbrev, fips, lat, lon = STATE_COORDINATES[state]

                # Color based on value (normalize to 0-1)
                max_val = max(state_data.values())
                min_val = min(state_data.values())
                normalized = (value - min_val) / (max_val - min_val) if max_val > min_val else 0.5

                # Green to red gradient
                if normalized < 0.5:
                    color = 'green'
                elif normalized < 0.75:
                    color = 'orange'
                else:
                    color = 'red'

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=10,
                    popup=f"{state}: {value:.1f}",
                    tooltip=f"{state}: {value:.1f}",
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.6,
                ).add_to(m)

        return m

    @staticmethod
    def create_multi_metric_dashboard(
        states: List[str],
        unemployment: List[float],
        labor_force: List[int],
        stem_workers: List[int],
    ) -> go.Figure:
        """Create multi-metric dashboard with subplots.

        Args:
            states: State names
            unemployment: Unemployment rates
            labor_force: Labor force sizes
            stem_workers: STEM worker counts

        Returns:
            Plotly figure with subplots
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Unemployment Rate',
                'Labor Force Size',
                'STEM Workers',
                'STEM % of Labor Force'
            ),
            specs=[
                [{'type': 'bar'}, {'type': 'bar'}],
                [{'type': 'bar'}, {'type': 'scatter'}]
            ]
        )

        # Unemployment rate
        fig.add_trace(
            go.Bar(x=states, y=unemployment, name='Unemployment %',
                   marker_color='indianred'),
            row=1, col=1
        )

        # Labor force size
        fig.add_trace(
            go.Bar(x=states, y=labor_force, name='Labor Force',
                   marker_color='lightseagreen'),
            row=1, col=2
        )

        # STEM workers
        fig.add_trace(
            go.Bar(x=states, y=stem_workers, name='STEM Workers',
                   marker_color='royalblue'),
            row=2, col=1
        )

        # STEM percentage
        stem_pct = [(stem / lf * 100) if lf > 0 else 0
                    for stem, lf in zip(stem_workers, labor_force)]
        fig.add_trace(
            go.Scatter(x=states, y=stem_pct, mode='markers+lines',
                       name='STEM %', marker=dict(size=12, color='purple')),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="Employment Metrics Dashboard",
            template='plotly_white'
        )

        fig.update_xaxes(tickangle=45)

        return fig

    @staticmethod
    def create_occupation_breakdown(
        occupation_data: Dict[str, int],
        title: str = "Employment by Occupation"
    ) -> go.Figure:
        """Create pie chart of occupation breakdown.

        Args:
            occupation_data: Occupation name -> worker count mapping
            title: Chart title

        Returns:
            Plotly pie chart
        """
        labels = list(occupation_data.keys())
        values = list(occupation_data.values())

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.3,
            textinfo='label+percent',
            textposition='auto',
        )])

        fig.update_layout(
            title=title,
            height=500,
            template='plotly_white'
        )

        return fig

    @staticmethod
    def create_trend_analysis(
        years: List[int],
        state_trends: Dict[str, List[float]],
        metric_name: str,
        title: str,
    ) -> go.Figure:
        """Create line chart showing trends over time.

        Args:
            years: List of years
            state_trends: State name -> list of values mapping
            metric_name: Name of metric
            title: Chart title

        Returns:
            Plotly line chart
        """
        fig = go.Figure()

        for state, values in state_trends.items():
            fig.add_trace(go.Scatter(
                x=years,
                y=values,
                mode='lines+markers',
                name=state,
                line=dict(width=2),
                marker=dict(size=8),
            ))

        fig.update_layout(
            title=title,
            xaxis_title="Year",
            yaxis_title=metric_name,
            height=500,
            template='plotly_white',
            hovermode='x unified'
        )

        return fig
