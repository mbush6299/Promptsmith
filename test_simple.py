#!/usr/bin/env python3
"""
Simple test for the enhanced Promptsmith API
"""

import requests
import json

def test_simple_optimization():
    """Test a simple chart optimization."""
    print("🧪 Testing Simple Chart Optimization")
    print("=" * 40)
    
    # Test data
    test_data = {
        "user_query": "Create a bar chart showing sales data by region",
        "max_iterations": 2
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/optimize",
            json=test_data,
            headers={
                "X-API-Key": "test-key-123",
                "Content-Type": "application/json"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            data = result.get("data", {})
            
            print("✅ Success!")
            print(f"📈 Final Score: {data.get('final_score', 0):.1f}/10")
            print(f"🔄 Total Iterations: {data.get('iteration', 1)}")
            
            # Show progress information
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
            
            # Show iteration history
            iteration_history = data.get("iteration_history", [])
            if iteration_history:
                print(f"\n📚 Iteration History ({len(iteration_history)} iterations):")
                for i, iteration in enumerate(iteration_history, 1):
                    print(f"  Iteration {i}: Score {iteration.get('final_score', 0):.1f}/10")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_simple_optimization()
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed!") 