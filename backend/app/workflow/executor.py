"""Workflow executor for running workflows with user queries."""
from app.workflow.validator import WorkflowValidator
from app.components import create_component
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """Executes workflows by running components in order."""
    
    def __init__(self, workflow_data: Dict[str, Any]):
        """
        Initialize workflow executor.
        
        Args:
            workflow_data: Workflow data including nodes and edges
        """
        self.workflow_id = workflow_data.get("id", "unknown")
        self.nodes = workflow_data.get("nodes", [])
        self.edges = workflow_data.get("edges", [])
        self.validator = WorkflowValidator(self.nodes, self.edges)
        self.components = {}
        self.execution_log = []
    
    async def execute(self, query: str) -> Dict[str, Any]:
        """
        Execute the workflow with a user query.
        
        Args:
            query: User query to process
            
        Returns:
            Execution result with final output and logs
        """
        logger.info(f"Executing workflow {self.workflow_id} with query: {query[:100]}...")
        
        # Validate workflow
        is_valid, error_msg = self.validator.validate()
        if not is_valid:
            logger.error(f"Workflow validation failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "output": None,
                "execution_log": []
            }
        
        # Get execution order
        execution_order = self.validator.get_execution_order()
        logger.info(f"Execution order: {execution_order}")
        
        # Initialize components
        self._initialize_components()
        
        # Execute components in order
        try:
            current_data = {"query": query}
            
            for node_id in execution_order:
                component = self.components[node_id]
                
                # Log execution start
                self._log_execution(node_id, "started", current_data)
                logger.info(f"Executing component: {node_id} ({component.component_type})")
                
                # Execute component
                output = await component.execute(current_data)
                
                # Log execution completion
                self._log_execution(node_id, "completed", output)
                
                # Pass output to next component
                current_data = output
            
            # Extract final response
            final_output = current_data.get("response", current_data.get("output", str(current_data)))
            
            logger.info(f"Workflow execution completed successfully")
            
            return {
                "success": True,
                "output": final_output,
                "execution_log": self.execution_log,
                "full_output": current_data
            }
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "output": None,
                "execution_log": self.execution_log
            }
    
    def _initialize_components(self):
        """Initialize all component instances."""
        for node in self.nodes:
            node_id = node["id"]
            node_data = node.get("data", {})
            
            try:
                component = create_component(node_id, node_data)
                self.components[node_id] = component
                logger.info(f"Initialized component: {node_id}")
            except Exception as e:
                logger.error(f"Error initializing component {node_id}: {e}")
                raise
    
    def _log_execution(self, node_id: str, status: str, data: Any):
        """
        Log execution step.
        
        Args:
            node_id: Node identifier
            status: Execution status (started/completed/error)
            data: Execution data
        """
        log_entry = {
            "node_id": node_id,
            "status": status,
            "timestamp":  str(logging.time.time()) if hasattr(logging, 'time') else "",
            "data_preview": str(data)[:200] if data else ""
        }
        self.execution_log.append(log_entry)
