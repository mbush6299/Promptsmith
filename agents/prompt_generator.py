"""
Prompt Generator Agent

This agent takes a natural language user query and generates a structured prompt
designed to elicit a chart specification from an LLM.

Input: user_query (string)
Output: prompt (string) - designed to elicit a chart spec from an LLM
"""

from typing import Dict, Any
import json
from llm_utils import chat_completion
from learning_cache import learning_cache


class PromptGeneratorAgent:
    """Agent responsible for generating visualization prompts from user queries."""
    
    def __init__(self):
        self.name = "prompt_generator"
        self.description = "Generates structured prompts for chart visualization from natural language queries"
    
    def generate_prompt(self, user_query: str) -> Dict[str, Any]:
        """
        Generate a visualization prompt from a user query.
        
        Args:
            user_query (str): User's natural language query
            
        Returns:
            Dict[str, Any]: Generated prompt and metadata
        """
        # Only use cache for exact matches to avoid generating identical prompts
        cached_prompt = learning_cache.suggest_prompt(user_query)
        if cached_prompt:
            # Double-check it's an exact match
            query_hash = learning_cache._hash_query(user_query)
            if query_hash in learning_cache.patterns["query_patterns"]:
                cached_query = learning_cache.patterns["query_patterns"][query_hash]["query"]
                if user_query.lower() == cached_query.lower():
                    print(f"🎯 Using cached prompt for exact match: {user_query[:50]}...")
                    return {
                        "prompt": cached_prompt,
                        "from_cache": True,
                        "cache_hit": "exact_match",
                        "generation_method": "cache"
                    }
        
        # Generate a new prompt using LLM
        system_prompt = (
            "You are a helpful assistant that converts user queries into detailed visualization prompts. "
            "Generate specific, actionable prompts that will help create effective charts. "
            "Include details about chart type, data requirements, and styling preferences. "
            "Return only the prompt text, no extra formatting."
        )
        user_message = f"Convert this user query into a detailed visualization prompt: {user_query}"
        llm_response = chat_completion(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=200
        )
        
        return {
            "prompt": llm_response.strip(),
            "from_cache": False,
            "cache_hit": None,
            "generation_method": "llm"
        }
    
    def _create_prompt_template(self, user_query: str) -> str:
        """
        Create a structured prompt template based on the user query.
        
        Args:
            user_query (str): Original user query
            
        Returns:
            str: Structured prompt
        """
        base_prompt = f"""
        Create a Vega-Lite chart specification based on the following user request:
        
        User Request: "{user_query}"
        
        Please generate a complete Vega-Lite JSON specification that:
        1. Uses appropriate chart type for the data and analysis
        2. Includes proper axis labels and titles
        3. Handles the data structure appropriately
        4. Uses meaningful colors and styling
        5. Is optimized for readability and insight
        
        Return only the JSON specification without any additional text.
        """
        
        return base_prompt.strip()
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for the agent.
        
        Args:
            state (Dict[str, Any]): Current state containing user_query
            
        Returns:
            Dict[str, Any]: Updated state with generated prompt
        """
        user_query = state.get("user_query", "")
        
        if not user_query:
            raise ValueError("user_query is required in state")
        
        prompt_result = self.generate_prompt(user_query)
        
        return {
            **state,
            "prompt": prompt_result["prompt"],
            "prompt_from_cache": prompt_result["from_cache"],
            "prompt_cache_hit": prompt_result["cache_hit"],
            "prompt_generation_method": prompt_result["generation_method"],
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "prompt_generator": {
                    "prompt": prompt_result["prompt"],
                    "from_cache": prompt_result["from_cache"],
                    "cache_hit": prompt_result["cache_hit"],
                    "generation_method": prompt_result["generation_method"],
                    "status": "completed",
                    "llm_fallback": prompt_result.get("llm_fallback", False),
                    "llm_error": prompt_result.get("llm_error", None)
                }
            }
        }


# Example usage
if __name__ == "__main__":
    agent = PromptGeneratorAgent()
    test_state = {"user_query": "Show me revenue by region over time"}
    result = agent.run(test_state)
    print(json.dumps(result, indent=2)) 