"""
Field of Study Selection Component

Provides UI components for selecting and filtering fields of study (CIP codes)
with STEM classification and popular field quick-select.
"""

import streamlit as st
from typing import List, Optional, Tuple
import pandas as pd

from ..code_lists.loaders import get_cip_loader


class FieldOfStudySelector:
    """UI component for field-of-study selection"""

    def __init__(self):
        self.cip_loader = get_cip_loader()

    def render_field_selector(
        self,
        key: str = "field_selector",
        allow_multiple: bool = False,
        show_stem_filter: bool = True,
        show_popular_fields: bool = True
    ) -> Optional[List[str]]:
        """Render field-of-study selector with optional filters

        Args:
            key: Unique key for widget
            allow_multiple: Allow selecting multiple fields
            show_stem_filter: Show STEM/non-STEM filter checkbox
            show_popular_fields: Show popular fields quick-select

        Returns:
            List of selected CIP codes, or None if no selection
        """
        st.subheader("🎓 Select Field of Study")

        # STEM filter
        if show_stem_filter:
            stem_only = st.checkbox(
                "STEM fields only",
                value=False,
                key=f"{key}_stem_filter",
                help="Filter to Science, Technology, Engineering, and Mathematics fields"
            )
        else:
            stem_only = False

        # Get all fields
        all_fields_df = self.cip_loader.get_all()

        # Apply STEM filter
        if stem_only:
            all_fields_df = all_fields_df[all_fields_df['code'].apply(self.cip_loader.is_stem)]

        # Popular fields quick-select
        if show_popular_fields:
            st.caption("**Popular Fields:**")
            popular_fields = {
                "Computer Science": "1107",
                "Engineering": "1401",
                "Business": "5201",
                "Nursing": "5138",
                "Psychology": "4201",
                "Biology": "2601",
                "Education": "1301",
                "Communications": "0901"
            }

            cols = st.columns(4)
            selected_popular = None

            for i, (name, code) in enumerate(popular_fields.items()):
                with cols[i % 4]:
                    if st.button(name, key=f"{key}_popular_{code}", use_container_width=True):
                        selected_popular = code

            if selected_popular:
                return [selected_popular] if allow_multiple else selected_popular

            st.divider()

        # Search box
        search_query = st.text_input(
            "Search fields:",
            placeholder="e.g., computer, engineering, biology",
            key=f"{key}_search"
        )

        # Filter fields based on search
        if search_query:
            search_results = self.cip_loader.search(search_query)
            if len(search_results) == 0:
                st.warning(f"No fields found matching '{search_query}'")
                return None
            fields_to_show = search_results
        else:
            fields_to_show = all_fields_df

        # Create display options
        field_options = {
            f"{row['title']} ({row['code']})": row['code']
            for _, row in fields_to_show.head(50).iterrows()
        }

        if len(field_options) == 0:
            st.info("No fields available. Try adjusting your filters.")
            return None

        # Selector
        if allow_multiple:
            selected_display = st.multiselect(
                "Select field(s):",
                options=list(field_options.keys()),
                key=f"{key}_multiselect",
                help="Select one or more fields of study to analyze"
            )
            if not selected_display:
                return None
            return [field_options[disp] for disp in selected_display]
        else:
            selected_display = st.selectbox(
                "Select field:",
                options=[""] + list(field_options.keys()),
                key=f"{key}_selectbox",
                help="Select a field of study to analyze"
            )
            if not selected_display:
                return None
            return field_options[selected_display]

    def render_education_level_selector(
        self,
        key: str = "edu_level",
        default: str = "23"
    ) -> str:
        """Render education level selector

        Args:
            key: Unique key for widget
            default: Default education level code

        Returns:
            Selected education level code
        """
        education_levels = {
            "Bachelor's degree": "23",
            "Master's degree": "24",
            "Professional degree": "25",
            "Doctoral degree": "26"
        }

        # Find default index
        default_label = [k for k, v in education_levels.items() if v == default]
        default_index = 0 if not default_label else list(education_levels.keys()).index(default_label[0])

        selected_label = st.selectbox(
            "Education Level:",
            options=list(education_levels.keys()),
            index=default_index,
            key=key,
            help="Select degree level to analyze"
        )

        return education_levels[selected_label]

    def render_gender_filter(
        self,
        key: str = "gender_filter"
    ) -> Optional[str]:
        """Render gender filter

        Args:
            key: Unique key for widget

        Returns:
            Gender code ("1" for male, "2" for female, None for all)
        """
        gender_options = {
            "All": None,
            "Male": "1",
            "Female": "2"
        }

        selected = st.radio(
            "Gender:",
            options=list(gender_options.keys()),
            horizontal=True,
            key=key,
            help="Filter by gender"
        )

        return gender_options[selected]

    def render_comparison_selector(
        self,
        key: str = "comparison",
        max_fields: int = 5
    ) -> List[str]:
        """Render field comparison selector

        Args:
            key: Unique key for widget
            max_fields: Maximum number of fields to compare

        Returns:
            List of selected CIP codes
        """
        st.subheader("🔬 Compare Fields")

        # Pre-defined comparisons
        st.caption("**Quick Comparisons:**")

        comparison_sets = {
            "STEM Fields": ["1107", "1401", "2601", "2701"],  # CS, Engineering, Biology, Math
            "Health Professions": ["5138", "5128", "5139"],  # Nursing, Public Health, Health Admin
            "Business & Social Sciences": ["5201", "4201", "4501"],  # Business, Psychology, Social Sciences
            "Education & Humanities": ["1301", "2301", "1601"]  # Education, English, Languages
        }

        cols = st.columns(len(comparison_sets))
        for i, (name, codes) in enumerate(comparison_sets.items()):
            with cols[i]:
                if st.button(name, key=f"{key}_preset_{i}", use_container_width=True):
                    return codes

        st.divider()

        # Custom selection
        return self.render_field_selector(
            key=f"{key}_custom",
            allow_multiple=True,
            show_stem_filter=True,
            show_popular_fields=False
        ) or []


def render_field_selector_simple(
    key: str = "field_selector",
    allow_multiple: bool = False
) -> Optional[List[str]]:
    """Simple function to render field selector (convenience wrapper)

    Args:
        key: Unique key for widget
        allow_multiple: Allow multiple selections

    Returns:
        Selected field code(s)
    """
    selector = FieldOfStudySelector()
    return selector.render_field_selector(key=key, allow_multiple=allow_multiple)
