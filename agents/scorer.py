"""
Scoring Agent

This agent combines outputs from Heuristic and LLM Evaluators to produce a weighted score
and determine whether to continue iterating or stop.

Input: heuristic_score, llm_score, heuristic_issues, llm_feedback
Output: weighted_score, summary, continue_flag
"""

from typing import Dict, Any, Tuple
import json


class ScoringAgent:
    """Agent responsible for combining evaluation scores and determining next steps."""
    
    def __init__(self):
        self.name = "scorer"
        self.description = "Combines evaluation scores and determines iteration control"
        
        # Scoring weights
        self.heuristic_weight = 0.4
        self.llm_weight = 0.6
        
        # Thresholds
        self.continue_threshold = 9.5  # Score above which to stop iterating
        self.max_iterations = 5  # Maximum number of iterations
    
    def calculate_final_score(self, heuristic_score: float, llm_score: float) -> float:
        """
        Calculate weighted final score from heuristic and LLM evaluations.
        
        Args:
            heuristic_score (float): Score from heuristic evaluator (0-10)
            llm_score (float): Score from LLM evaluator (0-10)
            
        Returns:
            float: Weighted final score (0-10)
        """
        weighted_score = (
            heuristic_score * self.heuristic_weight +
            llm_score * self.llm_weight
        )
        
        return round(weighted_score, 2)
    
    def generate_summary(self, heuristic_score: float, llm_score: float, 
                        heuristic_issues: list, llm_feedback: str) -> str:
        """
        Generate a summary of the evaluation results.
        
        Args:
            heuristic_score (float): Heuristic evaluation score
            llm_score (float): LLM evaluation score
            heuristic_issues (list): Issues identified by heuristic evaluator
            llm_feedback (str): Feedback from LLM evaluator
            
        Returns:
            str: Summary of evaluation results
        """
        summary_parts = []
        
        # Overall assessment
        final_score = self.calculate_final_score(heuristic_score, llm_score)
        
        if final_score >= 9.0:
            summary_parts.append("Excellent chart quality with high scores across all criteria.")
        elif final_score >= 7.0:
            summary_parts.append("Good chart quality with room for minor improvements.")
        elif final_score >= 5.0:
            summary_parts.append("Moderate chart quality requiring significant improvements.")
        else:
            summary_parts.append("Poor chart quality requiring major revisions.")
        
        # Score breakdown
        summary_parts.append(f"Heuristic score: {heuristic_score}/10")
        summary_parts.append(f"LLM score: {llm_score}/10")
        summary_parts.append(f"Final weighted score: {final_score}/10")
        
        # Issues summary
        if heuristic_issues:
            issues_str = ", ".join(heuristic_issues)
            summary_parts.append(f"Identified issues: {issues_str}")
        
        # LLM feedback summary
        if llm_feedback:
            summary_parts.append(f"LLM feedback: {llm_feedback}")
        
        return " ".join(summary_parts)
    
    def should_continue(self, final_score: float, iteration: int, 
                       heuristic_issues: list) -> Tuple[bool, str]:
        """
        Determine if the iteration should continue or stop.
        
        Args:
            final_score (float): Final weighted score
            iteration (int): Current iteration number
            heuristic_issues (list): Issues from heuristic evaluation
            
        Returns:
            Tuple[bool, str]: Whether to continue and reason
        """
        # Check if we've reached the maximum iterations
        if iteration >= self.max_iterations:
            return False, f"Maximum iterations ({self.max_iterations}) reached"
        
        # Only stop if score is 9.5 or greater and at least one iteration has been output
        if final_score >= self.continue_threshold and iteration > 1:
            return False, f"Target score ({self.continue_threshold}) achieved"
        
        # Check for critical issues that require clarification
        critical_issues = ["invalid_input", "invalid_chart_spec", "missing_data"]
        if any(issue in heuristic_issues for issue in critical_issues):
            return False, "Critical issues detected requiring clarification"
        
        # Continue if score is below threshold and no critical issues
        return True, f"Score {final_score} below threshold {self.continue_threshold}, continuing iteration"
    
    def determine_status(self, final_score: float, iteration: int) -> str:
        """
        Determine the current status of the optimization process.
        
        Args:
            final_score (float): Final weighted score
            iteration (int): Current iteration number
            
        Returns:
            str: Status description
        """
        if final_score >= self.continue_threshold:
            return "Optimal"
        elif iteration >= self.max_iterations:
            return "Max iterations reached"
        elif final_score >= 7.0:
            return "Good quality"
        elif final_score >= 5.0:
            return "Needs refinement"
        else:
            return "Poor quality"
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for the agent.
        
        Args:
            state (Dict[str, Any]): Current state containing evaluation results
            
        Returns:
            Dict[str, Any]: Updated state with scoring results
        """
        heuristic_score = state.get("heuristic_score", 0.0)
        llm_score = state.get("llm_score", 0.0)
        heuristic_issues = state.get("heuristic_issues", [])
        llm_feedback = state.get("llm_feedback", "")
        iteration = state.get("iteration", 1)
        
        # Calculate final score
        final_score = self.calculate_final_score(heuristic_score, llm_score)
        
        # Generate summary
        summary = self.generate_summary(
            heuristic_score, llm_score, heuristic_issues, llm_feedback
        )
        
        # Determine if should continue
        should_continue, continue_reason = self.should_continue(
            final_score, iteration, heuristic_issues
        )
        
        # Determine status
        status = self.determine_status(final_score, iteration)
        
        return {
            **state,
            "final_score": final_score,
            "summary": summary,
            "should_continue": should_continue,
            "continue_reason": continue_reason,
            "status": status,
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "scorer": {
                    "final_score": final_score,
                    "summary": summary,
                    "should_continue": should_continue,
                    "continue_reason": continue_reason,
                    "status": status,
                    "status": "completed"
                }
            }
        }


# Example usage
if __name__ == "__main__":
    agent = ScoringAgent()
    
    test_state = {
        "heuristic_score": 8.0,
        "llm_score": 7.5,
        "heuristic_issues": ["partial_styling"],
        "llm_feedback": "Chart has good clarity and appropriate chart type for time-based data.",
        "iteration": 2
    }
    
    result = agent.run(test_state)
    print(json.dumps(result, indent=2)) 