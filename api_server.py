"""
FastAPI Server for Promptsmith Chart Optimizer

This creates a REST API wrapper around the Promptsmith orchestrator
for integration with web applications.
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import sys
import json
import asyncio

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import PromptsmithOrchestrator
from learning_cache import learning_cache

app = FastAPI(
    title="Promptsmith Chart Optimizer API",
    description="API for generating and optimizing Vega-Lite chart specifications",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://maxbush.us",  # Your production domain
        "https://www.maxbush.us",  # With www
        "https://promptsmith-production.up.railway.app",  # Railway production URL
        "https://*.vercel.app",  # All Vercel preview deployments
        "http://localhost:3000",  # Local development
        "http://localhost:3001",  # Alternative local port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the orchestrator
orchestrator = PromptsmithOrchestrator()

# API Key validation
async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key from header"""
    expected_key = os.getenv("PROMPTSMITH_API_KEY")
    if not expected_key:
        # If no API key is set, allow all requests (for development)
        return True
    
    if not x_api_key or x_api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return True

class ChartRequest(BaseModel):
    user_query: str
    max_iterations: Optional[int] = 3

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    chart_spec: Optional[Dict[str, Any]] = None
    response_type: str = "text"
    final_score: Optional[float] = None
    from_cache: bool = False

class CacheStatsResponse(BaseModel):
    total_runs: int
    query_patterns: int
    issue_patterns: int
    prompt_patterns: int
    chart_patterns: int
    avg_score: float

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Promptsmith Chart Optimizer API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/optimize")
async def optimize_chart(
    request: ChartRequest,
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Generate and optimize a chart specification from a natural language query.
    
    Args:
        request: ChartRequest containing the user query and optional max_iterations
        
    Returns:
        Dict containing the optimization results including chart_spec, scores, etc.
    """
    try:
        result = orchestrator.run_optimization(
            user_query=request.user_query,
            max_iterations=request.max_iterations
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Chart optimization completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during chart optimization: {str(e)}"
        )

@app.post("/optimize/stream")
async def optimize_chart_stream(
    request: ChartRequest,
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Stream chart optimization progress in real-time.
    
    Args:
        request: ChartRequest containing the user query and optional max_iterations
        
    Returns:
        StreamingResponse with real-time progress updates
    """
    async def generate_stream():
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'start', 'message': 'Starting chart optimization...'})}\n\n"
            
            # Run optimization with progress tracking
            result = orchestrator.run_optimization(
                user_query=request.user_query,
                max_iterations=request.max_iterations
            )
            
            # Send progress updates for each iteration
            iteration_history = result.get("iteration_history", [])
            for iteration in iteration_history:
                progress_data = {
                    "type": "iteration_progress",
                    "iteration": iteration["iteration"],
                    "progress": iteration["progress"],
                    "agent_outputs": iteration["agent_outputs"],
                    "scores": {
                        "heuristic": iteration["heuristic_score"],
                        "llm": iteration["llm_score"],
                        "final": iteration["final_score"]
                    }
                }
                yield f"data: {json.dumps(progress_data)}\n\n"
                await asyncio.sleep(0.1)  # Small delay for streaming effect
            
            # Send final result
            final_data = {
                "type": "complete",
                "result": result,
                "message": "Chart optimization completed successfully"
            }
            yield f"data: {json.dumps(final_data)}\n\n"
            
        except Exception as e:
            error_data = {
                "type": "error",
                "error": str(e),
                "message": "Error during chart optimization"
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@app.get("/chat/greeting")
async def get_greeting():
    """Get the initial greeting message for the chat"""
    return {
        "success": True,
        "greeting": "Hi! I'm Max's AI assistant. I can help you navigate his website, answer questions about his projects, or provide information about his skills and experience. I can also generate charts and visualizations! What would you like to know?"
    }

@app.post("/chat")
async def chat_message(request: ChatRequest):
    """
    Handle chat messages and detect chart requests.
    
    Args:
        request: ChatRequest containing the message and optional session_id
        
    Returns:
        ChatResponse with the AI response and optional chart specification
    """
    try:
        message = request.message.lower()
        
        # Check if this is a chart request
        chart_keywords = [
            'chart', 'graph', 'visualization', 'plot', 'bar chart', 'line chart', 
            'pie chart', 'scatter plot', 'histogram', 'create', 'generate', 'show me',
            'display', 'visualize', 'data', 'sales', 'revenue', 'profit', 'metrics'
        ]
        
        is_chart_request = any(keyword in message for keyword in chart_keywords)
        
        if is_chart_request:
            # Route to Promptsmith for chart generation
            result = orchestrator.run_optimization(
                user_query=request.message,
                max_iterations=3
            )
            
            # Format the response
            response_text = f"I've created a chart for you! Here's a {result.get('chart_type', 'visualization')} showing your data. "
            response_text += f"The chart has a quality score of {result.get('final_score', 8.0):.1f}/10. "
            response_text += "You can interact with the chart below."
            
            return {
                "success": True,
                "response": response_text,
                "chart_spec": result.get('final_chart_spec') or result.get('chart_spec'),
                "response_type": "chart",
                "final_score": result.get('final_score'),
                "from_cache": result.get('from_cache', False)
            }
        else:
            # Handle regular chat messages
            # For now, provide a simple response
            response_text = "I'm here to help! I can answer questions about Max's projects, skills, and experience. I can also generate charts and visualizations if you ask for them. What would you like to know?"
            
            return {
                "success": True,
                "response": response_text,
                "response_type": "text",
                "from_cache": False
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

@app.get("/cache/stats")
async def get_cache_stats(api_key_valid: bool = Depends(verify_api_key)):
    """Get learning cache statistics"""
    try:
        stats = learning_cache.get_stats()
        return CacheStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving cache stats: {str(e)}"
        )

@app.delete("/cache")
async def clear_cache(api_key_valid: bool = Depends(verify_api_key)):
    """Clear the learning cache"""
    try:
        learning_cache.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        )

@app.get("/cache/suggest/{query}")
async def get_cache_suggestions(
    query: str,
    api_key_valid: bool = Depends(verify_api_key)
):
    """Get cached suggestions for a query"""
    try:
        suggestions = {
            "prompt": learning_cache.suggest_prompt(query),
            "chart_spec": learning_cache.suggest_chart_spec(query)
        }
        return suggestions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving cache suggestions: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 