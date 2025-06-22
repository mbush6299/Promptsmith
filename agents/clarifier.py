"""
Clarifier Agent

This agent handles vague or unrenderable inputs by asking follow-up questions
to clarify the user's intent.

Input: original_user_query (string)
Output: clarified_query (string) or follow_up_question (string)
"""

from typing import Dict, Any, Tuple, Optional
import json


class ClarifierAgent:
    """Agent responsible for clarifying vague or unrenderable user queries."""
    
    def __init__(self):
        self.name = "clarifier"
        self.description = "Clarifies vague or unrenderable user queries through follow-up questions"
        
        # Common clarification patterns
        self.clarification_patterns = {
            "vague_business": "What specific business metrics would you like to see? (e.g., revenue, profit, sales, customers)",
            "missing_timeframe": "What time period would you like to analyze? (e.g., last month, Q1 2024, past year)",
            "missing_dimensions": "What dimensions would you like to compare? (e.g., by region, product, department)",
            "missing_chart_type": "What type of visualization would you prefer? (e.g., bar chart, line chart, pie chart)",
            "missing_data_source": "What data source should I use for this analysis?",
            "too_broad": "Could you be more specific about what you'd like to visualize?",
            "ambiguous_metrics": "Which specific metrics are you interested in? (e.g., total, average, percentage change)"
        }
    
    def analyze_query(self, user_query: str) -> Tuple[str, Optional[str]]:
        """
        Analyze the user query and determine if clarification is needed.
        
        Args:
            user_query (str): Original user query
            
        Returns:
            Tuple[str, Optional[str]]: Clarification type and follow-up question
        """
        query_lower = user_query.lower()
        
        # Check for vague business queries
        if self._is_vague_business_query(query_lower):
            return "vague_business", self.clarification_patterns["vague_business"]
        
        # Check for missing timeframe
        if self._is_missing_timeframe(query_lower):
            return "missing_timeframe", self.clarification_patterns["missing_timeframe"]
        
        # Check for missing dimensions
        if self._is_missing_dimensions(query_lower):
            return "missing_dimensions", self.clarification_patterns["missing_dimensions"]
        
        # Check for too broad queries
        if self._is_too_broad(query_lower):
            return "too_broad", self.clarification_patterns["too_broad"]
        
        # Check for ambiguous metrics
        if self._is_ambiguous_metrics(query_lower):
            return "ambiguous_metrics", self.clarification_patterns["ambiguous_metrics"]
        
        # If no specific issues found, return None
        return "clear", None
    
    def _is_vague_business_query(self, query: str) -> bool:
        """Check if query is too vague about business metrics."""
        vague_terms = ["business", "performance", "metrics", "data", "results"]
        specific_terms = ["revenue", "profit", "sales", "customers", "orders", "growth"]
        
        has_vague = any(term in query for term in vague_terms)
        has_specific = any(term in query for term in specific_terms)
        
        return has_vague and not has_specific
    
    def _is_missing_timeframe(self, query: str) -> bool:
        """Check if query is missing timeframe information."""
        time_terms = ["time", "trend", "over time", "period", "month", "year", "quarter", "week"]
        return not any(term in query for term in time_terms)
    
    def _is_missing_dimensions(self, query: str) -> bool:
        """Check if query is missing dimension information."""
        dimension_terms = ["by", "region", "product", "department", "category", "group"]
        return not any(term in query for term in dimension_terms)
    
    def _is_too_broad(self, query: str) -> bool:
        """Check if query is too broad or generic."""
        broad_terms = ["everything", "all", "overview", "summary", "general"]
        return any(term in query for term in broad_terms)
    
    def _is_ambiguous_metrics(self, query: str) -> bool:
        """Check if query has ambiguous metric specifications."""
        ambiguous_terms = ["performance", "results", "numbers", "figures", "statistics"]
        specific_terms = ["total", "average", "percentage", "count", "sum", "mean"]
        
        has_ambiguous = any(term in query for term in ambiguous_terms)
        has_specific = any(term in query for term in specific_terms)
        
        return has_ambiguous and not has_specific
    
    def generate_clarification_question(self, clarification_type: str, original_query: str) -> str:
        """
        Generate a specific clarification question based on the issue type.
        
        Args:
            clarification_type (str): Type of clarification needed
            original_query (str): Original user query
            
        Returns:
            str: Follow-up question
        """
        base_question = self.clarification_patterns.get(clarification_type, "Could you provide more details?")
        
        # Customize question based on original query
        if clarification_type == "vague_business":
            return f"I see you want to analyze your business. {base_question}"
        
        elif clarification_type == "missing_timeframe":
            return f"For your query about '{original_query}', {base_question}"
        
        elif clarification_type == "missing_dimensions":
            return f"To better visualize '{original_query}', {base_question}"
        
        elif clarification_type == "too_broad":
            return f"Your request is quite broad. {base_question}"
        
        elif clarification_type == "ambiguous_metrics":
            return f"Regarding '{original_query}', {base_question}"
        
        else:
            return base_question
    
    def suggest_improved_query(self, original_query: str, clarification_type: str) -> str:
        """
        Suggest an improved version of the query based on common patterns.
        
        Args:
            original_query (str): Original user query
            clarification_type (str): Type of clarification needed
            
        Returns:
            str: Suggested improved query
        """
        suggestions = {
            "vague_business": "Show me revenue trends over the last 12 months",
            "missing_timeframe": f"{original_query} over the last quarter",
            "missing_dimensions": f"{original_query} by region",
            "too_broad": "Show me monthly revenue by product category",
            "ambiguous_metrics": f"Show me total {original_query} by month"
        }
        
        return suggestions.get(clarification_type, original_query)
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for the agent.
        
        Args:
            state (Dict[str, Any]): Current state containing user_query
            
        Returns:
            Dict[str, Any]: Updated state with clarification results
        """
        user_query = state.get("user_query", "")
        
        if not user_query:
            raise ValueError("user_query is required in state")
        
        # Analyze the query
        clarification_type, follow_up_question = self.analyze_query(user_query)
        
        # Generate clarification question if needed
        if follow_up_question:
            clarification_question = self.generate_clarification_question(clarification_type, user_query)
            suggested_query = self.suggest_improved_query(user_query, clarification_type)
            
            return {
                **state,
                "clarification_needed": True,
                "clarification_type": clarification_type,
                "clarification_question": clarification_question,
                "suggested_query": suggested_query,
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    "clarifier": {
                        "clarification_needed": True,
                        "clarification_type": clarification_type,
                        "clarification_question": clarification_question,
                        "suggested_query": suggested_query,
                        "status": "completed"
                    }
                }
            }
        else:
            # Query is clear, no clarification needed
            return {
                **state,
                "clarification_needed": False,
                "clarification_type": "clear",
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    "clarifier": {
                        "clarification_needed": False,
                        "clarification_type": "clear",
                        "status": "completed"
                    }
                }
            }


# Example usage
if __name__ == "__main__":
    agent = ClarifierAgent()
    
    # Test with vague query
    test_state = {"user_query": "How is my business doing?"}
    result = agent.run(test_state)
    print(json.dumps(result, indent=2))
    
    # Test with clear query
    test_state2 = {"user_query": "Show me revenue by region over time"}
    result2 = agent.run(test_state2)
    print(json.dumps(result2, indent=2)) 