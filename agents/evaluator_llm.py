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
    
    def evaluate_chart(self, chart_spec: Dict[str, Any], original_intent: str) -> Dict[str, Any]:
        """
        Evaluate a chart specification using LLM reasoning.
        
        Args:
            chart_spec (Dict[str, Any]): Vega-Lite chart specification
            original_intent (str): Original user intent/query
            
        Returns:
            Dict[str, Any]: Detailed evaluation results
        """
        # Try LLM-based evaluation
        system_prompt = (
            "You are an expert chart evaluator. Given a Vega-Lite chart specification and the original user intent, "
            "evaluate the chart on a scale of 0 to 10 for how well it fulfills the intent, clarity, insight, aesthetics, and modern best practices. "
            "Reward the use of modern color schemes, interactivity (selection, tooltips, hover effects), responsive design, and clean, readable axis titles (do not penalize for minor axis title imperfections if the chart is otherwise clear). "
            "Consider: Does the chart type match the intent? Is the chart visually appealing and interactive? Are tooltips, selection, and responsive sizing present? Are axis titles clear and non-redundant? Is the color palette modern? "
            "Provide a score, feedback, strengths, weaknesses, and educational insights."
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
            strengths = parsed.get("strengths", [])
            weaknesses = parsed.get("weaknesses", [])
            return {
                "score": score,
                "feedback": feedback,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "criterion_scores": {},  # Initialize empty criterion_scores for LLM evaluation
                "evaluation_method": "llm",
                "educational_insights": [],  # Initialize empty educational_insights for LLM evaluation
                "educational_summary": "LLM evaluation completed"
            }
        except Exception:
            # If LLM fails or returns mock/error, fall back to rule-based simulation
            return self._simulate_llm_evaluation(chart_spec, original_intent)
    
    def _simulate_llm_evaluation(self, chart_spec: Dict[str, Any], original_intent: str) -> Dict[str, Any]:
        """
        Simulate LLM evaluation using rule-based logic with detailed educational feedback.
        
        Args:
            chart_spec (Dict[str, Any]): Chart specification
            original_intent (str): Original user intent
            
        Returns:
            Dict[str, Any]: Simulated evaluation results with educational explanations
        """
        score = 7.0  # Base score
        feedback_parts = []
        strengths = []
        weaknesses = []
        criterion_scores = {}
        educational_insights = []
        
        # Evaluate appropriateness for intent
        intent_score, intent_feedback, intent_insight = self._evaluate_intent_appropriateness(chart_spec, original_intent)
        score += intent_score
        feedback_parts.append(intent_feedback)
        criterion_scores["intent_appropriateness"] = intent_score
        educational_insights.append(intent_insight)
        if intent_score > 0:
            strengths.append("Appropriate chart type for the request")
        else:
            weaknesses.append("Chart type may not be optimal for the request")
        
        # Evaluate clarity and readability
        clarity_score, clarity_feedback, clarity_insight = self._evaluate_clarity(chart_spec)
        score += clarity_score
        feedback_parts.append(clarity_feedback)
        criterion_scores["clarity"] = clarity_score
        educational_insights.append(clarity_insight)
        if clarity_score > 0.5:
            strengths.append("Clear and readable design")
        else:
            weaknesses.append("Could improve clarity and readability")
        
        # Evaluate insight potential
        insight_score, insight_feedback, insight_insight = self._evaluate_insight_potential(chart_spec)
        score += insight_score
        feedback_parts.append(insight_feedback)
        criterion_scores["insight_potential"] = insight_score
        educational_insights.append(insight_insight)
        if insight_score > 0.3:
            strengths.append("Good potential for insights")
        else:
            weaknesses.append("Limited insight potential")
        
        # Evaluate aesthetic quality
        aesthetic_score, aesthetic_feedback, aesthetic_insight = self._evaluate_aesthetics(chart_spec)
        score += aesthetic_score
        feedback_parts.append(aesthetic_feedback)
        criterion_scores["aesthetics"] = aesthetic_score
        educational_insights.append(aesthetic_insight)
        if aesthetic_score > 0.5:
            strengths.append("Good aesthetic quality")
        else:
            weaknesses.append("Could enhance visual appeal")
        
        # Evaluate data representation accuracy
        accuracy_score, accuracy_feedback, accuracy_insight = self._evaluate_data_accuracy(chart_spec)
        score += accuracy_score
        feedback_parts.append(accuracy_feedback)
        criterion_scores["data_accuracy"] = accuracy_score
        educational_insights.append(accuracy_insight)
        if accuracy_score > 0.8:
            strengths.append("Accurate data representation")
        else:
            weaknesses.append("Data representation could be improved")
        
        # Normalize score to 0-10 range
        final_score = max(0.0, min(10.0, score))
        
        # Combine feedback with educational insights
        combined_feedback = " ".join(feedback_parts)
        educational_summary = " | ".join(educational_insights)
        
        return {
            "score": final_score,
            "feedback": combined_feedback,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "criterion_scores": criterion_scores,
            "evaluation_method": "simulated",
            "educational_insights": educational_insights,
            "educational_summary": educational_summary
        }
    
    def _evaluate_intent_appropriateness(self, chart_spec: Dict[str, Any], original_intent: str) -> Tuple[float, str, str]:
        """Evaluate if chart type is appropriate for the original intent with educational feedback."""
        mark = chart_spec.get("mark", "")
        intent_lower = original_intent.lower()
        
        # Educational insights about chart type selection
        chart_type_guide = {
            "bar": "Bar charts are excellent for comparing categories or showing discrete values. They work well for sales by region, product comparisons, or any categorical data.",
            "line": "Line charts are perfect for showing trends over time, continuous data, or relationships between variables. They excel at displaying time series data.",
            "point": "Scatter plots (point charts) are ideal for showing correlations, distributions, or relationships between two continuous variables.",
            "area": "Area charts are great for showing cumulative data over time or emphasizing volume. They work well for stacked data or showing parts of a whole over time."
        }
        
        # Simple rule-based intent matching with educational feedback
        if "time" in intent_lower or "trend" in intent_lower or "month" in intent_lower or "year" in intent_lower:
            if mark == "line":
                return 1.0, "Line chart appropriately shows temporal trends.", f"✅ **Time Series Choice**: Perfect! Line charts are the standard choice for time-based data because they clearly show trends and patterns over time. {chart_type_guide.get('line', '')}"
            elif mark == "area":
                return 0.8, "Area chart shows temporal trends but line might be clearer.", f"⚠️ **Time Series Choice**: Good choice, but consider that line charts often show trends more clearly than area charts. {chart_type_guide.get('area', '')}"
            else:
                return -0.5, f"Chart type '{mark}' may not be optimal for time-based data.", f"❌ **Time Series Choice**: For time-based data, line charts are typically the best choice. {chart_type_guide.get('line', '')}"
        
        elif "compare" in intent_lower or "region" in intent_lower or "category" in intent_lower:
            if mark in ["bar", "column"]:
                return 1.0, "Bar chart effectively compares categories.", f"✅ **Comparison Choice**: Excellent! Bar charts are the gold standard for comparing categories because they make it easy to compare values at a glance. {chart_type_guide.get('bar', '')}"
            else:
                return 0.0, f"Chart type '{mark}' may not be optimal for comparisons.", f"⚠️ **Comparison Choice**: For comparing categories, bar charts are usually the most effective choice. {chart_type_guide.get('bar', '')}"
        
        elif "distribution" in intent_lower or "spread" in intent_lower or "correlation" in intent_lower:
            if mark in ["point", "circle"]:
                return 1.0, "Scatter plot effectively shows distribution and correlations.", f"✅ **Distribution Choice**: Perfect! Scatter plots excel at showing distributions, correlations, and relationships between variables. {chart_type_guide.get('point', '')}"
            else:
                return 0.0, f"Chart type '{mark}' may not show distribution effectively.", f"⚠️ **Distribution Choice**: For showing distributions and correlations, scatter plots are typically the best choice. {chart_type_guide.get('point', '')}"
        
        else:
            return 0.5, f"Chart type '{mark}' is generally suitable for the request.", f"ℹ️ **Chart Type**: The chosen chart type should work well for this request. Consider the data type and what you want to emphasize."
    
    def _evaluate_clarity(self, chart_spec: Dict[str, Any]) -> Tuple[float, str, str]:
        """Evaluate chart clarity and readability with educational feedback."""
        encoding = chart_spec.get("encoding", {})
        title = chart_spec.get("title", {})
        
        clarity_score = 0.0
        feedback_parts = []
        insights = []
        
        # Check title
        if title and (isinstance(title, str) or title.get("text")):
            clarity_score += 0.5
            feedback_parts.append("Chart has a clear title.")
            insights.append("✅ **Title**: Good! A clear title helps users immediately understand what the chart shows.")
        else:
            feedback_parts.append("Chart lacks a descriptive title.")
            insights.append("❌ **Title**: Missing! Titles are crucial for chart clarity. They should be descriptive and specific.")
        
        # Check axis labels
        x_has_title = encoding.get("x", {}).get("title") is not None
        y_has_title = encoding.get("y", {}).get("title") is not None
        
        if x_has_title and y_has_title:
            clarity_score += 0.5
            feedback_parts.append("Both axes are properly labeled.")
            insights.append("✅ **Axis Labels**: Excellent! Clear axis labels help users understand what each axis represents.")
        elif x_has_title or y_has_title:
            clarity_score += 0.25
            feedback_parts.append("One axis is labeled.")
            insights.append("⚠️ **Axis Labels**: Partial - Both axes should be labeled for maximum clarity.")
        else:
            feedback_parts.append("Axis labels are missing.")
            insights.append("❌ **Axis Labels**: Missing! Axis labels are essential for chart comprehension.")
        
        # Check for data field names
        x_field = encoding.get("x", {}).get("field")
        y_field = encoding.get("y", {}).get("field")
        
        if x_field and y_field:
            insights.append("✅ **Data Fields**: Good field mapping helps users understand what data is being visualized.")
        else:
            insights.append("⚠️ **Data Fields**: Ensure data fields are properly mapped to axes.")
        
        return clarity_score, " ".join(feedback_parts), " | ".join(insights)
    
    def _evaluate_insight_potential(self, chart_spec: Dict[str, Any]) -> Tuple[float, str, str]:
        """Evaluate the potential for insights with educational feedback."""
        data = chart_spec.get("data", {}).get("values", [])
        
        if len(data) >= 5:
            return 0.5, "Sufficient data points for meaningful analysis.", "✅ **Data Volume**: Good amount of data provides potential for meaningful insights and patterns."
        elif len(data) >= 3:
            return 0.3, "Moderate data points available.", "⚠️ **Data Volume**: More data points would provide better insight potential."
        else:
            return 0.0, "Limited data points for analysis.", "❌ **Data Volume**: Very few data points limit the potential for meaningful insights."
    
    def _evaluate_aesthetics(self, chart_spec: Dict[str, Any]) -> Tuple[float, str, str]:
        """Evaluate aesthetic quality with educational feedback."""
        has_width = "width" in chart_spec
        has_height = "height" in chart_spec
        has_title = chart_spec.get("title", {})
        
        aesthetic_score = 0.0
        feedback_parts = []
        insights = []
        
        if has_width and has_height:
            aesthetic_score += 0.5
            feedback_parts.append("Chart has appropriate dimensions.")
            insights.append("✅ **Dimensions**: Good sizing ensures the chart is readable and well-proportioned.")
        else:
            feedback_parts.append("Chart dimensions could be improved.")
            insights.append("⚠️ **Dimensions**: Explicit width and height help ensure consistent display across different devices.")
        
        if has_title:
            aesthetic_score += 0.3
            feedback_parts.append("Chart has a title for context.")
            insights.append("✅ **Title**: Provides important context for the visualization.")
        else:
            feedback_parts.append("Chart lacks a title.")
            insights.append("❌ **Title**: A title is essential for professional-looking charts.")
        
        # Check for color encoding
        color_encoding = chart_spec.get("encoding", {}).get("color")
        if color_encoding:
            aesthetic_score += 0.2
            feedback_parts.append("Chart uses color effectively.")
            insights.append("✅ **Color**: Color encoding can enhance readability and highlight important patterns.")
        
        return aesthetic_score, " ".join(feedback_parts), " | ".join(insights)
    
    def _evaluate_data_accuracy(self, chart_spec: Dict[str, Any]) -> Tuple[float, str, str]:
        """Evaluate data representation accuracy with educational feedback."""
        data = chart_spec.get("data", {}).get("values", [])
        encoding = chart_spec.get("encoding", {})
        
        accuracy_score = 0.0
        feedback_parts = []
        insights = []
        
        if data and len(data) > 0:
            accuracy_score += 0.5
            feedback_parts.append("Chart has data to visualize.")
            insights.append("✅ **Data Presence**: Chart contains data for visualization.")
            
            # Check if data structure is appropriate
            if isinstance(data[0], dict) and len(data[0]) >= 2:
                accuracy_score += 0.3
                feedback_parts.append("Data structure is appropriate.")
                insights.append("✅ **Data Structure**: Data is properly structured with multiple fields.")
            else:
                feedback_parts.append("Data structure could be improved.")
                insights.append("⚠️ **Data Structure**: Ensure data has appropriate fields for the chart type.")
        else:
            feedback_parts.append("No data available for visualization.")
            insights.append("❌ **Data Presence**: Charts need data to be meaningful.")
        
        # Check encoding accuracy
        x_field = encoding.get("x", {}).get("field")
        y_field = encoding.get("y", {}).get("field")
        
        if x_field and y_field:
            accuracy_score += 0.2
            feedback_parts.append("Data fields are properly encoded.")
            insights.append("✅ **Field Encoding**: Data fields are properly mapped to chart axes.")
        else:
            feedback_parts.append("Data encoding could be improved.")
            insights.append("⚠️ **Field Encoding**: Ensure data fields are properly mapped to chart axes.")
        
        return accuracy_score, " ".join(feedback_parts), " | ".join(insights)
    
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
        
        evaluation_results = self.evaluate_chart(chart_spec, user_query)
        
        return {
            **state,
            "llm_score": evaluation_results["score"],
            "llm_feedback": evaluation_results["feedback"],
            "strengths": evaluation_results["strengths"],
            "weaknesses": evaluation_results["weaknesses"],
            "criterion_scores": evaluation_results["criterion_scores"],
            "evaluation_method": evaluation_results["evaluation_method"],
            "educational_insights": evaluation_results["educational_insights"],
            "educational_summary": evaluation_results["educational_summary"],
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "llm_evaluator": {
                    "score": evaluation_results["score"],
                    "feedback": evaluation_results["feedback"],
                    "strengths": evaluation_results["strengths"],
                    "weaknesses": evaluation_results["weaknesses"],
                    "criterion_scores": evaluation_results["criterion_scores"],
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