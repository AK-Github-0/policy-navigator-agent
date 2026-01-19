"""
API Agent - Handles external API integrations
Uses aiXplain SDK for API management and external data source integration
Integrates with Federal Register API and CourtListener API
"""

from typing import Dict, List, Any
from loguru import logger
import requests
from datetime import datetime
import re

# Import aiXplain SDK components
try:
    from aixplain.factories import AgentFactory
    from aixplain.enums import Function
    AIXPLAIN_AVAILABLE = True
except ImportError:
    logger.warning("aiXplain SDK not available - using fallback mode")
    AIXPLAIN_AVAILABLE = False


class APIAgent:
    """
    Agent responsible for querying external government APIs
    Uses aiXplain SDK for API tool management
    - Federal Register API for policy status
    - CourtListener API for case law
    """
    
    def __init__(self, config):
        """
        Initialize API agent with aiXplain and credentials
        
        Args:
            config: Configuration object with API keys
        """
        logger.info("Initializing API Agent")
        
        self.config = config
        self.use_aixplain = AIXPLAIN_AVAILABLE
        
        # API endpoints
        self.federal_register_base = "https://www.federalregister.gov/api/v1"
        self.courtlistener_base = "https://www.courtlistener.com/api/rest/v3"
        
        # API keys
        self.federal_register_key = config.federal_register_api_key
        self.courtlistener_key = config.courtlistener_api_key
        self.aixplain_api_key = config.aixplain_api_key
        self.aixplain_team_id = config.aixplain_team_id
        
        # Initialize aiXplain agent if available
        if self.use_aixplain:
            try:
                logger.info("Initializing aiXplain AgentFactory for API tools")
                # Create or get API-enabled agent
                self.aixplain_agent = AgentFactory.create(
                    name="api_integration_agent",
                    description="Agent for managing external API calls",
                    team_id=self.aixplain_team_id,
                    api_key=self.aixplain_api_key
                )
                logger.success("aiXplain API Agent initialized")
            except Exception as e:
                logger.error(f"Error initializing aiXplain agent: {str(e)}")
                self.use_aixplain = False
                self.aixplain_agent = None
        else:
            self.aixplain_agent = None
        
        logger.success("API Agent initialized")
    
    def check_policy_status(self, policy_identifier: str) -> Dict[str, Any]:
        """
        Check policy status via Federal Register API using aiXplain or direct call
        
        Args:
            policy_identifier: Policy name or executive order number
            
        Returns:
            dict: Policy status information
        """
        logger.info(f"Checking policy status: {policy_identifier}")
        
        try:
            if self.use_aixplain and self.aixplain_agent:
                # Use aiXplain for API call management
                logger.info("Querying policy status via aiXplain")
                result = self._query_via_aixplain(
                    f"Check the status of policy: {policy_identifier}",
                    function_type="policy_check"
                )
                if result:
                    return result
            
            # Fallback to direct API call
            return self._check_policy_status_direct(policy_identifier)
            
        except Exception as e:
            logger.error(f"Error checking policy status: {str(e)}")
            return {
                'status': 'ERROR',
                'message': str(e),
                'last_checked': datetime.now().isoformat(),
                'source': 'API Agent'
            }
    
    def _check_policy_status_direct(self, policy_identifier: str) -> Dict[str, Any]:
        """
        Direct Federal Register API call
        
        Args:
            policy_identifier: Policy name or executive order number
            
        Returns:
            dict: Policy status information
        """
        try:
            # Extract executive order number if present
            eo_match = re.search(r'(\d{5})', policy_identifier)
            
            if eo_match:
                eo_number = eo_match.group(1)
                query = f"executive order {eo_number}"
            else:
                query = policy_identifier
            
            # Search Federal Register
            params = {
                'conditions[term]': query,
                'per_page': 5,
                'order': 'newest'
            }
            
            response = requests.get(
                f"{self.federal_register_base}/documents.json",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('results'):
                    latest = data['results'][0]
                    
                    return {
                        'status': 'ACTIVE',
                        'title': latest.get('title', 'N/A'),
                        'document_number': latest.get('document_number', 'N/A'),
                        'publication_date': latest.get('publication_date', 'N/A'),
                        'type': latest.get('type', 'N/A'),
                        'abstract': latest.get('abstract', 'N/A'),
                        'html_url': latest.get('html_url', 'N/A'),
                        'pdf_url': latest.get('pdf_url', 'N/A'),
                        'last_checked': datetime.now().isoformat(),
                        'source': 'Federal Register API'
                    }
                else:
                    return {
                        'status': 'NOT_FOUND',
                        'message': f'No results found for {policy_identifier}',
                        'last_checked': datetime.now().isoformat(),
                        'source': 'Federal Register API'
                    }
            else:
                logger.warning(f"API returned status {response.status_code}")
                return {
                    'status': 'ERROR',
                    'message': f'API error: {response.status_code}',
                    'last_checked': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error checking policy status: {str(e)}")
            return {
                'status': 'ERROR',
                'message': str(e),
                'last_checked': datetime.now().isoformat()
            }
    
    def _query_via_aixplain(self, query: str, function_type: str = None) -> Dict[str, Any]:
        """
        Execute query via aiXplain agent
        
        Args:
            query: Query string
            function_type: Type of function to use
            
        Returns:
            dict: Query results or None
        """
        try:
            if not self.use_aixplain or not self.aixplain_agent:
                return None
            
            logger.info(f"Executing query via aiXplain: {query}")
            result = self.aixplain_agent.run(query)
            
            if result:
                logger.success("aiXplain query executed successfully")
                # Parse result and return as dict
                return {
                    'status': 'SUCCESS',
                    'data': str(result),
                    'source': 'aiXplain Agent',
                    'last_checked': datetime.now().isoformat()
                }
            return None
        except Exception as e:
            logger.error(f"Error executing aiXplain query: {str(e)}")
            return None
    
    def search_cases(
        self,
        regulation: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for case law via CourtListener API
        
        Args:
            regulation: Regulation or law to search for
            limit: Maximum number of cases to return
            
        Returns:
            list: List of relevant cases
        """
        logger.info(f"Searching cases for: {regulation}")
        
        try:
            # Search opinions
            params = {
                'q': regulation,
                'order_by': 'score desc',
                'type': 'o',  # opinions
                'page_size': limit
            }
            
            headers = {}
            if self.courtlistener_key:
                headers['Authorization'] = f'Token {self.courtlistener_key}'
            
            response = requests.get(
                f"{self.courtlistener_base}/search/",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                cases = []
                for result in data.get('results', [])[:limit]:
                    cases.append({
                        'name': result.get('caseName', 'Unknown Case'),
                        'court': result.get('court', 'N/A'),
                        'year': result.get('dateFiled', 'N/A')[:4] if result.get('dateFiled') else 'N/A',
                        'citation': result.get('citation', [None])[0] if result.get('citation') else 'N/A',
                        'summary': result.get('snippet', 'No summary available'),
                        'url': result.get('absolute_url', 'N/A'),
                        'date_filed': result.get('dateFiled', 'N/A'),
                        'source': 'CourtListener API'
                    })
                
                logger.success(f"Found {len(cases)} cases")
                return cases
            else:
                logger.warning(f"CourtListener API returned status {response.status_code}")
                return self._get_mock_cases(regulation, limit)
                
        except Exception as e:
            logger.error(f"Error searching cases: {str(e)}")
            # Return mock data as fallback
            return self._get_mock_cases(regulation, limit)
    
    def _get_mock_cases(self, regulation: str, limit: int = 5) -> List[Dict]:
        """
        Return mock case data when API is unavailable
        
        Args:
            regulation: Regulation being searched
            limit: Number of cases to return
            
        Returns:
            list: Mock case data
        """
        logger.info("Using mock case data")
        
        mock_cases = {
            'section 230': [
                {
                    'name': 'Fair Housing Council v. Roommates.com',
                    'court': '9th Circuit Court of Appeals',
                    'year': '2008',
                    'citation': '521 F.3d 1157',
                    'summary': 'Clarified limits on Section 230 platform immunity. Court held that websites that contribute to illegal content development are not protected.',
                    'url': 'https://www.courtlistener.com/opinion/171033/',
                    'date_filed': '2008-04-03',
                    'source': 'Mock Data'
                },
                {
                    'name': 'Gonzalez v. Google LLC',
                    'court': 'Supreme Court of the United States',
                    'year': '2023',
                    'citation': '598 U.S. ___',
                    'summary': 'Examined whether algorithmic recommendations are protected by Section 230. Court narrowly construed Section 230 protections.',
                    'url': 'https://www.supremecourt.gov/opinions/22pdf/21-1333_6j7a.pdf',
                    'date_filed': '2023-05-18',
                    'source': 'Mock Data'
                }
            ],
            'gdpr': [
                {
                    'name': 'Google LLC v. CNIL',
                    'court': 'Court of Justice of the European Union',
                    'year': '2019',
                    'citation': 'Case C-507/17',
                    'summary': 'Addressed the territorial scope of the right to be forgotten under GDPR Article 17.',
                    'url': 'https://curia.europa.eu/juris/document/document.jsf?docid=218105',
                    'date_filed': '2019-09-24',
                    'source': 'Mock Data'
                }
            ]
        }
        
        # Find matching mock cases
        for key in mock_cases:
            if key.lower() in regulation.lower():
                return mock_cases[key][:limit]
        
        # Default mock case
        return [{
            'name': f'Related Case for {regulation}',
            'court': 'Various Courts',
            'year': '2023',
            'citation': 'N/A',
            'summary': f'Mock case data for {regulation}. Enable CourtListener API for real data.',
            'url': 'https://www.courtlistener.com/',
            'date_filed': '2023-01-01',
            'source': 'Mock Data'
        }]
    
    def get_recent_documents(
        self,
        document_type: str = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get recent documents from Federal Register
        
        Args:
            document_type: Type of document (rule, notice, etc.)
            days: Number of days to look back
            
        Returns:
            list: Recent documents
        """
        logger.info(f"Fetching recent documents (last {days} days)")
        
        try:
            params = {
                'per_page': 20,
                'order': 'newest'
            }
            
            if document_type:
                params['conditions[type]'] = document_type
            
            response = requests.get(
                f"{self.federal_register_base}/documents.json",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                documents = []
                for doc in data.get('results', []):
                    documents.append({
                        'title': doc.get('title', 'N/A'),
                        'type': doc.get('type', 'N/A'),
                        'abstract': doc.get('abstract', 'N/A'),
                        'publication_date': doc.get('publication_date', 'N/A'),
                        'document_number': doc.get('document_number', 'N/A'),
                        'html_url': doc.get('html_url', 'N/A')
                    })
                
                logger.success(f"Found {len(documents)} recent documents")
                return documents
            else:
                logger.warning(f"API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching recent documents: {str(e)}")
            return []
