#!/usr/bin/env python3
"""
Test script for the enhanced Promptsmith API
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "test-key-123"  # Should match your environment variable

def test_enhanced_optimization():
    """Test the enhanced optimization endpoint with detailed progress information."""
    print("🧪 Testing Enhanced Chart Optimization API")
    print("=" * 50)
    
    # Test data
    test_queries = [
        "Create a bar chart showing sales data by region",
        "Show me revenue trends over time",
        "Compare performance across departments"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📊 Test {i}: {query}")
        print("-" * 40)
        
        # Make request
        response = requests.post(
            f"{API_BASE_URL}/optimize",
            json={
                "user_query": query,
                "max_iterations": 3
            },
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            data = result.get("data", {})
            
            print(f"✅ Success! Status: {result.get('message')}")
            print(f"📈 Final Score: {data.get('final_score', 0):.1f}/10")
            print(f"🔄 Total Iterations: {data.get('iteration', 1)}")
            
            # Show detailed progress information
            progress = data.get("progress", {})
            print(f"📊 Progress: {progress.get('current_step', 'unknown')}")
            print(f"🤖 Current Agent: {progress.get('current_agent', 'none')}")
            print(f"📈 Overall Progress: {progress.get('overall_progress', 0):.1f}%")
            
            # Show agent outputs
            agent_outputs = data.get("agent_outputs", {})
            if agent_outputs:
                print("\n🤖 Agent Outputs:")
                for agent, output in agent_outputs.items():
                    print(f"  • {agent}: {output.get('status', 'unknown')}")
                    if agent == "prompt_generator":
                        print(f"    - From Cache: {output.get('from_cache', False)}")
                        print(f"    - Method: {output.get('generation_method', 'unknown')}")
                    elif agent == "chart_builder":
                        print(f"    - Chart Type: {output.get('chart_type', 'unknown')}")
                        print(f"    - From Cache: {output.get('from_cache', False)}")
                    elif agent == "heuristic_evaluator":
                        print(f"    - Score: {output.get('score', 0):.1f}/10")
                        print(f"    - Issues: {len(output.get('issues', []))}")
                    elif agent == "llm_evaluator":
                        print(f"    - Score: {output.get('score', 0):.1f}/10")
                        print(f"    - Strengths: {len(output.get('strengths', []))}")
                        print(f"    - Weaknesses: {len(output.get('weaknesses', []))}")
            
            # Show iteration history
            iteration_history = data.get("iteration_history", [])
            if iteration_history:
                print(f"\n📚 Iteration History ({len(iteration_history)} iterations):")
                for i, iteration in enumerate(iteration_history, 1):
                    print(f"  Iteration {i}:")
                    print(f"    - Final Score: {iteration.get('final_score', 0):.1f}/10")
                    print(f"    - Heuristic: {iteration.get('heuristic_score', 0):.1f}/10")
                    print(f"    - LLM: {iteration.get('llm_score', 0):.1f}/10")
                    print(f"    - Status: {iteration.get('status', 'unknown')}")
            
            # Show cache stats
            cache_stats = data.get("cache_stats", {})
            if cache_stats:
                print(f"\n🧠 Cache Statistics:")
                print(f"  - Total Runs: {cache_stats.get('total_runs', 0)}")
                print(f"  - Query Patterns: {cache_stats.get('query_patterns', 0)}")
                print(f"  - Average Score: {cache_stats.get('avg_score', 0):.2f}/10")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
        
        print("\n" + "=" * 50)

def test_streaming_optimization():
    """Test the streaming optimization endpoint."""
    print("\n🌊 Testing Streaming Chart Optimization API")
    print("=" * 50)
    
    query = "Create a line chart showing revenue by month"
    print(f"📊 Query: {query}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/optimize/stream",
            json={
                "user_query": query,
                "max_iterations": 3
            },
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            stream=True,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Streaming started successfully!")
            print("📡 Receiving real-time updates...")
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        try:
                            data = json.loads(data_str)
                            event_type = data.get('type', 'unknown')
                            
                            if event_type == 'start':
                                print(f"🚀 {data.get('message', '')}")
                            elif event_type == 'iteration_progress':
                                iteration = data.get('iteration', 0)
                                progress = data.get('progress', {})
                                scores = data.get('scores', {})
                                print(f"🔄 Iteration {iteration}: {progress.get('step', 'unknown')} - Final Score: {scores.get('final', 0):.1f}/10")
                            elif event_type == 'complete':
                                print(f"✅ {data.get('message', '')}")
                                result = data.get('result', {})
                                print(f"📈 Final Score: {result.get('final_score', 0):.1f}/10")
                                break
                            elif event_type == 'error':
                                print(f"❌ Error: {data.get('error', 'Unknown error')}")
                                break
                        except json.JSONDecodeError:
                            print(f"⚠️  Invalid JSON: {data_str}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception during streaming: {str(e)}")

def test_cache_stats():
    """Test the cache statistics endpoint."""
    print("\n📊 Testing Cache Statistics API")
    print("=" * 50)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/cache/stats",
            headers={"X-API-Key": API_KEY}
        )
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Cache Statistics:")
            print(f"  - Total Runs: {stats.get('total_runs', 0)}")
            print(f"  - Query Patterns: {stats.get('query_patterns', 0)}")
            print(f"  - Issue Patterns: {stats.get('issue_patterns', 0)}")
            print(f"  - Prompt Patterns: {stats.get('prompt_patterns', 0)}")
            print(f"  - Chart Patterns: {stats.get('chart_patterns', 0)}")
            print(f"  - Average Score: {stats.get('avg_score', 0):.2f}/10")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def main():
    """Run all tests."""
    print("🚀 Promptsmith Enhanced API Test Suite")
    print("=" * 60)
    
    # Test basic functionality
    test_enhanced_optimization()
    
    # Test streaming functionality
    test_streaming_optimization()
    
    # Test cache statistics
    test_cache_stats()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main() 