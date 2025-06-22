"""
Chart Builder Agent

This agent takes a visualization prompt and generates a Vega-Lite chart specification.

Input: prompt (string)
Output: chart_spec (JSON string) - Vega-Lite format
"""

from typing import Dict, Any, Optional
import json
import random
from llm_utils import chat_completion
from learning_cache import learning_cache


class ChartBuilderAgent:
    """Agent responsible for building chart specifications from prompts."""
    
    def __init__(self):
        self.name = "chart_builder"
        self.description = "Generates Vega-Lite chart specifications from visualization prompts"
    
    def build_chart(self, prompt: str, user_query: str = "") -> Dict[str, Any]:
        """
        Build a chart specification from a prompt.
        
        Args:
            prompt (str): Visualization prompt
            user_query (str): Original user query for cache lookup
            
        Returns:
            Dict[str, Any]: Chart specification and metadata
        """
        # First, check if we have a learned pattern for this query
        if user_query:
            cached_chart_spec = learning_cache.suggest_chart_spec(user_query)
            if cached_chart_spec:
                print(f"🎯 Using cached chart spec pattern for: {user_query[:50]}...")
                return {
                    "chart_spec": cached_chart_spec,
                    "from_cache": True,
                    "cache_hit": "chart_pattern",
                    "generation_method": "cache",
                    "chart_type": self._detect_chart_type(cached_chart_spec)
                }
        
        # Try LLM-based chart generation
        system_prompt = (
            "You are a helpful assistant that generates valid Vega-Lite JSON chart specifications "
            "from user prompts. Return only the Vega-Lite JSON, no extra text."
        )
        user_message = f"Prompt: {prompt}\nGenerate a valid Vega-Lite JSON chart specification."
        llm_response = chat_completion(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=800
        )
        
        # Try to parse the LLM response as JSON
        try:
            chart_spec = json.loads(llm_response)
            return {
                "chart_spec": chart_spec,
                "from_cache": False,
                "cache_hit": None,
                "generation_method": "llm",
                "chart_type": self._detect_chart_type(chart_spec)
            }
        except Exception as e:
            # If LLM fails or returns mock/error, fall back to mock chart spec
            mock_spec = self._generate_mock_chart_spec(prompt)
            return {
                "chart_spec": mock_spec,
                "from_cache": False,
                "cache_hit": None,
                "generation_method": "template",
                "llm_fallback": True,
                "llm_error": str(e),
                "chart_type": self._detect_chart_type(mock_spec)
            }
    
    def _detect_chart_type(self, chart_spec: Dict[str, Any]) -> str:
        """
        Detect the type of chart from the specification.
        
        Args:
            chart_spec (Dict[str, Any]): Chart specification
            
        Returns:
            str: Chart type (bar, line, scatter, etc.)
        """
        mark = chart_spec.get("mark", "")
        if isinstance(mark, dict):
            mark = mark.get("type", "")
        
        chart_types = {
            "bar": "bar",
            "line": "line", 
            "point": "scatter",
            "area": "area",
            "circle": "scatter",
            "square": "scatter",
            "tick": "tick",
            "rect": "heatmap",
            "rule": "rule",
            "text": "text"
        }
        
        return chart_types.get(mark.lower(), "unknown")
    
    def _generate_mock_chart_spec(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a mock Vega-Lite chart specification for testing.
        
        Args:
            prompt (str): Original prompt (used for context)
            
        Returns:
            Dict[str, Any]: Mock Vega-Lite specification
        """
        # Mock data for testing
        mock_data = [
            {"region": "North", "revenue": 120000, "month": "Jan"},
            {"region": "South", "revenue": 95000, "month": "Jan"},
            {"region": "East", "revenue": 110000, "month": "Jan"},
            {"region": "West", "revenue": 85000, "month": "Jan"},
            {"region": "North", "revenue": 135000, "month": "Feb"},
            {"region": "South", "revenue": 105000, "month": "Feb"},
            {"region": "East", "revenue": 125000, "month": "Feb"},
            {"region": "West", "revenue": 90000, "month": "Feb"},
            {"region": "North", "revenue": 150000, "month": "Mar"},
            {"region": "South", "revenue": 115000, "month": "Mar"},
            {"region": "East", "revenue": 140000, "month": "Mar"},
            {"region": "West", "revenue": 100000, "month": "Mar"}
        ]
        
        chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": "Revenue by region over time",
            "data": {
                "values": mock_data
            },
            "mark": "line",
            "encoding": {
                "x": {
                    "field": "month",
                    "type": "ordinal",
                    "title": "Month"
                },
                "y": {
                    "field": "revenue",
                    "type": "quantitative",
                    "title": "Revenue ($)"
                },
                "color": {
                    "field": "region",
                    "type": "nominal",
                    "title": "Region"
                }
            },
            "title": {
                "text": "Revenue by Region Over Time",
                "fontSize": 16
            },
            "width": 600,
            "height": 400
        }
        
        return chart_spec
    
    def validate_chart_spec(self, chart_spec: Dict[str, Any]) -> bool:
        """
        Validate that the chart specification is properly formatted.
        
        Args:
            chart_spec (Dict[str, Any]): Chart specification to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["$schema", "data", "mark", "encoding"]
        
        for field in required_fields:
            if field not in chart_spec:
                return False
        
        return True
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for the agent.
        
        Args:
            state (Dict[str, Any]): Current state containing prompt
            
        Returns:
            Dict[str, Any]: Updated state with chart specification
        """
        prompt = state.get("prompt", "")
        user_query = state.get("user_query", "")
        
        if not prompt:
            raise ValueError("prompt is required in state")
        
        chart_result = self.build_chart(prompt, user_query)
        
        # Validate the chart specification
        is_valid = self.validate_chart_spec(chart_result["chart_spec"])
        
        return {
            **state,
            "chart_spec": chart_result["chart_spec"],
            "chart_spec_json": json.dumps(chart_result["chart_spec"]),
            "chart_valid": is_valid,
            "chart_from_cache": chart_result["from_cache"],
            "chart_cache_hit": chart_result["cache_hit"],
            "chart_generation_method": chart_result["generation_method"],
            "chart_type": chart_result["chart_type"],
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "chart_builder": {
                    "chart_spec": chart_result["chart_spec"],
                    "chart_type": chart_result["chart_type"],
                    "from_cache": chart_result["from_cache"],
                    "cache_hit": chart_result["cache_hit"],
                    "generation_method": chart_result["generation_method"],
                    "is_valid": is_valid,
                    "status": "completed",
                    "llm_fallback": chart_result.get("llm_fallback", False),
                    "llm_error": chart_result.get("llm_error", None)
                }
            }
        }


# Example usage
if __name__ == "__main__":
    agent = ChartBuilderAgent()
    test_state = {
        "prompt": "Create a chart showing revenue by region over time"
    }
    result = agent.run(test_state)
    print(json.dumps(result, indent=2)) 