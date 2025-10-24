"""Convert MCP tool schemas to LLM-specific formats."""
from typing import List, Dict, Any
from enum import Enum

class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DATABRICKS_CLAUDE = "databricks_claude"  # OpenAI-compatible API

class ToolRegistry:
    """Registry for converting MCP tools to LLM formats."""
    
    def __init__(self, mcp_tools: List[Any]):
        """Initialize tool registry.
        
        Args:
            mcp_tools: List of MCP tool objects
        """
        self.mcp_tools = mcp_tools
    
    def to_llm_tools(self, provider: LLMProvider) -> List[Dict[str, Any]]:
        """Convert MCP tools to provider-specific format.
        
        Args:
            provider: Target LLM provider
            
        Returns:
            List of tools in provider-specific format
        """
        if provider in [LLMProvider.OPENAI, LLMProvider.DATABRICKS_CLAUDE]:
            return self._to_openai_format()
        elif provider == LLMProvider.ANTHROPIC:
            return self._to_anthropic_format()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _to_openai_format(self) -> List[Dict[str, Any]]:
        """Convert to OpenAI function calling format.
        
        Returns:
            List of tools in OpenAI format
        """
        tools = []
        
        for tool in self.mcp_tools:
            schema = self._simplify_schema(tool.inputSchema)
            
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or tool.name,
                    "parameters": schema
                }
            })
        
        return tools
    
    def _to_anthropic_format(self) -> List[Dict[str, Any]]:
        """Convert to Anthropic tool format.
        
        Returns:
            List of tools in Anthropic format
        """
        tools = []
        
        for tool in self.mcp_tools:
            schema = self._simplify_schema(tool.inputSchema)
            
            tools.append({
                "name": tool.name,
                "description": tool.description or tool.name,
                "input_schema": schema
            })
        
        return tools
    
    def _simplify_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify complex schemas for LLM compatibility.
        
        Handles:
        - anyOf types (extracts first non-null type)
        - Missing types (defaults to string)
        - Complex nested structures
        
        Args:
            schema: MCP tool input schema
            
        Returns:
            Simplified schema compatible with LLMs
        """
        if not isinstance(schema, dict):
            return {"type": "object", "properties": {}}
        
        simplified = {
            "type": "object",
            "properties": {},
            "required": schema.get("required", [])
        }
        
        for prop_name, prop_def in schema.get("properties", {}).items():
            if not isinstance(prop_def, dict):
                continue
            
            simple_prop = {}
            
            # Handle type
            if "type" in prop_def:
                simple_prop["type"] = prop_def["type"]
            elif "anyOf" in prop_def:
                # Extract first non-null type from anyOf
                for option in prop_def["anyOf"]:
                    if isinstance(option, dict) and option.get("type") != "null":
                        simple_prop["type"] = option["type"]
                        break
                if "type" not in simple_prop:
                    simple_prop["type"] = "string"
            else:
                simple_prop["type"] = "string"
            
            # Copy description
            if "description" in prop_def:
                simple_prop["description"] = prop_def["description"]
            
            # Handle enums
            if "enum" in prop_def:
                simple_prop["enum"] = prop_def["enum"]
            
            # Handle default values
            if "default" in prop_def:
                simple_prop["default"] = prop_def["default"]
            
            simplified["properties"][prop_name] = simple_prop
        
        return simplified

