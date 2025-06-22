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
    
    def evaluate_chart(self, chart_spec: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Evaluate a chart specification using heuristic rules.
        
        Args:
            chart_spec (Dict[str, Any]): Vega-Lite chart specification
            
        Returns:
            Tuple[float, List[str]]: Score (0-10) and list of issue tags
        """
        score = 0.0
        issues = []
        
        # Check if chart spec is valid
        if not self._is_valid_chart_spec(chart_spec):
            return 0.0, ["invalid_chart_spec"]
        
        # Evaluate each criterion
        for criterion, config in self.criteria.items():
            criterion_score, criterion_issues = self._evaluate_criterion(
                criterion, chart_spec, config
            )
            
            if criterion_score == 0 and config["required"]:
                issues.extend(criterion_issues)
                if "invalid_input" in criterion_issues:
                    return 0.0, ["invalid_input"]
            
            score += criterion_score * config["weight"]
            issues.extend(criterion_issues)
        
        return min(score * 10, 10.0), issues
    
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
        encoding = chart_spec.get("encoding", {})
        
        # Basic chart type validation
        valid_marks = ["bar", "line", "point", "area", "circle", "square", "tick"]
        if mark in valid_marks:
            return 1.0, []
        else:
            return 0.0, ["invalid_chart_type"]
    
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
        """Evaluate responsive design elements."""
        # For now, just check if autosize is present
        autosize = chart_spec.get("autosize")
        if autosize:
            return 1.0, []
        else:
            return 0.0, ["not_responsive"]
    
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
        
        score, issues = self.evaluate_chart(chart_spec)
        
        # Determine if clarifier should be triggered
        should_clarify = score == 0 and "invalid_input" in issues
        
        return {
            **state,
            "heuristic_score": score,
            "heuristic_issues": issues,
            "should_clarify": should_clarify,
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "heuristic_evaluator": {
                    "score": score,
                    "issues": issues,
                    "should_clarify": should_clarify,
                    "status": "completed"
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