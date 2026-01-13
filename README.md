# Policy Navigator Agent 🏛️

A sophisticated multi-agent system for intelligent policy navigation, compliance tracking, and regulatory analysis using Retrieval-Augmented Generation (RAG) with the aiXplain SDK.

## Overview

Policy Navigator is an AI-powered assistant that helps users navigate complex regulatory landscapes by:
- **Semantic Search**: Find relevant policies and regulations using vector embeddings
- **Policy Status Tracking**: Check the current status of policies and executive orders
- **Case Law Research**: Search for relevant court cases and legal precedents
- **Compliance Management**: Generate compliance checklists and track requirements
- **Multi-Channel Notifications**: Send updates via Slack, email, and calendar reminders

## Architecture

### Core Components

```
Policy Navigator (Orchestrator)
├── RetrievalAgent (Vector DB & Semantic Search)
├── APIAgent (Federal Register & CourtListener)
├── ActionAgent (Slack, Email, Calendar, Workflows)
├── SynthesizerAgent (LLM-based Response Generation)
└── OrchestratorAgent (Query Classification & Routing)
```

### Technology Stack

- **Vector Database**: ChromaDB with Cosine similarity
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2, 384-dim)
- **API Integrations**: 
  - Federal Register API (policy status)
  - CourtListener API (case law search)
  - Slack API (notifications)
- **Web Interface**: Streamlit
- **Logging**: Loguru
- **Language**: Python 3.8+

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd "aiXplain Certification Project"
```

### 2. Create Virtual Environment (recommended)
Use a dedicated virtual environment for this project to avoid dependency conflicts.

macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies (inside `venv`)
After activating the venv, install pinned dependencies:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Notes:
- If you prefer to use the system Python, install packages into a virtualenv or container.
- `requirements.txt` includes test and runtime dependencies (`pytest`, `streamlit`, `loguru`, etc.).

### 4. Environment Configuration
Copy the example environment file and fill in your API keys:
```bash
cp env_example.sh .env
```

Edit `.env` and add your API keys:
```env
# aiXplain SDK
AIXPLAIN_API_KEY=your_aixplain_api_key
AIXPLAIN_TEAM_ID=your_team_id

# Government APIs
FEDERAL_REGISTER_API_KEY=your_federal_register_key
COURTLISTENER_API_KEY=your_courtlistener_token

# Notifications
SLACK_WEBHOOK_URL=your_slack_webhook

# Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=gpt-3.5-turbo
TEMPERATURE=0.7
MAX_TOKENS=2000

# Vector Database
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K_DOCUMENTS=5
SIMILARITY_THRESHOLD=0.3

# Logging
LOG_LEVEL=INFO
```

## Getting Started

### 1. Download Policy Datasets
```bash
python download_datasets_script.py
```

This script downloads policy documents from:
- Federal Register API
- Government policy repositories
- Saves to `data/raw/`

### 2. Create Vector Index
```bash
python create_index_script.py
```

This script:
- Loads policy documents from `data/raw/`
- Splits documents into chunks (512 tokens, 50 overlap)
- Generates embeddings using Sentence-Transformers
- Stores in ChromaDB at `data/vector_store/`

### Run Web Interface (Streamlit)
Start the Streamlit UI after creating and activating the venv and installing dependencies:

```bash
source venv/bin/activate        # macOS/Linux
# on Windows: .\venv\Scripts\Activate.ps1 (PowerShell) or venv\Scripts\activate (cmd)
streamlit run streamlit_app.py --server.port 8501
```

Then visit `http://localhost:8501` in your browser.

If `streamlit` fails to import, make sure you're using the same Python interpreter that has the venv activated. If you get `ModuleNotFoundError: No module named 'loguru'`, the project includes a lightweight fallback (`loguru.py`) so the app can run even if the `loguru` package isn't installed. Installing the real `loguru` in the venv is recommended:

```bash
pip install loguru
```

### 4. Run Tests
```bash
python test_agents_file.py
```

## Usage Examples

### Web Interface (Streamlit)

Access three query modes:

#### 1. General Query
Ask any question about policies and regulations
```
"What are the recent changes to environmental protection regulations?"
```

#### 2. Policy Status Check
Check the status of a specific policy
```
"What is the current status of Executive Order 14008?"
```

#### 3. Case Law Search
Find relevant court cases
```
"Find cases related to data privacy regulations"
```

### Python API

```python
from main import PolicyNavigator

# Initialize
navigator = PolicyNavigator()

# General query
response = navigator.query("What are recent environmental policies?")
print(response['answer'])

# Check policy status
status = navigator.check_policy_status("Executive Order 14008")
print(f"Status: {status['api_results']['status']}")

# Search case law
cases = navigator.search_cases("GDPR compliance")
for case in cases['sources']:
    print(f"- {case['title']}")

# Add documents to vector store
navigator.add_document(
    document_id="doc_123",
    content="Policy text here...",
    metadata={"source": "Federal Register", "year": 2024}
)

# Get system statistics
stats = navigator.get_stats()
print(f"Total documents: {stats['vector_db']['total_documents']}")
```

## Project Structure

```
aiXplain Certification Project/
├── agents/
│   ├── __init__.py
│   ├── action_agent.py          # Slack, Email, Calendar integration
│   ├── api_agent.py             # Federal Register & CourtListener APIs
│   ├── retrieval_agent.py       # Vector DB & semantic search
│   ├── synthesizer_agent.py     # LLM-based response synthesis
│   └── orchestrator_agent.py    # Query routing & classification
├── utils/
│   ├── __init__.py
│   └── utils_config.py          # Configuration management
├── tools/
│   └── __init__.py
├── logs/                         # Application logs
├── data/
│   ├── raw/                      # Downloaded policy documents
│   ├── processed/                # Processed documents
│   └── vector_store/             # ChromaDB vector storage
├── main.py                       # Main PolicyNavigator orchestrator
├── streamlit_app.py              # Web interface
├── download_datasets_script.py   # Download policy documents
├── create_index_script.py        # Build vector index
├── test_agents_file.py           # Unit tests
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (create from env_example.sh)
├── env_example.sh                # Environment template
└── README.md                     # This file
```

## Agent Details

### RetrievalAgent
Manages vector database operations and semantic search.

**Key Methods:**
- `search(query, top_k=5)` - Semantic search
- `add_document(id, content, metadata)` - Add single document
- `add_documents_batch(documents)` - Batch add documents
- `search_by_metadata(filters)` - Filter-based search
- `get_stats()` - Database statistics

**Configuration:**
- Embedding Model: Sentence-Transformers (all-MiniLM-L6-v2)
- Vector Dimensions: 384
- Similarity Metric: Cosine
- Storage: ChromaDB

### APIAgent
Integrates with external government APIs.

**Key Methods:**
- `check_policy_status(policy)` - Query Federal Register API
- `search_cases(regulation, limit=5)` - Query CourtListener API
- `get_recent_documents(type, days=30)` - Fetch recent documents

**Features:**
- Automatic fallback to mock data if APIs unavailable
- Error handling and retry logic
- Response formatting and parsing

### ActionAgent
Handles third-party integrations and notifications.

**Key Methods:**
- `send_slack_notification(message, channel)` - Slack messages
- `create_subscription(policy, channel, frequency)` - Policy subscriptions
- `send_policy_update(policy, info, channels)` - Update notifications
- `create_calendar_reminder(policy, documents, days_before)` - Calendar events
- `send_compliance_checklist(policy, requirements)` - Compliance checklists
- `trigger_workflow(type, data)` - External workflow triggers

### SynthesizerAgent
Synthesizes comprehensive responses from multiple data sources.

**Key Methods:**
- `synthesize_response(query, docs, api_results)` - Generate response
- `format_for_display(response)` - Format for user display

**Features:**
- Multi-source synthesis (documents + APIs)
- Source tracking and citation
- Confidence scoring

### OrchestratorAgent
Routes queries to appropriate agents.

**Query Types:**
- `GENERAL_QUERY` - Use retrieval agent only
- `POLICY_STATUS` - Use retrieval + API agent
- `CASE_LAW_SEARCH` - Use retrieval + API agent
- `COMPLIANCE_CHECK` - Use retrieval + action agent

## Configuration

### Environment Variables

#### API Keys (Required)
```env
AIXPLAIN_API_KEY          # Your aiXplain API key
AIXPLAIN_TEAM_ID          # Your team ID
FEDERAL_REGISTER_API_KEY  # Federal Register API key
COURTLISTENER_API_KEY     # CourtListener API token
SLACK_WEBHOOK_URL         # Slack webhook for notifications
```

#### Model Settings
```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # Embedding model
LLM_MODEL=gpt-3.5-turbo                                 # LLM model
TEMPERATURE=0.7                                          # Generation temperature
MAX_TOKENS=2000                                          # Max output tokens
```

#### Chunking
```env
CHUNK_SIZE=512      # Document chunk size (tokens)
CHUNK_OVERLAP=50    # Chunk overlap (tokens)
```

#### Search
```env
TOP_K_DOCUMENTS=5           # Number of retrieved documents
SIMILARITY_THRESHOLD=0.3    # Minimum similarity score
```

#### Logging
```env
LOG_LEVEL=INFO  # Logging level (DEBUG, INFO, WARNING, ERROR)
```

## API Integration

### Federal Register API
- **Endpoint**: `https://www.federalregister.gov/api/v1`
- **Features**: Policy search, document retrieval, status checking
- **Rate Limit**: 1000 requests/hour (free tier)
- **Documentation**: https://www.federalregister.gov/documents/developers

### CourtListener API
- **Endpoint**: `https://www.courtlistener.com/api/rest/v3`
- **Features**: Case law search, opinion retrieval
- **Authentication**: Token-based
- **Documentation**: https://www.courtlistener.com/api/

### Slack API
- **Webhook Setup**: Create incoming webhook in Slack app settings
- **Features**: Send messages, attachments, notifications
- **Documentation**: https://api.slack.com/messaging

## Logging

All components use Loguru for structured logging:

```
logs/
└── policy_navigator.log
```

Log levels:
- `DEBUG` - Detailed debugging information
- `INFO` - General information
- `WARNING` - Warning messages
- `ERROR` - Error messages

View logs:
```bash
tail -f logs/policy_navigator.log
```

## Performance Considerations

### Vector Database
- **Embedding Dimension**: 384 (all-MiniLM-L6-v2)
- **Similarity Metric**: Cosine (optimal for text embeddings)
- **Index Type**: HNSW (approximate nearest neighbor)
- **Batch Size**: Recommended 100-500 documents

### Search Optimization
- Default `top_k=5` for balance between relevance and speed
- Adjust `similarity_threshold` to filter low-relevance results
- Use metadata filters for faster narrower searches

### Scaling
For large document collections (>100k):
- Consider distributed ChromaDB setup
- Implement document pagination
- Use metadata pre-filtering

## Troubleshooting

### ChromaDB Connection Issues
```bash
# Clear vector store and rebuild
rm -rf data/vector_store/
python create_index_script.py
```

### API Rate Limits
- Federal Register: 1000 req/hour → implement caching
- CourtListener: Check token limits → use mock fallback
- Slack: 60 msg/minute per webhook → queue messages

### Missing Embeddings
```python
# Verify embedding model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
```

### Streamlit Session Issues
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/cache
streamlit run streamlit_app.py --logger.level=debug
```

## Testing

Run unit tests:
```bash
python test_agents_file.py
```

Test individual agents:
```python
from agents.retrieval_agent import RetrievalAgent
from utils.utils_config import Config

config = Config()
retrieval = RetrievalAgent(config)

# Add test document
retrieval.add_document(
    "test_doc",
    "Sample policy content for testing",
    {"source": "test"}
)

# Search
results = retrieval.search("policy content")
print(f"Found {len(results)} results")
```

## Development

### Adding New Agents
1. Create new agent class in `agents/`
2. Inherit base methods (logging, config access)
3. Implement `__init__` and core methods
4. Add to `PolicyNavigator.__init__`
5. Update `OrchestratorAgent` routing

### Adding API Integrations
1. Implement in `APIAgent.search_cases()` or create new method
2. Add error handling and mock fallback
3. Update `requirements.txt` if new dependencies needed
4. Document API setup in README

### Custom Vector Database
1. Implement interface matching `RetrievalAgent`
2. Update initialization in `PolicyNavigator`
3. Test with same document corpus

## Contributing

1. Create feature branch
2. Make changes and test
3. Ensure all tests pass
4. Submit pull request

## License

[Specify your license here]

## Support

For issues and questions:
1. Check README troubleshooting section
2. Review agent logs in `logs/`
3. Test with mock data (APIs disabled)
4. Review aiXplain SDK documentation

## References

- **aiXplain Documentation**: https://docs.aixplain.com
- **ChromaDB**: https://docs.trychroma.com
- **Sentence-Transformers**: https://www.sbert.net
- **Streamlit**: https://docs.streamlit.io
- **Federal Register API**: https://www.federalregister.gov/documents/developers
- **CourtListener API**: https://www.courtlistener.com/api/

## Changelog

### v1.0.0 (Initial Release)
- Multi-agent RAG system with 5 core agents
- Vector database integration (ChromaDB)
- Federal Register and CourtListener API integration
- Slack and calendar notifications
- Streamlit web interface
- Comprehensive logging and error handling
- Full test coverage
