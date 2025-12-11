"""
Data validation utilities to verify application metrics match Census data

Ensures accuracy by comparing computed values against raw CPS responses
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from ..census_client.cps_client import CPSClient
from ..models.cps_models import CPSLaborStats, CPSEducationEmployment, CPSGigEconomyStats

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of data validation"""
    metric_name: str
    app_value: float
    census_value: float
    difference: float
    pct_difference: float
    is_valid: bool
    threshold: float


class DataValidator:
    """Validates application metrics against Census data"""

    # Validation thresholds (percentage)
    DEFAULT_THRESHOLD = 0.5  # 0.5% difference allowed
    RATE_THRESHOLD = 0.1     # 0.1% for rates (more sensitive)

    def __init__(self, cps_client: CPSClient):
        """Initialize validator with CPS client"""
        self.client = cps_client

    def validate_labor_stats(
        self,
        app_stats: CPSLaborStats,
        threshold: Optional[float] = None
    ) -> List[ValidationResult]:
        """Validate computed labor statistics against raw Census data

        Re-queries CPS for the same parameters and compares values

        Args:
            app_stats: Statistics computed by the application
            threshold: Max allowed difference (percentage), defaults to 0.5%

        Returns:
            List of ValidationResult objects

        Example:
            >>> validator = DataValidator(cps_client)
            >>> app_stats = get_labor_stats(...)  # From app
            >>> results = validator.validate_labor_stats(app_stats)
            >>> for r in results:
            ...     if not r.is_valid:
            ...         print(f"MISMATCH: {r.metric_name}: {r.pct_difference:.2f}%")
        """
        threshold = threshold or self.DEFAULT_THRESHOLD

        # Re-query Census for same parameters
        census_stats = self.client.get_cps_labor_stats(
            year=app_stats.year,
            month=app_stats.month,
            state_fips=app_stats.state_fips
        )

        results = []

        # Validate each metric
        validations = [
            ("unemployment_rate", app_stats.unemployment_rate, census_stats.unemployment_rate, self.RATE_THRESHOLD),
            ("labor_force_participation_rate", app_stats.labor_force_participation_rate, census_stats.labor_force_participation_rate, self.RATE_THRESHOLD),
            ("employment_population_ratio", app_stats.employment_population_ratio, census_stats.employment_population_ratio, self.RATE_THRESHOLD),
            ("labor_force", app_stats.labor_force, census_stats.labor_force, threshold),
            ("employed", app_stats.employed, census_stats.employed, threshold),
            ("unemployed", app_stats.unemployed, census_stats.unemployed, threshold),
        ]

        for metric_name, app_val, census_val, metric_threshold in validations:
            diff = abs(app_val - census_val)
            pct_diff = (diff / census_val * 100) if census_val != 0 else 0
            is_valid = pct_diff <= metric_threshold

            result = ValidationResult(
                metric_name=metric_name,
                app_value=app_val,
                census_value=census_val,
                difference=diff,
                pct_difference=pct_diff,
                is_valid=is_valid,
                threshold=metric_threshold
            )

            results.append(result)

            if not is_valid:
                logger.warning(
                    f"Validation failed for {metric_name}: "
                    f"app={app_val:.2f}, census={census_val:.2f}, "
                    f"diff={pct_diff:.2f}% (threshold={metric_threshold}%)"
                )

        return results

    def validate_education_employment(
        self,
        app_stats: CPSEducationEmployment,
        threshold: Optional[float] = None
    ) -> List[ValidationResult]:
        """Validate education-employment statistics

        Args:
            app_stats: Education employment stats from app
            threshold: Max allowed difference (percentage)

        Returns:
            List of ValidationResult objects
        """
        threshold = threshold or self.DEFAULT_THRESHOLD

        # Reverse lookup education level code
        edu_code = self._get_education_code(app_stats.education_level)
        if not edu_code:
            raise ValueError(f"Cannot find education code for {app_stats.education_level}")

        # Re-query Census
        census_stats = self.client.get_cps_education_employment(
            year=app_stats.year,
            month=app_stats.month,
            education_level=edu_code,
            state_fips=app_stats.state_fips
        )

        results = []

        validations = [
            ("employment_rate", app_stats.employment_rate, census_stats.employment_rate, self.RATE_THRESHOLD),
            ("unemployment_rate", app_stats.unemployment_rate, census_stats.unemployment_rate, self.RATE_THRESHOLD),
            ("total_population", app_stats.total_population, census_stats.total_population, threshold),
            ("employed", app_stats.employed, census_stats.employed, threshold),
        ]

        for metric_name, app_val, census_val, metric_threshold in validations:
            diff = abs(app_val - census_val)
            pct_diff = (diff / census_val * 100) if census_val != 0 else 0
            is_valid = pct_diff <= metric_threshold

            result = ValidationResult(
                metric_name=metric_name,
                app_value=app_val,
                census_value=census_val,
                difference=diff,
                pct_difference=pct_diff,
                is_valid=is_valid,
                threshold=metric_threshold
            )

            results.append(result)

            if not is_valid:
                logger.warning(
                    f"Validation failed for {metric_name}: "
                    f"app={app_val:.2f}, census={census_val:.2f}, "
                    f"diff={pct_diff:.2f}% (threshold={metric_threshold}%)"
                )

        return results

    def validate_gig_economy_stats(
        self,
        app_stats: CPSGigEconomyStats,
        threshold: Optional[float] = None
    ) -> List[ValidationResult]:
        """Validate gig economy statistics

        Args:
            app_stats: Gig economy stats from app
            threshold: Max allowed difference (percentage)

        Returns:
            List of ValidationResult objects
        """
        threshold = threshold or self.DEFAULT_THRESHOLD

        # Re-query Census
        census_stats = self.client.get_cps_gig_economy_stats(
            year=app_stats.year,
            month=app_stats.month,
            state_fips=app_stats.state_fips
        )

        results = []

        validations = [
            ("pct_self_employed", app_stats.pct_self_employed, census_stats.pct_self_employed, self.RATE_THRESHOLD),
            ("pct_multiple_jobs", app_stats.pct_multiple_jobs, census_stats.pct_multiple_jobs, self.RATE_THRESHOLD),
            ("gig_economy_estimate", app_stats.gig_economy_estimate, census_stats.gig_economy_estimate, threshold),
            ("self_employed", app_stats.self_employed, census_stats.self_employed, threshold),
        ]

        for metric_name, app_val, census_val, metric_threshold in validations:
            diff = abs(app_val - census_val)
            pct_diff = (diff / census_val * 100) if census_val != 0 else 0
            is_valid = pct_diff <= metric_threshold

            result = ValidationResult(
                metric_name=metric_name,
                app_value=app_val,
                census_value=census_val,
                difference=diff,
                pct_difference=pct_diff,
                is_valid=is_valid,
                threshold=metric_threshold
            )

            results.append(result)

            if not is_valid:
                logger.warning(
                    f"Validation failed for {metric_name}: "
                    f"app={app_val:.2f}, census={census_val:.2f}, "
                    f"diff={pct_diff:.2f}% (threshold={metric_threshold}%)"
                )

        return results

    def assert_valid(self, results: List[ValidationResult]):
        """Assert all validation results are valid

        Useful in tests to ensure data accuracy

        Args:
            results: List of ValidationResult

        Raises:
            AssertionError: If any validation failed
        """
        failed = [r for r in results if not r.is_valid]

        if failed:
            msg = "Data validation failed:\n"
            for r in failed:
                msg += f"  {r.metric_name}: {r.pct_difference:.2f}% diff (threshold {r.threshold}%)\n"
                msg += f"    App: {r.app_value:.2f}, Census: {r.census_value:.2f}\n"
            raise AssertionError(msg)

    def batch_validate(
        self,
        labor_stats: Optional[List[CPSLaborStats]] = None,
        education_stats: Optional[List[CPSEducationEmployment]] = None,
        gig_stats: Optional[List[CPSGigEconomyStats]] = None,
        threshold: Optional[float] = None
    ) -> Dict[str, List[ValidationResult]]:
        """Validate multiple statistics in batch

        Args:
            labor_stats: List of labor statistics to validate
            education_stats: List of education statistics to validate
            gig_stats: List of gig economy statistics to validate
            threshold: Max allowed difference

        Returns:
            Dictionary mapping category to validation results
        """
        results = {}

        if labor_stats:
            results["labor_stats"] = []
            for stats in labor_stats:
                results["labor_stats"].extend(
                    self.validate_labor_stats(stats, threshold)
                )

        if education_stats:
            results["education_stats"] = []
            for stats in education_stats:
                results["education_stats"].extend(
                    self.validate_education_employment(stats, threshold)
                )

        if gig_stats:
            results["gig_stats"] = []
            for stats in gig_stats:
                results["gig_stats"].extend(
                    self.validate_gig_economy_stats(stats, threshold)
                )

        return results

    def generate_validation_report(
        self,
        results: List[ValidationResult]
    ) -> Dict[str, any]:
        """Generate validation report

        Args:
            results: List of validation results

        Returns:
            Dictionary with validation summary
        """
        total = len(results)
        passed = sum(1 for r in results if r.is_valid)
        failed = total - passed

        failed_metrics = [r for r in results if not r.is_valid]

        return {
            "total_validations": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "failed_metrics": failed_metrics,
            "max_difference": max([r.pct_difference for r in results]) if results else 0,
            "avg_difference": sum([r.pct_difference for r in results]) / len(results) if results else 0
        }

    def _get_education_code(self, education_level: str) -> Optional[str]:
        """Reverse lookup education level code"""
        for code, name in self.client.EDUCATION_LEVELS.items():
            if name == education_level:
                return code
        return None
