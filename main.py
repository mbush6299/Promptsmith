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
            "iteration": 1,
            "agent_outputs": {},
            "iteration_history": []
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
                
                # Step 1: Generate prompt
                print("📝 Generating prompt...")
                state = self.prompt_generator.run(state)
                
                # Step 2: Build chart
                print("📊 Building chart...")
                state = self.chart_builder.run(state)
                
                # Step 3: Heuristic evaluation
                print("🔍 Running heuristic evaluation...")
                state = self.heuristic_evaluator.run(state)
                
                # Check if clarification is needed
                if state.get("should_clarify", False):
                    print("❓ Clarification needed, triggering clarifier...")
                    state = self.clarifier.run(state)
                    
                    if state.get("clarification_needed", False):
                        print(f"💡 Clarification Question: {state.get('clarification_question')}")
                        print(f"💡 Suggested Query: {state.get('suggested_query')}")
                        return {
                            "status": "clarification_needed",
                            "clarification_question": state.get("clarification_question"),
                            "suggested_query": state.get("suggested_query"),
                            "iteration": iteration
                        }
                
                # Step 4: LLM evaluation (only if heuristic passes)
                if state.get("chart_valid", True):
                    print("🤖 Running LLM evaluation...")
                    state = self.llm_evaluator.run(state)
                    
                    # Step 5: Scoring
                    print("📊 Calculating final score...")
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
                    
                    # Step 6: Rewrite prompt for next iteration
                    if iteration < max_iterations:
                        print("✏️ Rewriting prompt for next iteration...")
                        state = self.rewriter.run(state)
                        print(f"💡 Rewrite reason: {state.get('rewrite_reason')}")
                
                # Store iteration results
                iteration_result = {
                    "iteration": iteration,
                    "prompt": state.get("prompt", ""),
                    "chart_spec": state.get("chart_spec", {}),
                    "heuristic_score": state.get("heuristic_score", 0.0),
                    "llm_score": state.get("llm_score", 0.0),
                    "final_score": state.get("final_score", 0.0),
                    "status": state.get("status", "unknown")
                }
                
                self.iteration_history.append(iteration_result)
                state["iteration_history"] = self.iteration_history
                
                print(f"📈 Iteration {iteration} complete - Score: {final_score}/10")
            
            # Return best result or final result
            result_state = best_result if best_result else state
            
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
            
            return self._format_final_output(result_state)
            
        except Exception as e:
            print(f"❌ Error during optimization: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "iteration": state.get("iteration", 1)
            }
    
    def _format_final_output(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the final output according to the specified format.
        
        Args:
            state (Dict[str, Any]): Final state
            
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
            "iteration_history": state.get("iteration_history", [])
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