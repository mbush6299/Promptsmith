"""
Learning Cache System

This module implements a learning cache that stores patterns, issues, and solutions
from previous optimization runs to enable intelligent suggestions without LLM calls.
"""

import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib


class LearningCache:
    """Cache system that learns from previous optimization runs."""
    
    def __init__(self, cache_file: str = "learning_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        
        # Pattern categories
        self.patterns = {
            "query_patterns": {},      # User query → expected chart type
            "issue_patterns": {},      # Issues → common solutions
            "prompt_patterns": {},     # Query → effective prompts
            "chart_patterns": {},      # Query → chart specs
            "feedback_patterns": {}    # Issues → feedback patterns
        }
        
        # Load patterns from cache
        self._load_patterns()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache file: {e}")
        return {"runs": [], "patterns": {}}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache file: {e}")
    
    def _load_patterns(self):
        """Load learned patterns from cache."""
        patterns = self.cache.get("patterns", {})
        for pattern_type in self.patterns:
            self.patterns[pattern_type] = patterns.get(pattern_type, {})
    
    def _save_patterns(self):
        """Save learned patterns to cache."""
        self.cache["patterns"] = self.patterns
        self._save_cache()
    
    def add_run(self, user_query: str, prompt: str, chart_spec: Dict[str, Any], 
                heuristic_score: float, llm_score: float, heuristic_issues: List[str], 
                llm_feedback: str, final_score: float):
        """Add a completed optimization run to the cache."""
        run_data = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "prompt": prompt,
            "chart_spec": chart_spec,
            "heuristic_score": heuristic_score,
            "llm_score": llm_score,
            "heuristic_issues": heuristic_issues,
            "llm_feedback": llm_feedback,
            "final_score": final_score
        }
        
        self.cache["runs"].append(run_data)
        self._learn_from_run(run_data)
        self._save_patterns()  # Save patterns after learning
        self._save_cache()
    
    def _learn_from_run(self, run_data: Dict[str, Any]):
        """Extract patterns from a completed run."""
        user_query = run_data["user_query"]
        prompt = run_data["prompt"]
        chart_spec = run_data["chart_spec"]
        heuristic_issues = run_data["heuristic_issues"]
        llm_feedback = run_data["llm_feedback"]
        final_score = run_data["final_score"]
        
        # Learn query patterns
        query_hash = self._hash_query(user_query)
        if final_score >= 8.0:  # Only learn from successful runs
            self.patterns["query_patterns"][query_hash] = {
                "query": user_query,
                "chart_type": chart_spec.get("mark", ""),
                "effective_prompt": prompt,
                "score": final_score
            }
        
        # Learn issue patterns
        for issue in heuristic_issues:
            if issue not in self.patterns["issue_patterns"]:
                self.patterns["issue_patterns"][issue] = {
                    "count": 0,
                    "solutions": [],
                    "avg_score": 0.0
                }
            
            pattern = self.patterns["issue_patterns"][issue]
            pattern["count"] += 1
            
            # Store solution if score improved
            if final_score >= 7.0:
                solution = {
                    "prompt": prompt,
                    "chart_spec": chart_spec,
                    "score": final_score
                }
                pattern["solutions"].append(solution)
                # Prune to keep at most 20 highest scoring solutions
                pattern["solutions"] = sorted(pattern["solutions"], key=lambda x: x["score"], reverse=True)[:20]
        
        # Learn prompt patterns
        if final_score >= 8.0:
            self.patterns["prompt_patterns"][query_hash] = prompt
        
        # Learn chart patterns
        if final_score >= 8.0:
            self.patterns["chart_patterns"][query_hash] = chart_spec
    
    def _hash_query(self, query: str) -> str:
        """Create a hash for a user query."""
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    def suggest_prompt(self, user_query: str) -> Optional[str]:
        """Suggest a prompt based on learned patterns. Only use cache for exact matches."""
        query_hash = self._hash_query(user_query)
        if query_hash in self.patterns["prompt_patterns"]:
            return self.patterns["prompt_patterns"][query_hash]
        return None
    
    def suggest_chart_spec(self, user_query: str) -> Optional[Dict[str, Any]]:
        """Suggest a chart spec based on learned patterns. Only use cache for exact matches."""
        query_hash = self._hash_query(user_query)
        if query_hash in self.patterns["chart_patterns"]:
            return self.patterns["chart_patterns"][query_hash]
        return None
    
    def suggest_improvements(self, heuristic_issues: List[str], final_score: float = 0.0) -> List[str]:
        """Suggest improvements based on learned issue patterns. Only use cache if score is low (<8.0)."""
        if final_score >= 8.0:
            return []
        suggestions = []
        for issue in heuristic_issues:
            if not isinstance(issue, str):
                continue  # Skip non-string issues
            if issue in self.patterns["issue_patterns"]:
                pattern = self.patterns["issue_patterns"][issue]
                if pattern["solutions"]:
                    best_solution = max(pattern["solutions"], key=lambda x: x["score"])
                    suggestions.append(f"Based on previous runs, {issue} was resolved with: {best_solution['prompt'][:100]}...")
        return suggestions
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_runs": len(self.cache["runs"]),
            "query_patterns": len(self.patterns["query_patterns"]),
            "issue_patterns": len(self.patterns["issue_patterns"]),
            "prompt_patterns": len(self.patterns["prompt_patterns"]),
            "chart_patterns": len(self.patterns["chart_patterns"]),
            "avg_score": sum(run["final_score"] for run in self.cache["runs"]) / len(self.cache["runs"]) if self.cache["runs"] else 0
        }
    
    def clear_cache(self):
        """Clear all cached data and patterns."""
        self.cache = {"runs": [], "patterns": {}}
        for pattern_type in self.patterns:
            self.patterns[pattern_type] = {}
        self._save_cache()
        print("🧠 Learning cache cleared successfully")
    
    def reset_patterns(self):
        """Reset only the patterns while keeping run history."""
        for pattern_type in self.patterns:
            self.patterns[pattern_type] = {}
        self.cache["patterns"] = {}
        self._save_cache()
        print("🔄 Patterns reset successfully")


# Global cache instance
learning_cache = LearningCache() 