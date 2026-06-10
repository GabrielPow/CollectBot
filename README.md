<div style="text-align: right;">
  <a href="README.md">English</a> | <a href="README.pt.md">Português</a>
</div>

# CollectBot - AI Data Collection & Processing Pipeline

CollectBot is an intelligent data collection and processing system powered by AI agents. It automates the process of extracting, qualifying, and formatting structured data from CSV sources using a multi-agent architecture built on Google's Gemini API.

## System Architecture Overview

CollectBot employs a **distributed multi-agent pipeline architecture** where specialized AI agents work together in a coordinated workflow to transform raw data into refined, filtered, and formatted outputs.

```
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT WEB INTERFACE                       │
│  (Upload CSV → Define Criteria → Launch Pipeline → Download)    │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │   ORCHESTRATOR (Sync)    │
                    │  Coordinates 3-4 Agents  │
                    └──────────┬───────────────┘
                               │
        ┌──────────────────────┼──────────────────────┬──────────────┐
        ▼                      ▼                      ▼              ▼
    ┌────────────┐         ┌──────────┐         ┌──────────┐   ┌──────────┐
    │ COLLECTOR  │         │QUALIFIER │         │FORMATTER │   │CONVERTER │
    │   AGENT    │────────►│  AGENT   │────────►│  AGENT   │──►│(JSON→CSV)│
    │(Extract)   │         │(Filter)  │         │(Optional)│   │(System)  │
    └────────────┘         └──────────┘         └──────────┘   └──────────┘
        │                       │                    │              │
        └───────────────────────┴────────────────────┴──────────────┘
                                 │
                    ┌────────────────────────────┐
                    │  GEMINI 2.5 FLASH API      │
                    │ (Remote LLM Processing)    │
                    └────────────────────────────┘
```

## Architecture Components

### 1. **Frontend Layer** (`src/app.py`)
- **Framework**: Streamlit
- **Responsibility**: User interaction and visualization
- **Key Features**:
  - CSV file upload with preview
  - Three-field configuration panel:
    1. **Collection Task**: Define what data to extract
    2. **Qualification Criteria**: Set filtering rules
    3. **Formatting Suggestions**: Optional output formatting
  - Real-time pipeline execution feedback
  - Downloadable CSV output with formatted results

### 2. **Orchestration Layer** (`src/agents/agents.py`)
Implements three specialized agent classes:

#### **Collector Agent**
- **Role**: Extracts relevant raw data from the source CSV file
- **Input**: User task description + CSV file path
- **Process**:
  - Uploads CSV to Gemini Files API
  - Sends extraction task to Gemini with file context
  - Returns raw, unfiltered data rows
- **Output**: Raw data string

#### **Qualifier Agent**
- **Role**: Filters and scores data against user-defined criteria
- **Input**: Raw data + qualification criteria
- **Process**:
  - Analyzes each record against criteria rules
  - Assigns relevance scores when applicable
  - Structures output as JSON array (enforced via `response_mime_type`)
- **Output**: Valid JSON array of qualified records

#### **Formatter Agent** (Optional)
- **Role**: Applies stylistic transformations to data structure
- **Input**: Qualified JSON + formatting suggestions
- **Process**:
  - Renames columns per user request
  - Modifies field values (e.g., appending units)
  - Transforms text formatting
- **Output**: Reformatted JSON array
- **Status**: Skipped if no suggestions provided

#### **Orchestrator Class**
- **Role**: Coordinates the sequential execution of all agents
- **Execution Model**: Async/await pattern for non-blocking I/O
- **Pipeline Flow**:
  1. Collector extracts data
  2. Qualifier filters results
  3. Formatter refines output (if enabled)
  4. System converts final JSON to CSV
- **Output**: Final CSV string ready for download

### 3. **AI Model Layer** (`src/agents/ai_model.py`)
- **LLM Provider**: Google Gemini 2.5 Flash
- **Integration Method**: Google `genai` Python SDK
- **Key Functions**:

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `upload_csv()` | Uploads CSV to Gemini Files API | File path | File object |
| `collector_fetch_from_file()` | Extracts data using uploaded file | Task, file object | Raw data string |
| `qualifier_analyze()` | Filters data with JSON schema enforcement | Raw data, criteria | JSON array |
| `formatter_interpret()` | Applies formatting to JSON | JSON, suggestions | Refined JSON |
| `json_to_csv_dynamic()` | Converts JSON to CSV format | JSON string | CSV string |
| `call_gemini()` | Generic API wrapper | Prompt, system instruction | Response text |

### 4. **Data Pipeline** 
- **Input Format**: CSV files (uploaded via Streamlit)
- **Processing Flow**:
  ```
  CSV File → [Upload to Gemini] → Raw Data Extraction 
  → Criteria Filtering (JSON) → Optional Formatting 
  → CSV Conversion → Download
  ```
- **Output Format**: CSV file with qualified and formatted records

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Web UI** | Streamlit | Latest |
| **LLM Backend** | Google Gemini 2.5 Flash | API |
| **Python Runtime** | Python | 3.8+ |
| **API Client** | google-genai | Latest |
| **Data Processing** | Pandas | Latest |
| **Environment Config** | python-dotenv | Latest |
| **Async Runtime** | asyncio | Built-in |

## Execution Flow Diagram

```
User Action              System Response
──────────────────────────────────────
    │
    ├─► Upload CSV ─────────────────► Streamlit saves temp file
    │
    ├─► Define Task & Criteria ─────► Configuration stored in UI state
    │
    ├─► Click "Run Pipeline" ──────► Orchestrator.run_pipeline() starts
    │                                  ├─► Collector uploads CSV to Gemini
    │                                  ├─► Collector extracts relevant rows
    │                                  ├─► Qualifier filters with criteria
    │                                  ├─► Qualifier returns JSON array
    │                                  ├─► Formatter (if enabled) refines JSON
    │                                  └─► System converts JSON to CSV
    │
    └─► Download Results ──────────► User receives structured CSV file
```

## Key Design Patterns

1. **Asynchronous Processing**: Uses `asyncio` to prevent blocking during I/O-heavy Gemini API calls
2. **Agent Abstraction**: Each agent encapsulates a single responsibility (SRP)
3. **JSON Schema Enforcement**: Gemini API `response_mime_type` ensures structured JSON output
4. **File API Integration**: Leverages Gemini Files API for efficient CSV handling
5. **Stateful UI**: Streamlit session state persists orchestrator across reruns
6. **Graceful Degradation**: Formatter skips silently if no suggestions provided

## Data Transformation Example

```
Input CSV:
country,renewable_energy_%,status
Norway,98.5,active
Germany,46.2,active
India,12.1,developing

(User Task: "Find countries shifting to low-carbon options")
(User Criteria: "Renewable energy share > 20% OR notable increases")

↓ [Collector extracts] ↓ [Qualifier filters] ↓

Output JSON:
[
  {"country": "Norway", "renewable_energy_%": 98.5, "status": "active", "relevance": "high"},
  {"country": "Germany", "renewable_energy_%": 46.2, "status": "active", "relevance": "high"}
]

↓ [Convert to CSV] ↓

Output CSV:
country,renewable_energy_%,status,relevance
Norway,98.5,active,high
Germany,46.2,active,high
```

## Environment Configuration

The system requires a Gemini API key stored in `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

## Future Enhancements

- Multi-file batch processing
- Custom agent type registration
- Advanced scoring algorithms
- Caching layer for repeated criteria
- Export format options (JSON, Excel, Parquet)
- Agent performance analytics
