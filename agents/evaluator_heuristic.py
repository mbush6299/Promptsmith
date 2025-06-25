"""
Heuristic Evaluator Agent

This agent performs rule-based evaluation of chart specifications using predefined criteria.

Input: chart_spec (Dict)
Output: score (0-10), issue_tags (list of strings)
"""

from typing import Dict, Any, List, Tuple
import json


class HeuristicEvaluatorAgent:
    """Agent responsible for rule-based evaluation of chart specifications."""
    
    def __init__(self):
        self.name = "heuristic_evaluator"
        self.description = "Performs rule-based evaluation of chart specifications"
        
        # Define evaluation criteria
        self.criteria = {
            "has_title": {"weight": 0.1, "required": True},
            "has_axis_labels": {"weight": 0.15, "required": True},
            "appropriate_chart_type": {"weight": 0.2, "required": True},
            "has_data": {"weight": 0.15, "required": True},
            "proper_encoding": {"weight": 0.2, "required": True},
            "good_styling": {"weight": 0.1, "required": False},
            "responsive_design": {"weight": 0.1, "required": False}
        }
    
    def evaluate_chart(self, chart_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a chart specification using heuristic rules.
        
        Args:
            chart_spec (Dict[str, Any]): Vega-Lite chart specification
            
        Returns:
            Dict[str, Any]: Detailed evaluation results
        """
        score = 0.0
        issues = []
        criterion_scores = {}
        criterion_details = {}
        
        # Check if chart spec is valid
        if not self._is_valid_chart_spec(chart_spec):
            return {
                "score": 0.0,
                "issues": ["invalid_chart_spec"],
                "criterion_scores": {},
                "criterion_details": {},
                "chart_valid": False,
                "detailed_feedback": "Chart specification is missing required fields ($schema, data, mark, encoding)"
            }
        
        # Evaluate each criterion
        for criterion, config in self.criteria.items():
            criterion_score, criterion_issues = self._evaluate_criterion(
                criterion, chart_spec, config
            )
            
            # Debug: check for non-string issues
            for issue in criterion_issues:
                if not isinstance(issue, str):
                    print(f"[DEBUG] Non-string issue detected in criterion '{criterion}': {issue} (type: {type(issue)})")
            
            criterion_scores[criterion] = criterion_score
            criterion_details[criterion] = {
                "score": criterion_score,
                "issues": [str(issue) for issue in criterion_issues],
                "weight": config["weight"],
                "required": config["required"],
                "weighted_score": criterion_score * config["weight"]
            }
            
            if criterion_score == 0 and config["required"]:
                issues.extend([str(issue) for issue in criterion_issues])
                if "invalid_input" in [str(issue) for issue in criterion_issues]:
                    return {
                        "score": 0.0,
                        "issues": [str(i) for i in criterion_issues],
                        "criterion_scores": criterion_scores,
                        "criterion_details": criterion_details,
                        "chart_valid": False,
                        "detailed_feedback": f"Critical issue with {criterion}: {', '.join([str(i) for i in criterion_issues])}"
                    }
            
            score += criterion_score * config["weight"]
            issues.extend([str(issue) for issue in criterion_issues])
        
        # Generate detailed feedback
        detailed_feedback = self._generate_detailed_feedback(criterion_details, issues)
        
        # Only keep string issues for deduplication
        string_issues = [i for i in issues if isinstance(i, str)]
        return {
            "score": min(score * 10, 10.0),
            "issues": list(set(string_issues)),  # Remove duplicates, only strings
            "criterion_scores": criterion_scores,
            "criterion_details": criterion_details,
            "chart_valid": True,
            "raw_score": score,
            "max_possible_score": 1.0,
            "detailed_feedback": detailed_feedback
        }
    
    def _is_valid_chart_spec(self, chart_spec: Dict[str, Any]) -> bool:
        """Check if chart specification has basic required structure."""
        if not isinstance(chart_spec, dict):
            return False
        
        required_fields = ["$schema", "data", "mark", "encoding"]
        return all(field in chart_spec for field in required_fields)
    
    def _evaluate_criterion(self, criterion: str, chart_spec: Dict[str, Any], config: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Evaluate a specific criterion."""
        if criterion == "has_title":
            return self._evaluate_title(chart_spec)
        elif criterion == "has_axis_labels":
            return self._evaluate_axis_labels(chart_spec)
        elif criterion == "appropriate_chart_type":
            return self._evaluate_chart_type(chart_spec)
        elif criterion == "has_data":
            return self._evaluate_data(chart_spec)
        elif criterion == "proper_encoding":
            return self._evaluate_encoding(chart_spec)
        elif criterion == "good_styling":
            return self._evaluate_styling(chart_spec)
        elif criterion == "responsive_design":
            return self._evaluate_responsive_design(chart_spec)
        else:
            return 0.0, [f"unknown_criterion_{criterion}"]
    
    def _evaluate_title(self, chart_spec: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Evaluate if chart has a proper title."""
        title = chart_spec.get("title", {})
        if isinstance(title, dict) and title.get("text"):
            return 1.0, []
        elif isinstance(title, str) and title.strip():
            return 1.0, []
        else:
            return 0.0, ["missing_title"]
    
    def _evaluate_axis_labels(self, chart_spec: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Evaluate if chart has proper axis labels."""
        encoding = chart_spec.get("encoding", {})
        x_has_title = encoding.get("x", {}).get("title") is not None
        y_has_title = encoding.get("y", {}).get("title") is not None
        
        if x_has_title and y_has_title:
            return 1.0, []
        elif x_has_title or y_has_title:
            return 0.5, ["partial_axis_labels"]
        else:
            return 0.0, ["missing_axis_labels"]
    
    def _evaluate_chart_type(self, chart_spec: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Evaluate if chart type is appropriate."""
        mark = chart_spec.get("mark", "")
        # Handle dict mark (e.g., {"type": "line", ...})
        if isinstance(mark, dict):
            mark_type = mark.get("type", "")
        else:
            mark_type = mark
        # Expanded list of valid Vega-Lite marks
        valid_marks = [
            "bar", "line", "point", "area", "circle", "square", "tick", "rect", "rule", "arc", "text", "geoshape", "trail", "boxplot", "errorband", "errorbar"
        ]
        if mark_type in valid_marks:
            return 1.0, []
        else:
            return 0.0, [f"invalid_chart_type: {mark_type}"]
    
    def _evaluate_data(self, chart_spec: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Evaluate if chart has proper data structure."""
        data = chart_spec.get("data", {})
        if "values" in data and isinstance(data["values"], list) and len(data["values"]) > 0:
            return 1.0, []
        else:
            return 0.0, ["missing_data"]
    
    def _evaluate_encoding(self, chart_spec: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Evaluate if chart has proper encoding."""
        encoding = chart_spec.get("encoding", {})
        
        if not encoding:
            return 0.0, ["missing_encoding"]
        
        # Check for basic x and y encoding
        has_x = "x" in encoding
        has_y = "y" in encoding
        
        if has_x and has_y:
            return 1.0, []
        elif has_x or has_y:
            return 0.5, ["partial_encoding"]
        else:
            return 0.0, ["missing_encoding"]
    
    def _evaluate_styling(self, chart_spec: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Evaluate chart styling."""
        # Check for basic styling elements
        has_width = "width" in chart_spec
        has_height = "height" in chart_spec
        
        if has_width and has_height:
            return 1.0, []
        elif has_width or has_height:
            return 0.5, ["partial_styling"]
        else:
            return 0.0, ["missing_styling"]
    
    def _evaluate_responsive_design(self, chart_spec: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Evaluate responsive design elements (less strict)."""
        # Consider responsive if autosize is present, or if width/height are not both fixed
        autosize = chart_spec.get("autosize")
        width = chart_spec.get("width")
        height = chart_spec.get("height")
        if autosize:
            return 1.0, []
        # If width and height are both missing or not both numbers, consider responsive
        if not (isinstance(width, (int, float)) and isinstance(height, (int, float))):
            return 1.0, []
        # If width or height is set to 'container', consider responsive
        if width == "container" or height == "container":
            return 1.0, []
        # Otherwise, not responsive
        return 0.0, ["not_responsive"]
    
    def _generate_detailed_feedback(self, criterion_details: Dict[str, Any], issues: List[str]) -> str:
        """Generate detailed feedback about the evaluation."""
        feedback_parts = []
        
        for criterion, details in criterion_details.items():
            score = details["score"]
            criterion_issues = details["issues"]
            weight = details["weight"]
            
            # Create educational feedback for each criterion
            if criterion == "has_title":
                if score == 1.0:
                    feedback_parts.append(f"✅ **Chart Title**: Excellent - The chart has a clear, descriptive title that helps users understand what they're looking at.")
                elif score >= 0.7:
                    feedback_parts.append(f"⚠️ **Chart Title**: Good - The chart has a title, but it could be more descriptive or specific.")
                else:
                    feedback_parts.append(f"❌ **Chart Title**: Missing - Charts should have titles to provide context. Consider adding a descriptive title.")
            
            elif criterion == "has_axis_labels":
                if score == 1.0:
                    feedback_parts.append(f"✅ **Axis Labels**: Excellent - Both X and Y axes have clear labels explaining what the data represents.")
                elif score >= 0.5:
                    feedback_parts.append(f"⚠️ **Axis Labels**: Partial - Only one axis has a label. Both axes should be labeled for clarity.")
                else:
                    feedback_parts.append(f"❌ **Axis Labels**: Missing - Axis labels help users understand what the data represents. Add labels to both axes.")
            
            elif criterion == "appropriate_chart_type":
                if score == 1.0:
                    feedback_parts.append(f"✅ **Chart Type**: Excellent - The chart type ({self._get_chart_type_name(criterion_details)}) is appropriate for the data and request.")
                else:
                    feedback_parts.append(f"❌ **Chart Type**: Invalid - The chart type may not be suitable. Consider using bar, line, point, area, or other standard chart types.")
            
            elif criterion == "has_data":
                if score == 1.0:
                    feedback_parts.append(f"✅ **Data Structure**: Excellent - The chart has properly structured data with values to visualize.")
                else:
                    feedback_parts.append(f"❌ **Data Structure**: Missing - Charts need data to visualize. Ensure the chart specification includes data values.")
            
            elif criterion == "proper_encoding":
                if score == 1.0:
                    feedback_parts.append(f"✅ **Data Encoding**: Excellent - The chart properly encodes data with appropriate X and Y mappings.")
                elif score >= 0.5:
                    feedback_parts.append(f"⚠️ **Data Encoding**: Partial - Only one axis is properly encoded. Both X and Y should map to data fields.")
                else:
                    feedback_parts.append(f"❌ **Data Encoding**: Missing - Charts need to encode data on both axes. Add proper X and Y field mappings.")
            
            elif criterion == "good_styling":
                if score == 1.0:
                    feedback_parts.append(f"✅ **Visual Styling**: Excellent - The chart has appropriate width and height for good readability.")
                elif score >= 0.5:
                    feedback_parts.append(f"⚠️ **Visual Styling**: Partial - The chart has some styling but could benefit from explicit dimensions.")
                else:
                    feedback_parts.append(f"❌ **Visual Styling**: Missing - Add width and height to ensure the chart displays properly.")
            
            elif criterion == "responsive_design":
                if score == 1.0:
                    feedback_parts.append(f"✅ **Responsive Design**: Excellent - The chart is designed to adapt to different screen sizes.")
                else:
                    feedback_parts.append(f"⚠️ **Responsive Design**: Could be improved - Consider adding autosize properties for better responsiveness.")
            
            # Add specific issues if any
            if criterion_issues:
                issue_explanations = []
                for issue in criterion_issues:
                    if issue == "missing_title":
                        issue_explanations.append("No chart title provided")
                    elif issue == "missing_axis_labels":
                        issue_explanations.append("Axis labels are missing")
                    elif issue == "invalid_chart_type":
                        issue_explanations.append("Chart type is not recognized")
                    elif issue == "missing_data":
                        issue_explanations.append("No data values found")
                    elif issue == "missing_encoding":
                        issue_explanations.append("Data encoding is incomplete")
                    elif issue == "missing_styling":
                        issue_explanations.append("Chart dimensions not specified")
                    else:
                        issue_explanations.append(issue)
                
                if issue_explanations:
                    feedback_parts.append(f"   **Issues**: {', '.join(issue_explanations)}")
        
        return " | ".join(feedback_parts)
    
    def _get_chart_type_name(self, criterion_details: Dict[str, Any]) -> str:
        """Get the chart type name for feedback."""
        # This would need to be passed from the chart builder
        return "bar"  # Default fallback
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for the agent.
        
        Args:
            state (Dict[str, Any]): Current state containing chart_spec
            
        Returns:
            Dict[str, Any]: Updated state with evaluation results
        """
        chart_spec = state.get("chart_spec")
        
        if not chart_spec:
            raise ValueError("chart_spec is required in state")
        
        evaluation_results = self.evaluate_chart(chart_spec)
        
        # Determine if clarifier should be triggered
        should_clarify = evaluation_results["score"] == 0 and "invalid_input" in evaluation_results["issues"]
        
        return {
            **state,
            "heuristic_score": evaluation_results["score"],
            "heuristic_issues": evaluation_results["issues"],
            "should_clarify": should_clarify,
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "heuristic_evaluator": {
                    "score": evaluation_results["score"],
                    "issues": evaluation_results["issues"],
                    "should_clarify": should_clarify,
                    "status": "completed",
                    "criterion_scores": evaluation_results["criterion_scores"],
                    "criterion_details": evaluation_results["criterion_details"],
                    "chart_valid": evaluation_results["chart_valid"],
                    "raw_score": evaluation_results["raw_score"],
                    "max_possible_score": evaluation_results["max_possible_score"],
                    "detailed_feedback": evaluation_results["detailed_feedback"]
                }
            }
        }


# Example usage
if __name__ == "__main__":
    agent = HeuristicEvaluatorAgent()
    
    # Test with a valid chart spec
    test_chart_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": {"text": "Test Chart"},
        "data": {"values": [{"x": 1, "y": 2}]},
        "mark": "bar",
        "encoding": {
            "x": {"field": "x", "type": "quantitative", "title": "X Axis"},
            "y": {"field": "y", "type": "quantitative", "title": "Y Axis"}
        }
    }
    
    test_state = {"chart_spec": test_chart_spec}
    result = agent.run(test_state)
    print(json.dumps(result, indent=2)) 