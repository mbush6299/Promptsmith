from agents.scorer import ScoringAgent

def test_scorer_threshold():
    scorer = ScoringAgent()
    # Test: iteration 1, high score (should continue)
    should_continue, reason = scorer.should_continue(final_score=9.7, iteration=1, heuristic_issues=[])
    print(f"Iteration 1, score 9.7: should_continue={should_continue}, reason='{reason}'")
    assert should_continue, "Should continue on first iteration even if score is high"
    # Test: iteration 2, high score (should stop)
    should_continue, reason = scorer.should_continue(final_score=9.7, iteration=2, heuristic_issues=[])
    print(f"Iteration 2, score 9.7: should_continue={should_continue}, reason='{reason}'")
    assert not should_continue, "Should stop on second iteration if score is high"
    # Test: iteration 1, low score (should continue)
    should_continue, reason = scorer.should_continue(final_score=7.0, iteration=1, heuristic_issues=[])
    print(f"Iteration 1, score 7.0: should_continue={should_continue}, reason='{reason}'")
    assert should_continue, "Should continue on first iteration if score is low"
    # Test: iteration 2, low score (should continue)
    should_continue, reason = scorer.should_continue(final_score=7.0, iteration=2, heuristic_issues=[])
    print(f"Iteration 2, score 7.0: should_continue={should_continue}, reason='{reason}'")
    assert should_continue, "Should continue on second iteration if score is low"
    # Test: iteration 5, max iterations (should stop)
    should_continue, reason = scorer.should_continue(final_score=7.0, iteration=5, heuristic_issues=[])
    print(f"Iteration 5, score 7.0: should_continue={should_continue}, reason='{reason}'")
    assert not should_continue, "Should stop at max iterations"
    print("All scorer threshold tests passed.")

if __name__ == "__main__":
    test_scorer_threshold() 