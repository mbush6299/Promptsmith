# Enhanced Promptsmith API Summary

## Overview
The Promptsmith API has been significantly enhanced to provide much more detailed information about the chart optimization process, enabling better frontend tracking and user experience.

## Key Enhancements

### 1. Detailed Progress Tracking
The API now provides comprehensive progress information during chart optimization:

```json
{
  "progress": {
    "current_step": "generating_prompt|building_chart|heuristic_evaluation|llm_evaluation|scoring|rewriting_prompt|complete",
    "current_agent": "prompt_generator|chart_builder|heuristic_evaluator|llm_evaluator|scorer|rewriter|clarifier",
    "overall_progress": 0-100,
    "step_details": {}
  }
}
```

### 2. Agent Output Details
Each agent now provides detailed information about their execution:

#### Prompt Generator
```json
{
  "prompt_generator": {
    "prompt": "Generated prompt text",
    "from_cache": true/false,
    "cache_hit": "prompt_pattern|null",
    "generation_method": "cache|llm|template",
    "status": "completed",
    "llm_fallback": true/false,
    "llm_error": "error message if applicable"
  }
}
```

#### Chart Builder
```json
{
  "chart_builder": {
    "chart_spec": {...},
    "chart_type": "bar|line|scatter|area|etc",
    "from_cache": true/false,
    "cache_hit": "chart_pattern|null",
    "generation_method": "cache|llm|template",
    "is_valid": true/false,
    "status": "completed",
    "llm_fallback": true/false,
    "llm_error": "error message if applicable"
  }
}
```

#### Heuristic Evaluator
```json
{
  "heuristic_evaluator": {
    "score": 0.0-10.0,
    "issues": ["missing_title", "missing_axis_labels", ...],
    "should_clarify": true/false,
    "status": "completed",
    "criterion_scores": {
      "has_title": 0.0-1.0,
      "has_axis_labels": 0.0-1.0,
      "appropriate_chart_type": 0.0-1.0,
      "has_data": 0.0-1.0,
      "proper_encoding": 0.0-1.0,
      "good_styling": 0.0-1.0,
      "responsive_design": 0.0-1.0
    },
    "criterion_details": {
      "has_title": {
        "score": 0.0-1.0,
        "issues": [],
        "weight": 0.1,
        "required": true,
        "weighted_score": 0.0-0.1
      }
    },
    "chart_valid": true/false,
    "raw_score": 0.0-1.0,
    "max_possible_score": 1.0
  }
}
```

#### LLM Evaluator
```json
{
  "llm_evaluator": {
    "score": 0.0-10.0,
    "feedback": "Detailed feedback text",
    "strengths": ["Appropriate chart type", "Clear design", ...],
    "weaknesses": ["Could improve clarity", "Limited insight potential", ...],
    "criterion_scores": {
      "intent_appropriateness": 0.0-1.0,
      "clarity": 0.0-1.0,
      "insight_potential": 0.0-1.0,
      "aesthetics": 0.0-1.0,
      "data_accuracy": 0.0-1.0
    },
    "status": "completed",
    "evaluation_method": "llm|simulated"
  }
}
```

#### Scorer
```json
{
  "scorer": {
    "final_score": 0.0-10.0,
    "score_breakdown": {...},
    "should_continue": true/false,
    "continue_reason": "reason for continuing or stopping",
    "status": "completed"
  }
}
```

#### Rewriter
```json
{
  "rewriter": {
    "new_prompt": "Improved prompt text",
    "rewrite_reason": "Reason for the rewrite",
    "improvements_made": ["Added axis labels", "Improved clarity", ...],
    "from_cache": true/false,
    "status": "completed"
  }
}
```

### 3. Iteration History
Complete history of all iterations with detailed information:

```json
{
  "iteration_history": [
    {
      "iteration": 1,
      "prompt": "Generated prompt",
      "chart_spec": {...},
      "heuristic_score": 8.5,
      "llm_score": 7.2,
      "final_score": 7.8,
      "status": "completed",
      "agent_outputs": {...},
      "progress": {
        "step": "complete",
        "agent": null,
        "overall_progress": 33.33
      }
    }
  ]
}
```

### 4. Cache Statistics
Information about the learning cache:

```json
{
  "cache_stats": {
    "total_runs": 15,
    "query_patterns": 2,
    "issue_patterns": 3,
    "prompt_patterns": 2,
    "chart_patterns": 2,
    "avg_score": 7.56
  }
}
```

### 5. Streaming Endpoint
New `/optimize/stream` endpoint for real-time progress updates:

```javascript
// Frontend usage example
const eventSource = new EventSource('/optimize/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key'
  },
  body: JSON.stringify({
    user_query: "Create a bar chart showing sales data",
    max_iterations: 3
  })
});

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'start':
      console.log('Starting optimization...');
      break;
    case 'iteration_progress':
      console.log(`Iteration ${data.iteration}: ${data.progress.step}`);
      updateProgressUI(data);
      break;
    case 'complete':
      console.log('Optimization complete!');
      displayFinalResult(data.result);
      break;
    case 'error':
      console.error('Error:', data.error);
      break;
  }
};
```

## Frontend Integration Benefits

### 1. Real-time Progress Updates
- Show which agent is currently working
- Display current step in the optimization process
- Update progress bars and status indicators

### 2. Detailed Quality Metrics
- Show individual scores for heuristic and LLM evaluation
- Display specific issues found and strengths identified
- Provide actionable feedback for improvements

### 3. Learning Cache Insights
- Show when cached patterns are being used
- Display cache hit rates and effectiveness
- Demonstrate the system's learning capabilities

### 4. Iteration Transparency
- Show the complete optimization journey
- Display how each iteration improves the result
- Explain why certain decisions were made

### 5. Agent-specific Information
- Show which generation method was used (cache/LLM/template)
- Display fallback information when LLM fails
- Provide detailed feedback from each evaluation step

## API Endpoints

### 1. Standard Optimization
```
POST /optimize
```
Returns complete results with all detailed information.

### 2. Streaming Optimization
```
POST /optimize/stream
```
Returns real-time progress updates via Server-Sent Events.

### 3. Cache Statistics
```
GET /cache/stats
```
Returns learning cache statistics.

### 4. Chat Integration
```
POST /chat
GET /chat/greeting
```
Enhanced chat endpoints with chart detection and generation.

## Error Handling

The API now provides detailed error information:
- Agent-specific errors with context
- LLM fallback information
- Cache miss details
- Validation error explanations

## Performance Improvements

- Detailed progress tracking without significant overhead
- Cached pattern usage reduces API calls
- Streaming endpoint for real-time updates
- Comprehensive error handling and fallbacks

## Next Steps for Frontend

1. **Update Progress Indicators**: Use the detailed progress information to show real-time updates
2. **Quality Score Display**: Show detailed breakdowns of heuristic and LLM scores
3. **Agent Status**: Display which agent is currently working and their status
4. **Iteration History**: Show the complete optimization journey
5. **Cache Insights**: Display when cached patterns are being used
6. **Error Handling**: Provide better error messages and fallback options
7. **Streaming Integration**: Use the streaming endpoint for real-time updates

This enhanced API provides all the information needed to create a rich, informative user experience that shows the full power of the Promptsmith system. 