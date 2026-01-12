"""Output component for returning final results."""
from app.components.base import BaseComponent
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class OutputComponent(BaseComponent):
    """Component for formatting and returning final output."""
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        """Initialize Output component."""
        super().__init__(node_id, config)
        self.output_format = config.get("output_format", "text")
    
    async def execute(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Execute output component.
        
        Args:
            input_data: Data from previous component (typically LLM response)
            
        Returns:
            Formatted output ready for display
        """
        logger.info(f"Output component processing data")
        
        # Extract response from input
        response_text = ""
        if isinstance(input_data, dict):
            response_text = input_data.get("response", str(input_data))
        elif isinstance(input_data, str):
            response_text = input_data
        else:
            response_text = str(input_data)
        
        # Format output based on configuration
        if self.output_format == "text":
            output = response_text
        elif self.output_format == "json":
            output = {"response": response_text}
        else:
            output = response_text
        
        logger.info(f"Output component generated: {len(str(output))} characters")
        
        return {
            "output": output,
            "response": response_text,
            "component_type": "output",
            "node_id": self.node_id
        }
    
    def validate_config(self) -> bool:
        """Validate output configuration."""
        # Output component is simple and always valid
        return True
