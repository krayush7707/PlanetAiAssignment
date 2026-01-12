"""API endpoints for document management."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Document
from app.database.schemas import DocumentUploadResponse, DocumentList
from app.components.knowledgebase import KnowledgeBaseComponent
import os
import uuid
import aiofiles
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document.
    
    Args:
        file: PDF file to upload
        db: Database session
        
    Returns:
        Document metadata
    """
    logger.info(f"Uploading document: {file.filename}")
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        saved_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        file_size = len(content)
        
        # Create database record
        doc = Document(
            id=file_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            processed=False
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Process document in background (for now, process immediately)
        collection_name = f"doc_{file_id}"
        kb_component = KnowledgeBaseComponent(
            node_id=file_id,
            config={"type": "knowledge_base", "collection_name": collection_name}
        )
        
        result = await kb_component.process_document(file_path, file.filename)
        
        if result.get("success"):
            doc.processed = True
            doc.chunk_count = result.get("chunk_count", 0)
            doc.collection_name = collection_name
            db.commit()
            db.refresh(doc)
        
        logger.info(f"Document uploaded and processed: {file.filename}")
        return doc
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=DocumentList)
async def list_documents(db: Session = Depends(get_db)):
    """
    List all uploaded documents.
    
    Args:
        db: Database session
        
    Returns:
        List of documents
    """
    documents = db.query(Document).all()
    return {"documents": documents}


@router.get("/{document_id}", response_model=DocumentUploadResponse)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """
    Get document by ID.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Document metadata
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """
    Delete a document.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Success message
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from filesystem
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    
    # Delete from database
    db.delete(doc)
    db.commit()
    
    logger.info(f"Document deleted: {document_id}")
    return {"message": "Document deleted successfully"}
