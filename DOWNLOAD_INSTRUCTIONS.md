# 📥 DATA DOWNLOAD INSTRUCTIONS

The automated download script is blocked by network restrictions. Please download these files manually and place them in the specified directories.

---

## ⚠️ IMPORTANT: Network Restrictions

Direct downloads from external sites are blocked in this environment. You have **TWO OPTIONS**:

### Option A: Download on Local Machine, Then Upload
1. Download files on your local computer
2. Upload to this environment
3. Place in correct directories (see below)

### Option B: Use the Download Script Locally
```bash
# On your local machine with the repository:
python scripts/download_data.py --all
```

---

## 📋 REQUIRED DOWNLOADS

### 1. CIP 2010 Codes (Field of Study Classifications)

**File:** CIP2010_CSV.zip
**URL:** https://nces.ed.gov/ipeds/cipcode/Files/CIP2010_CSV.zip
**Size:** ~500 KB
**Destination:** `data/downloads/CIP2010_CSV.zip`

**After Download:**
```bash
cd data/downloads
unzip CIP2010_CSV.zip -d ../code_lists/
```

**What it contains:**
- CIP2010.csv - All field of study codes
- CIPDefinition.xls - Code definitions

---

### 2. SOC 2018 Occupation Codes

**Files to Download:**

#### a) SOC 2018 Structure
**URL:** https://www.bls.gov/soc/2018/soc_2018_structure.xls
**Destination:** `data/downloads/soc_2018_structure.xls`

#### b) SOC 2010 to 2018 Crosswalk
**URL:** https://www.bls.gov/soc/2018/soc_2010_to_2018_crosswalk.xlsx
**Destination:** `data/crosswalks/soc_2010_to_2018_crosswalk.xlsx`

#### c) Census OCC codes to SOC mapping
**URL:** https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2018-census-code-list.xlsx
**Destination:** `data/crosswalks/2018-census-code-list.xlsx`

---

### 3. NAICS 2017 Industry Codes

**Files to Download:**

#### a) NAICS 2017 Descriptions
**URL:** https://www.census.gov/naics/2017NAICS/2017_NAICS_Descriptions.xlsx
**Destination:** `data/downloads/naics_2017_descriptions.xlsx`

#### b) NAICS 2012 to 2017 Crosswalk
**URL:** https://www.census.gov/naics/concordances/2012_to_2017_NAICS.xlsx
**Destination:** `data/crosswalks/naics_2012_to_2017_crosswalk.xlsx`

---

### 4. ACS PUMS 2024 1-Year Data ⚠️ LARGE DOWNLOAD

**Warning:** This is ~3-4 GB total. Download on a good internet connection.

**Base URL:** https://www2.census.gov/programs-surveys/acs/data/pums/2024/1-Year/

**Required Files:**

#### Data Dictionary (Download First)
```
PUMS_Data_Dictionary_2024.pdf
→ Save to: data/acs_pums/1-year/2024/
```

#### Person Files (One per state - 50 files)
Format: `csv_{ST}.zip` where ST is state FIPS code

**Download All States:**
```
csv_01.zip  (Alabama)
csv_02.zip  (Alaska)
csv_04.zip  (Arizona)
csv_05.zip  (Arkansas)
csv_06.zip  (California)
csv_08.zip  (Colorado)
csv_09.zip  (Connecticut)
csv_10.zip  (Delaware)
csv_12.zip  (Florida)
csv_13.zip  (Georgia)
csv_15.zip  (Hawaii)
csv_16.zip  (Idaho)
csv_17.zip  (Illinois)
csv_18.zip  (Indiana)
csv_19.zip  (Iowa)
csv_20.zip  (Kansas)
csv_21.zip  (Kentucky)
csv_22.zip  (Louisiana)
csv_23.zip  (Maine)
csv_24.zip  (Maryland)
csv_25.zip  (Massachusetts)
csv_26.zip  (Michigan)
csv_27.zip  (Minnesota)
csv_28.zip  (Mississippi)
csv_29.zip  (Missouri)
csv_30.zip  (Montana)
csv_31.zip  (Nebraska)
csv_32.zip  (Nevada)
csv_33.zip  (New Hampshire)
csv_34.zip  (New Jersey)
csv_35.zip  (New Mexico)
csv_36.zip  (New York)
csv_37.zip  (North Carolina)
csv_38.zip  (North Dakota)
csv_39.zip  (Ohio)
csv_40.zip  (Oklahoma)
csv_41.zip  (Oregon)
csv_42.zip  (Pennsylvania)
csv_44.zip  (Rhode Island)
csv_45.zip  (South Carolina)
csv_46.zip  (South Dakota)
csv_47.zip  (Tennessee)
csv_48.zip  (Texas)
csv_49.zip  (Utah)
csv_50.zip  (Vermont)
csv_51.zip  (Virginia)
csv_53.zip  (Washington)
csv_54.zip  (West Virginia)
csv_55.zip  (Wisconsin)
csv_56.zip  (Wyoming)
csv_72.zip  (Puerto Rico - optional)
```

**After Download:**
```bash
# Extract all ZIP files
cd data/acs_pums/1-year/2024/
for f in csv_*.zip; do unzip -o "$f"; done

# This will create files like:
# psam_p01.csv (Alabama person records)
# psam_p06.csv (California person records)
# etc.
```

**Alternative - Download Subset for Testing:**
If you want to test with fewer states first, download these major states:
```
csv_06.zip  (California - largest population)
csv_48.zip  (Texas)
csv_36.zip  (New York)
csv_12.zip  (Florida)
csv_17.zip  (Illinois)
```

---

## 🚀 QUICK START SCRIPT

If you can run wget/curl on your local machine, use this:

```bash
#!/bin/bash
# Quick download script - run on local machine

BASE_DIR="data"
mkdir -p $BASE_DIR/{downloads,code_lists,crosswalks,acs_pums/1-year/2024}

# CIP Codes
wget -P $BASE_DIR/downloads https://nces.ed.gov/ipeds/cipcode/Files/CIP2010_CSV.zip
unzip $BASE_DIR/downloads/CIP2010_CSV.zip -d $BASE_DIR/code_lists/

# SOC Codes
wget -P $BASE_DIR/downloads https://www.bls.gov/soc/2018/soc_2018_structure.xls
wget -P $BASE_DIR/crosswalks https://www.bls.gov/soc/2018/soc_2010_to_2018_crosswalk.xlsx

# NAICS Codes
wget -P $BASE_DIR/downloads https://www.census.gov/naics/2017NAICS/2017_NAICS_Descriptions.xlsx
wget -P $BASE_DIR/crosswalks https://www.census.gov/naics/concordances/2012_to_2017_NAICS.xlsx

# Census Crosswalks
wget -P $BASE_DIR/crosswalks https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2018-census-code-list.xlsx

# ACS PUMS - Data Dictionary
wget -P $BASE_DIR/acs_pums/1-year/2024/ https://www2.census.gov/programs-surveys/acs/data/pums/2024/1-Year/PUMS_Data_Dictionary_2024.pdf

echo "Code lists downloaded. Now downloading PUMS data (this will take a while)..."

# ACS PUMS - Person files (comment out states you don't need)
cd $BASE_DIR/acs_pums/1-year/2024/
for state in 01 02 04 05 06 08 09 10 12 13 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 44 45 46 47 48 49 50 51 53 54 55 56; do
    wget https://www2.census.gov/programs-surveys/acs/data/pums/2024/1-Year/csv_${state}.zip
    unzip -o csv_${state}.zip
    rm csv_${state}.zip
done

echo "✅ All downloads complete!"
```

---

## 📂 EXPECTED DIRECTORY STRUCTURE

After all downloads and extractions:

```
data/
├── code_lists/
│   ├── CIP2010.csv
│   ├── CIPDefinition.xls
│   └── stem_fields.csv (will be generated)
├── crosswalks/
│   ├── soc_2010_to_2018_crosswalk.xlsx
│   ├── naics_2012_to_2017_crosswalk.xlsx
│   └── 2018-census-code-list.xlsx
├── downloads/
│   ├── CIP2010_CSV.zip
│   ├── soc_2018_structure.xls
│   └── naics_2017_descriptions.xlsx
└── acs_pums/
    └── 1-year/
        └── 2024/
            ├── PUMS_Data_Dictionary_2024.pdf
            ├── psam_p01.csv  (Alabama)
            ├── psam_p06.csv  (California)
            ├── psam_p48.csv  (Texas)
            └── ... (all 50 states)
```

---

## ✅ VERIFICATION

After downloading, verify files exist:

```bash
# Check code lists
ls -lh data/code_lists/
ls -lh data/crosswalks/

# Check PUMS data
ls -lh data/acs_pums/1-year/2024/ | wc -l
# Should show ~51 files (50 states + data dictionary)

# Check file sizes
du -sh data/acs_pums/1-year/2024/
# Should be ~3-4 GB total
```

---

## 🔄 NEXT STEPS AFTER DOWNLOAD

Once files are downloaded:

1. **Notify me** - I'll process and validate the files
2. **Create code list parsers** - Convert Excel/CSV to SQLite databases
3. **Build PUMS client** - Load and query microdata
4. **Implement analytics** - Field-of-study outcomes, gender gaps, etc.

---

## ⚠️ IPUMS CPS ASEC (MANUAL PROCESS)

CPS ASEC data requires a manual IPUMS extract:

1. **Register:** https://cps.ipums.org/cps/
2. **Select Variables:**
   - YEAR, MONTH, SERIAL, PERNUM, WTFINL
   - EDUC, EDDEGREE, GRADDEG
   - EMPSTAT, LABFORCE, OCC, IND
   - INCWAGE, HOURWAGE
   - AGE, SEX, STATEFIP
3. **Select Samples:** 2020-2024 ASEC
4. **Submit Extract**
5. **Download:** Will be emailed when ready
6. **Place in:** `data/cps_asec/extracts/`

---

## 🆘 NEED HELP?

If you encounter issues:
1. Check file sizes match expected values
2. Verify URLs are still active (Census occasionally moves files)
3. Try different download methods (browser, wget, curl, Python)
4. Let me know which specific file failed - I can provide mirrors

---

## 📊 DATA SIZE SUMMARY

| Dataset | Size | Priority |
|---------|------|----------|
| CIP Codes | 500 KB | High |
| SOC Codes | 2 MB | High |
| NAICS Codes | 1 MB | High |
| ACS PUMS 2024 | 3-4 GB | Critical |
| CPS ASEC (IPUMS) | 100-500 MB | Critical |

**Total:** ~4-5 GB
