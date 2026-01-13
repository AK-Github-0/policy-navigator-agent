# Installation & Setup Guide

## Quick Start (Automated)

The easiest way to set up the project is using the provided setup script:

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

This script will:
1. Check Python version (3.8+)
2. Create virtual environment
3. Install all dependencies
4. Setup environment variables
5. Optionally download datasets
6. Optionally build vector index

## Manual Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 2GB free disk space (for vector database)
- Internet connection (for API calls)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd "aiXplain Certification Project"
```

### Step 2: Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

This installs:
- `requests` - HTTP requests for APIs
- `loguru` - Advanced logging
- `chromadb` - Vector database
- `sentence-transformers` - Embedding models
- `streamlit` - Web interface
- `python-dotenv` - Environment configuration
- `numpy` - Numerical computing
- `scikit-learn` - Machine learning utilities
- `pandas` - Data processing

### Step 4: Setup Environment Variables

Copy the environment template:
```bash
cp env_example.sh .env
```

Edit `.env` and add your API keys:

```bash
# Open in your editor
nano .env  # or vim, VSCode, etc.
```

Required API keys:
1. **aiXplain SDK**
   - Get from: https://www.aixplain.com
   - Required: `AIXPLAIN_API_KEY`, `AIXPLAIN_TEAM_ID`

2. **Federal Register API** (Optional)
   - Get from: https://www.federalregister.gov/documents/developers
   - No key required but can register for higher rate limits

3. **CourtListener API** (Optional)
   - Get from: https://www.courtlistener.com/api/
   - Requires: `COURTLISTENER_API_KEY` (token)
   - Free account includes 10k requests/hour

4. **Slack Webhooks** (Optional)
   - Get from: https://api.slack.com/messaging/webhooks
   - Only needed for Slack notifications

### Step 5: Create Data Directories

```bash
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/vector_store
mkdir -p logs
```

### Step 6: Download Policy Datasets

```bash
python download_datasets_script.py
```

This will:
- Download policy documents from Federal Register API
- Create sample policy documents for testing
- Save to `data/raw/`

Takes 1-5 minutes depending on network speed.

### Step 7: Build Vector Index

```bash
python create_index_script.py
```

This will:
- Load documents from `data/raw/`
- Split into chunks (512 tokens, 50 overlap)
- Generate embeddings using Sentence-Transformers
- Store in ChromaDB vector database

Takes 2-10 minutes depending on number of documents.

### Step 8: Verify Installation

Test the installation:

```python
# In Python shell
from main import PolicyNavigator

# Initialize
navigator = PolicyNavigator()

# Test query
response = navigator.query("What are recent environmental policies?")
print(response['answer'])
```

## Running the Application

### Web Interface (Streamlit)

```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Start Streamlit
streamlit run streamlit_app.py
```

Visit `http://localhost:8501` in your browser

### Python API

```python
from main import PolicyNavigator

# Initialize
navigator = PolicyNavigator()

# Query
response = navigator.query("What are the GDPR requirements?")

# Check policy status
status = navigator.check_policy_status("Executive Order 14008")

# Search case law
cases = navigator.search_cases("data privacy")

# Get statistics
stats = navigator.get_stats()
print(f"Documents: {stats['vector_db']['total_documents']}")
```

### Command Line Testing

```bash
# Test individual agents
python test_agents_file.py
```

## Troubleshooting

### Virtual Environment Issues

**Problem**: "venv not found" after activation
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Problem**: Wrong Python version
```bash
# Check Python version
python --version

# Use specific Python 3 version
python3 -m venv venv
source venv/bin/activate
```

### Dependency Installation Issues

**Problem**: "pip: command not found"
```bash
# Install pip first
python -m ensurepip --upgrade
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Problem**: Permission denied on macOS/Linux
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

### API Configuration Issues

**Problem**: "API key not found" error
```bash
# Verify .env file exists
ls -la .env

# Check if variables are loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('AIXPLAIN_API_KEY'))"
```

**Problem**: "API rate limit exceeded"
```python
# Add delays between requests
import time

for query in queries:
    response = navigator.query(query)
    time.sleep(2)  # Wait 2 seconds between requests
```

### Vector Database Issues

**Problem**: "ChromaDB connection failed"
```bash
# Clear and rebuild vector store
rm -rf data/vector_store
python create_index_script.py
```

**Problem**: "Embedding model not found"
```bash
# Pre-download model manually
python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2')"
```

### Streamlit Issues

**Problem**: "Module not found" when running Streamlit
```bash
# Verify you're in correct directory
pwd  # Should be in project root

# Verify virtual environment is activated
which python  # Should show venv directory

# Reinstall Streamlit
pip uninstall streamlit -y
pip install streamlit
```

**Problem**: "Port 8501 already in use"
```bash
# Use different port
streamlit run streamlit_app.py --server.port 8502

# Or kill existing process
lsof -i :8501
kill -9 <PID>
```

## Testing Installation

### Unit Tests

```bash
python test_agents_file.py
```

### Integration Test

```python
# test_installation.py
from main import PolicyNavigator
from agents.retrieval_agent import RetrievalAgent
from agents.api_agent import APIAgent
from agents.action_agent import ActionAgent
from agents.synthesizer_agent import SynthesizerAgent
from agents.orchestrator_agent import OrchestratorAgent
from utils.utils_config import Config

# Test imports
print("✅ All modules imported successfully")

# Test config
config = Config()
print(f"✅ Config loaded: {config}")

# Test agents initialization
try:
    navigator = PolicyNavigator()
    print("✅ PolicyNavigator initialized")
    
    # Test vector store stats
    stats = navigator.get_stats()
    print(f"✅ Vector DB: {stats['vector_db']['total_documents']} documents")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
```

Run test:
```bash
python test_installation.py
```

## Next Steps After Installation

1. **Explore API Documentation**
   - Federal Register: https://www.federalregister.gov/documents/developers
   - CourtListener: https://www.courtlistener.com/api/
   - aiXplain: https://docs.aixplain.com

2. **Configure Notifications**
   - Setup Slack webhook for policy alerts
   - Configure email notifications

3. **Customize Vector Store**
   - Add custom policy documents to `data/raw/`
   - Rebuild index with `python create_index_script.py`

4. **Deploy Application**
   - Deploy Streamlit app to cloud (Streamlit Cloud, Heroku, AWS)
   - Setup CI/CD pipeline
   - Configure logging and monitoring

## System Requirements

### Minimum
- CPU: 2+ cores
- RAM: 4GB
- Disk: 2GB free space
- Network: Internet connection

### Recommended
- CPU: 4+ cores
- RAM: 8GB
- Disk: 10GB free space
- GPU: Optional (for faster embeddings)

### Network
- Outbound HTTPS for API calls
- No firewall blocking API endpoints

## Support

For issues:
1. Check Troubleshooting section above
2. Review application logs in `logs/`
3. Check README.md for detailed documentation
4. Review requirements.txt for dependency versions
