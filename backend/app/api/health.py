"""Health check endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.schemas import HealthResponse
from app.vector_store.chromadb_client import chroma_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Check health of the application and its dependencies.
    
    Args:
        db: Database session
        
    Returns:
        Health status
    """
    # Check database
    db_status = "healthy"
    try:
        db.execute("SELECT 1")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check vector store
    vector_status = "healthy"
    try:
        chroma_client.client.heartbeat()
    except Exception as e:
        logger.error(f"Vector store health check failed: {e}")
        vector_status = "unhealthy"
    
    overall_status = "healthy" if db_status == "healthy" and vector_status == "healthy" else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        database=db_status,
        vector_store=vector_status
    )
