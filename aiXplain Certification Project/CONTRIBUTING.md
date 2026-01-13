# Contributing to Policy Navigator

Thank you for your interest in contributing to Policy Navigator! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Report issues professionally
- Follow Python best practices

## Getting Started

### 1. Fork & Clone
```bash
git clone https://github.com/yourusername/policy-navigator.git
cd policy-navigator
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
git checkout -b fix/bug-description
```

### 3. Setup Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy

# Setup pre-commit hooks
pip install pre-commit
pre-commit install
```

## Development Workflow

### Code Style

Follow PEP 8 with the following conventions:

```python
# Type hints required
def search_documents(
    query: str,
    top_k: int = 5,
    metadata_filter: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """
    Search documents by semantic similarity.
    
    Args:
        query: Search query text
        top_k: Number of results to return
        metadata_filter: Optional metadata filters
        
    Returns:
        List of matching documents with scores
        
    Raises:
        ValueError: If query is empty
        ConnectionError: If database unavailable
    """
    # Implementation
    pass
```

### Code Quality Tools

**Black** - Code formatting:
```bash
black agents/
black utils/
```

**Flake8** - Linting:
```bash
flake8 agents/ utils/ --max-line-length=100
```

**MyPy** - Type checking:
```bash
mypy agents/ utils/ --strict
```

### Testing

Write tests for new features:

```python
# tests/test_retrieval_agent.py
import pytest
from agents.retrieval_agent import RetrievalAgent
from utils.utils_config import Config

class TestRetrievalAgent:
    @pytest.fixture
    def agent(self):
        config = Config()
        return RetrievalAgent(config)
    
    def test_search_returns_results(self, agent):
        results = agent.search("test query", top_k=5)
        assert isinstance(results, list)
        assert len(results) <= 5
    
    def test_add_document(self, agent):
        success = agent.add_document(
            "test_doc",
            "Sample content",
            {"source": "test"}
        )
        assert success is True
```

Run tests:
```bash
pytest tests/
pytest --cov=agents --cov=utils tests/
```

## Adding New Features

### 1. Adding a New Agent

Create `agents/new_agent.py`:

```python
"""
New Agent - Description of what this agent does
"""

from typing import Dict, Any
from loguru import logger
from utils.utils_config import Config


class NewAgent:
    """Agent description"""
    
    def __init__(self, config: Config):
        """Initialize agent"""
        logger.info("Initializing New Agent")
        self.config = config
        logger.success("New Agent initialized")
    
    def main_method(self, param: str) -> Dict[str, Any]:
        """Main method description"""
        logger.info(f"Processing: {param}")
        # Implementation
        return {}
```

Update `agents/__init__.py`:
```python
from .new_agent import NewAgent

__all__ = [
    # ... existing agents
    'NewAgent'
]
```

Update `main.py` PolicyNavigator:
```python
def __init__(self):
    # ... existing agents
    self.new_agent = NewAgent(self.config)
```

### 2. Adding API Integration

Extend `APIAgent`:

```python
def query_new_api(self, query: str) -> Dict[str, Any]:
    """Query new API endpoint"""
    logger.info(f"Querying new API: {query}")
    
    try:
        params = {
            'q': query,
            'limit': 10
        }
        
        response = requests.get(
            "https://api.example.com/search",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"API returned {response.status_code}")
            return {}
            
    except Exception as e:
        logger.error(f"Error querying API: {str(e)}")
        return {}
```

### 3. Adding Configuration Options

Edit `env_example.sh`:
```bash
# New API configuration
export NEW_API_KEY="your_key_here"
export NEW_API_ENDPOINT="https://api.example.com"
```

Update `utils/utils_config.py`:
```python
# In __init__ method
self.new_api_key = os.getenv('NEW_API_KEY', '')
self.new_api_endpoint = os.getenv('NEW_API_ENDPOINT', '')
```

## Pull Request Process

1. **Update Documentation**
   - Update README.md if adding features
   - Update ARCHITECTURE.md if changing design
   - Add docstrings to new functions

2. **Test Thoroughly**
   - Run all existing tests
   - Add tests for new code
   - Test edge cases

3. **Code Review**
   - Request review from maintainers
   - Address feedback
   - Keep PR focused and concise

4. **Merge**
   - Ensure all CI checks pass
   - Get approval from maintainers
   - Use squash commits for cleanliness

## Reporting Bugs

### Issue Template

```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version: 3.x.x
- OS: macOS/Linux/Windows
- Virtual environment: Yes/No

## Logs/Error Messages
```
Paste relevant logs here
```

## Suggesting Features

### Feature Template

```markdown
## Description
Clear description of the feature

## Use Case
Why this feature would be useful

## Proposed Solution
How you think it should work

## Alternative Solutions
Other possible approaches

## Additional Context
Any other relevant information
```

## Documentation

### Code Documentation

All public functions must have docstrings:

```python
def example_function(param1: str, param2: int = 5) -> bool:
    """
    Brief description of what the function does.
    
    Longer description if needed. Explain the behavior,
    important details, and any side effects.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 5)
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When value is invalid
        ConnectionError: When connection fails
        
    Example:
        >>> result = example_function("test", 10)
        >>> print(result)
        True
    """
    # Implementation
    pass
```

### Markdown Documentation

- Use clear headings
- Include code examples
- Add sections for troubleshooting
- Link to related documentation
- Keep lines under 100 characters

## Performance Considerations

When adding features:

1. **Optimize Search**
   - Use metadata filters before similarity search
   - Batch operations for multiple documents
   - Cache frequent queries

2. **Manage Memory**
   - Don't load full documents into memory
   - Use generators for large datasets
   - Profile memory usage

3. **Minimize API Calls**
   - Cache API responses
   - Batch API requests
   - Set appropriate rate limits

## Security Guidelines

1. **API Keys**
   - Never hardcode keys
   - Use environment variables
   - Don't log sensitive data

2. **Input Validation**
   - Validate all user inputs
   - Sanitize strings used in APIs
   - Check data types

3. **Error Handling**
   - Don't expose internal errors to users
   - Log detailed errors for debugging
   - Use try-catch appropriately

## Release Process

1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag v1.0.0`
4. Push to GitHub: `git push origin v1.0.0`
5. Create release on GitHub

## Resources

- **Python Style Guide**: [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- **Type Hints**: [PEP 484](https://www.python.org/dev/peps/pep-0484/)
- **Documentation**: [PEP 257](https://www.python.org/dev/peps/pep-0257/)
- **Testing**: [pytest Documentation](https://docs.pytest.org/)

## Questions?

- Create a GitHub issue
- Start a discussion
- Email the maintainers

## Thank You!

Thank you for contributing to Policy Navigator! Your contributions help make the project better for everyone.
