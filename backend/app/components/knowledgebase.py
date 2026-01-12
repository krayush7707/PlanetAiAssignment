"""Knowledge Base component for document processing and RAG."""
from app.components.base import BaseComponent
from app.vector_store.chromadb_client import chroma_client
from typing import Any, Optional, Dict, List
import fitz  # PyMuPDF
import os
import logging
from openai import OpenAI
from config import settings

logger = logging.getLogger(__name__)


class KnowledgeBaseComponent(BaseComponent):
    """Component for document processing, embedding generation, and retrieval."""
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        """Initialize Knowledge Base component."""
        super().__init__(node_id, config)
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.collection_name = config.get("collection_name", f"kb_{node_id}")
        self.chunk_size = config.get("chunk_size", 1000)
        self.chunk_overlap = config.get("chunk_overlap", 200)
        self.top_k = config.get("top_k", 5)
    
    async def execute(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Execute knowledge base retrieval.
        
        Args:
            input_data: Dictionary containing 'query' for retrieval
            
        Returns:
            Dictionary with retrieved context and original query
        """
        query = ""
        if isinstance(input_data, dict):
            query = input_data.get("query", "")
        elif isinstance(input_data, str):
            query = input_data
        
        if not query:
            logger.warning("No query provided to Knowledge Base component")
            return {"context": "", "query": query, "documents": []}
        
        logger.info(f"Knowledge Base retrieving context for query: {query[:100]}...")
        
        # Check if collection exists
        if not chroma_client.collection_exists(self.collection_name):
            logger.warning(f"Collection '{self.collection_name}' does not exist")
            return {"context": "", "query": query, "documents": []}
        
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Retrieve relevant documents
            results = chroma_client.query_embeddings(
                collection_name=self.collection_name,
                query_embedding=query_embedding,
                n_results=self.top_k
            )
            
            # Extract documents
            documents = results.get("documents", [[]])[0]
            distances = results.get("distances", [[]])[0]
            
            # Combine documents into context
            context = "\n\n".join(documents)
            
            logger.info(f"Retrieved {len(documents)} relevant chunks")
            
            return {
                "context": context,
                "query": query,
                "documents": documents,
                "distances": distances,
                "component_type": "knowledge_base",
                "node_id": self.node_id
            }
        except Exception as e:
            logger.error(f"Error retrieving from knowledge base: {e}")
            return {"context": "", "query": query, "documents": [], "error": str(e)}
    
    async def process_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Process a document: extract text, chunk, embed, and store.
        
        Args:
            file_path: Path to the document file
            filename: Original filename
            
        Returns:
            Processing result with chunk count and collection name
        """
        logger.info(f"Processing document: {filename}")
        
        try:
            # Extract text from PDF
            text = self._extract_text_from_pdf(file_path)
            
            # Chunk text
            chunks = self._chunk_text(text)
            logger.info(f"Created {len(chunks)} chunks from document")
            
            # Generate embeddings
            embeddings = []
            for chunk in chunks:
                embedding = await self._generate_embedding(chunk)
                embeddings.append(embedding)
            
            # Prepare metadata
            metadatas = [
                {"filename": filename, "chunk_idx": i, "source": file_path}
                for i in range(len(chunks))
            ]
            
            # Generate IDs
            ids = [f"{self.collection_name}_{i}" for i in range(len(chunks))]
            
            # Store in ChromaDB
            chroma_client.add_embeddings(
                collection_name=self.collection_name,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully processed {filename} with {len(chunks)} chunks")
            
            return {
                "success": True,
                "chunk_count": len(chunks),
                "collection_name": self.collection_name,
                "filename": filename
            }
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using PyMuPDF."""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Chunk text into smaller pieces with overlap.
        
        Args:
            text: Full text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using OpenAI API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def validate_config(self) -> bool:
        """Validate knowledge base configuration."""
        # Check if collection name is set
        if not self.collection_name:
            logger.error("Collection name is required")
            return False
        return True
