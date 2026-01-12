"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# Document Schemas
class DocumentUploadResponse(BaseModel):
    """Response schema for document upload."""
    id: str
    filename: str
    file_size: int
    uploaded_at: datetime
    processed: bool
    
    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """Schema for listing documents."""
    documents: List[DocumentUploadResponse]


# Workflow Schemas
class WorkflowCreate(BaseModel):
    """Schema for creating a new workflow."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)


class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    nodes: Optional[List[Dict[str, Any]]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    is_valid: Optional[bool] = None


class WorkflowResponse(BaseModel):
    """Response schema for workflow."""
    id: str
    name: str
    description: Optional[str]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    is_valid: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowList(BaseModel):
    """Schema for listing workflows."""
    workflows: List[WorkflowResponse]


# Chat Schemas
class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message."""
    content: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    """Response schema for chat message."""
    id: str
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatExecuteRequest(BaseModel):
    """Schema for executing a workflow with a query."""
    workflow_id: str
    query: str = Field(..., min_length=1)
    session_id: Optional[str] = None  # For continuing a conversation


class ChatExecuteResponse(BaseModel):
    """Response schema for chat execution."""
    session_id: str
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse


class ChatSessionResponse(BaseModel):
    """Response schema for chat session."""
    id: str
    workflow_id: str
    created_at: datetime
    messages: List[ChatMessageResponse]
    
    class Config:
        from_attributes = True


# Health Check Schema
class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str
    database: str
    vector_store: str
