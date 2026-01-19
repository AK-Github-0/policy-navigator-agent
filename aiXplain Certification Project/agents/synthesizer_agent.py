"""
Synthesizer Agent - LLM-based response synthesis
Uses aiXplain SDK ModelFactory for multi-model support
"""

from typing import Dict, List, Any
from loguru import logger
from datetime import datetime

# Import aiXplain SDK components
try:
    from aixplain.factories import ModelFactory
    from aixplain.enums import Function
    AIXPLAIN_AVAILABLE = True
except ImportError:
    logger.warning("aiXplain SDK not available - using fallback mode")
    AIXPLAIN_AVAILABLE = False


class SynthesizerAgent:
    """
    Agent responsible for synthesizing responses using LLM
    Uses aiXplain ModelFactory for LLM operations
    Combines retrieved documents and API results into coherent answers
    """
    
    def __init__(self, config):
        """
        Initialize synthesizer agent with aiXplain LLM
        
        Args:
            config: Configuration object
        """
        logger.info("Initializing Synthesizer Agent")
        
        self.config = config
        self.team_id = config.aixplain_team_id
        self.api_key = config.aixplain_api_key
        self.use_aixplain = AIXPLAIN_AVAILABLE
        
        # Initialize aiXplain LLM Model
        if self.use_aixplain:
            try:
                logger.info("Initializing aiXplain ModelFactory for LLM")
                # Get a pre-configured LLM model from aiXplain
                self.llm_model = ModelFactory.get_model(
                    model_id="660191da8e10e26495e4bf7b",  # GPT-3.5 via aiXplain
                    api_key=self.api_key,
                    team_id=self.team_id
                )
                logger.success("aiXplain LLM Model initialized")
            except Exception as e:
                logger.error(f"Error initializing aiXplain LLM: {str(e)}")
                self.use_aixplain = False
                self.llm_model = None
        else:
            self.llm_model = None
        
        logger.success("Synthesizer Agent initialized")
    
    def synthesize_response(
        self,
        query: str,
        retrieved_docs: List[Dict],
        api_results: Dict = None,
        context: str = None
    ) -> Dict[str, Any]:
        """
        Synthesize comprehensive response from multiple sources using LLM
        
        Args:
            query: User query
            retrieved_docs: Documents from retrieval agent
            api_results: Results from API agent
            context: Additional context
            
        Returns:
            dict: Synthesized response
        """
        logger.info("Synthesizing response with LLM")
        
        try:
            # Build response structure
            response = {
                'query': query,
                'answer': self._generate_answer(query, retrieved_docs, api_results),
                'sources': self._extract_sources(retrieved_docs, api_results),
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'retrieved_docs_count': len(retrieved_docs),
                    'includes_api_results': api_results is not None,
                    'used_llm': self.use_aixplain
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
        Generate answer using aiXplain LLM or fallback method
        
        Args:
            query: User query
            docs: Retrieved documents
            api_results: API results
            
        Returns:
            str: Generated answer
        """
        logger.info("Generating answer with LLM")
        
        # Build context from documents and API results
        context = self._build_context(query, docs, api_results)
        
        if self.use_aixplain and self.llm_model:
            try:
                # Use aiXplain LLM for synthesis
                prompt = f"""Based on the following information, provide a comprehensive answer to the user's question.

User Query: {query}

Context Information:
{context}

Please provide a detailed, well-structured answer that addresses the user's query:"""
                
                result = self.llm_model.run(prompt)
                
                # Extract text from result
                if hasattr(result, 'data'):
                    answer = result.data
                elif hasattr(result, 'output'):
                    answer = result.output
                else:
                    answer = str(result)
                
                logger.success("Answer generated via aiXplain LLM")
                return answer
            except Exception as e:
                logger.error(f"Error generating answer with aiXplain: {str(e)}")
                return self._generate_answer_fallback(query, docs, api_results)
        else:
            # Use fallback method
            return self._generate_answer_fallback(query, docs, api_results)
    
    def _generate_answer_fallback(
        self,
        query: str,
        docs: List[Dict],
        api_results: Dict
    ) -> str:
        """
        Fallback answer generation using string composition
        
        Args:
            query: User query
            docs: Retrieved documents
            api_results: API results
            
        Returns:
            str: Generated answer
        """
        logger.info("Generating answer using fallback method")
        
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
    
    def _build_context(
        self,
        query: str,
        docs: List[Dict],
        api_results: Dict
    ) -> str:
        """
        Build context string from documents and API results
        
        Args:
            query: User query
            docs: Retrieved documents
            api_results: API results
            
        Returns:
            str: Context string
        """
        context_parts = []
        
        # Add document context
        if docs:
            context_parts.append("Retrieved Documents:")
            for i, doc in enumerate(docs[:5], 1):
                content = doc.get('content', '')[:500]
                source = doc.get('metadata', {}).get('source', 'Unknown')
                context_parts.append(f"\nDocument {i} (from {source}):")
                context_parts.append(content)
        
        # Add API results context
        if api_results:
            context_parts.append("\nGovernment/Legal Information:")
            if api_results.get('status'):
                context_parts.append(f"Status: {api_results.get('status')}")
            if api_results.get('title'):
                context_parts.append(f"Title: {api_results.get('title')}")
            if api_results.get('abstract'):
                context_parts.append(f"Summary: {api_results.get('abstract')[:300]}")
        
        return "\n".join(context_parts)
    
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
        
        # Show if LLM was used
        metadata = response.get('metadata', {})
        if metadata.get('used_llm'):
            text += "\n🤖 *Powered by aiXplain LLM*"
        
        return text

    
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
