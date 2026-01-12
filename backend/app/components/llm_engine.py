"""LLM Engine component for generating responses using OpenAI GPT."""
from app.components.base import BaseComponent
from typing import Any, Optional, Dict
import logging
from openai import OpenAI
from config import settings
from serpapi import GoogleSearch

logger = logging.getLogger(__name__)


class LLMEngineComponent(BaseComponent):
    """Component for LLM-based response generation."""
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        """Initialize LLM Engine component."""
        super().__init__(node_id, config)
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.model = config.get("model", "gpt-4o-mini")
        self.temperature = config.get("temperature", 0.7)
        self.custom_prompt = config.get("custom_prompt", "")
        self.use_web_search = config.get("use_web_search", False)
        self.max_tokens = config.get("max_tokens", 1000)
    
    async def execute(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Execute LLM generation.
        
        Args:
            input_data: Dictionary containing 'query' and optional 'context'
            
        Returns:
            Dictionary with generated response
        """
        query = ""
        context = ""
        
        if isinstance(input_data, dict):
            query = input_data.get("query", "")
            context = input_data.get("context", "")
        elif isinstance(input_data, str):
            query = input_data
        
        if not query:
            logger.warning("No query provided to LLM Engine")
            return {"response": "No query provided", "query": query}
        
        logger.info(f"LLM Engine processing query: {query[:100]}...")
        
        try:
            # Optionally fetch web search results
            web_search_context = ""
            if self.use_web_search:
                web_search_context = await self._perform_web_search(query)
            
            # Build the prompt
            prompt = self._build_prompt(query, context, web_search_context)
            
            # Generate response using OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            generated_text = response.choices[0].message.content
            
            logger.info(f"LLM generated response: {len(generated_text)} characters")
            
            return {
                "response": generated_text,
                "query": query,
                "context_used": bool(context),
                "web_search_used": self.use_web_search,
                "component_type": "llm_engine",
                "node_id": self.node_id
            }
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return {
                "response": f"Error generating response: {str(e)}",
                "query": query,
                "error": str(e)
            }
    
    def _build_prompt(self, query: str, context: str = "", web_context: str = "") -> str:
        """
        Build the prompt for the LLM.
        
        Args:
            query: User query
            context: Context from knowledge base
            web_context: Context from web search
            
        Returns:
            Formatted prompt string
        """
        # Use custom prompt if provided
        if self.custom_prompt:
            prompt = self.custom_prompt
            prompt = prompt.replace("{query}", query)
            prompt = prompt.replace("{context}", context)
            prompt = prompt.replace("{User Query}", query)
            prompt = prompt.replace("{CONTEXT}", context)
            return prompt
        
        # Default prompt template
        prompt_parts = []
        
        if context:
            prompt_parts.append(f"Context from documents:\n{context}\n")
        
        if web_context:
            prompt_parts.append(f"Web search results:\n{web_context}\n")
        
        prompt_parts.append(f"User query: {query}\n")
        prompt_parts.append("Please provide a helpful response based on the above information.")
        
        return "\n".join(prompt_parts)
    
    async def _perform_web_search(self, query: str) -> str:
        """
        Perform web search using SerpAPI.
        
        Args:
            query: Search query
            
        Returns:
            Formatted search results as string
        """
        if not settings.serpapi_api_key:
            logger.warning("SerpAPI key not configured, skipping web search")
            return ""
        
        try:
            search = GoogleSearch({
                "q": query,
                "api_key": settings.serpapi_api_key,
                "num": 5
            })
            results = search.get_dict()
            
            # Extract organic results
            organic_results = results.get("organic_results", [])
            
            # Format results
            formatted_results = []
            for i, result in enumerate(organic_results[:5], 1):
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                formatted_results.append(f"{i}. {title}\n{snippet}")
            
            web_context = "\n\n".join(formatted_results)
            logger.info(f"Web search returned {len(organic_results)} results")
            return web_context
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            return ""
    
    def validate_config(self) -> bool:
        """Validate LLM engine configuration."""
        # Check if model is specified
        if not self.model:
            logger.error("Model is required")
            return False
        
        # Validate temperature range
        if not 0 <= self.temperature <= 2:
            logger.error("Temperature must be between 0 and 2")
            return False
        
        return True
