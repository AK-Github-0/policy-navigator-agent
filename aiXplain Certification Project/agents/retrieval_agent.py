"""
Retrieval Agent - Handles vector database operations
Uses aiXplain SDK IndexFactory for document management and semantic search
"""

from typing import Dict, List, Any
from loguru import logger
from datetime import datetime

# Import aiXplain SDK components
try:
    from aixplain.factories import IndexFactory
    from aixplain.enums import SortBy
    AIXPLAIN_AVAILABLE = True
except ImportError:
    logger.warning("aiXplain SDK not available - using fallback mode")
    AIXPLAIN_AVAILABLE = False

# Optional imports for fallback
try:
    import chromadb
except Exception:
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

try:
    import numpy as np
except Exception:
    np = None


class RetrievalAgent:
    """
    Agent responsible for semantic search and document retrieval
    Uses aiXplain SDK IndexFactory for vector storage and retrieval
    Falls back to ChromaDB if aiXplain SDK is unavailable
    """
    
    def __init__(self, config):
        """
        Initialize retrieval agent with aiXplain Index
        
        Args:
            config: Configuration object
        """
        logger.info("Initializing Retrieval Agent")
        
        self.config = config
        self.use_aixplain = AIXPLAIN_AVAILABLE
        
        # Initialize aiXplain Index
        if self.use_aixplain:
            try:
                logger.info("Initializing aiXplain IndexFactory")
                self.index = IndexFactory.create(
                    name="policy_documents_index",
                    description="Index for policy documents in RAG system",
                    team_id=config.aixplain_team_id,
                    api_key=config.aixplain_api_key
                )
                logger.success("aiXplain Index initialized")
            except Exception as e:
                logger.error(f"Error initializing aiXplain Index: {str(e)}")
                self.use_aixplain = False
                self.index = None
        else:
            self.index = None
        
        # Fallback to ChromaDB if needed
        self.embedder = None
        self.client = None
        self.collection = None
        self.embedding_model = getattr(config, 'embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
        
        if not self.use_aixplain:
            logger.info("Using fallback ChromaDB for vector storage")
            self._init_chromadb()
    
    def _init_chromadb(self):
        """Initialize ChromaDB as fallback"""
        try:
            if SentenceTransformer is not None:
                self.embedder = SentenceTransformer(
                    self.embedding_model,
                    device='cpu'
                )
                logger.success("Embedding model loaded")
            
            if chromadb is not None:
                self.client = chromadb.PersistentClient(
                    path=str(self.config.vector_store_path)
                )
                if callable(getattr(self.client, 'get_or_create_collection', None)):
                    self.collection = self.client.get_or_create_collection(
                        name="policy_documents",
                        metadata={"hnsw:space": "cosine"}
                    )
                logger.success("ChromaDB fallback initialized")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB fallback: {str(e)}")
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for text using aiXplain or local embeddings
        
        Args:
            text: Text to embed
            
        Returns:
            list: Embedding vector
        """
        if self.use_aixplain:
            try:
                # Use aiXplain for embeddings
                from aixplain.factories import ModelFactory
                
                embedding_model = ModelFactory.get_model(
                    model_id="6502d91a8e10e26495e3f789",  # aiXplain embedding model
                    api_key=self.config.aixplain_api_key
                )
                
                result = embedding_model.run(text)
                if hasattr(result, 'embedding'):
                    return result.embedding
                else:
                    logger.warning("Unable to extract embedding from aiXplain response")
                    return []
            except Exception as e:
                logger.error(f"Error creating embedding with aiXplain: {str(e)}")
                return []
        else:
            # Fallback to local embeddings
            try:
                if not self.embedder:
                    logger.warning("No embedder available, returning empty embedding")
                    return []
                
                raw = self.embedder.encode(text)
                if hasattr(raw, 'tolist'):
                    embedding = raw.tolist()
                else:
                    embedding = list(raw)
                return embedding
            except Exception as e:
                logger.error(f"Error creating embedding: {str(e)}")
                return []
    
    def add_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any] = None,
        source: str = None
    ) -> bool:
        """
        Add single document to index using aiXplain or ChromaDB
        
        Args:
            document_id: Unique document identifier
            content: Document content
            metadata: Document metadata
            source: Document source
            
        Returns:
            bool: Success status
        """
        logger.info(f"Adding document: {document_id}")
        
        try:
            if self.use_aixplain and self.index:
                # Use aiXplain Index
                doc_metadata = metadata or {}
                if source:
                    doc_metadata['source'] = source
                
                self.index.add_file(
                    file_path=None,
                    text=content,
                    metadata=doc_metadata,
                    reference_id=document_id
                )
                logger.success(f"Document added via aiXplain: {document_id}")
                return True
            else:
                # Use ChromaDB fallback
                if not self.collection:
                    logger.error("No vector store available")
                    return False
                
                embedding = self.create_embedding(content)
                if not embedding:
                    logger.error(f"Failed to create embedding for {document_id}")
                    return False
                
                doc_metadata = metadata or {}
                if source:
                    doc_metadata['source'] = source
                
                self.collection.add(
                    ids=[document_id],
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[doc_metadata]
                )
                logger.success(f"Document added via ChromaDB: {document_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            return False
    
    def add_documents_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> int:
        """
        Add multiple documents in batch using aiXplain or ChromaDB
        
        Args:
            documents: List of documents with 'id', 'content', 'metadata'
            
        Returns:
            int: Number of documents added
        """
        logger.info(f"Adding {len(documents)} documents in batch")
        
        try:
            added_count = 0
            
            if self.use_aixplain and self.index:
                # Use aiXplain Index for batch operations
                for doc in documents:
                    doc_id = doc.get('id') or f"doc_{added_count}"
                    content = doc.get('content', '')
                    metadata = doc.get('metadata', {})
                    
                    self.index.add_file(
                        file_path=None,
                        text=content,
                        metadata=metadata,
                        reference_id=doc_id
                    )
                    added_count += 1
                
                logger.success(f"Added {added_count} documents via aiXplain")
                return added_count
            else:
                # Use ChromaDB fallback
                if not self.collection:
                    logger.error("No vector store available")
                    return 0
                
                ids = []
                embeddings = []
                contents = []
                metadatas = []
                
                for doc in documents:
                    doc_id = doc.get('id') or f"doc_{len(ids)}"
                    content = doc.get('content', '')
                    metadata = doc.get('metadata', {})
                    
                    embedding = self.create_embedding(content)
                    
                    if embedding:
                        ids.append(doc_id)
                        embeddings.append(embedding)
                        contents.append(content)
                        metadatas.append(metadata)
                
                if ids:
                    self.collection.add(
                        ids=ids,
                        embeddings=embeddings,
                        documents=contents,
                        metadatas=metadatas
                    )
                    logger.success(f"Added {len(ids)} documents via ChromaDB")
                    return len(ids)
                
        except Exception as e:
            logger.error(f"Error in batch add: {str(e)}")
        
        return 0
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Dict = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for documents using aiXplain or ChromaDB
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Metadata filters
            
        Returns:
            list: Relevant documents
        """
        logger.info(f"Searching for: {query}")
        
        try:
            if self.use_aixplain and self.index:
                # Use aiXplain Index search
                results = self.index.search(
                    query=query,
                    number_of_results=top_k
                )
                
                documents = []
                if results and hasattr(results, 'results'):
                    for result in results.results[:top_k]:
                        documents.append({
                            'id': getattr(result, 'reference_id', 'unknown'),
                            'content': getattr(result, 'text', ''),
                            'metadata': getattr(result, 'metadata', {}),
                            'score': getattr(result, 'score', 0)
                        })
                
                logger.success(f"Found {len(documents)} results via aiXplain")
                return documents
            else:
                # Use ChromaDB fallback
                if not self.collection:
                    logger.error("No vector store available")
                    return []
                
                query_embedding = self.create_embedding(query)
                
                if not query_embedding:
                    logger.error("Failed to create query embedding")
                    return []
                
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=filter_metadata if filter_metadata else None
                )
                
                documents = []
                if results['ids'] and len(results['ids']) > 0:
                    for i, doc_id in enumerate(results['ids'][0]):
                        documents.append({
                            'id': doc_id,
                            'content': results['documents'][0][i] if results['documents'] else '',
                            'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                            'distance': results['distances'][0][i] if results['distances'] else 0
                        })
                
                logger.success(f"Found {len(documents)} results via ChromaDB")
                return documents
                
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            return []
    
    def search_by_metadata(
        self,
        filter_metadata: Dict[str, Any],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search documents by metadata filters
        
        Args:
            filter_metadata: Filter conditions
            top_k: Maximum results to return
            
        Returns:
            list: Matching documents
        """
        logger.info(f"Searching by metadata filters")
        
        try:
            results = self.collection.get(
                where=filter_metadata,
                limit=top_k
            )
            
            documents = []
            if results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    documents.append({
                        'id': doc_id,
                        'content': results['documents'][i] if results['documents'] else '',
                        'metadata': results['metadatas'][i] if results['metadatas'] else {}
                    })
            
            logger.success(f"Found {len(documents)} documents by metadata")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching by metadata: {str(e)}")
            return []
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get specific document
        
        Args:
            document_id: Document ID
            
        Returns:
            dict: Document details
        """
        logger.info(f"Retrieving document: {document_id}")
        
        try:
            results = self.collection.get(
                ids=[document_id]
            )
            
            if results['ids']:
                return {
                    'id': results['ids'][0],
                    'content': results['documents'][0] if results['documents'] else '',
                    'metadata': results['metadatas'][0] if results['metadatas'] else {}
                }
            else:
                logger.warning(f"Document not found: {document_id}")
                return {}
                
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            return {}
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete document from database
        
        Args:
            document_id: Document ID
            
        Returns:
            bool: Success status
        """
        logger.info(f"Deleting document: {document_id}")
        
        try:
            self.collection.delete(ids=[document_id])
            logger.success(f"Document deleted: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector database statistics
        
        Returns:
            dict: Database stats
        """
        try:
            count = self.collection.count()
            
            return {
                'total_documents': count,
                'collection_name': self.collection.name,
                'embedding_model': 'all-MiniLM-L6-v2',
                'embedding_dimension': 384,
                'vector_store_path': str(self.config.vector_store_path)
            }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {}
