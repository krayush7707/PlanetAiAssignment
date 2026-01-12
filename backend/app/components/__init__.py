"""Factory for creating component instances."""
from app.components.base import BaseComponent
from app.components.user_query import UserQueryComponent
from app.components.knowledgebase import KnowledgeBaseComponent
from app.components.llm_engine import LLMEngineComponent
from app.components.output import OutputComponent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


COMPONENT_REGISTRY = {
    "userQuery": UserQueryComponent,
    "user_query": UserQueryComponent,
    "input": UserQueryComponent,
    "knowledgeBase": KnowledgeBaseComponent,
    "knowledge_base": KnowledgeBaseComponent,
    "llmEngine": LLMEngineComponent,
    "llm_engine": LLMEngineComponent,
    "llm": LLMEngineComponent,
    "output": OutputComponent
}


def create_component(node_id: str, node_data: Dict[str, Any]) -> BaseComponent:
    """
    Create a component instance based on node data.
    
    Args:
        node_id: Unique node identifier
        node_data: Node configuration data
        
    Returns:
        Component instance
        
    Raises:
        ValueError: If component type is not recognized
    """
    component_type = node_data.get("type", "").lower()
    
    if component_type not in COMPONENT_REGISTRY:
        logger.error(f"Unknown component type: {component_type}")
        raise ValueError(f"Unknown component type: {component_type}")
    
    component_class = COMPONENT_REGISTRY[component_type]
    return component_class(node_id, node_data)
