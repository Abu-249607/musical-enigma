# Census Employment RAG Tool

A RAG-powered tool for accessing U.S. Census Bureau employment data with citation-backed insights. Built to integrate with the [official Census Bureau MCP server](https://github.com/uscensusbureau/us-census-bureau-data-api-mcp).

## Features

- **Citation-backed responses**: Every data point includes traceable Census Bureau citations
- **RAG retrieval pipeline**: Semantic search over employment data for accurate answers
- **Caching layer**: Reduces API calls and improves response times
- **Multi-audience support**: Tailored insights for recruiters and students
- **Multiple LLM providers**: Works with Anthropic Claude and OpenAI

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Census Employment Assistant                       │
├─────────────────────────────────────────────────────────────────────┤
│  User Query → Hybrid Search → RAG Context → LLM → Cited Response    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                        RAG Pipeline                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Census MCP   │  │ Preprocessor │  │ Vector Store (ChromaDB)  │  │
│  │ Client       │→ │ & Chunker    │→ │ with Citations           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│              Census Bureau MCP Server (Official)                     │
│  Tools: list-datasets, fetch-aggregate-data, resolve-geography-fips │
│  https://github.com/uscensusbureau/us-census-bureau-data-api-mcp    │
└─────────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone repository
git clone <repository-url>
cd census-employment-rag

# Install dependencies
pip install -e .

# For LLM support
pip install -e ".[llm]"

# For development
pip install -e ".[dev]"
```

## Configuration

1. Get a Census Bureau API key from [api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)

2. Create a `.env` file:

```env
CENSUS_API_KEY=your_census_api_key
ANTHROPIC_API_KEY=your_anthropic_key  # Optional
OPENAI_API_KEY=your_openai_key        # Optional
```

## Quick Start

### Basic Usage

```python
from src.llm import CensusEmploymentAssistant

# Initialize assistant
assistant = CensusEmploymentAssistant(
    census_api_key="your_census_key",
    llm_provider_name="anthropic",
    llm_api_key="your_anthropic_key",
)

# Pre-load data for states of interest
assistant.setup_geographies(["California", "Texas", "New York"])

# Ask questions
result = assistant.ask("What is the unemployment rate in California?")
print(result["answer"])
print(result["citations"])
```

### For Recruiters

```python
# Get recruiting-focused insights
insights = assistant.get_recruiter_insights(
    geography="California",
    industry="Technology",
    year=2022,
)
print(insights["answer"])

# Compare job markets
comparison = assistant.compare_markets(
    geographies=["California", "Texas", "Washington"],
    focus="industry",
)
print(comparison["analysis"])
```

### For Students

```python
# Get career-focused information
career_info = assistant.get_student_career_info(
    geography="New York",
    field_of_interest="Healthcare",
)
print(career_info["answer"])
```

### Direct Data Access (No LLM)

```python
from src.census_client import CensusMCPClient

client = CensusMCPClient(api_key="your_census_key")

# Get employment data with citation
record, citation = client.get_employment_data("California", year=2022)

print(f"Unemployment Rate: {record.unemployment_rate}%")
print(f"Source: {citation.to_reference_string()}")
```

## Key Components

### Citation System

Every data point is tracked with full provenance:

```python
Citation(
    citation_id="ACS-ACS5-2022-001",
    dataset_name="acs/acs5",
    dataset_year=2022,
    variables=["B23025_001E", "B23025_004E", ...],
    geography="state",
    geography_name="California",
    api_endpoint="https://api.census.gov/data/2022/acs/acs5",
)
```

### Supported Datasets

| Dataset | Description | Use Case |
|---------|-------------|----------|
| ACS 5-Year (acs/acs5) | Detailed estimates, smaller geographies | County/city analysis |
| ACS 1-Year (acs/acs1) | More current, larger areas only | State-level trends |
| Decennial Census | Complete count, every 10 years | Historical comparisons |

### Employment Variables

The tool focuses on key employment metrics from ACS Table B23025:
- Total population 16+
- Labor force participation
- Employment/unemployment counts
- Employment rates

And industry breakdown from Table C24050:
- Employment by NAICS industry sector

## Census Bureau MCP Server Integration

This tool is designed to work with the official Census Bureau MCP server. To set up the MCP server:

1. Clone the MCP server repository:
```bash
git clone https://github.com/uscensusbureau/us-census-bureau-data-api-mcp
```

2. Follow the setup instructions in their README

3. Configure your AI assistant to use the MCP server

## Project Structure

```
census-employment-rag/
├── src/
│   ├── census_client/     # Census API client with caching
│   ├── preprocessing/     # Data normalization and chunking
│   ├── retrieval/         # Vector store and RAG pipeline
│   ├── llm/               # LLM providers and assistant
│   ├── models/            # Pydantic data models
│   └── config/            # Settings management
├── tests/                 # Test suite
├── data/
│   ├── cache/             # API response cache
│   └── vectordb/          # ChromaDB storage
└── examples/              # Usage examples
```

## Best Practices

### Ensuring Accuracy

1. **Always check citations**: Every response includes citation IDs linking to specific Census datasets
2. **Note data vintage**: ACS data has release schedules; check the year in citations
3. **Understand estimates**: ACS data are estimates with margins of error
4. **Verify with source**: Use the census_api_url in citations to view data directly

### Performance Tips

1. **Pre-load geographies**: Use `setup_geographies()` before querying
2. **Enable caching**: Cache is on by default, significantly reducing API calls
3. **Batch requests**: Use `compare_markets()` for multi-geography queries

## License

This project is designed to work with public Census Bureau data. See the [Census Bureau Data API Terms of Service](https://www.census.gov/data/developers/about/terms-of-service.html).

## Contributing

Contributions welcome! Please ensure:
- All data responses include proper citations
- Tests pass with `pytest`
- Code formatted with `ruff`
