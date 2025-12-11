# Quick Start Guide

Get up and running with the Census Employment RAG tool in 5 minutes.

## 🚀 Installation

### 1. Clone and Install

```bash
cd musical-enigma

# Install base dependencies
pip install -e .

# Install web interface dependencies
pip install -e ".[web]"
```

### 2. Set Up Census API Key

Get a free API key from: https://api.census.gov/data/key_signup.html

Create a `.env` file:

```bash
echo "CENSUS_API_KEY=your_key_here" > .env
```

## 🎯 Quick Examples

### Example 1: Simple Data Retrieval

```python
from src.census_client import CensusMCPClient

# Create client
client = CensusMCPClient(api_key="YOUR_KEY")

# Get 2024 employment data
record, citation = client.get_employment_data("California")

print(f"Unemployment Rate: {record.unemployment_rate}%")
print(f"Labor Force: {record.labor_force:,}")
print(f"\nCitation: {citation.to_reference_string()}")
```

**Output**:
```
Unemployment Rate: 5.2%
Labor Force: 19,381,457

Citation: U.S. Census Bureau. (2024). American Community Survey 1-Year Estimates...
```

---

### Example 2: Conversational RAG

```python
from src.retrieval import ConversationalRAGPipeline

# Create RAG pipeline
rag = ConversationalRAGPipeline(api_key="YOUR_KEY")

# Start conversation
conv_id = rag.start_conversation()

# Ask questions
response1 = rag.chat(
    "What's the unemployment rate in California in 2024?",
    conversation_id=conv_id
)

response2 = rag.chat(
    "How does it compare to Texas?",  # Understands context!
    conversation_id=conv_id
)

print(response2['context'])
```

---

### Example 3: State Comparison

```python
from src.retrieval import ConversationalRAGPipeline

rag = ConversationalRAGPipeline(api_key="YOUR_KEY")

# Compare multiple states
comparison = rag.compare_geographies_conversational(
    geographies=["California", "Texas", "New York"],
    metric="unemployment",
    year=2024
)

for state, data in comparison['geographies'].items():
    print(f"{state}: {data['unemployment_rate']}%")
```

---

## 🌐 Web Interface

### Run the Enhanced Streamlit App

```bash
streamlit run app_enhanced.py
```

Then open http://localhost:8501 in your browser.

### Features:
- **💬 Chat Assistant**: Ask questions in natural language
- **📊 Dashboard**: View state employment statistics with charts
- **📈 Comparisons**: Compare multiple states side-by-side
- **🔬 Analytics**: Access advanced STEM and career insights (coming soon)

---

## 🎓 Tutorial: Your First Analysis

### Step 1: Get State Data

```python
from src.census_client import CensusMCPClient

client = CensusMCPClient(api_key="YOUR_KEY")

# Get California data
ca_record, ca_citation = client.get_employment_data("California", year=2024)

# Get Texas data
tx_record, tx_citation = client.get_employment_data("Texas", year=2024)

print(f"California Unemployment: {ca_record.unemployment_rate}%")
print(f"Texas Unemployment: {tx_record.unemployment_rate}%")
```

### Step 2: Get Industry Breakdown

```python
# Get industry data for California
industry_data, citation = client.get_industry_employment("California", year=2024)

# Find top industries
sorted_industries = sorted(
    industry_data.items(),
    key=lambda x: x[1],
    reverse=True
)[:5]

print("\nTop 5 Industries in California:")
for industry, count in sorted_industries:
    print(f"  {industry}: {count:,}")
```

### Step 3: Use RAG for Insights

```python
from src.retrieval import ConversationalRAGPipeline

rag = ConversationalRAGPipeline(api_key="YOUR_KEY")

# Ingest data first
rag.ingest_geography("California", years=[2024])
rag.ingest_geography("Texas", years=[2024])

# Query with RAG
response = rag.query(
    "Which state has better employment prospects for job seekers?"
)

print("\nRAG Insights:")
print(response['context'])
print(f"\nBased on {len(response['citations'])} sources")
```

---

## 🔧 Advanced Usage

### Using the MCP Server Client

```python
from src.mcp import CensusMCPClient

# Connect to official Census MCP server
mcp_client = CensusMCPClient(
    mcp_server_path="/path/to/us-census-bureau-data-api-mcp",
    api_key="YOUR_KEY"
)

# List all available datasets
datasets = mcp_client.list_datasets()

for ds in datasets[:5]:
    print(f"{ds.identifier}: {ds.title}")

# Resolve geography with fuzzy matching
matches = mcp_client.resolve_geography_fips("San Francisco")
print(f"\nFound {len(matches)} matches for 'San Francisco'")

# Get 2024 data via MCP
data = mcp_client.get_employment_data_2024("California")
print(f"\nUnemployment: {data['unemployment_rate']}%")
```

### Custom Conversation Management

```python
from src.retrieval import ConversationalRAGPipeline

rag = ConversationalRAGPipeline(enable_memory=True, api_key="YOUR_KEY")

# Create multiple conversations
conv1 = rag.start_conversation()  # For California analysis
conv2 = rag.start_conversation()  # For Texas analysis

# Each maintains separate context
rag.chat("Tell me about California employment", conv1)
rag.chat("Tell me about Texas employment", conv2)

# View all conversations
conversations = rag.list_conversations()
print(f"Active conversations: {len(conversations)}")

# Clear when done
rag.clear_conversation(conv1)
```

---

## 📊 Data Years Available

- **2024 (Latest)**: ACS 1-year estimates (released Sep 2025)
- **2023**: ACS 1-year and 5-year estimates
- **2022**: ACS 1-year and 5-year estimates
- **2021**: ACS 1-year and 5-year estimates
- **2020**: ACS 5-year estimates

**Recommendation**: Use 2024 ACS 1-year for most current data.

---

## 🐛 Troubleshooting

### "No module named 'diskcache'"
```bash
pip install -e .
```

### "Could not resolve geography"
Check spelling - geography names must match Census naming:
- ✅ "California", "New York", "North Carolina"
- ❌ "CA", "NY", "NC"

### "Census API key invalid"
- Verify key at: https://api.census.gov/data/key_signup.html
- Check `.env` file format: `CENSUS_API_KEY=abc123...`
- API works without key (rate-limited to 500 calls/day)

### Streamlit won't start
```bash
# Install web dependencies
pip install -e ".[web]"

# Or manually
pip install streamlit pandas plotly altair
```

---

## 📚 Next Steps

1. **Explore Examples**: Check `examples/basic_usage.py`
2. **Read Features**: See `FEATURES.md` for all capabilities
3. **Run Tests**: `pytest tests/`
4. **Customize**: Modify `app_enhanced.py` for your needs

---

## 💡 Tips

- **Use Caching**: The client caches responses automatically
- **Batch Queries**: Compare multiple states in one call
- **Save Citations**: Always track sources for credibility
- **Use 2024 Data**: Most current employment statistics
- **Try Chat**: Conversational interface is more intuitive

---

## 🤝 Need Help?

- **Issues**: https://github.com/anthropics/claude-code/issues
- **Census API Docs**: https://www.census.gov/data/developers/data-sets.html
- **ACS Documentation**: https://www.census.gov/programs-surveys/acs/

---

**Happy Analyzing! 📊**
