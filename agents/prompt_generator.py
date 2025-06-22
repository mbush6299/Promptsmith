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
            user_query (str): Natural language query from user
            
        Returns:
            Dict[str, Any]: Prompt and metadata about generation
        """
        # First, check if we have a learned pattern for this query
        cached_prompt = learning_cache.suggest_prompt(user_query)
        if cached_prompt:
            print(f"🎯 Using cached prompt pattern for: {user_query[:50]}...")
            return {
                "prompt": cached_prompt,
                "from_cache": True,
                "cache_hit": "prompt_pattern",
                "generation_method": "cache"
            }
        
        # Try LLM-based prompt generation
        system_prompt = (
            "You are a helpful assistant that converts user requests into structured prompts "
            "for chart specification generation. The prompt should be clear, concise, and designed "
            "to elicit a high-quality Vega-Lite chart spec from an LLM."
        )
        user_message = (
            f"User query: {user_query}\n"
            "Generate a prompt that will instruct an LLM to create a Vega-Lite chart specification "
            "for this request."
        )
        llm_prompt = chat_completion(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=300
        )
        
        # If the LLM utility returns a mock or error, fall back to template
        if llm_prompt.startswith("[MOCK") or llm_prompt.startswith("[LLM ERROR"):
            template_prompt = self._create_prompt_template(user_query)
            return {
                "prompt": template_prompt,
                "from_cache": False,
                "cache_hit": None,
                "generation_method": "template",
                "llm_fallback": True,
                "llm_error": llm_prompt
            }
        
        return {
            "prompt": llm_prompt.strip(),
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