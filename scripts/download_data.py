#!/usr/bin/env python3
"""
Download all required datasets for Census Career Intelligence Platform

This script downloads:
1. CIP 2010 codes (field of study classifications)
2. SOC 2018 occupation codes and crosswalks
3. NAICS 2017 industry codes and crosswalks
4. ACS PUMS 2024 1-Year data (person records for all states)
5. Additional crosswalk files

Usage:
    python scripts/download_data.py --all
    python scripts/download_data.py --cip
    python scripts/download_data.py --pums --year 2024
"""

import os
import sys
import argparse
import urllib.request
import zipfile
import gzip
import shutil
from pathlib import Path
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataDownloader:
    """Download and extract Census and related datasets"""

    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.downloads_dir = self.base_dir / "downloads"
        self.code_lists_dir = self.base_dir / "code_lists"
        self.crosswalks_dir = self.base_dir / "crosswalks"
        self.acs_pums_dir = self.base_dir / "acs_pums"

        # Create directories
        for dir_path in [self.downloads_dir, self.code_lists_dir,
                         self.crosswalks_dir, self.acs_pums_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def download_file(self, url: str, dest_path: Path, description: str = ""):
        """Download a file with progress indication"""
        try:
            logger.info(f"Downloading {description or url}...")
            logger.info(f"URL: {url}")
            logger.info(f"Destination: {dest_path}")

            def progress_hook(count, block_size, total_size):
                if total_size > 0:
                    percent = int(count * block_size * 100 / total_size)
                    sys.stdout.write(f"\r{description}: {percent}%")
                    sys.stdout.flush()

            urllib.request.urlretrieve(url, dest_path, progress_hook)
            print()  # New line after progress
            logger.info(f"✅ Downloaded {description}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to download {description}: {e}")
            return False

    def extract_zip(self, zip_path: Path, extract_to: Path):
        """Extract a ZIP file"""
        try:
            logger.info(f"Extracting {zip_path.name}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            logger.info(f"✅ Extracted to {extract_to}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to extract {zip_path}: {e}")
            return False

    def download_cip_codes(self):
        """Download CIP 2010 codes (Classification of Instructional Programs)"""
        logger.info("=" * 60)
        logger.info("DOWNLOADING CIP 2010 CODES")
        logger.info("=" * 60)

        # CIP 2010 codes
        cip_url = "https://nces.ed.gov/ipeds/cipcode/Files/CIP2010_CSV.zip"
        cip_zip = self.downloads_dir / "CIP2010_CSV.zip"

        if self.download_file(cip_url, cip_zip, "CIP 2010 codes"):
            self.extract_zip(cip_zip, self.code_lists_dir)

            # Also create a STEM classification file
            self._create_stem_classification()

    def _create_stem_classification(self):
        """Create STEM field classification based on DHS/NSF definitions"""
        stem_fields = {
            "01": "Agriculture, Agriculture Operations, and Related Sciences",
            "03": "Natural Resources and Conservation",
            "11": "Computer and Information Sciences",
            "14": "Engineering",
            "15": "Engineering Technologies",
            "26": "Biological and Biomedical Sciences",
            "27": "Mathematics and Statistics",
            "29": "Military Technologies and Applied Sciences",
            "40": "Physical Sciences",
            "41": "Science Technologies/Technicians",
        }

        stem_file = self.code_lists_dir / "stem_fields.csv"
        with open(stem_file, 'w') as f:
            f.write("cip_2digit,cip_broad_field,is_stem\n")
            for cip_code, field_name in stem_fields.items():
                f.write(f"{cip_code},{field_name},1\n")

        logger.info(f"✅ Created STEM classification: {stem_file}")

    def download_soc_codes(self):
        """Download SOC 2018 occupation codes and crosswalks"""
        logger.info("=" * 60)
        logger.info("DOWNLOADING SOC 2018 OCCUPATION CODES")
        logger.info("=" * 60)

        # SOC 2018 structure file
        soc_url = "https://www.bls.gov/soc/2018/soc_2018_structure.xls"
        soc_file = self.downloads_dir / "soc_2018_structure.xls"

        self.download_file(soc_url, soc_file, "SOC 2018 structure")

        # SOC 2010 to 2018 crosswalk
        crosswalk_url = "https://www.bls.gov/soc/soccrosswalks.htm"
        logger.info(f"SOC crosswalks available at: {crosswalk_url}")
        logger.info("Note: Manual download may be required for some crosswalk files")

        # Download the direct crosswalk if available
        soc_crosswalk_url = "https://www.bls.gov/soc/2018/soc_2010_to_2018_crosswalk.xlsx"
        crosswalk_file = self.downloads_dir / "soc_2010_to_2018_crosswalk.xlsx"

        self.download_file(soc_crosswalk_url, crosswalk_file, "SOC 2010->2018 crosswalk")

    def download_naics_codes(self):
        """Download NAICS 2017 industry codes"""
        logger.info("=" * 60)
        logger.info("DOWNLOADING NAICS 2017 INDUSTRY CODES")
        logger.info("=" * 60)

        # NAICS 2017 codes
        naics_url = "https://www.census.gov/naics/2017NAICS/2017_NAICS_Descriptions.xlsx"
        naics_file = self.downloads_dir / "naics_2017_descriptions.xlsx"

        if self.download_file(naics_url, naics_file, "NAICS 2017 codes"):
            logger.info("✅ NAICS 2017 codes downloaded")

        # NAICS 2012 to 2017 crosswalk
        crosswalk_url = "https://www.census.gov/naics/concordances/2012_to_2017_NAICS.xlsx"
        crosswalk_file = self.downloads_dir / "naics_2012_to_2017_crosswalk.xlsx"

        self.download_file(crosswalk_url, crosswalk_file, "NAICS 2012->2017 crosswalk")

    def download_acs_pums(self, year: int = 2024, dataset: str = "1-Year", states: Optional[list] = None):
        """Download ACS PUMS data files

        Args:
            year: Survey year (2024 for latest 1-year)
            dataset: "1-Year" or "5-Year"
            states: List of state FIPS codes (None = all states)
        """
        logger.info("=" * 60)
        logger.info(f"DOWNLOADING ACS PUMS {year} {dataset}")
        logger.info("=" * 60)

        # Construct base URL
        base_url = f"https://www2.census.gov/programs-surveys/acs/data/pums/{year}/{dataset}/"

        # Destination directory
        dest_dir = self.acs_pums_dir / dataset.lower().replace("-", "_") / str(year)
        dest_dir.mkdir(parents=True, exist_ok=True)

        # State FIPS codes (all 50 states + DC + PR)
        if states is None:
            states = [f"{i:02d}" for i in range(1, 57)]  # 01-56 includes all states
            # Exclude gaps in FIPS codes
            exclude = ['03', '07', '11', '14', '43', '52']
            states = [s for s in states if s not in exclude]

        logger.info(f"Will download person files for {len(states)} states/territories")

        # Download data dictionary first
        dict_url = f"{base_url}PUMS_Data_Dictionary_{year}.pdf"
        dict_file = dest_dir / f"PUMS_Data_Dictionary_{year}.pdf"
        self.download_file(dict_url, dict_file, f"Data Dictionary {year}")

        # Download person files for each state
        success_count = 0
        failed = []

        for state_fips in states:
            # Person file
            csv_filename = f"psam_p{state_fips}.csv"
            csv_url = f"{base_url}csv_{state_fips}.zip"  # They're zipped
            zip_file = dest_dir / f"csv_{state_fips}.zip"

            if self.download_file(csv_url, zip_file, f"State {state_fips} person records"):
                # Extract the ZIP
                try:
                    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                        zip_ref.extractall(dest_dir)
                    zip_file.unlink()  # Remove ZIP after extraction
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to extract {zip_file}: {e}")
                    failed.append(state_fips)
            else:
                failed.append(state_fips)

        logger.info("=" * 60)
        logger.info(f"✅ Successfully downloaded {success_count}/{len(states)} states")
        if failed:
            logger.warning(f"⚠️  Failed states: {', '.join(failed)}")
        logger.info("=" * 60)

    def download_census_crosswalks(self):
        """Download Census occupation/industry crosswalks"""
        logger.info("=" * 60)
        logger.info("DOWNLOADING CENSUS CROSSWALKS")
        logger.info("=" * 60)

        # These are text files from Census
        crosswalks = {
            "occ_2018_to_soc_2018.txt":
                "https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2018-census-code-list.xlsx",
        }

        for filename, url in crosswalks.items():
            dest = self.crosswalks_dir / filename
            self.download_file(url, dest, filename)

    def download_all(self, pums_year: int = 2024):
        """Download all datasets"""
        logger.info("=" * 60)
        logger.info("DOWNLOADING ALL DATASETS")
        logger.info("This may take 30-60 minutes depending on connection speed")
        logger.info("Total download size: ~3-4 GB")
        logger.info("=" * 60)

        # Step 1: Code lists
        self.download_cip_codes()
        self.download_soc_codes()
        self.download_naics_codes()

        # Step 2: Crosswalks
        self.download_census_crosswalks()

        # Step 3: PUMS data (largest download)
        logger.info("\n⚠️  ACS PUMS download is ~3GB. This will take a while.")
        response = input("Continue with PUMS download? (y/n): ")
        if response.lower() == 'y':
            self.download_acs_pums(year=pums_year, dataset="1-Year")

        logger.info("=" * 60)
        logger.info("✅ ALL DOWNLOADS COMPLETE")
        logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Download Census datasets")
    parser.add_argument('--all', action='store_true', help='Download all datasets')
    parser.add_argument('--cip', action='store_true', help='Download CIP codes only')
    parser.add_argument('--soc', action='store_true', help='Download SOC codes only')
    parser.add_argument('--naics', action='store_true', help='Download NAICS codes only')
    parser.add_argument('--pums', action='store_true', help='Download ACS PUMS only')
    parser.add_argument('--year', type=int, default=2024, help='PUMS year (default: 2024)')
    parser.add_argument('--dataset', choices=['1-Year', '5-Year'], default='1-Year',
                       help='PUMS dataset type')
    parser.add_argument('--base-dir', default='data', help='Base data directory')

    args = parser.parse_args()

    downloader = DataDownloader(base_dir=args.base_dir)

    if args.all:
        downloader.download_all(pums_year=args.year)
    else:
        if args.cip:
            downloader.download_cip_codes()
        if args.soc:
            downloader.download_soc_codes()
        if args.naics:
            downloader.download_naics_codes()
        if args.pums:
            downloader.download_acs_pums(year=args.year, dataset=args.dataset)

        if not any([args.cip, args.soc, args.naics, args.pums]):
            parser.print_help()


if __name__ == "__main__":
    main()
