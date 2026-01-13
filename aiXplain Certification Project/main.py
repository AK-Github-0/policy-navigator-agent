"""
Policy Navigator - Main orchestrator for multi-agent RAG system
Coordinates all agents to provide comprehensive policy navigation
"""

from typing import Dict, List, Any
from loguru import logger
from datetime import datetime

from agents.retrieval_agent import RetrievalAgent
from agents.api_agent import APIAgent
from agents.action_agent import ActionAgent
from agents.synthesizer_agent import SynthesizerAgent
from agents.orchestrator_agent import OrchestratorAgent, QueryType
from utils.utils_config import Config


class PolicyNavigator:
    """
    Main orchestrator for Policy Navigator Agent system
    Coordinates multiple agents for comprehensive policy search and analysis
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize PolicyNavigator with all agents
        
        Args:
            config_path: Path to config file (optional)
        """
        logger.info("Initializing PolicyNavigator")
        
        # Initialize configuration
        self.config = Config(config_path)
        
        # Initialize all agents
        try:
            self.retrieval_agent = RetrievalAgent(self.config)
            self.api_agent = APIAgent(self.config)
            self.action_agent = ActionAgent(self.config)
            self.synthesizer_agent = SynthesizerAgent(self.config)
            self.orchestrator_agent = OrchestratorAgent(self.config)
            
            logger.success("All agents initialized")
        except Exception as e:
            logger.error(f"Error initializing agents: {str(e)}")
            raise
        
        # Initialize conversation history
        self.conversation_history = []
    
    def query(self, query_text: str) -> Dict[str, Any]:
        """
        Process user query through multi-agent pipeline
        
        Args:
            query_text: User query text
            
        Returns:
            dict: Synthesized response with sources
        """
        logger.info(f"Processing query: {query_text}")
        
        try:
            # Add to conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'user_query',
                'content': query_text
            })
            
            # Step 1: Classify query
            query_type = self.orchestrator_agent.classify_query(query_text)
            
            # Step 2: Retrieve relevant documents
            retrieved_docs = self.retrieval_agent.search(query_text, top_k=5)
            
            # Step 3: Get API results if needed
            api_results = None
            if self.orchestrator_agent.should_call_api_agent(query_type):
                if query_type == QueryType.POLICY_STATUS:
                    api_results = self.api_agent.check_policy_status(query_text)
                elif query_type == QueryType.CASE_LAW_SEARCH:
                    api_results = {
                        'cases': self.api_agent.search_cases(query_text, limit=5)
                    }
            
            # Step 4: Synthesize response
            response = self.synthesizer_agent.synthesize_response(
                query=query_text,
                retrieved_docs=retrieved_docs,
                api_results=api_results
            )
            
            # Add to conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'agent_response',
                'content': response
            })
            
            logger.success("Query processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                'query': query_text,
                'answer': f'Error processing query: {str(e)}',
                'sources': [],
                'error': str(e),
                'confidence': 0.0
            }
    
    def check_policy_status(self, policy_identifier: str) -> Dict[str, Any]:
        """
        Check policy status
        
        Args:
            policy_identifier: Policy name or identifier
            
        Returns:
            dict: Policy status information
        """
        logger.info(f"Checking policy status: {policy_identifier}")
        
        try:
            # Search for policy documents
            docs = self.retrieval_agent.search(policy_identifier, top_k=3)
            
            # Get status from API
            status = self.api_agent.check_policy_status(policy_identifier)
            
            # Synthesize response
            response = self.synthesizer_agent.synthesize_response(
                query=f"Status of {policy_identifier}",
                retrieved_docs=docs,
                api_results=status
            )
            
            logger.success("Policy status retrieved")
            return response
            
        except Exception as e:
            logger.error(f"Error checking policy status: {str(e)}")
            return {
                'query': policy_identifier,
                'error': str(e),
                'sources': []
            }
    
    def search_cases(self, regulation: str) -> Dict[str, Any]:
        """
        Search for case law related to regulation
        
        Args:
            regulation: Regulation to search for
            
        Returns:
            dict: Search results with cases and documents
        """
        logger.info(f"Searching cases for: {regulation}")
        
        try:
            # Search for related documents
            docs = self.retrieval_agent.search(regulation, top_k=5)
            
            # Search for cases
            cases = self.api_agent.search_cases(regulation, limit=5)
            
            # Synthesize response
            response = self.synthesizer_agent.synthesize_response(
                query=f"Cases related to {regulation}",
                retrieved_docs=docs,
                api_results={'cases': cases}
            )
            
            logger.success("Case law search completed")
            return response
            
        except Exception as e:
            logger.error(f"Error searching cases: {str(e)}")
            return {
                'query': regulation,
                'error': str(e),
                'sources': []
            }
    
    def add_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Add document to vector database
        
        Args:
            document_id: Document ID
            content: Document content
            metadata: Document metadata
            
        Returns:
            bool: Success status
        """
        logger.info(f"Adding document: {document_id}")
        return self.retrieval_agent.add_document(
            document_id,
            content,
            metadata
        )
    
    def add_documents_batch(self, documents: List[Dict]) -> int:
        """
        Add multiple documents
        
        Args:
            documents: List of documents
            
        Returns:
            int: Number of documents added
        """
        logger.info(f"Adding {len(documents)} documents")
        return self.retrieval_agent.add_documents_batch(documents)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get system statistics
        
        Returns:
            dict: System statistics
        """
        logger.info("Retrieving system statistics")
        
        return {
            'vector_db': self.retrieval_agent.get_stats(),
            'conversation_history_length': len(self.conversation_history),
            'system_initialized': True
        }
    
    def get_conversation_history(self) -> List[Dict]:
        """
        Get conversation history
        
        Returns:
            list: Conversation history
        """
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        logger.info("Clearing conversation history")
        self.conversation_history = []


# Singleton instance
_policy_navigator = None


def get_policy_navigator(config_path: str = None) -> PolicyNavigator:
    """
    Get or create PolicyNavigator singleton
    
    Args:
        config_path: Path to config file (optional)
        
    Returns:
        PolicyNavigator: Instance of PolicyNavigator
    """
    global _policy_navigator
    
    if _policy_navigator is None:
        _policy_navigator = PolicyNavigator(config_path)
    
    return _policy_navigator
