"""Base component interface for workflow components."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseComponent(ABC):
    """Base class for all workflow components."""
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        """
        Initialize a component.
        
        Args:
            node_id: Unique identifier for this component instance
            config: Configuration dictionary from the node data
        """
        self.node_id = node_id
        self.config = config
        self.component_type = config.get("type", "unknown")
        logger.info(f"Initialized {self.component_type} component: {node_id}")
    
    @abstractmethod
    async def execute(self, input_data: Optional[Any] = None) -> Any:
        """
        Execute the component logic.
        
        Args:
            input_data: Input data from previous component in workflow
            
        Returns:
            Output data to pass to next component
        """
        pass
    
    def validate_config(self) -> bool:
        """
        Validate component configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        return True
    
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Get the output schema for this component.
        
        Returns:
            Dictionary describing the output structure
        """
        return {"type": "any"}
