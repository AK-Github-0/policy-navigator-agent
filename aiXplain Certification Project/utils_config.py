"""
Configuration management for Policy Navigator Agent
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration class"""
    
    def __init__(self):
        # Base paths
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_data_dir = self.data_dir / "processed"
        self.vector_store_path = str(self.data_dir / "vector_store")
        
        # Create directories if they don't exist
        for dir_path in [
            self.data_dir,
            self.raw_data_dir,
            self.processed_data_dir,
            Path(self.vector_store_path)
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # API Keys
        self.aixplain_api_key = os.getenv('AIXPLAIN_API_KEY')
        self.team_api_key = os.getenv('TEAM_API_KEY')
        self.federal_register_api_key = os.getenv('FEDERAL_REGISTER_API_KEY', '')
        self.courtlistener_api_key = os.getenv('COURTLISTENER_API_KEY', '')
        
        # Integration keys
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL', '')
        
        # Model configuration
        self.llm_model_id = os.getenv('LLM_MODEL_ID', '63e8f2c9e8082c389798f81c')  # Default GPT-4
        self.embedding_model = 'all-MiniLM-L6-v2'
        
        # Vector store settings
        self.chunk_size = 512
        self.chunk_overlap = 50
        self.top_k_results = 5
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_dir = self.base_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
    
    def validate(self) -> bool:
        """
        Validate that required configuration is present
        
        Returns:
            bool: True if valid, False otherwise
        """
        required = [
            ('aixplain_api_key', self.aixplain_api_key),
            ('team_api_key', self.team_api_key)
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            print(f"❌ Missing required configuration: {', '.join(missing)}")
            return False
        
        return True
    
    def __repr__(self):
        return f"Config(base_dir={self.base_dir})"