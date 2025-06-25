"""
Prompt Rewriter Agent

This agent takes evaluation feedback and rewrites the prompt to address issues
and improve the chart specification.

Input: prompt (string), heuristic_issues (list), llm_feedback (string), final_score (float)
Output: rewritten_prompt (string), rewrite_reason (string)
"""

from typing import Dict, Any, List
import json
from llm_utils import chat_completion
from learning_cache import learning_cache


class PromptRewriterAgent:
    """Agent responsible for rewriting prompts based on evaluation feedback."""
    
    def __init__(self):
        self.name = "rewriter"
        self.description = "Rewrites prompts based on evaluation feedback to improve chart quality"
    
    def rewrite_prompt(self, prompt: str, heuristic_issues: List[str], 
                      llm_feedback: str, final_score: float) -> tuple[str, str]:
        """
        Rewrite the prompt based on evaluation feedback.
        
        Args:
            prompt (str): Original prompt
            heuristic_issues (List[str]): Issues found by heuristic evaluator
            llm_feedback (str): Feedback from LLM evaluator
            final_score (float): Final score from scoring agent
            
        Returns:
            tuple[str, str]: (rewritten_prompt, rewrite_reason)
        """
        # Debug logging
        print(f"[REWRITER DEBUG] Original prompt: {prompt}")
        print(f"[REWRITER DEBUG] Heuristic issues: {heuristic_issues}")
        print(f"[REWRITER DEBUG] LLM feedback: {llm_feedback}")
        print(f"[REWRITER DEBUG] Final score: {final_score}")
        # Only use cache if score is low (<8.0)
        cache_suggestions = []
        if final_score < 8.0:
            cache_suggestions = learning_cache.suggest_improvements(heuristic_issues)
        if cache_suggestions:
            print(f"🎯 Using cached improvement patterns for {len(heuristic_issues)} issues")
            cached_suggestion = cache_suggestions[0]
            rewrite_reason = f"Applied learned pattern for issues: {', '.join(heuristic_issues)}. Suggestion: {cached_suggestion}"
            improved_prompt = self._apply_cached_suggestion(prompt, cached_suggestion)
            prompt_for_llm = improved_prompt
        else:
            prompt_for_llm = prompt
        # Always allow LLM to rewrite, and encourage modern features
        system_prompt = (
            "You are a helpful assistant that rewrites visualization prompts to address "
            "specific issues and improve chart quality. Focus on clarity, specificity, "
            "modern color schemes, interactivity (tooltips, selection, hover), and responsive design. "
            "Use the LLM evaluator's feedback to guide improvements."
        )
        user_message = f"""
        Original Prompt: {prompt_for_llm}
        Issues to Address:
        - Heuristic Issues: {', '.join(heuristic_issues) if heuristic_issues else 'None'}
        - LLM Feedback: {llm_feedback}
        - Current Score: {final_score}/10
        Please rewrite the prompt to address these issues and improve the chart specification.\nFocus on making the prompt more specific, clear, actionable, and modern.\nExplicitly request modern color schemes, interactivity (tooltips, selection, hover), and responsive design if not already present."
        """
        llm_response = chat_completion(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=400
        )
        if llm_response.startswith("[MOCK") or llm_response.startswith("[LLM ERROR"):
            rewritten_prompt, rewrite_reason = self._template_rewrite(prompt_for_llm, heuristic_issues, llm_feedback, final_score)
        else:
            rewritten_prompt = llm_response.strip()
            main_issues = ', '.join(heuristic_issues) if heuristic_issues else 'none'
            feedback_summary = llm_feedback[:80] + ('...' if len(llm_feedback) > 80 else '')
            rewrite_reason = f"LLM rewrite: addressed issues [{main_issues}] and feedback: '{feedback_summary}'"
        print(f"[REWRITER DEBUG] Rewritten prompt: {rewritten_prompt}")
        return rewritten_prompt, rewrite_reason
    
    def _apply_cached_suggestion(self, prompt: str, suggestion: str) -> str:
        """
        Apply a cached suggestion to improve the prompt.
        
        Args:
            prompt (str): Original prompt
            suggestion (str): Cached improvement suggestion
            
        Returns:
            str: Improved prompt
        """
        # Simple improvement based on common patterns
        improved_prompt = prompt
        
        # Add specificity if the suggestion mentions it
        if "specific" in suggestion.lower():
            improved_prompt += "\n\nPlease be very specific about chart type, data handling, and visual elements."
        
        # Add clarity if the suggestion mentions it
        if "clear" in suggestion.lower():
            improved_prompt += "\n\nEnsure the chart is clear and easy to interpret with proper labels and titles."
        
        # Add data handling if the suggestion mentions it
        if "data" in suggestion.lower():
            improved_prompt += "\n\nInclude proper data transformations and aggregations as needed."
        
        return improved_prompt
    
    def _template_rewrite(self, prompt: str, heuristic_issues: List[str], 
                         llm_feedback: str, final_score: float) -> tuple[str, str]:
        """
        Template-based prompt rewriting when LLM is unavailable.
        
        Args:
            prompt (str): Original prompt
            heuristic_issues (List[str]): Issues found by heuristic evaluator
            llm_feedback (str): Feedback from LLM evaluator
            final_score (float): Final score from scoring agent
            
        Returns:
            tuple[str, str]: (rewritten_prompt, rewrite_reason)
        """
        improvements = []
        
        # Address common issues
        if any("axis" in issue.lower() for issue in heuristic_issues):
            improvements.append("Include clear axis labels and titles")
        
        if any("color" in issue.lower() for issue in heuristic_issues):
            improvements.append("Use meaningful colors and ensure good contrast")
        
        if any("data" in issue.lower() for issue in heuristic_issues):
            improvements.append("Specify data handling and transformations")
        
        if any("type" in issue.lower() for issue in heuristic_issues):
            improvements.append("Be specific about chart type and mark selection")
        
        # Add improvements to prompt
        if improvements:
            improved_prompt = prompt + "\n\nAdditional requirements:\n" + "\n".join(f"- {imp}" for imp in improvements)
            rewrite_reason = f"Template rewrite addressing {len(heuristic_issues)} issues"
        else:
            improved_prompt = prompt + "\n\nPlease ensure the chart is clear, well-labeled, and effectively communicates the data insights."
            rewrite_reason = "General improvement template applied"
        
        return improved_prompt, rewrite_reason
    
    def should_continue_optimization(self, final_score: float, iteration: int, 
                                   max_iterations: int) -> tuple[bool, str]:
        """
        Determine if optimization should continue.
        
        Args:
            final_score (float): Current final score
            iteration (int): Current iteration number
            max_iterations (int): Maximum allowed iterations
        
        Returns:
            tuple[bool, str]: (should_continue, reason)
        """
        if iteration >= max_iterations:
            return False, f"Reached maximum iterations ({max_iterations})"
        # Only stop if score is 9.5 or greater and at least one iteration has been output
        if final_score >= 9.5 and iteration > 1:
            return False, "Achieved excellent score (≥9.5)"
        if final_score >= 8.0 and iteration >= 2:
            return False, "Achieved good score (≥8.0) after multiple iterations"
        if final_score < 3.0 and iteration >= 2:
            return False, "Score too low after multiple iterations"
        return True, "Continuing optimization"
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for the agent.
        
        Args:
            state (Dict[str, Any]): Current state containing prompt, issues, and feedback
            
        Returns:
            Dict[str, Any]: Updated state with rewritten prompt
        """
        prompt = state.get("prompt", "")
        heuristic_issues = state.get("heuristic_issues", [])
        llm_feedback = state.get("llm_feedback", "")
        final_score = state.get("final_score", 0.0)
        iteration = state.get("iteration", 1)
        max_iterations = state.get("max_iterations", 5)
        
        if not prompt:
            raise ValueError("prompt is required in state")
        
        # Rewrite the prompt
        rewritten_prompt, rewrite_reason = self.rewrite_prompt(
            prompt, heuristic_issues, llm_feedback, final_score
        )
        
        # Determine if optimization should continue
        should_continue, continue_reason = self.should_continue_optimization(
            final_score, iteration, max_iterations
        )
        
        return {
            **state,
            "prompt": rewritten_prompt,
            "rewrite_reason": rewrite_reason,
            "should_continue": should_continue,
            "continue_reason": continue_reason,
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "rewriter": {
                    "rewritten_prompt": rewritten_prompt,
                    "rewrite_reason": rewrite_reason,
                    "should_continue": should_continue,
                    "continue_reason": continue_reason,
                    "status": "completed"
                }
            }
        }


# Example usage
if __name__ == "__main__":
    agent = PromptRewriterAgent()
    test_state = {
        "prompt": "Create a chart showing revenue by region",
        "heuristic_issues": ["Missing axis labels", "No title specified"],
        "llm_feedback": "Chart is functional but could be more informative",
        "final_score": 6.5,
        "iteration": 1,
        "max_iterations": 5
    }
    result = agent.run(test_state)
    print(json.dumps(result, indent=2)) 