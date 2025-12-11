"""
Code List Loaders for Census Classifications

Loads and caches CIP (field of study), SOC (occupation), and NAICS (industry) code lists.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class CIPCodeLoader:
    """Load and query CIP 2010 (Classification of Instructional Programs) codes

    CIP codes classify fields of study using a hierarchical structure:
    - 2-digit: Broad field (e.g., "11" = Computer Science)
    - 4-digit: Specific field (e.g., "1107" = Computer Science)
    - 6-digit: Detailed program (e.g., "110701" = Computer Science, General)
    """

    def __init__(self, code_list_path: Optional[Path] = None):
        """Initialize CIP code loader

        Args:
            code_list_path: Path to CIP CSV file. If None, uses default location.
        """
        if code_list_path is None:
            # Try full CIP2010.csv first, fall back to sample
            base_dir = Path("data/code_lists")
            if (base_dir / "CIP2010.csv").exists():
                code_list_path = base_dir / "CIP2010.csv"
            else:
                code_list_path = base_dir / "cip_2010_sample.csv"
                logger.info("Using sample CIP codes. Download full CIP2010.csv for complete list.")

        self.code_list_path = Path(code_list_path)
        self._df: Optional[pd.DataFrame] = None
        self._code_to_info: Optional[Dict] = None

    @property
    def df(self) -> pd.DataFrame:
        """Lazy-load CIP codes DataFrame"""
        if self._df is None:
            self._load()
        return self._df

    def _load(self):
        """Load CIP codes from CSV"""
        try:
            self._df = pd.read_csv(self.code_list_path)
            logger.info(f"Loaded {len(self._df)} CIP codes from {self.code_list_path}")

            # Create lookup dictionary
            self._code_to_info = {
                row['cip_code']: {
                    'title': row['cip_title'],
                    'broad_field': row['cip_broad_field'],
                    'is_stem': bool(row['is_stem'])
                }
                for _, row in self._df.iterrows()
            }
        except Exception as e:
            logger.error(f"Failed to load CIP codes: {e}")
            # Create empty dataframe as fallback
            self._df = pd.DataFrame(columns=['cip_code', 'cip_title', 'cip_2digit', 'cip_broad_field', 'is_stem'])
            self._code_to_info = {}

    def get_title(self, cip_code: str) -> Optional[str]:
        """Get title for a CIP code

        Args:
            cip_code: CIP code (e.g., "1107" or "11")

        Returns:
            Field title or None if not found
        """
        info = self._code_to_info.get(cip_code)
        return info['title'] if info else None

    def is_stem(self, cip_code: str) -> bool:
        """Check if CIP code is STEM field

        Args:
            cip_code: CIP code

        Returns:
            True if STEM field
        """
        info = self._code_to_info.get(cip_code)
        return info['is_stem'] if info else False

    def get_stem_fields(self) -> pd.DataFrame:
        """Get all STEM fields

        Returns:
            DataFrame of STEM fields only
        """
        return self.df[self.df['is_stem'] == 1].copy()

    def get_broad_field(self, cip_code: str) -> Optional[str]:
        """Get broad field category for a CIP code

        Args:
            cip_code: CIP code

        Returns:
            Broad field name
        """
        info = self._code_to_info.get(cip_code)
        return info['broad_field'] if info else None

    def search(self, query: str) -> pd.DataFrame:
        """Search CIP codes by title

        Args:
            query: Search string (case-insensitive)

        Returns:
            DataFrame of matching codes
        """
        mask = self.df['cip_title'].str.contains(query, case=False, na=False)
        return self.df[mask].copy()


class SOCCodeLoader:
    """Load and query SOC 2018 (Standard Occupational Classification) codes

    SOC codes classify occupations:
    - 2-digit: Major group (e.g., "15" = Computer and Mathematical)
    - 4-digit: Minor group (e.g., "15-12" = Computer Systems Analysts)
    - 6-digit: Detailed occupation (e.g., "15-1252" = Software Developers)
    """

    def __init__(self, code_list_path: Optional[Path] = None):
        """Initialize SOC code loader

        Args:
            code_list_path: Path to SOC CSV file. If None, uses default location.
        """
        if code_list_path is None:
            base_dir = Path("data/code_lists")
            if (base_dir / "soc_2018_structure.csv").exists():
                code_list_path = base_dir / "soc_2018_structure.csv"
            else:
                code_list_path = base_dir / "soc_2018_sample.csv"
                logger.info("Using sample SOC codes. Download full SOC file for complete list.")

        self.code_list_path = Path(code_list_path)
        self._df: Optional[pd.DataFrame] = None
        self._code_to_info: Optional[Dict] = None

    @property
    def df(self) -> pd.DataFrame:
        """Lazy-load SOC codes DataFrame"""
        if self._df is None:
            self._load()
        return self._df

    def _load(self):
        """Load SOC codes from CSV"""
        try:
            self._df = pd.read_csv(self.code_list_path)
            logger.info(f"Loaded {len(self._df)} SOC codes from {self.code_list_path}")

            # Create lookup dictionary
            self._code_to_info = {
                row['soc_code']: {
                    'title': row['soc_title'],
                    'major_group': row['soc_major_group'],
                    'is_stem': bool(row.get('is_stem', 0))
                }
                for _, row in self._df.iterrows()
            }
        except Exception as e:
            logger.error(f"Failed to load SOC codes: {e}")
            self._df = pd.DataFrame(columns=['soc_code', 'soc_title', 'soc_2digit', 'soc_major_group', 'is_stem'])
            self._code_to_info = {}

    def get_title(self, soc_code: str) -> Optional[str]:
        """Get title for a SOC code

        Args:
            soc_code: SOC code (e.g., "15-1252")

        Returns:
            Occupation title or None if not found
        """
        info = self._code_to_info.get(soc_code)
        return info['title'] if info else None

    def is_stem(self, soc_code: str) -> bool:
        """Check if SOC code is STEM occupation

        Args:
            soc_code: SOC code

        Returns:
            True if STEM occupation
        """
        info = self._code_to_info.get(soc_code)
        return info['is_stem'] if info else False

    def get_stem_occupations(self) -> pd.DataFrame:
        """Get all STEM occupations

        Returns:
            DataFrame of STEM occupations only
        """
        return self.df[self.df['is_stem'] == 1].copy()

    def search(self, query: str) -> pd.DataFrame:
        """Search SOC codes by title

        Args:
            query: Search string (case-insensitive)

        Returns:
            DataFrame of matching codes
        """
        mask = self.df['soc_title'].str.contains(query, case=False, na=False)
        return self.df[mask].copy()


class NAICSCodeLoader:
    """Load and query NAICS 2017 (North American Industry Classification System) codes

    NAICS codes classify industries:
    - 2-digit: Sector (e.g., "51" = Information)
    - 3-digit: Subsector (e.g., "511" = Publishing Industries)
    - 4-digit: Industry Group (e.g., "5112" = Software Publishers)
    - 6-digit: Detailed Industry (e.g., "511210" = Software Publishers)
    """

    def __init__(self, code_list_path: Optional[Path] = None):
        """Initialize NAICS code loader

        Args:
            code_list_path: Path to NAICS CSV file. If None, uses default location.
        """
        if code_list_path is None:
            base_dir = Path("data/code_lists")
            if (base_dir / "naics_2017_descriptions.csv").exists():
                code_list_path = base_dir / "naics_2017_descriptions.csv"
            else:
                code_list_path = base_dir / "naics_2017_sample.csv"
                logger.info("Using sample NAICS codes. Download full NAICS file for complete list.")

        self.code_list_path = Path(code_list_path)
        self._df: Optional[pd.DataFrame] = None
        self._code_to_info: Optional[Dict] = None

    @property
    def df(self) -> pd.DataFrame:
        """Lazy-load NAICS codes DataFrame"""
        if self._df is None:
            self._load()
        return self._df

    def _load(self):
        """Load NAICS codes from CSV"""
        try:
            self._df = pd.read_csv(self.code_list_path)
            logger.info(f"Loaded {len(self._df)} NAICS codes from {self.code_list_path}")

            # Create lookup dictionary
            self._code_to_info = {
                str(row['naics_code']): {
                    'title': row['naics_title'],
                    'sector': row['naics_sector'],
                    'is_tech': bool(row.get('is_tech_sector', 0))
                }
                for _, row in self._df.iterrows()
            }
        except Exception as e:
            logger.error(f"Failed to load NAICS codes: {e}")
            self._df = pd.DataFrame(columns=['naics_code', 'naics_title', 'naics_2digit', 'naics_sector', 'is_tech_sector'])
            self._code_to_info = {}

    def get_title(self, naics_code: str) -> Optional[str]:
        """Get title for a NAICS code

        Args:
            naics_code: NAICS code (e.g., "5112")

        Returns:
            Industry title or None if not found
        """
        info = self._code_to_info.get(str(naics_code))
        return info['title'] if info else None

    def is_tech_sector(self, naics_code: str) -> bool:
        """Check if NAICS code is technology sector

        Args:
            naics_code: NAICS code

        Returns:
            True if tech sector
        """
        info = self._code_to_info.get(str(naics_code))
        return info['is_tech'] if info else False

    def get_tech_sectors(self) -> pd.DataFrame:
        """Get all technology sectors

        Returns:
            DataFrame of tech sectors only
        """
        return self.df[self.df['is_tech_sector'] == 1].copy()

    def search(self, query: str) -> pd.DataFrame:
        """Search NAICS codes by title

        Args:
            query: Search string (case-insensitive)

        Returns:
            DataFrame of matching codes
        """
        mask = self.df['naics_title'].str.contains(query, case=False, na=False)
        return self.df[mask].copy()


# =====================================================================
# SINGLETON INSTANCES (cached)
# =====================================================================

@lru_cache(maxsize=1)
def get_cip_loader() -> CIPCodeLoader:
    """Get cached CIP code loader instance"""
    return CIPCodeLoader()


@lru_cache(maxsize=1)
def get_soc_loader() -> SOCCodeLoader:
    """Get cached SOC code loader instance"""
    return SOCCodeLoader()


@lru_cache(maxsize=1)
def get_naics_loader() -> NAICSCodeLoader:
    """Get cached NAICS code loader instance"""
    return NAICSCodeLoader()
