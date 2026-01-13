"""
Script to create vector index from policy documents
"""

import os
from pathlib import Path
from loguru import logger
from agents.retrieval_agent import RetrievalAgent
from utils.utils_config import Config

# Setup logging
logger.remove()
logger.add("logs/indexing_{time}.log", level="INFO")


class IndexBuilder:
    """Build vector index from policy documents"""
    
    def __init__(self):
        self.config = Config()
        self.retrieval_agent = RetrievalAgent(self.config)
        
        self.raw_data_dir = Path("data/raw")
        self.processed_data_dir = Path("data/processed")
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Index Builder initialized")
    
    def process_text_documents(self):
        """Process text documents and add to vector store"""
        logger.info("Processing text documents...")
        
        text_files = list(self.raw_data_dir.glob('*.txt'))
        
        if not text_files:
            logger.warning("No text files found in data/raw")
            return 0
        
        documents = []
        
        for file_path in text_files:
            try:
                logger.info(f"Processing: {file_path.name}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title from content
                title = file_path.stem
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('Title:'):
                        title = line.replace('Title:', '').strip()
                        break
                
                # Create document entry
                doc_id = f"doc_{file_path.stem}"
                
                metadata = {
                    'title': title,
                    'source': file_path.name,
                    'type': 'policy_document',
                    'file_path': str(file_path)
                }
                
                documents.append({
                    'id': doc_id,
                    'content': content,
                    'metadata': metadata
                })
                
                logger.success(f"Processed: {title}")
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
        
        # Add documents to vector store in batch
        if documents:
            logger.info(f"Adding {len(documents)} documents to vector store...")
            count = self.retrieval_agent.add_documents_batch(documents)
            logger.success(f"Added {count} documents to vector index")
        
        return len(documents)
    
    def build_index(self):
        """Main method to build complete index"""
        logger.info("Starting index building process...")
        
        try:
            # Process text documents
            text_count = self.process_text_documents()
            
            # Get statistics
            stats = self.retrieval_agent.get_stats()
            
            # Print summary
            logger.success("Index building complete!")
            logger.info("\n" + "="*60)
            logger.info("INDEXING SUMMARY")
            logger.info("="*60)
            logger.info(f"Text documents processed: {text_count}")
            logger.info(f"\nVector Store:")
            logger.info(f"  Total documents: {stats.get('total_documents', 0)}")
            logger.info(f"  Collection: {stats.get('collection_name', 'N/A')}")
            logger.info(f"  Embedding model: {stats.get('embedding_model', 'N/A')}")
            logger.info(f"  Store path: {stats.get('vector_store_path', 'N/A')}")
            logger.info("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")
            return False


def main():
    """Main execution"""
    print("\n🔨 Building Policy Navigator Index...\n")
    
    builder = IndexBuilder()
    success = builder.build_index()
    
    if success:
        print("\n✅ Index building complete!")
        print("\nNext steps:")
        print("  1. Test queries: python main.py interactive")
        print("  2. Start web UI: streamlit run app.py")
    else:
        print("\n❌ Index building failed. Check logs for details.")


if __name__ == '__main__':
    main()