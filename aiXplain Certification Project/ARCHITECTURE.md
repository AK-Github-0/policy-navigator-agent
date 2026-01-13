# Policy Navigator Architecture

## System Overview

Policy Navigator is a sophisticated multi-agent Retrieval-Augmented Generation (RAG) system designed for intelligent policy navigation and compliance tracking. The system coordinates multiple specialized agents to provide comprehensive policy search, analysis, and monitoring.

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interfaces                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Streamlit   │  │  Python API  │  │   CLI Tools  │      │
│  │   Web UI     │  │  (main.py)   │  │    Scripts   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│          Policy Navigator Orchestrator                       │
│                  (main.py)                                   │
│  • Query coordination  • Pipeline management                │
│  • Agent sequencing   • Response synthesis                  │
└─────────────────────────────────────────────────────────────┘
                    ↓         ↓         ↓
    ┌───────────────┘         │         └──────────────┬──────────────┐
    │                         │                        │              │
    ↓                         ↓                        ↓              ↓
┌─────────────┐      ┌────────────────┐      ┌──────────────┐  ┌──────────────┐
│ Orchestrator│      │  Retrieval     │      │     API      │  │   Action     │
│   Agent     │      │    Agent       │      │    Agent     │  │    Agent     │
│             │      │                │      │              │  │              │
│ • Classify  │      │ • Search       │      │ • Fed Reg    │  │ • Slack      │
│ • Route     │      │ • Add Docs     │      │ • CourtList  │  │ • Calendar   │
│ • Log       │      │ • Delete       │      │ • Recent Doc │  │ • Email      │
└─────────────┘      │ • Stats        │      │ • Mock data  │  │ • Workflows  │
                     └────────────────┘      └──────────────┘  └──────────────┘
                            ↓                      ↓
                     ┌────────────────┐     ┌──────────────┐
                     │ ChromaDB Vector│     │  Government  │
                     │ Database       │     │     APIs     │
                     │                │     │              │
                     │ • Documents    │     │ • Federal    │
                     │ • Embeddings   │     │   Register   │
                     │ • Metadata     │     │ • Court      │
                     │ • Similarity   │     │   Listener   │
                     └────────────────┘     └──────────────┘
                            ↓
                     ┌────────────────┐
                     │Synthesizer Agent│
                     │  (LLM-based)    │
                     │                 │
                     │ • Generate      │
                     │ • Summarize     │
                     │ • Citation      │
                     └────────────────┘
```

## Agent Architecture

### 1. PolicyNavigator (Orchestrator)
**Purpose**: Main coordination and entry point for the system

**Key Methods**:
- `query(text)` - Process user query through full pipeline
- `check_policy_status(policy)` - Check specific policy status
- `search_cases(regulation)` - Search for related cases
- `add_document(id, content, metadata)` - Add to vector store
- `get_stats()` - System statistics

**Responsibilities**:
- Initialize all agents with configuration
- Route queries to appropriate agents
- Manage conversation history
- Synthesize final responses
- Handle errors and logging

### 2. OrchestratorAgent
**Purpose**: Query classification and intelligent routing

**Query Types**:
- `GENERAL_QUERY` - Basic information search
- `POLICY_STATUS` - Check policy/regulation status
- `CASE_LAW_SEARCH` - Find relevant court cases
- `COMPLIANCE_CHECK` - Generate compliance checklists

**Key Methods**:
- `classify_query(text)` - Determine query type
- `route_query(text, type)` - Determine agent sequence
- `should_call_api_agent()` - Check if API needed
- `should_call_action_agent()` - Check if action needed

**Keywords for Classification**:
- Policy Status: "status", "active", "effective", "deadline"
- Case Law: "case", "court", "legal", "ruling"
- Compliance: "comply", "requirement", "mandatory", "audit"

### 3. RetrievalAgent
**Purpose**: Semantic search in vector database

**Technology**:
- **Embedding Model**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Dimensions**: 384-dimensional vectors
- **Database**: ChromaDB with HNSW indexing
- **Similarity**: Cosine distance

**Key Methods**:
- `search(query, top_k=5)` - Semantic similarity search
- `add_document(id, content, metadata)` - Add single document
- `add_documents_batch(documents)` - Batch add (efficient)
- `search_by_metadata(filters)` - Filter-based search
- `get_document(id)` - Retrieve specific document
- `delete_document(id)` - Remove from database
- `get_stats()` - Database statistics

**Features**:
- Full-text semantic search
- Metadata-based filtering
- Batch processing (50-500 docs recommended)
- Cosine similarity for text embeddings
- HNSW approximate nearest neighbor search

### 4. APIAgent
**Purpose**: Query external government APIs

**Supported APIs**:
1. **Federal Register API**
   - Endpoint: `https://www.federalregister.gov/api/v1`
   - Purpose: Policy/executive order search
   - Rate Limit: 1000 req/hour (free)
   - Methods: search, recent_documents

2. **CourtListener API**
   - Endpoint: `https://www.courtlistener.com/api/rest/v3`
   - Purpose: Case law and opinion search
   - Rate Limit: 10000+ req/hour (free)
   - Methods: opinion_search, case_search

**Key Methods**:
- `check_policy_status(policy)` - Query Federal Register
- `search_cases(regulation, limit)` - Search CourtListener
- `get_recent_documents(type, days)` - Fetch recent docs
- `_get_mock_cases()` - Fallback mock data

**Features**:
- Error handling with mock fallbacks
- Automatic retry on network errors
- Response formatting and normalization
- Caching for repeated queries (optional)

### 5. ActionAgent
**Purpose**: Third-party integrations and notifications

**Integrations**:
- **Slack**: Message webhooks for notifications
- **Calendar**: Create reminders (interface for tools)
- **Email**: Send alerts (interface for tools)
- **Workflows**: Trigger external automation (Zapier, Make, etc.)

**Key Methods**:
- `send_slack_notification(message, channel, attachments)` - Send Slack message
- `create_subscription(policy, channel, frequency)` - Policy monitoring
- `send_policy_update(policy, info, channels)` - Update notification
- `create_calendar_reminder(policy, docs, days_before)` - Schedule reminder
- `send_compliance_checklist(policy, requirements)` - Send checklist
- `trigger_workflow(type, data)` - External workflow trigger
- `log_action(action_type, details)` - Audit logging

**Features**:
- Rich message formatting (Slack)
- Scheduled reminders
- Compliance checklist generation
- Audit trail logging
- Multi-channel support

### 6. SynthesizerAgent
**Purpose**: LLM-based response generation and synthesis

**Key Methods**:
- `synthesize_response(query, docs, api_results)` - Generate response
- `format_for_display(response)` - Format for user display

**Features**:
- Multi-source synthesis (docs + APIs)
- Source tracking and citation
- Confidence scoring
- Structured response formatting

**Response Structure**:
```python
{
    'query': str,           # Original query
    'answer': str,          # Generated response
    'sources': List[Dict],  # Source citations
    'confidence': float,    # 0.0-1.0 confidence score
    'metadata': Dict        # Generation metadata
}
```

## Data Flow

### Query Processing Pipeline

```
User Input
    ↓
[1] OrchestratorAgent: Classify query type
    ↓
[2] RetrievalAgent: Semantic search (always)
    ↓
[3] Decision: Should call other agents?
    ├─ YES → [4a] APIAgent: Query external APIs
    │           ↓
    │        [4b] ActionAgent: Trigger actions (if needed)
    │           ↓
    └─ NO → [5] SynthesizerAgent: Generate response
    ↓
[6] Return synthesized response with sources
```

### Document Ingestion Pipeline

```
Policy Document
    ↓
[1] Parse & Chunk (512 tokens, 50 overlap)
    ↓
[2] Extract Metadata
    ├─ Title
    ├─ Source
    ├─ Type
    ├─ Date
    └─ Custom fields
    ↓
[3] Generate Embeddings (Sentence-Transformers)
    ↓
[4] Store in ChromaDB
    ├─ Document ID
    ├─ Text content
    ├─ Embedding vector
    └─ Metadata
    ↓
Indexed & Searchable
```

## Configuration Management

### Config Class (utils_config.py)

**Manages**:
- API credentials
- Directory paths
- Model settings
- Chunking parameters
- Search configuration
- Logging setup

**Load Order**:
1. Default values
2. Environment variables (.env file)
3. Explicit overrides

**Key Configurations**:
```python
# API Keys
aixplain_api_key       # aiXplain SDK
federal_register_key   # Federal Register API
courtlistener_key      # CourtListener API
slack_webhook_url      # Slack notifications

# Paths
data_dir               # Base data directory
raw_data_dir           # Downloaded documents
processed_data_dir     # Processed documents
vector_store_path      # ChromaDB storage
logs_dir               # Application logs

# Models
embedding_model        # Sentence-Transformers
llm_model              # LLM for synthesis
temperature            # Generation temperature
max_tokens             # Max output length

# Processing
chunk_size             # Document chunk size
chunk_overlap          # Chunk overlap
top_k_documents        # Retrieval results count
similarity_threshold   # Minimum similarity score
```

## Error Handling & Fallbacks

### API Failures
- **Federal Register**: Uses mock policy data
- **CourtListener**: Uses mock case data
- **Slack**: Logs error, continues processing
- **All APIs**: Automatic retry with exponential backoff

### Database Failures
- ChromaDB unavailable → Memory-based fallback
- Document not found → Return empty results
- Embedding failure → Skip document, log error

### Processing Errors
- Parsing error → Log and continue
- Chunking error → Skip document
- Search error → Return empty results

## Performance Characteristics

### Search Performance
- **Semantic Search**: 50-200ms for 1000 documents
- **Top-K Retrieval**: O(log n) with HNSW index
- **Batch Operations**: 1000 docs/sec on modern hardware

### Embedding Generation
- **Model Size**: 22.7 MB (all-MiniLM-L6-v2)
- **Speed**: 3000+ sentences/sec on CPU
- **Dimensions**: 384-dimensional vectors

### API Response Times
- **Federal Register**: 500-1500ms
- **CourtListener**: 1000-2000ms
- **Mock Data**: <10ms (instant fallback)

### Storage Requirements
- **ChromaDB**: ~1KB per document (metadata + vector)
- **Vector Dimensions**: 384 × 4 bytes = 1536 bytes per document
- **1000 Documents**: ~2MB total storage

## Scalability Considerations

### Vertical Scaling (Single Machine)
- **Documents**: Up to 1 million (with 16GB+ RAM)
- **QPS**: 100+ queries per second
- **Latency**: <500ms avg response time

### Horizontal Scaling
- Multiple API agent instances (load balanced)
- Distributed ChromaDB (Chroma Cloud)
- Multiple Streamlit app servers
- Shared vector store (network accessible)

### Optimization Techniques
- Batch document processing
- Vector search caching
- API response caching
- Metadata pre-filtering

## Security Architecture

### API Key Management
- Stored in .env (not in code)
- Loaded via python-dotenv
- Never logged or transmitted insecurely
- Environment-specific configurations

### Data Privacy
- No user data stored by default
- Documents stored locally
- Optional anonymization
- Audit logging of all operations

### API Rate Limiting
- Exponential backoff retry
- Request throttling
- Rate limit detection
- Queue management

## Deployment Architecture

### Development
- Single machine setup
- SQLite/ChromaDB for vector store
- Local API key configuration

### Production
- Containerized with Docker
- Load-balanced Streamlit instances
- Cloud-based ChromaDB (Chroma Cloud)
- External vector store (e.g., Pinecone)
- Database (PostgreSQL) for policies
- Monitoring and alerting (DataDog, New Relic)
- Log aggregation (ELK stack)

## Integration Points

### External Services
- **aiXplain SDK** - LLM orchestration
- **Federal Register API** - Policy data
- **CourtListener API** - Case law data
- **Slack API** - Notifications
- **Calendar API** - Reminders (via calendar service)
- **Email Service** - Alert delivery

### Data Sources
- Federal policy documents
- Court opinions and cases
- Regulatory frameworks
- Compliance standards
- Custom policy repositories

## Monitoring & Observability

### Logging
- All agent operations logged
- Request/response logging
- Error tracking and alerting
- Audit trail for compliance
- Log files in `logs/` directory

### Metrics
- Query latency
- API response times
- Vector search performance
- Cache hit rates
- Error rates

### Debugging
- Detailed error messages
- Stack traces in logs
- Query execution tracing
- Agent communication logging
