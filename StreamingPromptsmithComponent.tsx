import React, { useState, useRef, useEffect } from 'react';
import { vega } from 'vega-embed';

interface StreamingEvent {
  type: 'start' | 'iteration_progress' | 'complete' | 'error';
  message?: string;
  iteration?: number;
  progress?: {
    step: string;
    agent: string | null;
    overall_progress: number;
  };
  agent_outputs?: Record<string, any>;
  scores?: {
    heuristic: number;
    llm: number;
    final: number;
  };
  result?: any;
  error?: string;
}

const StreamingPromptsmithComponent: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [iterationHistory, setIterationHistory] = useState<any[]>([]);
  const [finalResult, setFinalResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [showChartSpec, setShowChartSpec] = useState(false);
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

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

  const handleStreamingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsProcessing(true);
    setError(null);
    setFinalResult(null);
    setIterationHistory([]);
    setCurrentStep('');
    setCurrentAgent(null);
    setProgress(0);

    try {
      // Create a POST request with streaming
      const response = await fetch(`${API_BASE_URL}/optimize/stream`, {
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

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data: StreamingEvent = JSON.parse(line.slice(6));
              handleStreamingEvent(data);
            } catch (parseError) {
              console.error('Error parsing streaming data:', parseError);
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsProcessing(false);
    }
  };

  const handleStreamingEvent = (event: StreamingEvent) => {
    switch (event.type) {
      case 'start':
        setCurrentStep('initializing');
        setCurrentAgent(null);
        setProgress(0);
        break;

      case 'iteration_progress':
        if (event.progress) {
          setCurrentStep(event.progress.step);
          setCurrentAgent(event.progress.agent);
          setProgress(event.progress.overall_progress);
        }
        if (event.iteration && event.agent_outputs && event.scores) {
          const iterationData = {
            iteration: event.iteration,
            progress: event.progress,
            agent_outputs: event.agent_outputs,
            scores: event.scores
          };
          setIterationHistory(prev => [...prev, iterationData]);
        }
        break;

      case 'complete':
        setCurrentStep('complete');
        setCurrentAgent(null);
        setProgress(100);
        setFinalResult(event.result);
        setIsProcessing(false);
        
        if (event.result?.chart_spec) {
          renderChart(event.result.chart_spec);
        }
        break;

      case 'error':
        setError(event.error || 'An error occurred during processing');
        setIsProcessing(false);
        break;
    }
  };

  const renderProgressIndicator = () => {
    if (!isProcessing && !finalResult) return null;

    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-blue-900">
            {isProcessing ? '🔄 Processing...' : '✅ Complete!'}
          </h3>
          <div className="flex items-center space-x-2">
            {currentAgent && (
              <span className="text-sm text-blue-600">
                {getAgentIcon(currentAgent)} {currentAgent.replace('_', ' ')}
              </span>
            )}
            <span className="text-sm text-blue-600">
              {progress.toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-blue-200 rounded-full h-2 mb-4">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>

        {/* Current Step */}
        {currentStep && (
          <div className="flex items-center text-sm text-blue-700">
            <span className="mr-2">{getStepIcon(currentStep)}</span>
            <span className="capitalize">{currentStep.replace('_', ' ')}</span>
          </div>
        )}

        {/* Iteration Progress */}
        {iterationHistory.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-blue-900 mb-2">Iteration Progress:</h4>
            <div className="space-y-2">
              {iterationHistory.map((iteration, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <span>Iteration {iteration.iteration}</span>
                  <div className="flex items-center space-x-3">
                    <span className={`${getScoreColor(iteration.scores.final)}`}>
                      Final: {iteration.scores.final.toFixed(1)}/10
                    </span>
                    <span className="text-gray-600">
                      H: {iteration.scores.heuristic.toFixed(1)}/10
                    </span>
                    <span className="text-gray-600">
                      L: {iteration.scores.llm.toFixed(1)}/10
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderFinalResults = () => {
    if (!finalResult) return null;

    return (
      <div className="space-y-6">
        {/* Final Summary */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-green-900">
              🎉 Optimization Complete!
            </h3>
            <div className="flex items-center space-x-4">
              <span className={`text-lg font-semibold ${getScoreColor(finalResult.final_score)}`}>
                Final Score: {finalResult.final_score.toFixed(1)}/10
              </span>
              <span className="text-sm text-green-600">
                Iterations: {finalResult.iteration}
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium">Heuristic Score:</span>
              <span className={`ml-2 ${getScoreColor(finalResult.scores.heuristic)}`}>
                {finalResult.scores.heuristic.toFixed(1)}/10
              </span>
            </div>
            <div>
              <span className="font-medium">LLM Score:</span>
              <span className={`ml-2 ${getScoreColor(finalResult.scores.llm)}`}>
                {finalResult.scores.llm.toFixed(1)}/10
              </span>
            </div>
            <div>
              <span className="font-medium">Chart Type:</span>
              <span className="ml-2 text-green-600">
                {finalResult.agent_outputs?.chart_builder?.chart_type || 'Unknown'}
              </span>
            </div>
          </div>
        </div>

        {/* Chart Display */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">📈 Generated Chart</h3>
          <div ref={chartContainerRef} className="w-full h-96 border border-gray-200 rounded-lg"></div>
        </div>

        {/* Agent Analysis */}
        {finalResult.agent_outputs && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">🤖 Agent Analysis</h3>
            <div className="space-y-3">
              {Object.entries(finalResult.agent_outputs).map(([agent, output]: [string, any]) => (
                <div key={agent} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <span className="text-xl mr-2">{getAgentIcon(agent)}</span>
                    <h4 className="font-semibold capitalize">{agent.replace('_', ' ')}</h4>
                    <span className="ml-auto px-2 py-1 rounded text-xs bg-green-100 text-green-800">
                      {output.status || 'completed'}
                    </span>
                  </div>

                  {output.from_cache && (
                    <div className="text-sm text-blue-600 mb-2">
                      🎯 Using cached pattern: {output.cache_hit}
                    </div>
                  )}

                  {output.score !== undefined && (
                    <div className="text-sm mb-2">
                      Score: <span className={getScoreColor(output.score)}>{output.score.toFixed(1)}/10</span>
                    </div>
                  )}

                  {output.feedback && (
                    <div className="text-sm text-gray-700 mb-2">
                      Feedback: {output.feedback}
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
                </div>
              ))}
            </div>
          </div>
        )}

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
              {JSON.stringify(finalResult.chart_spec, null, 2)}
            </pre>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🌊 Streaming Promptsmith Chart Optimizer
        </h1>
        <p className="text-lg text-gray-600">
          Real-time chart generation with live progress updates
        </p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleStreamingSubmit} className="mb-8">
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
              'Generate Chart (Streaming)'
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

      {/* Progress Indicator */}
      {renderProgressIndicator()}

      {/* Final Results */}
      {renderFinalResults()}
    </div>
  );
};

export default StreamingPromptsmithComponent; 