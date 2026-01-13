"""
Orchestrator Agent - Query routing and classification
Routes queries to appropriate agents based on type
"""

from typing import Dict, Any, Tuple
from loguru import logger
from enum import Enum


class QueryType(Enum):
    """Query type enumeration"""
    GENERAL_QUERY = "general"
    POLICY_STATUS = "policy_status"
    CASE_LAW_SEARCH = "case_law"
    COMPLIANCE_CHECK = "compliance"
    UNKNOWN = "unknown"


class OrchestratorAgent:
    """
    Agent responsible for query classification and routing
    Determines which agents should handle a query
    """
    
    def __init__(self, config):
        """
        Initialize orchestrator agent
        
        Args:
            config: Configuration object
        """
        logger.info("Initializing Orchestrator Agent")
        
        self.config = config
        
        # Keywords for query classification
        self.policy_status_keywords = [
            'status', 'active', 'effective', 'deadline', 'when', 'date',
            'executive order', 'policy', 'rule', 'regulation'
        ]
        
        self.case_law_keywords = [
            'case', 'court', 'legal', 'ruling', 'judgment', 'decision',
            'lawsuit', 'litigation', 'precedent', 'law'
        ]
        
        self.compliance_keywords = [
            'comply', 'compliance', 'requirement', 'obligation', 'mandatory',
            'must', 'should', 'checklist', 'audit', 'assessment'
        ]
        
        logger.success("Orchestrator Agent initialized")
    
    def classify_query(self, query: str) -> QueryType:
        """
        Classify query type
        
        Args:
            query: User query
            
        Returns:
            QueryType: Classified query type
        """
        logger.info(f"Classifying query: {query}")
        
        query_lower = query.lower()
        
        # Check compliance keywords
        if any(kw in query_lower for kw in self.compliance_keywords):
            logger.info("Classified as COMPLIANCE_CHECK")
            return QueryType.COMPLIANCE_CHECK
        
        # Check case law keywords
        if any(kw in query_lower for kw in self.case_law_keywords):
            logger.info("Classified as CASE_LAW_SEARCH")
            return QueryType.CASE_LAW_SEARCH
        
        # Check policy status keywords
        if any(kw in query_lower for kw in self.policy_status_keywords):
            logger.info("Classified as POLICY_STATUS")
            return QueryType.POLICY_STATUS
        
        # Default to general query
        logger.info("Classified as GENERAL_QUERY")
        return QueryType.GENERAL_QUERY
    
    def route_query(
        self,
        query: str,
        query_type: QueryType
    ) -> Dict[str, Any]:
        """
        Route query to appropriate agents
        
        Args:
            query: User query
            query_type: Classified query type
            
        Returns:
            dict: Routing instructions
        """
        logger.info(f"Routing query of type: {query_type.value}")
        
        routing = {
            'query': query,
            'query_type': query_type.value,
            'agents_to_call': [],
            'parameters': {}
        }
        
        if query_type == QueryType.POLICY_STATUS:
            routing['agents_to_call'] = ['retrieval_agent', 'api_agent']
            routing['parameters'] = {
                'search_query': query,
                'api_operation': 'check_policy_status'
            }
        
        elif query_type == QueryType.CASE_LAW_SEARCH:
            routing['agents_to_call'] = ['retrieval_agent', 'api_agent']
            routing['parameters'] = {
                'search_query': query,
                'api_operation': 'search_cases'
            }
        
        elif query_type == QueryType.COMPLIANCE_CHECK:
            routing['agents_to_call'] = ['retrieval_agent', 'action_agent']
            routing['parameters'] = {
                'search_query': query,
                'action_type': 'send_compliance_checklist'
            }
        
        else:  # GENERAL_QUERY
            routing['agents_to_call'] = ['retrieval_agent']
            routing['parameters'] = {
                'search_query': query
            }
        
        logger.success(f"Query routed to: {routing['agents_to_call']}")
        return routing
    
    def should_call_api_agent(self, query_type: QueryType) -> bool:
        """
        Determine if API agent should be called
        
        Args:
            query_type: Query type
            
        Returns:
            bool: Whether to call API agent
        """
        return query_type in [
            QueryType.POLICY_STATUS,
            QueryType.CASE_LAW_SEARCH
        ]
    
    def should_call_action_agent(self, query_type: QueryType) -> bool:
        """
        Determine if action agent should be called
        
        Args:
            query_type: Query type
            
        Returns:
            bool: Whether to call action agent
        """
        return query_type in [
            QueryType.COMPLIANCE_CHECK
        ]
