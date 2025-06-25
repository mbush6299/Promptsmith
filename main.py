"""
Promptsmith Chart Optimizer - Main Orchestrator

This is the main entry point for the multi-agent system that optimizes chart generation
through iterative prompt improvement and evaluation.

Flow: User Input → Prompt Generator → Chart Builder → Evaluators → Scoring → Rewriter → Loop
"""

import json
import sys
from typing import Dict, Any, List
from agents.prompt_generator import PromptGeneratorAgent
from agents.chart_builder import ChartBuilderAgent
from agents.evaluator_heuristic import HeuristicEvaluatorAgent
from agents.evaluator_llm import LLMEvaluatorAgent
from agents.scorer import ScoringAgent
from agents.rewriter import PromptRewriterAgent
from agents.clarifier import ClarifierAgent
from learning_cache import learning_cache
from config import Config
import traceback


class PromptsmithOrchestrator:
    """Main orchestrator for the Promptsmith Chart Optimizer system."""
    
    def __init__(self):
        """Initialize all agents."""
        self.prompt_generator = PromptGeneratorAgent()
        self.chart_builder = ChartBuilderAgent()
        self.heuristic_evaluator = HeuristicEvaluatorAgent()
        self.llm_evaluator = LLMEvaluatorAgent()
        self.scorer = ScoringAgent()
        self.rewriter = PromptRewriterAgent()
        self.clarifier = ClarifierAgent()
        
        # Track iteration history
        self.iteration_history = []
    
    def run_optimization(self, user_query: str, max_iterations: int = 5) -> Dict[str, Any]:
        iteration_history = []  # Local variable for iteration history
        """
        Run the complete chart optimization process.
        
        Args:
            user_query (str): User's natural language query
            max_iterations (int): Maximum number of iterations
            
        Returns:
            Dict[str, Any]: Final results with optimized chart and prompt
        """
        print(f"🚀 Starting Promptsmith Chart Optimizer")
        print(f"📝 User Query: {user_query}")
        print(f"🔄 Max Iterations: {max_iterations}")
        
        # Show cache stats
        cache_stats = learning_cache.get_stats()
        if cache_stats["total_runs"] > 0:
            print(f"🧠 Learning Cache: {cache_stats['total_runs']} previous runs, {cache_stats['query_patterns']} patterns learned")
            print(f"📊 Average Score: {cache_stats['avg_score']:.2f}/10")
        
        print("-" * 50)
        
        # Initialize state
        state = {
            "user_query": user_query,
            "max_iterations": max_iterations,
            "iteration": 1,
            "agent_outputs": {},
            "iteration_history": [],
            "progress": {
                "current_step": "initializing",
                "current_agent": None,
                "step_details": {},
                "overall_progress": 0
            }
        }
        
        best_result = None
        best_score = 0.0
        
        try:
            # Main optimization loop
            for iteration in range(1, max_iterations + 1):
                print(f"\n🔄 Iteration {iteration}")
                print("-" * 30)
                
                # Update iteration number
                state["iteration"] = iteration
                state["progress"]["overall_progress"] = (iteration - 1) / max_iterations * 100
                
                # Step 1: Generate prompt (only on first iteration)
                if iteration == 1:
                    print("📝 Generating prompt...")
                    state["progress"]["current_step"] = "generating_prompt"
                    state["progress"]["current_agent"] = "prompt_generator"
                    state = self.prompt_generator.run(state)
                
                # Step 2: Build chart (always use current prompt)
                print("📊 Building chart...")
                state["progress"]["current_step"] = "building_chart"
                state["progress"]["current_agent"] = "chart_builder"
                state = self.chart_builder.run(state)
                
                # Step 3: Heuristic evaluation
                print("🔍 Running heuristic evaluation...")
                state["progress"]["current_step"] = "heuristic_evaluation"
                state["progress"]["current_agent"] = "heuristic_evaluator"
                state = self.heuristic_evaluator.run(state)
                
                # Check if clarification is needed
                if state.get("should_clarify", False):
                    print("❓ Clarification needed, triggering clarifier...")
                    state["progress"]["current_step"] = "clarification"
                    state["progress"]["current_agent"] = "clarifier"
                    state = self.clarifier.run(state)
                    
                    if state.get("clarification_needed", False):
                        print(f"💡 Clarification Question: {state.get('clarification_question')}")
                        print(f"💡 Suggested Query: {state.get('suggested_query')}")
                        return {
                            "status": "clarification_needed",
                            "clarification_question": state.get("clarification_question"),
                            "suggested_query": state.get("suggested_query"),
                            "iteration": iteration,
                            "progress": state["progress"]
                        }
                
                # Step 4: LLM evaluation (only if heuristic passes)
                if state.get("chart_valid", True):
                    print("🤖 Running LLM evaluation...")
                    state["progress"]["current_step"] = "llm_evaluation"
                    state["progress"]["current_agent"] = "llm_evaluator"
                    state = self.llm_evaluator.run(state)
                    
                    # Step 5: Scoring
                    print("📊 Calculating final score...")
                    state["progress"]["current_step"] = "scoring"
                    state["progress"]["current_agent"] = "scorer"
                    state = self.scorer.run(state)
                    
                    final_score = state.get("final_score", 0.0)
                    print(f"🎯 Final Score: {final_score}/10")
                    
                    # Track best result
                    if final_score > best_score:
                        best_score = final_score
                        best_result = state.copy()
                    
                    # Check if we should continue
                    if not state.get("should_continue", True):
                        print(f"✅ Optimization complete: {state.get('continue_reason')}")
                        break
                    
                    # Step 6: Rewrite prompt for next iteration (from iteration 2 onward)
                    if iteration < max_iterations:
                        print("✏️ Rewriting prompt for next iteration...")
                        state["progress"]["current_step"] = "rewriting_prompt"
                        state["progress"]["current_agent"] = "rewriter"
                        state = self.rewriter.run(state)
                        print(f"💡 Rewrite reason: {state.get('rewrite_reason')}")
                        # Use the rewritten prompt for the next iteration
                        state["prompt"] = state.get("prompt", state.get("rewritten_prompt", ""))
                
                # Store detailed iteration results
                iteration_result = {
                    "iteration": iteration,
                    "prompt": state.get("prompt", ""),
                    "chart_spec": state.get("chart_spec", {}),
                    "heuristic_score": state.get("heuristic_score", 0.0),
                    "llm_score": state.get("llm_score", 0.0),
                    "final_score": state.get("final_score", 0.0),
                    "status": state.get("status", "unknown"),
                    "agent_outputs": {
                        "prompt_generator": {
                            "prompt": state.get("prompt", ""),
                            "from_cache": state.get("prompt_from_cache", False),
                            "cache_hit": state.get("prompt_cache_hit", None),
                            "generation_method": state.get("prompt_generation_method", "unknown"),
                            "reasoning": "The prompt generator analyzes your request and creates a detailed specification for the chart builder. It considers chart type, data requirements, and styling preferences to ensure the final visualization meets your needs."
                        },
                        "chart_builder": {
                            "chart_spec": state.get("chart_spec", {}),
                            "chart_type": state.get("chart_type", "unknown"),
                            "from_cache": state.get("chart_from_cache", False),
                            "cache_hit": state.get("chart_cache_hit", None),
                            "generation_method": state.get("chart_generation_method", "unknown"),
                            "reasoning": "The chart builder converts the prompt into a Vega-Lite specification. It generates appropriate sample data and ensures the chart structure follows best practices for data visualization."
                        },
                        "heuristic_evaluator": {
                            "score": state.get("heuristic_score", 0.0),
                            "issues": state.get("heuristic_issues", []),
                            "chart_valid": state.get("chart_valid", True),
                            "should_clarify": state.get("should_clarify", False),
                            "detailed_feedback": state.get("heuristic_detailed_feedback", ""),
                            "reasoning": "The heuristic evaluator checks technical aspects like chart structure, data encoding, and visual elements. It ensures the chart follows Vega-Lite best practices and will render correctly."
                        },
                        "llm_evaluator": {
                            "score": state.get("llm_score", 0.0),
                            "feedback": state.get("llm_feedback", ""),
                            "strengths": state.get("llm_strengths", []),
                            "weaknesses": state.get("llm_weaknesses", []),
                            "educational_insights": state.get("llm_educational_insights", []),
                            "educational_summary": state.get("llm_educational_summary", ""),
                            "reasoning": "The LLM evaluator assesses how well the chart fulfills your original request. It considers appropriateness, clarity, insight potential, and provides educational feedback about chart design principles."
                        },
                        "scorer": {
                            "final_score": state.get("final_score", 0.0),
                            "score_breakdown": state.get("score_breakdown", {}),
                            "should_continue": state.get("should_continue", True),
                            "continue_reason": state.get("continue_reason", ""),
                            "reasoning": "The scorer combines heuristic and LLM evaluations to determine overall quality. It decides whether to continue optimization or if the chart meets quality standards."
                        },
                        "rewriter": {
                            "rewrite_reason": state.get("rewrite_reason", ""),
                            "reasoning": "The rewriter analyzes feedback from evaluators and suggests improvements to the prompt for the next iteration. It applies learned patterns to address common issues."
                        }
                    },
                    "progress": {
                        "step": state["progress"]["current_step"],
                        "agent": state["progress"]["current_agent"],
                        "overall_progress": (iteration / max_iterations) * 100
                    }
                }
                
                iteration_history.append(iteration_result)
                state["iteration_history"] = iteration_history
                
                print(f"📈 Iteration {iteration} complete - Score: {final_score}/10")
            
            # Return best result or final result
            result_state = best_result if best_result else state
            result_state["progress"]["overall_progress"] = 100
            result_state["progress"]["current_step"] = "complete"
            result_state["progress"]["current_agent"] = None
            
            # Save to learning cache
            if result_state.get("final_score", 0.0) > 0:
                learning_cache.add_run(
                    user_query=user_query,
                    prompt=result_state.get("prompt", ""),
                    chart_spec=result_state.get("chart_spec", {}),
                    heuristic_score=result_state.get("heuristic_score", 0.0),
                    llm_score=result_state.get("llm_score", 0.0),
                    heuristic_issues=result_state.get("heuristic_issues", []),
                    llm_feedback=result_state.get("llm_feedback", ""),
                    final_score=result_state.get("final_score", 0.0)
                )
                print(f"🧠 Saved run to learning cache")
            
            return self._format_final_output(result_state, iteration_history)
            
        except Exception as e:
            print(f"❌ Error during optimization: {str(e)}")
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "iteration": state.get("iteration", 1),
                "progress": state.get("progress", {})
            }
    
    def _format_final_output(self, state: Dict[str, Any], iteration_history: list) -> Dict[str, Any]:
        """
        Format the final output according to the specified format.
        
        Args:
            state (Dict[str, Any]): Final state
            iteration_history (list): Iteration history
            
        Returns:
            Dict[str, Any]: Formatted output
        """
        return {
            "iteration": state.get("iteration", 1),
            "prompt": state.get("prompt", ""),
            "chart_spec": state.get("chart_spec", {}),
            "chart_image_url": "mock_chart_url.png",  # Placeholder for actual chart rendering
            "scores": {
                "heuristic": state.get("heuristic_score", 0.0),
                "llm": state.get("llm_score", 0.0)
            },
            "final_score": state.get("final_score", 0.0),
            "rewrite_reason": state.get("rewrite_reason", ""),
            "status": state.get("status", "unknown"),
            "iteration_history": iteration_history,  # Use the local iteration history
            "progress": state.get("progress", {}),
            "agent_outputs": {
                "prompt_generator": {
                    "prompt": state.get("prompt", ""),
                    "from_cache": state.get("prompt_from_cache", False),
                    "cache_hit": state.get("prompt_cache_hit", None),
                    "generation_method": state.get("prompt_generation_method", "unknown"),
                    "status": "completed",
                    "reasoning": "The prompt generator analyzes your request and creates a detailed specification for the chart builder. It considers chart type, data requirements, and styling preferences to ensure the final visualization meets your needs."
                },
                "chart_builder": {
                    "chart_spec": state.get("chart_spec", {}),
                    "chart_type": state.get("chart_type", "unknown"),
                    "from_cache": state.get("chart_from_cache", False),
                    "cache_hit": state.get("chart_cache_hit", None),
                    "generation_method": state.get("chart_generation_method", "unknown"),
                    "status": "completed",
                    "reasoning": "The chart builder converts the prompt into a Vega-Lite specification. It generates appropriate sample data and ensures the chart structure follows best practices for data visualization."
                },
                "heuristic_evaluator": {
                    "score": state.get("heuristic_score", 0.0),
                    "issues": state.get("heuristic_issues", []),
                    "chart_valid": state.get("chart_valid", True),
                    "should_clarify": state.get("should_clarify", False),
                    "detailed_feedback": state.get("heuristic_detailed_feedback", ""),
                    "status": "completed",
                    "reasoning": "The heuristic evaluator checks technical aspects like chart structure, data encoding, and visual elements. It ensures the chart follows Vega-Lite best practices and will render correctly."
                },
                "llm_evaluator": {
                    "score": state.get("llm_score", 0.0),
                    "feedback": state.get("llm_feedback", ""),
                    "strengths": state.get("llm_strengths", []),
                    "weaknesses": state.get("llm_weaknesses", []),
                    "educational_insights": state.get("llm_educational_insights", []),
                    "educational_summary": state.get("llm_educational_summary", ""),
                    "status": "completed",
                    "reasoning": "The LLM evaluator assesses chart effectiveness, clarity, and insight potential using AI reasoning. It provides detailed feedback on how well the chart meets the user's intent."
                },
                "scorer": {
                    "final_score": state.get("final_score", 0.0),
                    "score_breakdown": state.get("score_breakdown", {}),
                    "should_continue": state.get("should_continue", True),
                    "continue_reason": state.get("continue_reason", ""),
                    "status": "completed",
                    "reasoning": "The scorer combines heuristic and LLM evaluations to determine overall quality. It decides whether to continue optimization or if the chart meets quality standards."
                },
                "rewriter": {
                    "rewrite_reason": state.get("rewrite_reason", ""),
                    "status": "completed",
                    "reasoning": "The rewriter analyzes feedback from evaluators and suggests improvements to the prompt for the next iteration. It applies learned patterns to address common issues."
                }
            },
            "cache_stats": learning_cache.get_stats(),
            "user_query": state.get("user_query", ""),
            "max_iterations": state.get("max_iterations", 3),
            "educational_notes": {
                "chart_type_choice": self._explain_chart_type_choice(state.get("chart_spec", {}), state.get("user_query", "")),
                "data_visualization_principles": self._get_data_viz_principles(state.get("chart_spec", {})),
                "improvement_suggestions": self._get_improvement_suggestions(state.get("heuristic_issues", []), state.get("llm_weaknesses", []))
            }
        }
    
    def print_summary(self, result: Dict[str, Any]):
        """Print a summary of the optimization results."""
        print("\n" + "=" * 60)
        print("🎉 OPTIMIZATION COMPLETE")
        print("=" * 60)
        
        print(f"📊 Final Score: {result.get('final_score', 0.0)}/10")
        print(f"🔄 Total Iterations: {result.get('iteration', 1)}")
        print(f"📈 Status: {result.get('status', 'unknown')}")
        
        scores = result.get("scores", {})
        print(f"🔍 Heuristic Score: {scores.get('heuristic', 0.0)}/10")
        print(f"🤖 LLM Score: {scores.get('llm', 0.0)}/10")
        
        if result.get("rewrite_reason"):
            print(f"✏️ Final Rewrite Reason: {result['rewrite_reason']}")
        
        print("\n📝 Final Prompt:")
        print("-" * 30)
        print(result.get("prompt", ""))
        
        print("\n📊 Chart Specification:")
        print("-" * 30)
        print(json.dumps(result.get("chart_spec", {}), indent=2))
        
        # Show updated cache stats
        cache_stats = learning_cache.get_stats()
        print(f"\n🧠 Learning Cache Stats:")
        print(f"   Total Runs: {cache_stats['total_runs']}")
        print(f"   Patterns Learned: {cache_stats['query_patterns']}")
        print(f"   Average Score: {cache_stats['avg_score']:.2f}/10")

    def _explain_chart_type_choice(self, chart_spec: Dict[str, Any], user_query: str) -> str:
        """Explain why a particular chart type was chosen."""
        mark = chart_spec.get("mark", "")
        print(f"[DEBUG] chart_spec['mark']: {mark} (type: {type(mark)})")
        if isinstance(mark, dict):
            mark = mark.get("type", "")
        query_lower = user_query.lower()
        
        chart_explanations = {
            "bar": "Bar charts are excellent for comparing categories or discrete values. They make it easy to compare values at a glance and work well for categorical data like regions, products, or time periods.",
            "line": "Line charts are perfect for showing trends over time or continuous relationships. They excel at displaying how values change and can reveal patterns, trends, and cycles in your data.",
            "point": "Scatter plots (point charts) are ideal for showing correlations and relationships between two variables. They can reveal clusters, outliers, and the strength of relationships in your data.",
            "area": "Area charts are great for showing cumulative data or emphasizing volume over time. They work well for stacked data or when you want to show parts of a whole changing over time.",
            "circle": "Circle charts (scatter plots) are excellent for showing relationships between variables and can handle large datasets effectively while revealing patterns and outliers."
        }
        
        base_explanation = chart_explanations.get(mark, f"The {mark} chart type was chosen based on your request.")
        
        # Add context-specific explanation
        if "time" in query_lower or "trend" in query_lower:
            if mark == "line":
                return f"{base_explanation} Since you asked about time-based data, a line chart is the optimal choice as it clearly shows how values change over time."
            else:
                return f"{base_explanation} For time-based data, consider using a line chart in future iterations as it typically shows trends more clearly."
        
        elif "compare" in query_lower or "region" in query_lower:
            if mark == "bar":
                return f"{base_explanation} Since you're comparing categories, a bar chart is the perfect choice as it makes comparisons easy and clear."
            else:
                return f"{base_explanation} For comparing categories, bar charts are usually the most effective choice."
        
        return base_explanation
    
    def _get_data_viz_principles(self, chart_spec: Dict[str, Any]) -> str:
        """Provide educational content about data visualization principles."""
        principles = [
            "**Clarity First**: The most important principle is that your chart should be immediately understandable to your audience.",
            "**Choose the Right Chart Type**: Different chart types serve different purposes - bars for comparisons, lines for trends, scatter plots for relationships.",
            "**Label Everything**: Always include clear titles, axis labels, and legends to provide context.",
            "**Use Color Purposefully**: Color should enhance understanding, not just decoration. Use it to highlight important information.",
            "**Keep It Simple**: Avoid unnecessary visual elements that don't add value to the data story.",
            "**Consider Your Audience**: Design charts that your specific audience can understand and find useful."
        ]
        
        return " | ".join(principles)
    
    def _get_improvement_suggestions(self, heuristic_issues: List[str], llm_weaknesses: List[str]) -> str:
        """Provide specific improvement suggestions based on issues found."""
        suggestions = []
        
        # Map issues to suggestions
        issue_suggestions = {
            "missing_title": "Add a descriptive title that explains what the chart shows",
            "missing_axis_labels": "Include clear labels for both X and Y axes",
            "invalid_chart_type": "Consider using standard chart types like bar, line, point, or area",
            "missing_data": "Ensure the chart specification includes data values",
            "missing_encoding": "Map data fields properly to chart axes",
            "missing_styling": "Add width and height properties for consistent display"
        }
        
        for issue in heuristic_issues:
            if issue in issue_suggestions:
                suggestions.append(f"• {issue_suggestions[issue]}")
        
        # Add general suggestions based on LLM weaknesses
        if "clarity" in " ".join(llm_weaknesses).lower():
            suggestions.append("• Improve chart clarity by adding more descriptive labels and titles")
        
        if "aesthetic" in " ".join(llm_weaknesses).lower():
            suggestions.append("• Enhance visual appeal with better styling and color choices")
        
        if not suggestions:
            suggestions.append("• The chart is well-designed! Consider adding more data points for richer insights")
        
        return " | ".join(suggestions)


def main():
    """Main entry point for the application."""
    # Example usage
    orchestrator = PromptsmithOrchestrator()
    
    # Test queries
    test_queries = [
        "Show me revenue by region over time",
        "How is my business doing?",
        "Compare sales performance across departments",
        "Display customer satisfaction trends"
    ]
    
    # Use first query as default
    user_query = test_queries[0]
    
    # Allow command line argument for custom query
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    
    print("🎯 Promptsmith Chart Optimizer")
    print("=" * 50)
    
    # Run optimization
    result = orchestrator.run_optimization(user_query, max_iterations=3)
    
    # Print summary
    orchestrator.print_summary(result)
    
    # Save results to file
    with open("optimization_result.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Results saved to optimization_result.json")


if __name__ == "__main__":
    main() 