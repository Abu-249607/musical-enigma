# Streamlit App Quick Start Guide

## 🚀 Running the Census Employment Intelligence App

### Prerequisites

```bash
# 1. Make sure you're in the project directory
cd ~/musical-enigma  # or wherever you cloned the repo

# 2. Activate virtual environment (if using one)
source venv/bin/activate  # macOS/Linux

# 3. Ensure dependencies are installed
pip install -e ".[web]"
```

### Running the App

```bash
streamlit run app_enhanced.py
```

The app will automatically open in your browser at `http://localhost:8501`

---

## 📊 Features Available

### Tab 1: 💬 Chat Assistant
- Ask questions about employment data
- Get AI-powered insights with citations
- Query 2024 Census data in real-time

### Tab 2: 🎯 Employment Dashboard
- State-by-state employment metrics
- Occupation breakdowns
- Industry analysis

### Tab 3: 📈 State Comparison
- Compare employment across states
- Side-by-side metrics
- Interactive visualizations

### **Tab 4: 🎓 Field-of-Study Analytics** ⭐ NEW!

#### 📊 Field Comparison
- Compare employment outcomes across academic fields
- Quick-select popular field groups:
  - STEM Fields (CS, Engineering, Biology, Math)
  - Health Professions (Nursing, Public Health, Health Admin)
  - Business & Social Sciences (Business, Psychology, Economics)
- Interactive charts:
  - Employment rates by field
  - Median earnings comparison
  - Female representation metrics

#### ⚖️ Gender Gap Analysis
- Analyze employment and earnings gaps
- Male vs Female metrics:
  - Employment rate comparison
  - Median earnings comparison
  - Earnings gap percentage
- Female representation statistics
- Field-specific gender insights

#### 🗺️ Geographic Insights
- State-level talent distribution
- Employment concentration by field
- Median earnings by state
- Gender distribution maps

### Tab 5: 🎓 Student Analytics (CPS)
- Education ROI Calculator
- Gig Economy Tracker
- Talent Mapping

---

## 🎯 Quick Demo

### To test the new Field-of-Study Analytics:

1. **Launch the app:**
   ```bash
   streamlit run app_enhanced.py
   ```

2. **Navigate to Tab 4** ("🎓 Field-of-Study Analytics")

3. **Try Field Comparison:**
   - Click the "Field Comparison" subtab
   - Select "STEM Fields" from Quick Select dropdown
   - Click "Compare Fields"
   - See employment rates, earnings, and gender metrics across CS, Engineering, Biology, and Math

4. **Try Gender Gap Analysis:**
   - Click the "Gender Gap Analysis" subtab
   - Select "Computer Science" from the dropdown
   - Choose "Bachelor's degree"
   - Click "Analyze Gender Gap"
   - View employment gaps, earnings gaps, and female representation

5. **Try Geographic Insights:**
   - Click the "Geographic Insights" subtab
   - Select "Computer Science"
   - Choose "Employment Concentration"
   - Click "Show Geographic Distribution"
   - See state-by-state talent concentration

---

## 💡 Current Status

**Demonstration Mode Active:**
The Field-of-Study Analytics currently display realistic demo data to showcase the functionality. The analytics are fully functional and use the actual UI components and visualization logic.

**To Enable Real Data:**
When ACS PUMS data is loaded into `data/acs_pums/5-year/2019-2023/`, the backend analytics (already implemented) will automatically provide real Census microdata instead of demo data.

---

## 🎨 Customization

### Sidebar Settings
- **Data Year**: Select 2024, 2023, 2022, etc.
- **Dataset**: Choose ACS 1-year (recent) or 5-year (smaller geographies)
- **Clear Chat**: Reset chat history

### Field Selection Options
- **STEM Filter**: Filter to STEM fields only
- **Popular Fields**: Quick-select buttons for common fields
- **Search**: Search for fields by name
- **Custom Selection**: Choose any field from dropdown

---

## 🐛 Troubleshooting

### App won't start
```bash
# Reinstall dependencies
pip install -e ".[web]" --force-reinstall
```

### Port already in use
```bash
# Use a different port
streamlit run app_enhanced.py --server.port 8502
```

### Missing modules
```bash
# Install specific dependencies
pip install streamlit plotly pandas
```

### Census API errors
- Check your `.env` file has a valid Census API key
- Get a free API key at: https://api.census.gov/data/key_signup.html

---

## 📚 Additional Resources

- **Implementation Guide**: `FIELD_OF_STUDY_IMPLEMENTATION.md`
- **Features Overview**: `FEATURES.md`
- **Demo Guide**: `DEMO_GUIDE.md`
- **Download Instructions**: `DOWNLOAD_INSTRUCTIONS.md` (for PUMS data)

---

## 🔄 Updating the App

```bash
# Pull latest changes
git pull origin claude/census-employment-mcp-server-01HDTn2pVSmxVC7WGZ5nX1xp

# Reinstall if new dependencies were added
pip install -e ".[web]"

# Run the app
streamlit run app_enhanced.py
```

---

## ✨ What's New

**Latest Update: Field-of-Study Analytics Integration**

- ✅ Interactive field comparison with 3 visualizations
- ✅ Gender gap analysis with employment and earnings metrics
- ✅ Geographic talent distribution by state
- ✅ Quick-select for popular field groups
- ✅ Professional UI with Plotly charts
- ✅ Ready for real PUMS data integration

**All backend analytics already implemented:**
- Field-of-study outcome calculations
- Gender gap analysis
- Occupation pipeline analysis
- Sector distribution analysis
- Weighted statistics with Census person weights
- Margin of error calculations

**Next Steps:**
- Download ACS PUMS data (9.8GB) for real analytics
- Or use demonstration mode to explore features immediately

---

## 🎉 Enjoy!

You now have a fully functional Census Employment Intelligence platform with comprehensive field-of-study analytics!

**Quick Start Command:**
```bash
streamlit run app_enhanced.py
```

Then navigate to **Tab 4: Field-of-Study Analytics** to see the new features! 🚀
