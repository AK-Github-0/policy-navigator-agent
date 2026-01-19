"""
Orchestrator Agent - Query routing and classification
Uses aiXplain SDK AgentFactory for intelligent query routing
Routes queries to appropriate agents based on type
"""

from typing import Dict, Any, Tuple
from loguru import logger
from enum import Enum

# Import aiXplain SDK components
try:
    from aixplain.factories import AgentFactory
    AIXPLAIN_AVAILABLE = True
except ImportError:
    logger.warning("aiXplain SDK not available - using fallback mode")
    AIXPLAIN_AVAILABLE = False


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
    Uses aiXplain AgentFactory for intelligent routing
    Determines which agents should handle a query
    """
    
    def __init__(self, config):
        """
        Initialize orchestrator agent with aiXplain routing
        
        Args:
            config: Configuration object
        """
        logger.info("Initializing Orchestrator Agent")
        
        self.config = config
        self.use_aixplain = AIXPLAIN_AVAILABLE
        
        # Initialize aiXplain orchestration agent if available
        if self.use_aixplain:
            try:
                logger.info("Initializing aiXplain AgentFactory for orchestration")
                self.router_agent = AgentFactory.create(
                    name="query_router_agent",
                    description="Agent for intelligent query routing and classification",
                    team_id=config.aixplain_team_id,
                    api_key=config.aixplain_api_key
                )
                logger.success("aiXplain orchestration agent initialized")
            except Exception as e:
                logger.error(f"Error initializing aiXplain router: {str(e)}")
                self.use_aixplain = False
                self.router_agent = None
        else:
            self.router_agent = None
        
        # Keywords for query classification (used as fallback)
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
        Classify query type using aiXplain or keyword matching
        
        Args:
            query: User query
            
        Returns:
            QueryType: Classified query type
        """
        logger.info(f"Classifying query: {query[:100]}...")
        
        # Try aiXplain classification first
        if self.use_aixplain and self.router_agent:
            try:
                logger.debug("Using aiXplain classification")
                classification_prompt = f"""
Classify this query into one of these categories:
1. 'POLICY_STATUS' - Questions about policy status, effectiveness, deadlines
2. 'CASE_LAW_SEARCH' - Questions about legal cases, court decisions, precedents
3. 'COMPLIANCE_CHECK' - Questions about compliance requirements, obligations

Query: {query}

Respond with only the category name (exactly as shown above).
"""
                result = self.router_agent.run(classification_prompt)
                classification = result.strip().upper()
                
                # Map result to QueryType
                for query_type in QueryType:
                    if query_type.value.upper() == classification:
                        logger.success(f"Query classified as: {query_type.value}")
                        return query_type
            except Exception as e:
                logger.warning(f"aiXplain classification failed: {str(e)}, falling back to keyword matching")
        
        # Fallback: Keyword-based classification
        logger.debug("Using keyword-based classification")
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
        Route query to appropriate agents using aiXplain or heuristics
        
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
        
        # Try to use aiXplain for agent selection
        if self.use_aixplain and self.router_agent:
            try:
                logger.debug("Using aiXplain for agent routing")
                routing_prompt = f"""
Based on this query type '{query_type.value}', which agents should handle this query?
Available agents: retrieval_agent, api_agent, action_agent

Query: {query}
Type: {query_type.value}

Return a comma-separated list of agent names (e.g., 'retrieval_agent,api_agent').
"""
                result = self.router_agent.run(routing_prompt)
                agents = [a.strip() for a in result.split(',')]
                routing['agents_to_call'] = agents
                logger.debug(f"aiXplain suggested agents: {agents}")
            except Exception as e:
                logger.warning(f"aiXplain routing failed: {str(e)}, using heuristics")
                routing['agents_to_call'] = self._get_default_agents(query_type)
        else:
            # Use heuristic-based routing
            routing['agents_to_call'] = self._get_default_agents(query_type)
        
        # Set routing parameters based on query type
        if query_type == QueryType.POLICY_STATUS:
            routing['parameters'] = {
                'search_query': query,
                'api_operation': 'check_policy_status'
            }
        
        elif query_type == QueryType.CASE_LAW_SEARCH:
            routing['parameters'] = {
                'search_query': query,
                'api_operation': 'search_cases'
            }
        
        elif query_type == QueryType.COMPLIANCE_CHECK:
            routing['parameters'] = {
                'search_query': query,
                'action_type': 'send_compliance_checklist'
            }
        
        else:  # GENERAL_QUERY
            routing['parameters'] = {
                'search_query': query
            }
        
        logger.success(f"Query routed to: {routing['agents_to_call']}")
        return routing
    
    def _get_default_agents(self, query_type: QueryType) -> list:
        """
        Get default agents for a query type
        
        Args:
            query_type: Query type
            
        Returns:
            list: Default agents to call
        """
        if query_type == QueryType.POLICY_STATUS:
            return ['retrieval_agent', 'api_agent']
        elif query_type == QueryType.CASE_LAW_SEARCH:
            return ['retrieval_agent', 'api_agent']
        elif query_type == QueryType.COMPLIANCE_CHECK:
            return ['retrieval_agent', 'action_agent']
        else:  # GENERAL_QUERY
            return ['retrieval_agent']
    
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
