import React, { useState, useRef, useEffect } from 'react';
import { vega } from 'vega-embed';

interface AgentOutput {
  status: string;
  from_cache?: boolean;
  cache_hit?: string;
  generation_method?: string;
  chart_type?: string;
  is_valid?: boolean;
  score?: number;
  issues?: string[];
  feedback?: string;
  strengths?: string[];
  weaknesses?: string[];
  criterion_scores?: Record<string, number>;
  llm_fallback?: boolean;
  llm_error?: string;
}

interface ProgressInfo {
  current_step: string;
  current_agent: string | null;
  overall_progress: number;
  step_details: Record<string, any>;
}

interface IterationHistory {
  iteration: number;
  prompt: string;
  chart_spec: any;
  heuristic_score: number;
  llm_score: number;
  final_score: number;
  status: string;
  agent_outputs: Record<string, AgentOutput>;
  progress: {
    step: string;
    agent: string | null;
    overall_progress: number;
  };
}

interface CacheStats {
  total_runs: number;
  query_patterns: number;
  issue_patterns: number;
  prompt_patterns: number;
  chart_patterns: number;
  avg_score: number;
}

interface EnhancedPromptsmithResponse {
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
    progress: ProgressInfo;
    agent_outputs: Record<string, AgentOutput>;
    iteration_history: IterationHistory[];
    cache_stats: CacheStats;
    user_query: string;
    max_iterations: number;
  };
  message: string;
}

const EnhancedPromptsmithComponent: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<EnhancedPromptsmithResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showChartSpec, setShowChartSpec] = useState(false);
  const [showIterationDetails, setShowIterationDetails] = useState<number | null>(null);
  const chartContainerRef = useRef<HTMLDivElement>(null);

  const API_BASE_URL = process.env.REACT_APP_PROMPTSMITH_API_URL || 'https://promptsmith-production.up.railway.app';
  const API_KEY = process.env.REACT_APP_PROMPTSMITH_API_KEY || 'test-key-123';

  const getStepIcon = (step: string) => {
    const icons: Record<string, string> = {
      'generating_prompt': '📝',
      'building_chart': '📊',
      'heuristic_evaluation': '🔍',
      'llm_evaluation': '🤖',
      'scoring': '📈',
      'rewriting_prompt': '✏️',
      'clarification': '❓',
      'complete': '✅',
      'initializing': '🚀'
    };
    return icons[step] || '⚙️';
  };

  const getAgentIcon = (agent: string) => {
    const icons: Record<string, string> = {
      'prompt_generator': '📝',
      'chart_builder': '📊',
      'heuristic_evaluator': '🔍',
      'llm_evaluator': '🤖',
      'scorer': '📈',
      'rewriter': '✏️',
      'clarifier': '❓'
    };
    return icons[agent] || '🤖';
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const renderAgentOutput = (agentName: string, output: AgentOutput) => {
    return (
      <div key={agentName} className="bg-gray-50 rounded-lg p-4 mb-3">
        <div className="flex items-center mb-2">
          <span className="text-xl mr-2">{getAgentIcon(agentName)}</span>
          <h4 className="font-semibold capitalize">{agentName.replace('_', ' ')}</h4>
          <span className={`ml-auto px-2 py-1 rounded text-xs ${
            output.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
          }`}>
            {output.status}
          </span>
        </div>

        {output.from_cache && (
          <div className="text-sm text-blue-600 mb-2">
            🎯 Using cached pattern: {output.cache_hit}
          </div>
        )}

        {output.generation_method && (
          <div className="text-sm text-gray-600 mb-2">
            Method: {output.generation_method}
          </div>
        )}

        {output.chart_type && (
          <div className="text-sm text-gray-600 mb-2">
            Chart Type: {output.chart_type}
          </div>
        )}

        {output.score !== undefined && (
          <div className="text-sm mb-2">
            Score: <span className={getScoreColor(output.score)}>{output.score.toFixed(1)}/10</span>
          </div>
        )}

        {output.issues && output.issues.length > 0 && (
          <div className="text-sm text-red-600 mb-2">
            Issues: {output.issues.join(', ')}
          </div>
        )}

        {output.strengths && output.strengths.length > 0 && (
          <div className="text-sm text-green-600 mb-2">
            Strengths: {output.strengths.join(', ')}
          </div>
        )}

        {output.weaknesses && output.weaknesses.length > 0 && (
          <div className="text-sm text-orange-600 mb-2">
            Areas for improvement: {output.weaknesses.join(', ')}
          </div>
        )}

        {output.feedback && (
          <div className="text-sm text-gray-700 mb-2">
            Feedback: {output.feedback}
          </div>
        )}

        {output.llm_fallback && (
          <div className="text-sm text-yellow-600 mb-2">
            ⚠️ Used fallback method (LLM unavailable)
          </div>
        )}
      </div>
    );
  };

  const renderIterationHistory = () => {
    if (!result?.data.iteration_history) return null;

    return (
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-4">📚 Optimization Journey</h3>
        <div className="space-y-4">
          {result.data.iteration_history.map((iteration, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold">Iteration {iteration.iteration}</h4>
                <div className="flex items-center space-x-4">
                  <span className={`text-sm ${getScoreColor(iteration.final_score)}`}>
                    Final: {iteration.final_score.toFixed(1)}/10
                  </span>
                  <span className="text-sm text-gray-600">
                    Heuristic: {iteration.heuristic_score.toFixed(1)}/10
                  </span>
                  <span className="text-sm text-gray-600">
                    LLM: {iteration.llm_score.toFixed(1)}/10
                  </span>
                  <button
                    onClick={() => setShowIterationDetails(showIterationDetails === index ? null : index)}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    {showIterationDetails === index ? 'Hide Details' : 'Show Details'}
                  </button>
                </div>
              </div>

              {showIterationDetails === index && (
                <div className="mt-3 space-y-3">
                  <div className="text-sm text-gray-700">
                    <strong>Prompt:</strong> {iteration.prompt}
                  </div>
                  {Object.entries(iteration.agent_outputs).map(([agent, output]) => 
                    renderAgentOutput(agent, output)
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderChart = async (chartSpec: any) => {
    if (!chartContainerRef.current || !chartSpec) return;

    try {
      chartContainerRef.current.innerHTML = '';
      await vega(chartContainerRef.current, chartSpec, {
        actions: false,
        theme: 'default'
      });
    } catch (error) {
      console.error('Error rendering chart:', error);
      chartContainerRef.current.innerHTML = '<p className="text-red-600">Error rendering chart</p>';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY,
        },
        body: JSON.stringify({
          user_query: query,
          max_iterations: 3
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: EnhancedPromptsmithResponse = await response.json();
      setResult(data);

      if (data.data.chart_spec) {
        await renderChart(data.data.chart_spec);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🚀 Enhanced Promptsmith Chart Optimizer
        </h1>
        <p className="text-lg text-gray-600">
          AI-powered chart generation with detailed progress tracking and quality analysis
        </p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Describe the chart you want to create..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isProcessing}
          />
          <button
            type="submit"
            disabled={isProcessing || !query.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {isProcessing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Processing...
              </>
            ) : (
              'Generate Chart'
            )}
          </button>
        </div>
      </form>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800">❌ Error: {error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Progress Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-blue-900">
                📊 Optimization Complete
              </h3>
              <div className="flex items-center space-x-4">
                <span className={`text-lg font-semibold ${getScoreColor(result.data.final_score)}`}>
                  Final Score: {result.data.final_score.toFixed(1)}/10
                </span>
                <span className="text-sm text-blue-600">
                  Iterations: {result.data.iteration}
                </span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="font-medium">Heuristic Score:</span>
                <span className={`ml-2 ${getScoreColor(result.data.scores.heuristic)}`}>
                  {result.data.scores.heuristic.toFixed(1)}/10
                </span>
              </div>
              <div>
                <span className="font-medium">LLM Score:</span>
                <span className={`ml-2 ${getScoreColor(result.data.scores.llm)}`}>
                  {result.data.scores.llm.toFixed(1)}/10
                </span>
              </div>
              <div>
                <span className="font-medium">Progress:</span>
                <span className="ml-2 text-blue-600">
                  {result.data.progress.overall_progress.toFixed(0)}%
                </span>
              </div>
            </div>
          </div>

          {/* Cache Statistics */}
          {result.data.cache_stats && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-green-900 mb-3">🧠 Learning Cache</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="font-medium">Total Runs:</span>
                  <span className="ml-2">{result.data.cache_stats.total_runs}</span>
                </div>
                <div>
                  <span className="font-medium">Patterns Learned:</span>
                  <span className="ml-2">{result.data.cache_stats.query_patterns}</span>
                </div>
                <div>
                  <span className="font-medium">Avg Score:</span>
                  <span className="ml-2">{result.data.cache_stats.avg_score.toFixed(2)}/10</span>
                </div>
                <div>
                  <span className="font-medium">Cache Hit Rate:</span>
                  <span className="ml-2">
                    {result.data.cache_stats.total_runs > 0 
                      ? ((result.data.cache_stats.query_patterns / result.data.cache_stats.total_runs) * 100).toFixed(1)
                      : '0'}%
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Chart Display */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">📈 Generated Chart</h3>
            <div ref={chartContainerRef} className="w-full h-96 border border-gray-200 rounded-lg"></div>
          </div>

          {/* Agent Outputs */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">🤖 Agent Analysis</h3>
            <div className="space-y-3">
              {Object.entries(result.data.agent_outputs).map(([agent, output]) => 
                renderAgentOutput(agent, output)
              )}
            </div>
          </div>

          {/* Iteration History */}
          {renderIterationHistory()}

          {/* Chart Specification */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">🔧 Chart Specification</h3>
              <button
                onClick={() => setShowChartSpec(!showChartSpec)}
                className="text-blue-600 hover:text-blue-800"
              >
                {showChartSpec ? 'Hide' : 'Show'} JSON
              </button>
            </div>
            {showChartSpec && (
              <pre className="bg-gray-100 p-4 rounded-lg overflow-auto text-sm">
                {JSON.stringify(result.data.chart_spec, null, 2)}
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedPromptsmithComponent; 