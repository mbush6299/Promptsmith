#!/usr/bin/env python3
"""
Test script to verify the enhanced Promptsmith API is working
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "https://promptsmith-production.up.railway.app"
API_KEY = "test-key-123"  # Should match your environment variable

def test_enhanced_api():
    """Test the enhanced API endpoints."""
    print("🧪 Testing Enhanced Promptsmith API")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Enhanced Optimization
    print("\n2️⃣ Testing Enhanced Optimization...")
    test_query = "Create a bar chart showing sales data by region"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/optimize",
            json={
                "user_query": test_query,
                "max_iterations": 3
            },
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            data = result.get("data", {})
            
            print("✅ Enhanced optimization successful!")
            print(f"📈 Final Score: {data.get('final_score', 0):.1f}/10")
            print(f"🔄 Total Iterations: {data.get('iteration', 1)}")
            
            # Check for enhanced features
            progress = data.get("progress", {})
            if progress:
                print(f"📊 Progress: {progress.get('current_step', 'unknown')}")
                print(f"🤖 Current Agent: {progress.get('current_agent', 'none')}")
                print(f"📈 Overall Progress: {progress.get('overall_progress', 0):.1f}%")
            
            agent_outputs = data.get("agent_outputs", {})
            if agent_outputs:
                print(f"🤖 Agent Outputs: {len(agent_outputs)} agents")
                for agent, output in agent_outputs.items():
                    print(f"  • {agent}: {output.get('status', 'unknown')}")
                    if output.get('from_cache'):
                        print(f"    - Using cached pattern: {output.get('cache_hit')}")
            
            iteration_history = data.get("iteration_history", [])
            if iteration_history:
                print(f"📚 Iteration History: {len(iteration_history)} iterations")
                for i, iteration in enumerate(iteration_history, 1):
                    print(f"  Iteration {i}: Score {iteration.get('final_score', 0):.1f}/10")
            
            cache_stats = data.get("cache_stats", {})
            if cache_stats:
                print(f"🧠 Cache Stats: {cache_stats.get('total_runs', 0)} runs, {cache_stats.get('query_patterns', 0)} patterns")
            
            return True
        else:
            print(f"❌ Optimization failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Optimization error: {e}")
        return False
    
    # Test 3: Cache Statistics
    print("\n3️⃣ Testing Cache Statistics...")
    try:
        response = requests.get(
            f"{API_BASE_URL}/cache/stats",
            headers={"X-API-Key": API_KEY},
            timeout=10
        )
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Cache statistics retrieved!")
            print(f"Total Runs: {stats.get('total_runs', 0)}")
            print(f"Query Patterns: {stats.get('query_patterns', 0)}")
            print(f"Average Score: {stats.get('avg_score', 0):.2f}/10")
            return True
        else:
            print(f"❌ Cache stats failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cache stats error: {e}")
        return False

def test_streaming_api():
    """Test the streaming API endpoint."""
    print("\n4️⃣ Testing Streaming API...")
    test_query = "Show me revenue trends over time"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/optimize/stream",
            json={
                "user_query": test_query,
                "max_iterations": 2
            },
            headers={
                "X-API-Key": API_KEY,
                "Content-Type": "application/json"
            },
            stream=True,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Streaming API working!")
            print("📡 Receiving stream data...")
            
            event_count = 0
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        event_count += 1
                        try:
                            data = json.loads(line_str[6:])
                            event_type = data.get('type', 'unknown')
                            print(f"  Event {event_count}: {event_type}")
                            
                            if event_type == 'complete':
                                print("✅ Streaming completed successfully!")
                                break
                        except json.JSONDecodeError:
                            print(f"  ⚠️ Invalid JSON: {line_str[:50]}...")
            
            return True
        else:
            print(f"❌ Streaming failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Streaming error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Enhanced Promptsmith API Test Suite")
    print("=" * 60)
    
    # Test basic functionality
    if not test_enhanced_api():
        print("\n❌ Basic API tests failed!")
        return
    
    # Test streaming functionality
    if not test_streaming_api():
        print("\n❌ Streaming API tests failed!")
        return
    
    print("\n🎉 All tests passed! Your enhanced API is working correctly.")
    print("\n📋 Next steps:")
    print("1. Update your frontend to use the enhanced components")
    print("2. Test the new detailed information display")
    print("3. Verify real-time progress updates work")

if __name__ == "__main__":
    main() 