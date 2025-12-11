"""Data governance module for Census Career Intelligence Platform

Enforces data availability rules and prevents requests for non-existent data.
"""

from .availability import (
    DatasetType,
    DatasetAvailability,
    DATASET_REGISTRY,
    validate_data_request,
    get_latest_available_year,
    get_available_years,
    check_release_status,
    DataAvailabilityError,
)

__all__ = [
    "DatasetType",
    "DatasetAvailability",
    "DATASET_REGISTRY",
    "validate_data_request",
    "get_latest_available_year",
    "get_available_years",
    "check_release_status",
    "DataAvailabilityError",
]
