"""
Test script for Promptsmith Chart Optimizer agents

This script demonstrates the functionality of each individual agent
and validates the complete system flow.
"""

import json
from agents.prompt_generator import PromptGeneratorAgent
from agents.chart_builder import ChartBuilderAgent
from agents.evaluator_heuristic import HeuristicEvaluatorAgent
from agents.evaluator_llm import LLMEvaluatorAgent
from agents.scorer import ScoringAgent
from agents.rewriter import PromptRewriterAgent
from agents.clarifier import ClarifierAgent


def test_prompt_generator():
    """Test the Prompt Generator Agent."""
    print("🧪 Testing Prompt Generator Agent")
    print("-" * 40)
    
    agent = PromptGeneratorAgent()
    test_state = {"user_query": "Show me revenue by region over time"}
    
    result = agent.run(test_state)
    print(f"✅ Generated prompt: {result['prompt'][:100]}...")
    return result


def test_chart_builder():
    """Test the Chart Builder Agent."""
    print("\n🧪 Testing Chart Builder Agent")
    print("-" * 40)
    
    agent = ChartBuilderAgent()
    test_state = {"prompt": "Create a line chart showing revenue trends"}
    
    result = agent.run(test_state)
    print(f"✅ Chart spec generated: {result['chart_spec']['mark']} chart")
    print(f"✅ Chart valid: {result['chart_valid']}")
    return result


def test_heuristic_evaluator():
    """Test the Heuristic Evaluator Agent."""
    print("\n🧪 Testing Heuristic Evaluator Agent")
    print("-" * 40)
    
    agent = HeuristicEvaluatorAgent()
    
    # Test with valid chart spec
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
    
    print(f"✅ Heuristic score: {result['heuristic_score']}/10")
    print(f"✅ Issues found: {result['heuristic_issues']}")
    print(f"✅ Should clarify: {result['should_clarify']}")
    return result


def test_llm_evaluator():
    """Test the LLM Evaluator Agent."""
    print("\n🧪 Testing LLM Evaluator Agent")
    print("-" * 40)
    
    agent = LLMEvaluatorAgent()
    
    test_chart_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": {"text": "Revenue by Region"},
        "data": {"values": [{"region": "North", "revenue": 100000}]},
        "mark": "line",
        "encoding": {
            "x": {"field": "region", "type": "nominal", "title": "Region"},
            "y": {"field": "revenue", "type": "quantitative", "title": "Revenue ($)"}
        }
    }
    
    test_state = {
        "chart_spec": test_chart_spec,
        "user_query": "Show me revenue by region over time"
    }
    
    result = agent.run(test_state)
    print(f"✅ LLM score: {result['llm_score']}/10")
    print(f"✅ LLM feedback: {result['llm_feedback'][:100]}...")
    return result


def test_scorer():
    """Test the Scoring Agent."""
    print("\n🧪 Testing Scoring Agent")
    print("-" * 40)
    
    agent = ScoringAgent()
    
    test_state = {
        "heuristic_score": 8.0,
        "llm_score": 7.5,
        "heuristic_issues": ["partial_styling"],
        "llm_feedback": "Chart has good clarity and appropriate chart type.",
        "iteration": 2
    }
    
    result = agent.run(test_state)
    print(f"✅ Final score: {result['final_score']}/10")
    print(f"✅ Should continue: {result['should_continue']}")
    print(f"✅ Status: {result['status']}")
    print(f"✅ Summary: {result['summary'][:100]}...")
    return result


def test_rewriter():
    """Test the Prompt Rewriter Agent."""
    print("\n🧪 Testing Prompt Rewriter Agent")
    print("-" * 40)
    
    agent = PromptRewriterAgent()
    
    test_state = {
        "prompt": "Create a chart showing revenue by region over time",
        "heuristic_issues": ["missing_title", "partial_styling"],
        "llm_feedback": "Chart has good clarity but could use better styling.",
        "heuristic_score": 6.5,
        "llm_score": 7.0
    }
    
    result = agent.run(test_state)
    print(f"✅ Rewrite reason: {result['rewrite_reason']}")
    print(f"✅ New prompt length: {len(result['prompt'])} characters")
    return result


def test_clarifier():
    """Test the Clarifier Agent."""
    print("\n🧪 Testing Clarifier Agent")
    print("-" * 40)
    
    agent = ClarifierAgent()
    
    # Test with vague query
    test_state = {"user_query": "How is my business doing?"}
    result = agent.run(test_state)
    
    print(f"✅ Clarification needed: {result['clarification_needed']}")
    if result['clarification_needed']:
        print(f"✅ Clarification type: {result['clarification_type']}")
        print(f"✅ Question: {result['clarification_question']}")
        print(f"✅ Suggested query: {result['suggested_query']}")
    
    # Test with clear query
    test_state2 = {"user_query": "Show me revenue by region over time"}
    result2 = agent.run(test_state2)
    
    print(f"✅ Clear query - clarification needed: {result2['clarification_needed']}")
    return result, result2


def test_complete_flow():
    """Test the complete agent flow."""
    print("\n🧪 Testing Complete Agent Flow")
    print("-" * 40)
    
    # Initialize agents
    prompt_gen = PromptGeneratorAgent()
    chart_builder = ChartBuilderAgent()
    heuristic_eval = HeuristicEvaluatorAgent()
    llm_eval = LLMEvaluatorAgent()
    scorer = ScoringAgent()
    
    # Step 1: Generate prompt
    state = {"user_query": "Show me revenue by region over time"}
    state = prompt_gen.run(state)
    print(f"✅ Step 1: Prompt generated ({len(state['prompt'])} chars)")
    
    # Step 2: Build chart
    state = chart_builder.run(state)
    print(f"✅ Step 2: Chart built ({state['chart_spec']['mark']} chart)")
    
    # Step 3: Heuristic evaluation
    state = heuristic_eval.run(state)
    print(f"✅ Step 3: Heuristic score {state['heuristic_score']}/10")
    
    # Step 4: LLM evaluation
    state = llm_eval.run(state)
    print(f"✅ Step 4: LLM score {state['llm_score']}/10")
    
    # Step 5: Scoring
    state = scorer.run(state)
    print(f"✅ Step 5: Final score {state['final_score']}/10")
    print(f"✅ Step 5: Status {state['status']}")
    
    return state


def main():
    """Run all tests."""
    print("🚀 Promptsmith Chart Optimizer - Agent Tests")
    print("=" * 60)
    
    try:
        # Test individual agents
        test_prompt_generator()
        test_chart_builder()
        test_heuristic_evaluator()
        test_llm_evaluator()
        test_scorer()
        test_rewriter()
        test_clarifier()
        
        # Test complete flow
        final_state = test_complete_flow()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("=" * 60)
        
        # Save test results
        with open("test_results.json", "w") as f:
            json.dump({
                "final_state": final_state,
                "test_status": "passed"
            }, f, indent=2)
        
        print("💾 Test results saved to test_results.json")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    main() 