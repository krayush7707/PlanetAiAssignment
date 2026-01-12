"""API endpoints for workflow management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Workflow
from app.database.schemas import (
    WorkflowCreate,
    WorkflowResponse,
    WorkflowUpdate,
    WorkflowList
)
from app.workflow.validator import WorkflowValidator
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new workflow.
    
    Args:
        workflow_data: Workflow data
        db: Database session
        
    Returns:
        Created workflow
    """
    logger.info(f"Creating workflow: {workflow_data.name}")
    
    # Validate workflow if it has nodes and edges
    is_valid = False
    if workflow_data.nodes and workflow_data.edges:
        validator = WorkflowValidator(workflow_data.nodes, workflow_data.edges)
        is_valid, error_msg = validator.validate()
        if not is_valid:
            logger.warning(f"Workflow validation failed: {error_msg}")
    
    try:
        workflow = Workflow(
            name=workflow_data.name,
            description=workflow_data.description,
            nodes=workflow_data.nodes,
            edges=workflow_data.edges,
            is_valid=is_valid
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        
        logger.info(f"Workflow created: {workflow.id}")
        return workflow
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=WorkflowList)
async def list_workflows(db: Session = Depends(get_db)):
    """
    List all workflows.
    
    Args:
        db: Database session
        
    Returns:
        List of workflows
    """
    workflows = db.query(Workflow).order_by(Workflow.created_at.desc()).all()
    return {"workflows": workflows}


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """
    Get workflow by ID.
    
    Args:
        workflow_id: Workflow ID
        db: Database session
        
    Returns:
        Workflow data
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_data: WorkflowUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a workflow.
    
    Args:
        workflow_id: Workflow ID
        workflow_data: Updated workflow data
        db: Database session
        
    Returns:
        Updated workflow
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Update fields
    if workflow_data.name is not None:
        workflow.name = workflow_data.name
    if workflow_data.description is not None:
        workflow.description = workflow_data.description
    if workflow_data.nodes is not None:
        workflow.nodes = workflow_data.nodes
    if workflow_data.edges is not None:
        workflow.edges = workflow_data.edges
    
    # Revalidate workflow if nodes/edges were updated
    if workflow_data.nodes is not None or workflow_data.edges is not None:
        validator = WorkflowValidator(workflow.nodes, workflow.edges)
        is_valid, error_msg = validator.validate()
        workflow.is_valid = is_valid
        if not is_valid:
            logger.warning(f"Workflow validation failed: {error_msg}")
    
    if workflow_data.is_valid is not None:
        workflow.is_valid = workflow_data.is_valid
    
    db.commit()
    db.refresh(workflow)
    
    logger.info(f"Workflow updated: {workflow_id}")
    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """
    Delete a workflow.
    
    Args:
        workflow_id: Workflow ID
        db: Database session
        
    Returns:
        Success message
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    
    logger.info(f"Workflow deleted: {workflow_id}")
    return {"message": "Workflow deleted successfully"}


@router.post("/{workflow_id}/validate")
async def validate_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """
    Validate a workflow.
    
    Args:
        workflow_id: Workflow ID
        db: Database session
        
    Returns:
        Validation result
    """
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    validator = WorkflowValidator(workflow.nodes, workflow.edges)
    is_valid, message = validator.validate()
    
    # Update workflow validation status
    workflow.is_valid = is_valid
    db.commit()
    
    return {
        "workflow_id": workflow_id,
        "is_valid": is_valid,
        "message": message
    }
