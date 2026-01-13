"""
Configuration management for Policy Navigator Agent
Centralized settings, API keys, and paths
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger


class Config:
    """
    Centralized configuration management
    Handles environment variables, paths, and settings
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to .env file (optional)
        """
        # Load environment variables
        if config_path:
            load_dotenv(config_path)
        else:
            load_dotenv()
        
        logger.info("Loading configuration")
        
        # API Keys
        self.aixplain_api_key = os.getenv('AIXPLAIN_API_KEY', '')
        self.aixplain_team_id = os.getenv('AIXPLAIN_TEAM_ID', '')
        self.federal_register_api_key = os.getenv('FEDERAL_REGISTER_API_KEY', '')
        self.courtlistener_api_key = os.getenv('COURTLISTENER_API_KEY', '')
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL', '')
        
        # Paths
        project_root = Path(__file__).parent.parent
        self.data_dir = project_root / 'data'
        self.raw_data_dir = self.data_dir / 'raw'
        self.processed_data_dir = self.data_dir / 'processed'
        self.vector_store_path = self.data_dir / 'vector_store'
        self.logs_dir = project_root / 'logs'
        
        # Create directories
        self._create_directories()
        
        # Model settings
        self.embedding_model = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
        self.embedding_dimension = 384
        
        # LLM settings
        self.llm_model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('MAX_TOKENS', '2000'))
        
        # Chunking settings
        self.chunk_size = int(os.getenv('CHUNK_SIZE', '512'))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '50'))
        
        # Search settings
        self.top_k_documents = int(os.getenv('TOP_K_DOCUMENTS', '5'))
        self.similarity_threshold = float(os.getenv('SIMILARITY_THRESHOLD', '0.3'))
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self._setup_logging()
        
        logger.success("Configuration loaded")
    
    def _create_directories(self):
        """Create necessary directories"""
        for directory in [
            self.data_dir,
            self.raw_data_dir,
            self.processed_data_dir,
            self.vector_store_path,
            self.logs_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {directory}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = self.logs_dir / 'policy_navigator.log'
        
        logger.add(
            str(log_file),
            rotation='500 MB',
            retention='7 days',
            level=self.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        )
        
        logger.debug(f"Logging configured to {log_file}")
    
    def __str__(self):
        """String representation"""
        return f"Config(data_dir={self.data_dir}, vector_store={self.vector_store_path})"
