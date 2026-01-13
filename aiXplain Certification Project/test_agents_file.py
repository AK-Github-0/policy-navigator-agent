"""
Unit tests for Policy Navigator Agents
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.orchestrator import OrchestratorAgent
from agents.retrieval_agent import RetrievalAgent
from agents.api_agent import APIAgent
from agents.synthesizer import SynthesizerAgent
from agents.action_agent import ActionAgent
from utils.config import Config


class TestConfig:
    """Test configuration"""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration"""
        config = Mock(spec=Config)
        config.aixplain_api_key = "test_key"
        config.team_api_key = "test_team_key"
        config.vector_store_path = "test_vector_store"
        config.federal_register_api_key = "test_fr_key"
        config.courtlistener_api_key = "test_cl_key"
        config.slack_webhook_url = "https://hooks.slack.com/test"
        config.llm_model_id = "test_model_id"
        return config


class TestOrchestratorAgent(TestConfig):
    """Test Orchestrator Agent"""
    
    @patch('agents.orchestrator.RetrievalAgent')
    @patch('agents.orchestrator.APIAgent')
    @patch('agents.orchestrator.SynthesizerAgent')
    @patch('agents.orchestrator.ActionAgent')
    def test_orchestrator_initialization(
        self,
        mock_action,
        mock_synthesizer,
        mock_api,
        mock_retrieval,
        mock_config
    ):
        """Test orchestrator initializes all agents"""
        orchestrator = OrchestratorAgent(mock_config)
        
        assert orchestrator.retrieval_agent is not None
        assert orchestrator.api_agent is not None
        assert orchestrator.synthesizer is not None
        assert orchestrator.action_agent is not None
    
    def test_query_classification(self, mock_config):
        """Test query type classification"""
        with patch('agents.orchestrator.RetrievalAgent'), \
             patch('agents.orchestrator.APIAgent'), \
             patch('agents.orchestrator.SynthesizerAgent'), \
             patch('agents.orchestrator.ActionAgent'):
            
            orchestrator = OrchestratorAgent(mock_config)
            
            # Test status check classification
            query1 = "Is Executive Order 14067 still in effect?"
            assert orchestrator.classify_query(query1) == 'status_check'
            
            # Test case law classification
            query2 = "Has Section 230 been challenged in court?"
            assert orchestrator.classify_query(query2) == 'case_law'
            
            # Test compliance classification
            query3 = "What are the requirements for GDPR compliance?"
            assert orchestrator.classify_query(query3) == 'compliance'
            
            # Test general classification
            query4 = "Tell me about privacy laws"
            assert orchestrator.classify_query(query4) == 'general'


class TestRetrievalAgent(TestConfig):
    """Test Retrieval Agent"""
    
    @patch('agents.retrieval_agent.chromadb')
    @patch('agents.retrieval_agent.SentenceTransformer')
    def test_retrieval_agent_initialization(
        self,
        mock_transformer,
        mock_chromadb,
        mock_config
    ):
        """Test retrieval agent initialization"""
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 100
        mock_client.get_collection.return_value = mock_collection
        mock_chromadb.PersistentClient.return_value = mock_client
        
        agent = RetrievalAgent(mock_config)
        
        assert agent.embedding_model is not None
        assert agent.collection is not None
    
    @patch('agents.retrieval_agent.chromadb')
    @patch('agents.retrieval_agent.SentenceTransformer')
    def test_create_embedding(
        self,
        mock_transformer,
        mock_chromadb,
        mock_config
    ):
        """Test embedding creation"""
        mock_model = Mock()
        mock_model.encode.return_value = [0.1, 0.2, 0.3]
        mock_transformer.return_value = mock_model
        
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.get_collection.return_value = mock_collection
        mock_chromadb.PersistentClient.return_value = mock_client
        
        agent = RetrievalAgent(mock_config)
        embedding = agent.create_embedding("test text")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 3
    
    @patch('agents.retrieval_agent.chromadb')
    @patch('agents.retrieval_agent.SentenceTransformer')
    def test_search(
        self,
        mock_transformer,
        mock_chromadb,
        mock_config
    ):
        """Test document search"""
        mock_model = Mock()
        mock_model.encode.return_value = [0.1, 0.2, 0.3]
        mock_transformer.return_value = mock_model
        
        mock_client = Mock()
        mock_collection = Mock()
        
        # Mock search results
        mock_collection.query.return_value = {
            'ids': [['doc1', 'doc2']],
            'documents': [['Content 1', 'Content 2']],
            'metadatas': [[{'title': 'Doc 1'}, {'title': 'Doc 2'}]],
            'distances': [[0.1, 0.2]]
        }
        
        mock_client.get_collection.return_value = mock_collection
        mock_chromadb.PersistentClient.return_value = mock_client
        
        agent = RetrievalAgent(mock_config)
        results = agent.search("test query", top_k=2)
        
        assert len(results) == 2
        assert results[0]['id'] == 'doc1'
        assert results[0]['content'] == 'Content 1'


class TestAPIAgent(TestConfig):
    """Test API Agent"""
    
    def test_api_agent_initialization(self, mock_config):
        """Test API agent initialization"""
        agent = APIAgent(mock_config)
        
        assert agent.federal_register_base is not None
        assert agent.courtlistener_base is not None
    
    @patch('agents.api_agent.requests.get')
    def test_check_policy_status(self, mock_get, mock_config):
        """Test policy status check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{
                'title': 'Test Policy',
                'document_number': '2024-001',
                'publication_date': '2024-01-01',
                'type': 'Rule',
                'abstract': 'Test abstract'
            }]
        }
        mock_get.return_value = mock_response
        
        agent = APIAgent(mock_config)
        status = agent.check_policy_status("Executive Order 14067")
        
        assert status['status'] == 'ACTIVE'
        assert status['title'] == 'Test Policy'
    
    @patch('agents.api_agent.requests.get')
    def test_search_cases(self, mock_get, mock_config):
        """Test case law search"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{
                'caseName': 'Test v. Case',
                'court': 'Supreme Court',
                'dateFiled': '2023-01-01',
                'citation': ['123 U.S. 456'],
                'snippet': 'Test summary'
            }]
        }
        mock_get.return_value = mock_response
        
        agent = APIAgent(mock_config)
        cases = agent.search_cases("Section 230", limit=1)
        
        assert len(cases) == 1
        assert cases[0]['name'] == 'Test v. Case'


class TestSynthesizerAgent(TestConfig):
    """Test Synthesizer Agent"""
    
    @patch('agents.synthesizer.aixplain')
    def test_synthesizer_initialization(self, mock_aixplain, mock_config):
        """Test synthesizer initialization"""
        agent = SynthesizerAgent(mock_config)
        assert agent.config is not None
    
    @patch('agents.synthesizer.aixplain')
    def test_synthesize_response(self, mock_aixplain, mock_config):
        """Test response synthesis"""
        agent = SynthesizerAgent(mock_config)
        
        gathered_info = {
            'vector_results': [{
                'id': 'doc1',
                'content': 'Test content',
                'metadata': {'title': 'Test Doc'},
                'score': 0.9
            }],
            'api_results': {},
            'query_type': 'general'
        }
        
        response = agent.synthesize(
            query="Test query",
            gathered_info=gathered_info
        )
        
        assert 'answer' in response
        assert 'sources' in response
        assert len(response['sources']) > 0


class TestActionAgent(TestConfig):
    """Test Action Agent"""
    
    def test_action_agent_initialization(self, mock_config):
        """Test action agent initialization"""
        agent = ActionAgent(mock_config)
        assert agent.slack_webhook is not None
    
    @patch('agents.action_agent.requests.post')
    def test_send_slack_notification(self, mock_post, mock_config):
        """Test Slack notification"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        agent = ActionAgent(mock_config)
        result = agent.send_slack_notification("Test message")
        
        assert result == True
    
    def test_create_subscription(self, mock_config):
        """Test subscription creation"""
        agent = ActionAgent(mock_config)
        
        subscription = agent.create_subscription(
            policy="Test Policy",
            channel="#test",
            frequency="daily"
        )
        
        assert subscription['policy'] == "Test Policy"
        assert subscription['channel'] == "#test"
        assert subscription['status'] == 'active'


class TestIntegration(TestConfig):
    """Integration tests"""
    
    @patch('agents.orchestrator.aixplain')
    @patch('agents.retrieval_agent.chromadb')
    @patch('agents.retrieval_agent.SentenceTransformer')
    @patch('agents.api_agent.requests')
    def test_end_to_end_query(
        self,
        mock_requests,
        mock_transformer,
        mock_chromadb,
        mock_aixplain,
        mock_config
    ):
        """Test complete query flow"""
        # Setup mocks
        mock_model = Mock()
        mock_model.encode.return_value = [0.1, 0.2, 0.3]
        mock_transformer.return_value = mock_model
        
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'ids': [['doc1']],
            'documents': [['Test content']],
            'metadatas': [[{'title': 'Test'}]],
            'distances': [[0.1]]
        }
        mock_client.get_collection.return_value = mock_collection
        mock_chromadb.PersistentClient.return_value = mock_client
        
        # This is a simplified integration test
        # In practice, you'd want more comprehensive testing
        assert True  # Placeholder


if __name__ == '__main__':
    pytest.main([__file__, '-v'])