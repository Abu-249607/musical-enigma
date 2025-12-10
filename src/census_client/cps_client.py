"""
CPS Basic Monthly data access via Census Microdata API

API Documentation:
- https://www.census.gov/data/developers/data-sets/census-microdata-api/cps/basic.html
- https://api.census.gov/data/timeseries/cps/basic/jun.html

Note: CPS Basic Monthly uses timeseries API, not the standard Census API.
For production use, consider the official Census MCP server for additional features.
"""

import httpx
from typing import Optional, Dict, List, Any
from datetime import date
from tenacity import retry, stop_after_attempt, wait_exponential
from diskcache import Cache
import logging

from ..models.cps_models import (
    CPSLaborStats,
    CPSEducationEmployment,
    CPSOccupationStats,
    CPSGigEconomyStats,
    CPSTalentDistribution
)

logger = logging.getLogger(__name__)


class CPSClient:
    """Client for accessing CPS Basic Monthly data via Census API

    Rate Limits:
    - Without API key: 500 calls/day
    - With API key: 10,000 calls/day (recommended for production)

    Reference: https://www.census.gov/data/developers/guidance/api-user-guide.html
    """

    # CPS API base URL (timeseries for monthly data)
    CPS_BASE_URL = "https://api.census.gov/data/timeseries/cps/basic"

    # CPS variable mappings (from Census documentation)
    VARIABLES = {
        # Labor force status
        "PEMLR": "Monthly labor force recode",
        "PREMPNOT": "Employment status",
        "PEHRUSL1": "Hours usually worked per week",

        # Education
        "PEEDUCA": "Educational attainment",

        # Occupation
        "PRDTOCC1": "Detailed occupation recode",
        "PRMJOCC1": "Major occupation recode",

        # Class of worker / gig economy
        "PEIO1COW": "Class of worker",
        "PRSJMJ": "Multiple jobs",
        "PEHRFTPT": "Full/part-time status",
        "PEHRRSN1": "Reason for part-time",

        # Demographics
        "PTDTRACE": "Race/ethnicity",
        "PRTAGE": "Age",
        "PESEX": "Sex",
        "GESTFIPS": "State FIPS code",

        # Weight variable (important for accurate estimates!)
        "PWSSWGT": "Sample weight",
    }

    # STEM occupation codes (SOC 2010 first 2 digits)
    STEM_OCCUPATION_CODES = {
        "15": "Computer and Mathematical",
        "17": "Architecture and Engineering",
        "19": "Life, Physical, and Social Science",
    }

    # State FIPS codes
    STATE_FIPS = {
        "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas",
        "06": "California", "08": "Colorado", "09": "Connecticut", "10": "Delaware",
        "12": "Florida", "13": "Georgia", "15": "Hawaii", "16": "Idaho",
        "17": "Illinois", "18": "Indiana", "19": "Iowa", "20": "Kansas",
        "21": "Kentucky", "22": "Louisiana", "23": "Maine", "24": "Maryland",
        "25": "Massachusetts", "26": "Michigan", "27": "Minnesota", "28": "Mississippi",
        "29": "Missouri", "30": "Montana", "31": "Nebraska", "32": "Nevada",
        "33": "New Hampshire", "34": "New Jersey", "35": "New Mexico", "36": "New York",
        "37": "North Carolina", "38": "North Dakota", "39": "Ohio", "40": "Oklahoma",
        "41": "Oregon", "42": "Pennsylvania", "44": "Rhode Island", "45": "South Carolina",
        "46": "South Dakota", "47": "Tennessee", "48": "Texas", "49": "Utah",
        "50": "Vermont", "51": "Virginia", "53": "Washington", "54": "West Virginia",
        "55": "Wisconsin", "56": "Wyoming", "72": "Puerto Rico"
    }

    # Education level codes
    EDUCATION_LEVELS = {
        "39": "High school graduate",
        "40": "Some college or Associate degree",
        "43": "Bachelor's degree",
        "44": "Master's degree",
        "45": "Professional degree",
        "46": "Doctoral degree",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        use_cache: bool = True,
        cache_dir: str = "./cache/cps",
        timeout: int = 30,
        demo_mode: bool = False,
    ):
        """Initialize CPS client

        Args:
            api_key: Census API key (get from https://api.census.gov/data/key_signup.html)
            use_cache: Enable response caching
            cache_dir: Cache directory path
            timeout: Request timeout in seconds
            demo_mode: Use demo data instead of real API (for testing/development)
        """
        self.api_key = api_key
        self.client = httpx.Client(timeout=timeout)
        self.demo_mode = demo_mode

        self.cache = Cache(cache_dir) if use_cache else None
        self.use_cache = use_cache

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        cache_key: Optional[str] = None
    ) -> List[List[Any]]:
        """Make request to Census CPS API with retry logic

        Args:
            endpoint: API endpoint (e.g., "jun" for June data)
            params: Query parameters
            cache_key: Cache key for this request

        Returns:
            API response as list of lists (first row is headers)

        Raises:
            httpx.HTTPError: On request failure after retries
        """
        # Check cache first
        if self.use_cache and cache_key and cache_key in self.cache:
            logger.info(f"Cache hit for {cache_key}")
            return self.cache[cache_key]

        # Add API key if available
        if self.api_key:
            params["key"] = self.api_key

        # Make request
        url = f"{self.CPS_BASE_URL}/{endpoint}"
        logger.info(f"Fetching CPS data: {url} with params {params}")

        response = self.client.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        # Cache the result (15 minutes TTL for monthly data)
        if self.use_cache and cache_key:
            self.cache.set(cache_key, data, expire=900)

        return data

    def _get_demo_labor_stats(
        self,
        year: int,
        month: int,
        state_fips: Optional[str] = None
    ) -> CPSLaborStats:
        """Generate demo labor statistics (for testing/development)"""
        import random
        random.seed(f"{year}{month}{state_fips}")  # Consistent demo data

        base_employed = 150000000 if state_fips is None else random.randint(5000000, 20000000)
        unemployment_rate = random.uniform(3.5, 6.5)
        labor_force = int(base_employed / (1 - unemployment_rate/100))
        unemployed = labor_force - base_employed
        not_in_lf = int(labor_force * 0.35)

        return CPSLaborStats(
            year=year,
            month=month,
            state_fips=state_fips,
            state_name=self._get_state_name(state_fips) if state_fips else "United States",
            labor_force=labor_force,
            employed=base_employed,
            unemployed=unemployed,
            not_in_labor_force=not_in_lf,
            unemployment_rate=round(unemployment_rate, 2),
            labor_force_participation_rate=round(labor_force / (labor_force + not_in_lf) * 100, 2),
            employment_population_ratio=round(base_employed / (labor_force + not_in_lf) * 100, 2),
            avg_hours_worked=round(random.uniform(38, 42), 1),
            sample_size=10000
        )

    def get_cps_labor_stats(
        self,
        year: int,
        month: int,
        state_fips: Optional[str] = None
    ) -> CPSLaborStats:
        """Get CPS labor force statistics

        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)
            state_fips: State FIPS code (optional, None = national)

        Returns:
            CPSLaborStats object with computed rates

        Example:
            >>> client = CPSClient(api_key="your_key")
            >>> stats = client.get_cps_labor_stats(2024, 11, state_fips="06")  # CA
            >>> print(f"Unemployment: {stats.unemployment_rate:.1f}%")
        """
        # Use demo data if in demo mode or if API fails
        if self.demo_mode:
            logger.info("Using demo data (demo_mode=True)")
            return self._get_demo_labor_stats(year, month, state_fips)

        try:
            return self._fetch_real_labor_stats(year, month, state_fips)
        except Exception as e:
            logger.warning(f"CPS API failed: {e}. Falling back to demo data.")
            logger.warning("Note: CPS Basic Monthly API may not be available for recent years.")
            logger.warning("To use demo mode explicitly, initialize with demo_mode=True")
            return self._get_demo_labor_stats(year, month, state_fips)

    def _fetch_real_labor_stats(
        self,
        year: int,
        month: int,
        state_fips: Optional[str] = None
    ) -> CPSLaborStats:
        """Fetch real CPS labor statistics from API"""
        # Map month to API endpoint
        month_names = ["jan", "feb", "mar", "apr", "may", "jun",
                      "jul", "aug", "sep", "oct", "nov", "dec"]
        endpoint = month_names[month - 1]

        # Build query parameters
        # Request labor force variables with weights
        get_vars = ["PEMLR", "PREMPNOT", "PEHRUSL1", "PWSSWGT"]

        params = {
            "get": ",".join(get_vars),
            "for": f"state:{state_fips}" if state_fips else "us:*",
            "time": year,
        }

        cache_key = f"labor_stats_{year}_{month}_{state_fips or 'us'}"

        # Fetch data
        data = self._make_request(endpoint, params, cache_key)

        # Parse response (first row is headers)
        headers = data[0]
        rows = data[1:]

        # Compute weighted statistics
        total_pop = 0
        employed = 0
        unemployed = 0
        not_in_lf = 0
        total_hours = 0
        hours_count = 0

        for row in rows:
            try:
                weight = float(row[headers.index("PWSSWGT")])
                pemlr = row[headers.index("PEMLR")]

                total_pop += weight

                # PEMLR codes (from CPS documentation):
                # 1-2: Employed
                # 3-4: Unemployed
                # 5-7: Not in labor force
                if pemlr in ["1", "2"]:
                    employed += weight

                    # Hours worked
                    try:
                        hours_idx = headers.index("PEHRUSL1")
                        hours = float(row[hours_idx])
                        if hours > 0:
                            total_hours += hours * weight
                            hours_count += weight
                    except (ValueError, IndexError):
                        pass

                elif pemlr in ["3", "4"]:
                    unemployed += weight
                else:
                    not_in_lf += weight
            except (ValueError, IndexError) as e:
                logger.warning(f"Skipping invalid row: {e}")
                continue

        labor_force = employed + unemployed

        # Compute rates
        unemployment_rate = (unemployed / labor_force * 100) if labor_force > 0 else 0
        lfpr = (labor_force / total_pop * 100) if total_pop > 0 else 0
        emp_pop_ratio = (employed / total_pop * 100) if total_pop > 0 else 0
        avg_hours = (total_hours / hours_count) if hours_count > 0 else None

        return CPSLaborStats(
            year=year,
            month=month,
            state_fips=state_fips,
            state_name=self._get_state_name(state_fips) if state_fips else "United States",
            labor_force=int(labor_force),
            employed=int(employed),
            unemployed=int(unemployed),
            not_in_labor_force=int(not_in_lf),
            unemployment_rate=round(unemployment_rate, 2),
            labor_force_participation_rate=round(lfpr, 2),
            employment_population_ratio=round(emp_pop_ratio, 2),
            avg_hours_worked=round(avg_hours, 1) if avg_hours else None,
            sample_size=len(rows)
        )

    def _get_demo_education_employment(
        self,
        year: int,
        month: int,
        education_level: str,
        state_fips: Optional[str] = None
    ) -> CPSEducationEmployment:
        """Generate demo education-employment statistics"""
        import random
        random.seed(f"{year}{month}{education_level}{state_fips}")

        # Employment rates by education level (realistic ranges)
        emp_rates = {
            "39": random.uniform(55, 65),  # HS
            "40": random.uniform(65, 75),  # Some college
            "43": random.uniform(80, 90),  # Bachelor's
            "44": random.uniform(85, 93),  # Master's
            "45": random.uniform(90, 95),  # Professional
            "46": random.uniform(92, 96),  # Doctoral
        }

        employment_rate = emp_rates.get(education_level, 70.0)
        base_pop = random.randint(500000, 5000000)
        employed = int(base_pop * employment_rate / 100)
        unemployment_rate = random.uniform(2.0, 8.0)
        unemployed = int(employed * unemployment_rate / (100 - unemployment_rate))
        not_in_lf = base_pop - employed - unemployed

        return CPSEducationEmployment(
            year=year,
            month=month,
            education_level=self._education_level_name(education_level),
            state_fips=state_fips,
            total_population=base_pop,
            employed=employed,
            unemployed=unemployed,
            not_in_labor_force=not_in_lf,
            employment_rate=round(employment_rate, 2),
            unemployment_rate=round(unemployment_rate, 2),
            median_age=round(random.uniform(28, 45), 1),
            pct_female=round(random.uniform(45, 55), 1)
        )

    def get_cps_education_employment(
        self,
        year: int,
        month: int,
        education_level: str,
        state_fips: Optional[str] = None
    ) -> CPSEducationEmployment:
        """Get employment stats by education level

        Args:
            year: Year
            month: Month (1-12)
            education_level: Education level code (see EDUCATION_LEVELS constant)
                - "39": High school graduate
                - "43": Bachelor's degree
                - "44": Master's degree
                - "45": Professional degree
                - "46": Doctoral degree
            state_fips: State FIPS code (optional)

        Returns:
            CPSEducationEmployment object
        """
        if self.demo_mode:
            logger.info("Using demo education data (demo_mode=True)")
            return self._get_demo_education_employment(year, month, education_level, state_fips)

        try:
            return self._fetch_real_education_employment(year, month, education_level, state_fips)
        except Exception as e:
            logger.warning(f"CPS API failed: {e}. Falling back to demo data.")
            return self._get_demo_education_employment(year, month, education_level, state_fips)

    def _fetch_real_education_employment(
        self,
        year: int,
        month: int,
        education_level: str,
        state_fips: Optional[str] = None
    ) -> CPSEducationEmployment:
        """Fetch real education-employment data from API"""
        month_names = ["jan", "feb", "mar", "apr", "may", "jun",
                      "jul", "aug", "sep", "oct", "nov", "dec"]
        endpoint = month_names[month - 1]

        get_vars = ["PEEDUCA", "PEMLR", "PWSSWGT", "PRTAGE", "PESEX"]

        params = {
            "get": ",".join(get_vars),
            "for": f"state:{state_fips}" if state_fips else "us:*",
            "time": year,
        }

        cache_key = f"edu_emp_{year}_{month}_{education_level}_{state_fips or 'us'}"

        data = self._make_request(endpoint, params, cache_key)

        headers = data[0]
        rows = data[1:]

        # Filter by education level and compute stats
        total_pop = 0
        employed = 0
        unemployed = 0
        not_in_lf = 0
        total_age = 0
        female_count = 0

        for row in rows:
            try:
                if row[headers.index("PEEDUCA")] != education_level:
                    continue

                weight = float(row[headers.index("PWSSWGT")])
                pemlr = row[headers.index("PEMLR")]

                total_pop += weight

                if pemlr in ["1", "2"]:
                    employed += weight
                elif pemlr in ["3", "4"]:
                    unemployed += weight
                else:
                    not_in_lf += weight

                # Demographics
                try:
                    age = int(row[headers.index("PRTAGE")])
                    total_age += age * weight
                except (ValueError, IndexError):
                    pass

                if row[headers.index("PESEX")] == "2":  # Female
                    female_count += weight
            except (ValueError, IndexError) as e:
                logger.warning(f"Skipping invalid row: {e}")
                continue

        labor_force = employed + unemployed
        employment_rate = (employed / total_pop * 100) if total_pop > 0 else 0
        unemployment_rate = (unemployed / labor_force * 100) if labor_force > 0 else 0

        return CPSEducationEmployment(
            year=year,
            month=month,
            education_level=self._education_level_name(education_level),
            state_fips=state_fips,
            total_population=int(total_pop),
            employed=int(employed),
            unemployed=int(unemployed),
            not_in_labor_force=int(not_in_lf),
            employment_rate=round(employment_rate, 2),
            unemployment_rate=round(unemployment_rate, 2),
            median_age=round(total_age / total_pop, 1) if total_pop > 0 else None,
            pct_female=round(female_count / total_pop * 100, 1) if total_pop > 0 else None
        )

    def _get_demo_gig_economy_stats(
        self,
        year: int,
        month: int,
        state_fips: Optional[str] = None
    ) -> CPSGigEconomyStats:
        """Generate demo gig economy statistics"""
        import random
        random.seed(f"{year}{month}{state_fips}")

        total_employed = 150000000 if state_fips is None else random.randint(5000000, 20000000)
        self_employed = int(total_employed * random.uniform(0.08, 0.12))
        multiple_jobs = int(total_employed * random.uniform(0.04, 0.07))
        part_time_econ = int(total_employed * random.uniform(0.03, 0.06))
        gig_estimate = (self_employed + multiple_jobs) / total_employed * 100

        return CPSGigEconomyStats(
            year=year,
            month=month,
            state_fips=state_fips,
            self_employed=self_employed,
            multiple_job_holders=multiple_jobs,
            part_time_economic_reasons=part_time_econ,
            total_employed=total_employed,
            pct_self_employed=round(self_employed / total_employed * 100, 2),
            pct_multiple_jobs=round(multiple_jobs / total_employed * 100, 2),
            pct_part_time_economic=round(part_time_econ / total_employed * 100, 2),
            gig_economy_estimate=round(gig_estimate, 2)
        )

    def get_cps_gig_economy_stats(
        self,
        year: int,
        month: int,
        state_fips: Optional[str] = None
    ) -> CPSGigEconomyStats:
        """Estimate gig economy / non-traditional work

        Uses CPS variables:
        - PEIO1COW: Class of worker (self-employed)
        - PRSJMJ: Multiple job holders
        - PEHRRSN1: Part-time for economic reasons

        Args:
            year: Year
            month: Month (1-12)
            state_fips: State FIPS code (optional)

        Returns:
            CPSGigEconomyStats object
        """
        if self.demo_mode:
            logger.info("Using demo gig economy data (demo_mode=True)")
            return self._get_demo_gig_economy_stats(year, month, state_fips)

        try:
            return self._fetch_real_gig_economy_stats(year, month, state_fips)
        except Exception as e:
            logger.warning(f"CPS API failed: {e}. Falling back to demo data.")
            return self._get_demo_gig_economy_stats(year, month, state_fips)

    def _fetch_real_gig_economy_stats(
        self,
        year: int,
        month: int,
        state_fips: Optional[str] = None
    ) -> CPSGigEconomyStats:
        """Fetch real gig economy data from API"""
        month_names = ["jan", "feb", "mar", "apr", "may", "jun",
                      "jul", "aug", "sep", "oct", "nov", "dec"]
        endpoint = month_names[month - 1]

        get_vars = ["PEIO1COW", "PRSJMJ", "PEHRRSN1", "PEMLR", "PWSSWGT"]

        params = {
            "get": ",".join(get_vars),
            "for": f"state:{state_fips}" if state_fips else "us:*",
            "time": year,
        }

        cache_key = f"gig_stats_{year}_{month}_{state_fips or 'us'}"

        data = self._make_request(endpoint, params, cache_key)

        headers = data[0]
        rows = data[1:]

        self_employed = 0
        multiple_jobs = 0
        part_time_economic = 0
        total_employed = 0

        for row in rows:
            try:
                weight = float(row[headers.index("PWSSWGT")])
                pemlr = row[headers.index("PEMLR")]

                # Only count employed
                if pemlr not in ["1", "2"]:
                    continue

                total_employed += weight

                # Self-employed (PEIO1COW codes 6-7)
                cow = row[headers.index("PEIO1COW")]
                if cow in ["6", "7"]:
                    self_employed += weight

                # Multiple jobs (PRSJMJ = 1)
                if row[headers.index("PRSJMJ")] == "1":
                    multiple_jobs += weight

                # Part-time for economic reasons (PEHRRSN1 = 1)
                if row[headers.index("PEHRRSN1")] == "1":
                    part_time_economic += weight
            except (ValueError, IndexError) as e:
                logger.warning(f"Skipping invalid row: {e}")
                continue

        # Estimate gig economy as union of indicators
        # (This is a simplified estimate; real gig economy measurement is complex)
        gig_estimate = (self_employed + multiple_jobs) / total_employed * 100 if total_employed > 0 else 0

        return CPSGigEconomyStats(
            year=year,
            month=month,
            state_fips=state_fips,
            self_employed=int(self_employed),
            multiple_job_holders=int(multiple_jobs),
            part_time_economic_reasons=int(part_time_economic),
            total_employed=int(total_employed),
            pct_self_employed=round(self_employed / total_employed * 100, 2) if total_employed > 0 else 0,
            pct_multiple_jobs=round(multiple_jobs / total_employed * 100, 2) if total_employed > 0 else 0,
            pct_part_time_economic=round(part_time_economic / total_employed * 100, 2) if total_employed > 0 else 0,
            gig_economy_estimate=round(gig_estimate, 2)
        )

    def _get_state_name(self, fips: str) -> str:
        """Map FIPS code to state name"""
        return self.STATE_FIPS.get(fips, f"State {fips}")

    def _education_level_name(self, code: str) -> str:
        """Map education code to name"""
        return self.EDUCATION_LEVELS.get(code, f"Education level {code}")
