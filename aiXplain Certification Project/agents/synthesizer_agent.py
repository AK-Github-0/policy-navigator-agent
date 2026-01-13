"""
Synthesizer Agent - LLM-based response synthesis
Uses aiXplain SDK for multi-model support
"""

from typing import Dict, List, Any
from loguru import logger
from datetime import datetime


class SynthesizerAgent:
    """
    Agent responsible for synthesizing responses using LLM
    Combines retrieved documents and API results into coherent answers
    """
    
    def __init__(self, config):
        """
        Initialize synthesizer agent
        
        Args:
            config: Configuration object
        """
        logger.info("Initializing Synthesizer Agent")
        
        self.config = config
        self.team_id = config.aixplain_team_id
        self.api_key = config.aixplain_api_key
        
        logger.success("Synthesizer Agent initialized")
    
    def synthesize_response(
        self,
        query: str,
        retrieved_docs: List[Dict],
        api_results: Dict = None,
        context: str = None
    ) -> Dict[str, Any]:
        """
        Synthesize comprehensive response from multiple sources
        
        Args:
            query: User query
            retrieved_docs: Documents from retrieval agent
            api_results: Results from API agent
            context: Additional context
            
        Returns:
            dict: Synthesized response
        """
        logger.info("Synthesizing response")
        
        try:
            # Build response structure
            response = {
                'query': query,
                'answer': self._generate_answer(query, retrieved_docs, api_results),
                'sources': self._extract_sources(retrieved_docs, api_results),
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'retrieved_docs_count': len(retrieved_docs),
                    'includes_api_results': api_results is not None
                },
                'confidence': self._calculate_confidence(retrieved_docs, api_results)
            }
            
            logger.success("Response synthesized")
            return response
            
        except Exception as e:
            logger.error(f"Error synthesizing response: {str(e)}")
            return {
                'query': query,
                'answer': 'Unable to synthesize response',
                'error': str(e),
                'sources': [],
                'confidence': 0.0
            }
    
    def _generate_answer(
        self,
        query: str,
        docs: List[Dict],
        api_results: Dict
    ) -> str:
        """
        Generate answer from documents
        
        Args:
            query: User query
            docs: Retrieved documents
            api_results: API results
            
        Returns:
            str: Generated answer
        """
        logger.info("Generating answer text")
        
        # Simple answer generation (would use LLM in production)
        answer_parts = []
        
        # Add query summary
        answer_parts.append(f"Query: {query}\n")
        
        # Add document insights
        if docs:
            answer_parts.append(f"Found {len(docs)} relevant documents:\n")
            for i, doc in enumerate(docs[:3], 1):
                content_preview = doc.get('content', '')[:200]
                answer_parts.append(f"{i}. {content_preview}...")
        
        # Add API results
        if api_results:
            if api_results.get('status') == 'ACTIVE':
                answer_parts.append(f"\nPolicy Status: ACTIVE")
                answer_parts.append(f"Last Updated: {api_results.get('publication_date', 'N/A')}")
            
            if api_results.get('cases'):
                answer_parts.append(f"\nRelated Cases: {len(api_results.get('cases', []))}")
        
        return "\n".join(answer_parts)
    
    def _extract_sources(
        self,
        docs: List[Dict],
        api_results: Dict = None
    ) -> List[Dict]:
        """
        Extract sources from documents and API results
        
        Args:
            docs: Retrieved documents
            api_results: API results
            
        Returns:
            list: Source list
        """
        sources = []
        
        # Extract from documents
        for doc in docs:
            source = {
                'type': 'document',
                'id': doc.get('id', 'unknown'),
                'title': doc.get('metadata', {}).get('title', 'Untitled'),
                'source': doc.get('metadata', {}).get('source', 'Vector DB')
            }
            sources.append(source)
        
        # Extract from API results
        if api_results:
            if api_results.get('html_url'):
                sources.append({
                    'type': 'government',
                    'url': api_results.get('html_url'),
                    'title': api_results.get('title', 'Federal Register'),
                    'source': 'Federal Register API'
                })
            
            if api_results.get('cases'):
                for case in api_results.get('cases', []):
                    sources.append({
                        'type': 'case_law',
                        'url': case.get('url'),
                        'title': case.get('name'),
                        'source': 'CourtListener API'
                    })
        
        return sources
    
    def _calculate_confidence(
        self,
        docs: List[Dict],
        api_results: Dict = None
    ) -> float:
        """
        Calculate confidence score for response
        
        Args:
            docs: Retrieved documents
            api_results: API results
            
        Returns:
            float: Confidence score (0.0 - 1.0)
        """
        confidence = 0.0
        
        # Document-based confidence
        if docs:
            avg_distance = sum(d.get('distance', 0.5) for d in docs) / len(docs)
            # Lower distance = higher confidence
            doc_confidence = 1.0 - min(avg_distance, 1.0)
            confidence += doc_confidence * 0.6
        
        # API results confidence
        if api_results:
            if api_results.get('status') == 'ACTIVE':
                confidence += 0.3
            else:
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def format_for_display(self, response: Dict[str, Any]) -> str:
        """
        Format response for display
        
        Args:
            response: Synthesized response
            
        Returns:
            str: Formatted display text
        """
        logger.info("Formatting response for display")
        
        text = f"📋 **Response to Query: {response.get('query', 'N/A')}**\n\n"
        text += f"{response.get('answer', 'No answer available')}\n\n"
        
        # Sources
        sources = response.get('sources', [])
        if sources:
            text += "📚 **Sources:**\n"
            for source in sources[:5]:  # Limit to 5 sources
                text += f"- {source.get('title', 'Unknown')} ({source.get('source', 'Unknown')})\n"
        
        # Confidence
        confidence = response.get('confidence', 0.0)
        text += f"\n✅ **Confidence:** {confidence * 100:.0f}%"
        
        return text
