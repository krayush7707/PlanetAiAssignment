"""User Query component for accepting user input."""
from app.components.base import BaseComponent
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class UserQueryComponent(BaseComponent):
    """Component for handling user query input."""
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        """Initialize User Query component."""
        super().__init__(node_id, config)
        self.query_text = ""
    
    async def execute(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Execute user query component.
        
        Args:
            input_data: User query string or dict with 'query' key
            
        Returns:
            Dictionary with query text
        """
        # Extract query from input_data
        if isinstance(input_data, str):
            self.query_text = input_data
        elif isinstance(input_data, dict) and "query" in input_data:
            self.query_text = input_data["query"]
        else:
            self.query_text = input_data or ""
        
        logger.info(f"User Query component received: {self.query_text[:100]}...")
        
        return {
            "query": self.query_text,
            "component_type": "user_query",
            "node_id": self.node_id
        }
    
    def validate_config(self) -> bool:
        """Validate user query configuration."""
        # User query component doesn't need special configuration
        return True
