"""API endpoints for chat execution."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Workflow, ChatSession, ChatMessage
from app.database.schemas import (
    ChatExecuteRequest,
    ChatExecuteResponse,
    ChatSessionResponse,
    ChatMessageResponse
)
from app.workflow.executor import WorkflowExecutor
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/execute", response_model=ChatExecuteResponse)
async def execute_chat(
    request: ChatExecuteRequest,
    db: Session = Depends(get_db)
):
    """
    Execute a workflow with a chat query.
    
    Args:
        request: Chat execution request
        db: Database session
        
    Returns:
        Chat execution response with user and assistant messages
    """
    logger.info(f"Executing chat for workflow: {request.workflow_id}")
    
    # Get workflow
    workflow = db.query(Workflow).filter(Workflow.id == request.workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check if workflow is valid
    if not workflow.is_valid:
        raise HTTPException(status_code=400, detail="Workflow is not valid. Please validate it first.")
    
    try:
        # Get or create chat session
        session_id = request.session_id
        if session_id:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if not session:
                raise HTTPException(status_code=404, detail="Chat session not found")
        else:
            # Create new session
            session = ChatSession(workflow_id=request.workflow_id)
            db.add(session)
            db.commit()
            db.refresh(session)
            session_id = session.id
        
        # Create user message
        user_message = ChatMessage(
            session_id=session_id,
            role="user",
            content=request.query
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # Execute workflow
        workflow_data = {
            "id": workflow.id,
            "nodes": workflow.nodes,
            "edges": workflow.edges
        }
        executor = WorkflowExecutor(workflow_data)
        result = await executor.execute(request.query)
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error during execution")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Create assistant message
        assistant_content = result.get("output", "No response generated")
        assistant_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=assistant_content
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        logger.info(f"Chat execution completed for session: {session_id}")
        
        return ChatExecuteResponse(
            session_id=session_id,
            user_message=user_message,
            assistant_message=assistant_message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(session_id: str, db: Session = Depends(get_db)):
    """
    Get chat session with all messages.
    
    Args:
        session_id: Chat session ID
        db: Database session
        
    Returns:
        Chat session with messages
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Get messages ordered by creation time
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return ChatSessionResponse(
        id=session.id,
        workflow_id=session.workflow_id,
        created_at=session.created_at,
        messages=messages
    )


@router.get("/workflows/{workflow_id}/sessions")
async def list_workflow_sessions(workflow_id: str, db: Session = Depends(get_db)):
    """
    List all chat sessions for a workflow.
    
    Args:
        workflow_id: Workflow ID
        db: Database session
        
    Returns:
        List of chat sessions
    """
    sessions = db.query(ChatSession).filter(
        ChatSession.workflow_id == workflow_id
    ).order_by(ChatSession.created_at.desc()).all()
    
    return {"sessions": [{"id": s.id, "created_at": s.created_at} for s in sessions]}


@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str, db: Session = Depends(get_db)):
    """
    Delete a chat session and all its messages.
    
    Args:
        session_id: Chat session ID
        db: Database session
        
    Returns:
        Success message
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    db.delete(session)
    db.commit()
    
    logger.info(f"Chat session deleted: {session_id}")
    return {"message": "Chat session deleted successfully"}
