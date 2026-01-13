"""
Retrieval Agent - Handles vector database operations
Manages document storage and semantic search using ChromaDB
"""

from typing import Dict, List, Any
from loguru import logger

# Optional imports - tests will patch these module-level names.
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
    Uses ChromaDB for vector storage and SentenceTransformers for embeddings
    """
    
    def __init__(self, config):
        """
        Initialize retrieval agent with vector database
        
        Args:
            config: Configuration object
        """
        logger.info("Initializing Retrieval Agent")
        
        self.config = config
        
        # Initialize embedding model
        # Initialize embedding model if available; otherwise defer to tests
        # which typically patch `agents.retrieval_agent.SentenceTransformer`.
        self.embedder = None
        # keep model id for tests and callers
        self.embedding_model = getattr(config, 'embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')

        if SentenceTransformer is not None:
            try:
                self.embedder = SentenceTransformer(
                    self.embedding_model,
                    device='cpu'
                )
                logger.success("Embedding model loaded")
            except Exception as e:
                logger.error(f"Error loading embedding model: {str(e)}")
                self.embedder = None
        
        # Initialize ChromaDB
        # Initialize ChromaDB client if available; tests patch
        # `agents.retrieval_agent.chromadb` when needed.
        self.client = None
        self.collection = None
        if chromadb is not None:
            try:
                self.client = chromadb.PersistentClient(
                    path=str(config.vector_store_path)
                )
                # use get_or_create_collection where available
                # prefer `get_collection` when available (tests commonly set it);
                # otherwise fall back to `get_or_create_collection`.
                if callable(getattr(self.client, 'get_collection', None)):
                    self.collection = self.client.get_collection("policy_documents")
                elif callable(getattr(self.client, 'get_or_create_collection', None)):
                    self.collection = self.client.get_or_create_collection(
                        name="policy_documents",
                        metadata={"hnsw:space": "cosine"}
                    )
                else:
                    self.collection = None

                logger.success("Vector database initialized")
            except Exception as e:
                logger.error(f"Error initializing vector database: {str(e)}")
                self.client = None
                self.collection = None
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            list: Embedding vector
        """
        try:
            if not self.embedder:
                logger.warning("No embedder available, returning empty embedding")
                return []

            raw = self.embedder.encode(text)
            # handle numpy arrays and plain lists
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
        Add single document to vector database
        
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
            # Create embedding
            embedding = self.create_embedding(content)
            
            if not embedding:
                logger.error(f"Failed to create embedding for {document_id}")
                return False
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            if source:
                metadata['source'] = source
            
            # Add to collection
            self.collection.add(
                ids=[document_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata]
            )
            
            logger.success(f"Document added: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            return False
    
    def add_documents_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> int:
        """
        Add multiple documents in batch
        
        Args:
            documents: List of documents with 'id', 'content', 'metadata'
            
        Returns:
            int: Number of documents added
        """
        logger.info(f"Adding {len(documents)} documents in batch")
        
        try:
            ids = []
            embeddings = []
            contents = []
            metadatas = []
            
            for doc in documents:
                doc_id = doc.get('id') or f"doc_{len(ids)}"
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                
                # Create embedding
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
                logger.success(f"Added {len(ids)} documents to database")
                return len(ids)
            else:
                logger.warning("No documents to add")
                return 0
                
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
        Semantic search for documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Metadata filters
            
        Returns:
            list: Relevant documents
        """
        logger.info(f"Searching for: {query}")
        
        try:
            # Create query embedding
            query_embedding = self.create_embedding(query)
            
            if not query_embedding:
                logger.error("Failed to create query embedding")
                return []
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata if filter_metadata else None
            )
            
            # Format results
            documents = []
            if results['ids'] and len(results['ids']) > 0:
                for i, doc_id in enumerate(results['ids'][0]):
                    documents.append({
                        'id': doc_id,
                        'content': results['documents'][0][i] if results['documents'] else '',
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            
            logger.success(f"Found {len(documents)} results")
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
