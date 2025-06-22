"""
Test script to demonstrate the learning cache functionality.

This script runs multiple optimization cycles to show how the system learns
from previous runs and can make intelligent suggestions without LLM calls.
"""

import json
from main import PromptsmithOrchestrator
from learning_cache import learning_cache


def test_learning_cache():
    """Test the learning cache with multiple similar queries."""
    
    print("🧠 Testing Learning Cache Functionality")
    print("=" * 60)
    
    # Clear cache to start fresh
    learning_cache.clear_cache()
    print("🗑️ Cleared learning cache")
    
    orchestrator = PromptsmithOrchestrator()
    
    # Test queries - similar patterns to learn from
    test_queries = [
        "Show me revenue by region over time",
        "Display revenue by region over time", 
        "Create a chart for revenue by region over time",
        "Revenue by region over time visualization",
        "Show me sales by department over time",  # Similar but different
        "Display profit by region over time"      # Similar but different
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔄 Run {i}/6: {query}")
        print("-" * 40)
        
        # Run optimization
        result = orchestrator.run_optimization(query, max_iterations=2)
        results.append(result)
        
        # Show cache stats after each run
        cache_stats = learning_cache.get_stats()
        print(f"📊 Cache Stats: {cache_stats['total_runs']} runs, {cache_stats['query_patterns']} patterns")
        
        if result.get("final_score", 0) > 0:
            print(f"✅ Run completed with score: {result.get('final_score', 0):.1f}/10")
        else:
            print(f"❌ Run failed or incomplete")
    
    # Test cache suggestions
    print(f"\n🎯 Testing Cache Suggestions")
    print("=" * 40)
    
    # Test with a new but similar query
    new_query = "Revenue by region over time chart"
    print(f"🔍 Testing with new query: {new_query}")
    
    # Check for cached suggestions
    cached_prompt = learning_cache.suggest_prompt(new_query)
    cached_chart_spec = learning_cache.suggest_chart_spec(new_query)
    
    if cached_prompt:
        print(f"✅ Found cached prompt pattern!")
        print(f"📝 Cached prompt: {cached_prompt[:100]}...")
    else:
        print(f"❌ No cached prompt pattern found")
    
    if cached_chart_spec:
        print(f"✅ Found cached chart spec pattern!")
        print(f"📊 Chart type: {cached_chart_spec.get('mark', 'unknown')}")
    else:
        print(f"❌ No cached chart spec pattern found")
    
    # Test issue pattern suggestions
    test_issues = ["Missing axis labels", "No title specified"]
    suggestions = learning_cache.suggest_improvements(test_issues)
    
    if suggestions:
        print(f"✅ Found {len(suggestions)} improvement suggestions:")
        for suggestion in suggestions:
            print(f"   💡 {suggestion}")
    else:
        print(f"❌ No improvement suggestions found")
    
    # Final cache statistics
    print(f"\n📈 Final Learning Cache Statistics")
    print("=" * 40)
    final_stats = learning_cache.get_stats()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")
    
    # Save detailed results
    with open("learning_cache_test_results.json", "w") as f:
        json.dump({
            "results": results,
            "cache_stats": final_stats,
            "test_queries": test_queries
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to learning_cache_test_results.json")
    
    return results


def demonstrate_cache_efficiency():
    """Demonstrate how the cache improves efficiency."""
    
    print(f"\n⚡ Cache Efficiency Demonstration")
    print("=" * 50)
    
    orchestrator = PromptsmithOrchestrator()
    
    # Run the same query twice to show cache usage
    query = "Show me revenue by region over time"
    
    print(f"🔄 First run (with LLM calls):")
    result1 = orchestrator.run_optimization(query, max_iterations=1)
    
    print(f"\n🔄 Second run (should use cache):")
    result2 = orchestrator.run_optimization(query, max_iterations=1)
    
    # Compare results
    print(f"\n📊 Comparison:")
    print(f"   First run score: {result1.get('final_score', 0):.1f}/10")
    print(f"   Second run score: {result2.get('final_score', 0):.1f}/10")
    
    # Check if cache was used
    cache_stats = learning_cache.get_stats()
    print(f"   Cache patterns: {cache_stats['query_patterns']}")
    
    return result1, result2


if __name__ == "__main__":
    # Run the main test
    test_learning_cache()
    
    # Demonstrate efficiency
    demonstrate_cache_efficiency()
    
    print(f"\n🎉 Learning cache test completed!")
    print(f"Check learning_cache.json for the persistent cache data.") 