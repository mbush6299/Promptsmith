"""
LLM Evaluator Agent

This agent performs AI-based evaluation of chart specifications using LLM reasoning.

Input: chart_spec (Dict), original_intent (string)
Output: score (0-10), feedback (string rationale)
"""

from typing import Dict, Any, Tuple
import json
from llm_utils import chat_completion


class LLMEvaluatorAgent:
    """Agent responsible for LLM-based evaluation of chart specifications."""
    
    def __init__(self):
        self.name = "llm_evaluator"
        self.description = "Performs AI-based evaluation of chart specifications using LLM reasoning"
        
        # Evaluation criteria for LLM assessment
        self.evaluation_criteria = [
            "appropriateness_for_intent",
            "clarity_and_readability", 
            "insight_potential",
            "aesthetic_quality",
            "data_representation_accuracy"
        ]
    
    def evaluate_chart(self, chart_spec: Dict[str, Any], original_intent: str) -> Tuple[float, str]:
        """
        Evaluate a chart specification using LLM reasoning.
        
        Args:
            chart_spec (Dict[str, Any]): Vega-Lite chart specification
            original_intent (str): Original user intent/query
            
        Returns:
            Tuple[float, str]: Score (0-10) and feedback rationale
        """
        # Try LLM-based evaluation
        system_prompt = (
            "You are an expert chart evaluator. Given a Vega-Lite chart specification and the original user intent, "
            "evaluate the chart on a scale of 0 to 10 for how well it fulfills the intent, clarity, insight, and aesthetics. "
            "Return your answer as a JSON object: {\"score\": <float 0-10>, \"feedback\": <string rationale>}"
        )
        user_message = (
            f"User intent: {original_intent}\n"
            f"Vega-Lite spec:\n{json.dumps(chart_spec, indent=2)}"
        )
        llm_response = chat_completion(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=400
        )
        try:
            parsed = json.loads(llm_response)
            score = float(parsed.get("score", 0.0))
            feedback = parsed.get("feedback", "No feedback provided.")
            return score, feedback
        except Exception:
            # If LLM fails or returns mock/error, fall back to rule-based simulation
            return self._simulate_llm_evaluation(chart_spec, original_intent)
    
    def _simulate_llm_evaluation(self, chart_spec: Dict[str, Any], original_intent: str) -> Tuple[float, str]:
        """
        Simulate LLM evaluation using rule-based logic.
        
        Args:
            chart_spec (Dict[str, Any]): Chart specification
            original_intent (str): Original user intent
            
        Returns:
            Tuple[float, str]: Simulated score and feedback
        """
        score = 7.0  # Base score
        feedback_parts = []
        
        # Evaluate appropriateness for intent
        intent_score, intent_feedback = self._evaluate_intent_appropriateness(chart_spec, original_intent)
        score += intent_score
        feedback_parts.append(intent_feedback)
        
        # Evaluate clarity and readability
        clarity_score, clarity_feedback = self._evaluate_clarity(chart_spec)
        score += clarity_score
        feedback_parts.append(clarity_feedback)
        
        # Evaluate insight potential
        insight_score, insight_feedback = self._evaluate_insight_potential(chart_spec)
        score += insight_score
        feedback_parts.append(insight_feedback)
        
        # Evaluate aesthetic quality
        aesthetic_score, aesthetic_feedback = self._evaluate_aesthetics(chart_spec)
        score += aesthetic_score
        feedback_parts.append(aesthetic_feedback)
        
        # Evaluate data representation accuracy
        accuracy_score, accuracy_feedback = self._evaluate_data_accuracy(chart_spec)
        score += accuracy_score
        feedback_parts.append(accuracy_feedback)
        
        # Normalize score to 0-10 range
        final_score = max(0.0, min(10.0, score))
        
        # Combine feedback
        combined_feedback = " ".join(feedback_parts)
        
        return final_score, combined_feedback
    
    def _evaluate_intent_appropriateness(self, chart_spec: Dict[str, Any], original_intent: str) -> Tuple[float, str]:
        """Evaluate if chart type is appropriate for the original intent."""
        mark = chart_spec.get("mark", "")
        intent_lower = original_intent.lower()
        
        # Simple rule-based intent matching
        if "time" in intent_lower or "trend" in intent_lower:
            if mark == "line":
                return 1.0, "Line chart appropriately shows temporal trends."
            elif mark == "area":
                return 0.8, "Area chart shows temporal trends but line might be clearer."
            else:
                return -0.5, f"Chart type '{mark}' may not be optimal for time-based data."
        
        elif "compare" in intent_lower or "region" in intent_lower:
            if mark in ["bar", "column"]:
                return 1.0, "Bar chart effectively compares categories."
            else:
                return 0.0, f"Chart type '{mark}' may not be optimal for comparisons."
        
        elif "distribution" in intent_lower or "spread" in intent_lower:
            if mark in ["histogram", "boxplot"]:
                return 1.0, "Appropriate chart type for distribution analysis."
            else:
                return 0.0, f"Chart type '{mark}' may not show distribution effectively."
        
        else:
            return 0.5, f"Chart type '{mark}' is generally suitable for the request."
    
    def _evaluate_clarity(self, chart_spec: Dict[str, Any]) -> Tuple[float, str]:
        """Evaluate chart clarity and readability."""
        encoding = chart_spec.get("encoding", {})
        title = chart_spec.get("title", {})
        
        clarity_score = 0.0
        feedback_parts = []
        
        # Check title
        if title and (isinstance(title, str) or title.get("text")):
            clarity_score += 0.5
            feedback_parts.append("Chart has a clear title.")
        else:
            feedback_parts.append("Chart lacks a descriptive title.")
        
        # Check axis labels
        x_title = encoding.get("x", {}).get("title")
        y_title = encoding.get("y", {}).get("title")
        
        if x_title and y_title:
            clarity_score += 0.5
            feedback_parts.append("Both axes are properly labeled.")
        elif x_title or y_title:
            clarity_score += 0.2
            feedback_parts.append("Some axes are labeled.")
        else:
            feedback_parts.append("Axis labels are missing.")
        
        return clarity_score, " ".join(feedback_parts)
    
    def _evaluate_insight_potential(self, chart_spec: Dict[str, Any]) -> Tuple[float, str]:
        """Evaluate potential for generating insights."""
        data = chart_spec.get("data", {})
        values = data.get("values", [])
        
        if len(values) > 10:
            return 0.5, "Sufficient data points for meaningful analysis."
        elif len(values) > 5:
            return 0.3, "Moderate data points available."
        else:
            return 0.0, "Limited data may restrict insight generation."
    
    def _evaluate_aesthetics(self, chart_spec: Dict[str, Any]) -> Tuple[float, str]:
        """Evaluate aesthetic quality of the chart."""
        aesthetics_score = 0.0
        feedback_parts = []
        
        # Check for color encoding
        encoding = chart_spec.get("encoding", {})
        if "color" in encoding:
            aesthetics_score += 0.3
            feedback_parts.append("Color encoding enhances visual appeal.")
        
        # Check for size specifications
        if "width" in chart_spec and "height" in chart_spec:
            aesthetics_score += 0.2
            feedback_parts.append("Chart has appropriate dimensions.")
        
        # Check for title styling
        title = chart_spec.get("title", {})
        if isinstance(title, dict) and title.get("fontSize"):
            aesthetics_score += 0.2
            feedback_parts.append("Title has good typography.")
        
        if aesthetics_score == 0:
            feedback_parts.append("Basic styling could be enhanced.")
        
        return aesthetics_score, " ".join(feedback_parts)
    
    def _evaluate_data_accuracy(self, chart_spec: Dict[str, Any]) -> Tuple[float, str]:
        """Evaluate accuracy of data representation."""
        encoding = chart_spec.get("encoding", {})
        
        # Check for appropriate data types
        x_encoding = encoding.get("x", {})
        y_encoding = encoding.get("y", {})
        
        accuracy_score = 0.0
        feedback_parts = []
        
        # Validate data types
        if x_encoding.get("type") in ["ordinal", "nominal", "quantitative", "temporal"]:
            accuracy_score += 0.3
            feedback_parts.append("X-axis has appropriate data type.")
        
        if y_encoding.get("type") in ["ordinal", "nominal", "quantitative", "temporal"]:
            accuracy_score += 0.3
            feedback_parts.append("Y-axis has appropriate data type.")
        
        # Check for field mappings
        if x_encoding.get("field") and y_encoding.get("field"):
            accuracy_score += 0.4
            feedback_parts.append("Data fields are properly mapped.")
        else:
            feedback_parts.append("Some data field mappings may be missing.")
        
        return accuracy_score, " ".join(feedback_parts)
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for the agent.
        
        Args:
            state (Dict[str, Any]): Current state containing chart_spec and user_query
            
        Returns:
            Dict[str, Any]: Updated state with LLM evaluation results
        """
        chart_spec = state.get("chart_spec")
        user_query = state.get("user_query", "")
        
        if not chart_spec:
            raise ValueError("chart_spec is required in state")
        
        score, feedback = self.evaluate_chart(chart_spec, user_query)
        
        return {
            **state,
            "llm_score": score,
            "llm_feedback": feedback,
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "llm_evaluator": {
                    "score": score,
                    "feedback": feedback,
                    "status": "completed"
                }
            }
        }


# Example usage
if __name__ == "__main__":
    agent = LLMEvaluatorAgent()
    
    test_chart_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": {"text": "Revenue by Region Over Time"},
        "data": {"values": [{"region": "North", "revenue": 120000, "month": "Jan"}]},
        "mark": "line",
        "encoding": {
            "x": {"field": "month", "type": "ordinal", "title": "Month"},
            "y": {"field": "revenue", "type": "quantitative", "title": "Revenue ($)"},
            "color": {"field": "region", "type": "nominal", "title": "Region"}
        }
    }
    
    test_state = {
        "chart_spec": test_chart_spec,
        "user_query": "Show me revenue by region over time"
    }
    
    result = agent.run(test_state)
    print(json.dumps(result, indent=2)) 