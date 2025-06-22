# Frontend Integration Guide for Enhanced Promptsmith API

## Overview
This guide will help you integrate the enhanced Promptsmith API into your React website, providing users with detailed progress tracking, quality metrics, and real-time updates.

## Step 1: Deploy Enhanced API to Railway

### Option A: Using Railway CLI
```bash
# Login to Railway
railway login

# Link to your existing project
railway link
# Select: promptsmith-production

# Deploy the enhanced API
railway up
```

### Option B: Manual Deployment
1. Push your enhanced code to GitHub
2. Railway will automatically deploy from your connected repository
3. Verify environment variables in Railway dashboard:
   - `OPENAI_API_KEY`
   - `PROMPTSMITH_API_KEY`

## Step 2: Install Required Dependencies

Add these to your React project's `package.json`:

```json
{
  "dependencies": {
    "vega-embed": "^6.21.0",
    "vega": "^5.24.0",
    "vega-lite": "^5.6.0"
  }
}
```

Install with:
```bash
npm install vega-embed vega vega-lite
```

## Step 3: Environment Variables

Add these to your `.env` file:

```env
REACT_APP_PROMPTSMITH_API_URL=https://promptsmith-production.up.railway.app
REACT_APP_PROMPTSMITH_API_KEY=your-api-key-here
```

## Step 4: Choose Your Integration Approach

### Option A: Enhanced Component (Recommended)
Use the `EnhancedPromptsmithComponent.tsx` for detailed analysis and complete information.

### Option B: Streaming Component
Use the `StreamingPromptsmithComponent.tsx` for real-time progress updates.

### Option C: Hybrid Approach
Combine both components with a toggle for users to choose their preferred experience.

## Step 5: Integration Examples

### Basic Integration
```tsx
import React from 'react';
import EnhancedPromptsmithComponent from './components/EnhancedPromptsmithComponent';

function App() {
  return (
    <div className="App">
      <EnhancedPromptsmithComponent />
    </div>
  );
}
```

### With Navigation
```tsx
import React, { useState } from 'react';
import EnhancedPromptsmithComponent from './components/EnhancedPromptsmithComponent';
import StreamingPromptsmithComponent from './components/StreamingPromptsmithComponent';

function App() {
  const [mode, setMode] = useState<'enhanced' | 'streaming'>('enhanced');

  return (
    <div className="App">
      <nav className="bg-gray-800 text-white p-4">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold">Promptsmith Demo</h1>
          <div className="flex space-x-4">
            <button
              onClick={() => setMode('enhanced')}
              className={`px-4 py-2 rounded ${mode === 'enhanced' ? 'bg-blue-600' : 'bg-gray-600'}`}
            >
              Enhanced Mode
            </button>
            <button
              onClick={() => setMode('streaming')}
              className={`px-4 py-2 rounded ${mode === 'streaming' ? 'bg-blue-600' : 'bg-gray-600'}`}
            >
              Streaming Mode
            </button>
          </div>
        </div>
      </nav>

      <main>
        {mode === 'enhanced' ? (
          <EnhancedPromptsmithComponent />
        ) : (
          <StreamingPromptsmithComponent />
        )}
      </main>
    </div>
  );
}
```

## Step 6: API Response Structure

The enhanced API returns detailed information:

```typescript
interface EnhancedResponse {
  success: boolean;
  data: {
    iteration: number;
    prompt: string;
    chart_spec: any;
    scores: {
      heuristic: number;
      llm: number;
    };
    final_score: number;
    progress: {
      current_step: string;
      current_agent: string | null;
      overall_progress: number;
    };
    agent_outputs: {
      prompt_generator: AgentOutput;
      chart_builder: AgentOutput;
      heuristic_evaluator: AgentOutput;
      llm_evaluator: AgentOutput;
      scorer: AgentOutput;
      rewriter: AgentOutput;
    };
    iteration_history: IterationHistory[];
    cache_stats: CacheStats;
    user_query: string;
    max_iterations: number;
  };
  message: string;
}
```

## Step 7: Key Features to Highlight

### 1. Real-time Progress Tracking
- Show which agent is currently working
- Display current step in the optimization process
- Update progress bars and status indicators

### 2. Quality Metrics
- Individual scores for heuristic and LLM evaluation
- Specific issues found and strengths identified
- Actionable feedback for improvements

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

## Step 8: Styling and Theming

The components use Tailwind CSS classes. If you're not using Tailwind, you can:

### Option A: Install Tailwind CSS
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Option B: Convert to CSS Modules
Create corresponding CSS files and replace Tailwind classes with custom CSS.

### Option C: Use Inline Styles
Replace Tailwind classes with inline styles or your preferred styling solution.

## Step 9: Error Handling

The components include comprehensive error handling:

```tsx
// Example error handling
{error && (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
    <p className="text-red-800">❌ Error: {error}</p>
  </div>
)}
```

## Step 10: Testing

### Test the API Endpoints
```bash
# Test health check
curl https://promptsmith-production.up.railway.app/

# Test optimization
curl -X POST https://promptsmith-production.up.railway.app/optimize \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"user_query": "Create a bar chart showing sales data", "max_iterations": 3}'

# Test cache stats
curl https://promptsmith-production.up.railway.app/cache/stats \
  -H "X-API-Key: your-api-key"
```

### Test the Frontend
1. Start your React development server
2. Navigate to the Promptsmith page
3. Try different chart requests
4. Verify all information is displayed correctly

## Step 11: Performance Optimization

### Lazy Loading
```tsx
import React, { lazy, Suspense } from 'react';

const EnhancedPromptsmithComponent = lazy(() => import('./components/EnhancedPromptsmithComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <EnhancedPromptsmithComponent />
    </Suspense>
  );
}
```

### Caching
Consider implementing client-side caching for repeated requests:

```tsx
const usePromptsmithCache = () => {
  const cache = useRef(new Map());
  
  const getCachedResult = (query: string) => {
    return cache.current.get(query);
  };
  
  const setCachedResult = (query: string, result: any) => {
    cache.current.set(query, result);
  };
  
  return { getCachedResult, setCachedResult };
};
```

## Step 12: Deployment

### Vercel Deployment
1. Push your updated code to GitHub
2. Vercel will automatically deploy
3. Set environment variables in Vercel dashboard:
   - `REACT_APP_PROMPTSMITH_API_URL`
   - `REACT_APP_PROMPTSMITH_API_KEY`

### Environment Variables in Vercel
```bash
REACT_APP_PROMPTSMITH_API_URL=https://promptsmith-production.up.railway.app
REACT_APP_PROMPTSMITH_API_KEY=your-api-key-here
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure your Railway API has the correct CORS settings
2. **API Key Issues**: Verify the API key is set correctly in both frontend and backend
3. **Chart Rendering**: Make sure vega-embed is properly installed
4. **Streaming Issues**: Check that your server supports streaming responses

### Debug Mode
Add debug logging to see what's happening:

```tsx
const DEBUG = process.env.NODE_ENV === 'development';

const handleSubmit = async (e: React.FormEvent) => {
  // ... existing code ...
  
  if (DEBUG) {
    console.log('API Response:', data);
  }
  
  // ... rest of code ...
};
```

## Next Steps

1. **Deploy the enhanced API** to Railway
2. **Integrate the components** into your React app
3. **Test thoroughly** with different chart requests
4. **Customize the styling** to match your site's theme
5. **Add analytics** to track usage and performance
6. **Consider adding more features** like:
   - Chart export functionality
   - Save/load chart specifications
   - User preferences and settings
   - Advanced customization options

The enhanced Promptsmith API provides a rich, informative experience that showcases the full power of your multi-agent chart optimization system! 