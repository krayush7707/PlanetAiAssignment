"""ChromaDB client for vector store operations."""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)


class ChromaDBClient:
    """Client for interacting with ChromaDB vector store."""
    
    def __init__(self):
        """Initialize ChromaDB client."""
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=settings.chroma_persist_dir,
                anonymized_telemetry=False
            )
        )
        logger.info(f"ChromaDB initialized at {settings.chroma_persist_dir}")
    
    def create_collection(self, collection_name: str) -> chromadb.Collection:
        """
        Create or get a collection in ChromaDB.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            ChromaDB collection object
        """
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Document embeddings collection"}
            )
            logger.info(f"Collection '{collection_name}' created/retrieved")
            return collection
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def add_embeddings(
        self,
        collection_name: str,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add embeddings to a collection.
        
        Args:
            collection_name: Name of the collection
            embeddings: List of embedding vectors
            documents: List of text chunks
            metadatas: List of metadata dictionaries
            ids: List of unique IDs for each embedding
        """
        try:
            collection = self.create_collection(collection_name)
            collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(embeddings)} embeddings to '{collection_name}'")
        except Exception as e:
            logger.error(f"Error adding embeddings: {e}")
            raise
    
    def query_embeddings(
        self,
        collection_name: str,
        query_embedding: List[float],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Query embeddings from a collection.
        
        Args:
            collection_name: Name of the collection
            query_embedding: Query embedding vector
            n_results: Number of results to return
            
        Returns:
            Query results containing documents, distances, and metadata
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            logger.info(f"Queried '{collection_name}', found {len(results['documents'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Error querying embeddings: {e}")
            raise
    
    def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection.
        
        Args:
            collection_name: Name of the collection to delete
        """
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Collection '{collection_name}' deleted")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise
    
    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if collection exists, False otherwise
        """
        try:
            collections = self.client.list_collections()
            return any(col.name == collection_name for col in collections)
        except Exception as e:
            logger.error(f"Error checking collection existence: {e}")
            return False


# Global ChromaDB client instance
chroma_client = ChromaDBClient()
