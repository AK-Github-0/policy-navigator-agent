"""
Retrieval Agent - Handles vector database search
"""

from typing import List, Dict, Any
from loguru import logger
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np


class RetrievalAgent:
    """
    Agent responsible for semantic search in vector database
    Uses embeddings to find most relevant policy documents
    """
    
    def __init__(self, config):
        """
        Initialize retrieval agent with vector store
        
        Args:
            config: Configuration object
        """
        logger.info("Initializing Retrieval Agent")
        
        self.config = config
        
        # Initialize embedding model
        logger.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB client
        logger.info("Connecting to vector database...")
        self.chroma_client = chromadb.PersistentClient(
            path=config.vector_store_path
        )
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(
                name="policy_documents"
            )
            logger.success(f"Loaded collection with {self.collection.count()} documents")
        except Exception as e:
            logger.warning(f"Collection not found, creating new: {str(e)}")
            self.collection = self.chroma_client.create_collection(
                name="policy_documents",
                metadata={"description": "Government policy documents"}
            )
        
        logger.success("Retrieval Agent initialized")
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding vector for text
        
        Args:
            text: Text to embed
            
        Returns:
            list: Embedding vector
        """
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
    
    def add_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict[str, Any]
    ):
        """
        Add a document to the vector store
        
        Args:
            document_id: Unique document identifier
            content: Document text content
            metadata: Document metadata (title, source, date, etc.)
        """
        logger.info(f"Adding document: {document_id}")
        
        try:
            # Create embedding
            embedding = self.create_embedding(content)
            
            # Add to collection
            self.collection.add(
                ids=[document_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata]
            )
            
            logger.success(f"Document added: {document_id}")
            
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            raise
    
    def add_documents_batch(
        self,
        documents: List[Dict[str, Any]]
    ):
        """
        Add multiple documents in batch
        
        Args:
            documents: List of documents with id, content, and metadata
        """
        logger.info(f"Adding {len(documents)} documents in batch")
        
        try:
            ids = []
            contents = []
            metadatas = []
            embeddings = []
            
            for doc in documents:
                ids.append(doc['id'])
                contents.append(doc['content'])
                metadatas.append(doc.get('metadata', {}))
                
                # Create embedding
                embedding = self.create_embedding(doc['content'])
                embeddings.append(embedding)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas
            )
            
            logger.success(f"Added {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error adding documents batch: {str(e)}")
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            list: List of relevant documents with scores
        """
        logger.info(f"Searching for: {query}")
        
        try:
            # Create query embedding
            query_embedding = self.create_embedding(query)
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None,
                        'score': 1 - (results['distances'][0][i] if 'distances' in results else 0)
                    })
            
            logger.success(f"Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            return []
    
    def search_by_metadata(
        self,
        filters: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search documents by metadata filters
        
        Args:
            filters: Metadata filters (e.g., {'policy_type': 'privacy'})
            limit: Maximum results
            
        Returns:
            list: Matching documents
        """
        logger.info(f"Searching by metadata: {filters}")
        
        try:
            results = self.collection.get(
                where=filters,
                limit=limit
            )
            
            formatted_results = []
            
            if results['ids']:
                for i in range(len(results['ids'])):
                    formatted_results.append({
                        'id': results['ids'][i],
                        'content': results['documents'][i],
                        'metadata': results['metadatas'][i]
                    })
            
            logger.success(f"Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching by metadata: {str(e)}")
            return []
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific document by ID
        
        Args:
            document_id: Document identifier
            
        Returns:
            dict: Document data
        """
        logger.info(f"Retrieving document: {document_id}")
        
        try:
            results = self.collection.get(
                ids=[document_id]
            )
            
            if results['ids']:
                return {
                    'id': results['ids'][0],
                    'content': results['documents'][0],
                    'metadata': results['metadatas'][0]
                }
            else:
                logger.warning(f"Document not found: {document_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            return None
    
    def delete_document(self, document_id: str):
        """
        Delete a document from vector store
        
        Args:
            document_id: Document identifier
        """
        logger.info(f"Deleting document: {document_id}")
        
        try:
            self.collection.delete(ids=[document_id])
            logger.success(f"Document deleted: {document_id}")
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store
        
        Returns:
            dict: Statistics
        """
        try:
            count = self.collection.count()
            
            return {
                'total_documents': count,
                'collection_name': self.collection.name,
                'embedding_dimension': 384  # all-MiniLM-L6-v2 dimension
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {}