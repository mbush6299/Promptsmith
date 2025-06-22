# Deploy Enhanced Promptsmith API to Railway

## Prerequisites
- Railway account (you already have this)
- Your existing Railway project: `promptsmith-production`

## Step 1: Login to Railway CLI
```bash
railway login
```

## Step 2: Link to Existing Project
```bash
railway link
# Select your existing project: promptsmith-production
```

## Step 3: Deploy Enhanced API
```bash
railway up
```

## Step 4: Verify Environment Variables
Make sure these are set in your Railway dashboard:
- `OPENAI_API_KEY` - Your OpenAI API key
- `PROMPTSMITH_API_KEY` - Your API key (e.g., "test-key-123")

## Step 5: Test the Enhanced API
Your enhanced API will be available at: `https://promptsmith-production.up.railway.app`

### Test Endpoints:
1. **Health Check**: `GET /`
2. **Enhanced Optimization**: `POST /optimize`
3. **Streaming Optimization**: `POST /optimize/stream`
4. **Cache Statistics**: `GET /cache/stats`

## What's New in the Enhanced API:

### 1. Detailed Progress Tracking
- Real-time step-by-step progress
- Agent status updates
- Overall progress percentage

### 2. Comprehensive Agent Outputs
- Prompt Generator: Cache usage, generation method
- Chart Builder: Chart type, validation status
- Heuristic Evaluator: Detailed scores, issues found
- LLM Evaluator: Strengths, weaknesses, feedback
- Scorer: Final scores, continuation logic
- Rewriter: Improvement details

### 3. Iteration History
- Complete optimization journey
- Score progression across iterations
- Agent outputs for each step

### 4. Streaming Endpoint
- Real-time progress updates
- Server-Sent Events for live updates

### 5. Enhanced Error Handling
- Detailed error messages
- Fallback information
- Cache miss details

## API Response Format (Enhanced)

```json
{
  "success": true,
  "data": {
    "iteration": 3,
    "prompt": "Enhanced prompt text",
    "chart_spec": {...},
    "scores": {
      "heuristic": 8.5,
      "llm": 7.2
    },
    "final_score": 7.8,
    "progress": {
      "current_step": "complete",
      "current_agent": null,
      "overall_progress": 100
    },
    "agent_outputs": {
      "prompt_generator": {...},
      "chart_builder": {...},
      "heuristic_evaluator": {...},
      "llm_evaluator": {...},
      "scorer": {...},
      "rewriter": {...}
    },
    "iteration_history": [...],
    "cache_stats": {...},
    "user_query": "Create a bar chart showing sales data",
    "max_iterations": 3
  },
  "message": "Chart optimization completed successfully"
}
```

## Next Steps After Deployment:
1. Update your frontend to use the enhanced API
2. Test the streaming endpoint for real-time updates
3. Show detailed progress and quality metrics
4. Display agent status and cache insights

The enhanced API is ready to provide a much richer user experience! 