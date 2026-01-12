"""Workflow validator for checking workflow structure and configuration."""
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class WorkflowValidator:
    """Validates workflow structure and component configurations."""
    
    def __init__(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]):
        """
        Initialize workflow validator.
        
        Args:
            nodes: List of workflow nodes
            edges: List of workflow edges
        """
        self.nodes = nodes
        self.edges = edges
        self.node_map = {node["id"]: node for node in nodes}
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate the workflow.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if workflow has nodes
        if not self.nodes:
            return False, "Workflow must have at least one component"
        
        # Check if workflow has edges (for multi-node workflows)
        if len(self.nodes) > 1 and not self.edges:
            return False, "Workflow components must be connected"
        
        # Validate node types
        valid, msg = self._validate_node_types()
        if not valid:
            return False, msg
        
        # Validate connections
        valid, msg = self._validate_connections()
        if not valid:
            return False, msg
        
        # Check for cycles
        valid, msg = self._check_for_cycles()
        if not valid:
            return False, msg
        
        # Validate component configurations
        valid, msg = self._validate_component_configs()
        if not valid:
            return False, msg
        
        # Check workflow flow (Input -> ... -> Output)
        valid, msg = self._validate_workflow_flow()
        if not valid:
            return False, msg
        
        logger.info("Workflow validation passed")
        return True, "Workflow is valid"
    
    def _validate_node_types(self) -> Tuple[bool, str]:
        """Validate that all nodes have recognized types."""
        valid_types = {
            "userquery", "user_query", "input",
            "knowledgebase", "knowledge_base",
            "llmengine", "llm_engine", "llm",
            "output"
        }
        
        for node in self.nodes:
            node_type = node.get("data", {}).get("type", "").lower()
            if not node_type:
                return False, f"Node {node['id']} is missing a type"
            if node_type not in valid_types:
                return False, f"Unknown component type: {node_type}"
        
        return True, ""
    
    def _validate_connections(self) -> Tuple[bool, str]:
        """Validate that all edges connect valid nodes."""
        node_ids = {node["id"] for node in self.nodes}
        
        for edge in self.edges:
            source = edge.get("source")
            target = edge.get("target")
            
            if source not in node_ids:
                return False, f"Edge references non-existent source node: {source}"
            if target not in node_ids:
                return False, f"Edge references non-existent target node: {target}"
        
        return True, ""
    
    def _check_for_cycles(self) -> Tuple[bool, str]:
        """Check for cycles in the workflow graph."""
        # Build adjacency list
        graph = {node["id"]: [] for node in self.nodes}
        for edge in self.edges:
            graph[edge["source"]].append(edge["target"])
        
        # DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for neighbor in graph.get(node_id, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in graph:
            if node_id not in visited:
                if has_cycle(node_id):
                    return False, "Workflow contains a cycle"
        
        return True, ""
    
    def _validate_component_configs(self) -> Tuple[bool, str]:
        """Validate that components have required configurations."""
        for node in self.nodes:
            node_type = node.get("data", {}).get("type", "").lower()
            node_data = node.get("data", {})
            
            # LLM Engine must have model specified
            if node_type in ["llmengine", "llm_engine", "llm"]:
                if not node_data.get("model"):
                    return False, f"LLM Engine node {node['id']} must have a model specified"
            
            # Knowledge Base should have collection name
            if node_type in ["knowledgebase", "knowledge_base"]:
                if not node_data.get("collection_name"):
                    logger.warning(f"Knowledge Base node {node['id']} should have a collection_name")
        
        return True, ""
    
    def _validate_workflow_flow(self) -> Tuple[bool, str]:
        """Validate that workflow has proper input and output."""
        # Check for Input/User Query component
        has_input = any(
            node.get("data", {}).get("type", "").lower() in ["userquery", "user_query", "input"]
            for node in self.nodes
        )
        
        # Check for Output component
        has_output = any(
            node.get("data", {}).get("type", "").lower() == "output"
            for node in self.nodes
        )
        
        if not has_input:
            return False, "Workflow must have an Input/User Query component"
        
        if not has_output:
            return False, "Workflow must have an Output component"
        
        return True, ""
    
    def get_execution_order(self) -> List[str]:
        """
        Get nodes in topological order for execution.
        
        Returns:
            List of node IDs in execution order
        """
        # Build adjacency list and in-degree map
        graph = {node["id"]: [] for node in self.nodes}
        in_degree = {node["id"]: 0 for node in self.nodes}
        
        for edge in self.edges:
            graph[edge["source"]].append(edge["target"])
            in_degree[edge["target"]] += 1
        
        # Topological sort using Kahn's algorithm
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        order = []
        
        while queue:
            node_id = queue.pop(0)
            order.append(node_id)
            
            for neighbor in graph[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return order
