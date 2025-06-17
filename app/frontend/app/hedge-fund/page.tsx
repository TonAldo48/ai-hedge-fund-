'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Badge } from '../../components/ui/badge';
import { Separator } from '../../components/ui/separator';
import { TrendingUp, TrendingDown, Minus, DollarSign, BarChart3, PieChart, Activity } from 'lucide-react';

// API configuration
const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw';

interface Agent {
  id: string;
  name: string;
}

interface Model {
  display_name: string;
  model_name: string;
  provider: string;
}

interface AnalysisResult {
  decisions: Record<string, any>;
  analyst_signals: Record<string, any>;
  metadata: any;
}

interface BacktestResult {
  status: string;
  weight_session_id?: string;
  performance_metrics?: any;
  portfolio_history?: any[];
  final_portfolio?: any;
}

export default function HedgeFundDashboard() {
  // State for API data
  const [agents, setAgents] = useState<Agent[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null);
  
  // Form state
  const [tickers, setTickers] = useState('AAPL,MSFT,GOOGL');
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('');
  const [initialCash, setInitialCash] = useState(100000);
  const [marginRequirement, setMarginRequirement] = useState(0);
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  
  // Active tab
  const [activeTab, setActiveTab] = useState<'analysis' | 'backtest'>('analysis');

  // Fetch available agents and models on load
  useEffect(() => {
    fetchAgents();
    fetchModels();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/hedge-fund/agents`);
      const data = await response.json();
      setAgents(data.agents || []);
    } catch (err) {
      setError('Failed to load agents');
    }
  };

  const fetchModels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/hedge-fund/models`);
      const data = await response.json();
      setModels(data.models || []);
      if (data.models && data.models.length > 0) {
        setSelectedModel(data.models[0].model_name);
        setSelectedProvider(data.models[0].provider);
      }
    } catch (err) {
      setError('Failed to load models');
    }
  };

  const runAnalysis = async () => {
    if (!tickers.trim() || selectedAgents.length === 0) {
      setError('Please select tickers and agents');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const requestBody = {
        tickers: tickers.split(',').map(t => t.trim().toUpperCase()),
        selected_agents: selectedAgents,
        model_name: selectedModel,
        model_provider: selectedProvider,
        initial_cash: initialCash,
        margin_requirement: marginRequirement,
        start_date: startDate,
        end_date: endDate
      };

      const response = await fetch(`${API_BASE_URL}/hedge-fund/run-sync`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${API_KEY}`
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(`Analysis failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const runBacktest = async () => {
    if (!tickers.trim() || selectedAgents.length === 0) {
      setError('Please select tickers and agents');
      return;
    }

    setLoading(true);
    setError('');
    setBacktestResult(null);

    try {
      const requestBody = {
        tickers: tickers.split(',').map(t => t.trim().toUpperCase()),
        selected_agents: selectedAgents,
        model_name: selectedModel,
        model_provider: selectedProvider,
        initial_capital: initialCash,
        margin_requirement: marginRequirement,
        start_date: startDate,
        end_date: endDate
      };

      const response = await fetch(`${API_BASE_URL}/backtest/run-sync`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${API_KEY}`
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setBacktestResult(data);
    } catch (err) {
      setError(`Backtest failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const toggleAgent = (agentId: string) => {
    setSelectedAgents(prev => 
      prev.includes(agentId) 
        ? prev.filter(id => id !== agentId)
        : [...prev, agentId]
    );
  };

  const handleModelChange = (modelName: string) => {
    const model = models.find(m => m.model_name === modelName);
    if (model) {
      setSelectedModel(model.model_name);
      setSelectedProvider(model.provider);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight text-gray-900">Aeero</h2>
        <div className="flex items-center space-x-2">
          <Button
            variant={activeTab === 'analysis' ? 'default' : 'outline'}
            onClick={() => setActiveTab('analysis')}
            size="sm"
            className={activeTab === 'analysis' ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'border-gray-300 text-gray-700 hover:bg-gray-50'}
          >
            <BarChart3 className="mr-2 h-4 w-4" />
            Analysis
          </Button>
          <Button
            variant={activeTab === 'backtest' ? 'default' : 'outline'}
            onClick={() => setActiveTab('backtest')}
            size="sm"
            className={activeTab === 'backtest' ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'border-gray-300 text-gray-700 hover:bg-gray-50'}
          >
            <Activity className="mr-2 h-4 w-4" />
            Backtest
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-white shadow-sm border-gray-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-700">Portfolio Value</CardTitle>
            <DollarSign className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">${initialCash.toLocaleString()}</div>
            <p className="text-xs text-gray-500">Initial Capital</p>
          </CardContent>
        </Card>
        
        <Card className="bg-white shadow-sm border-gray-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-700">Active Agents</CardTitle>
            <PieChart className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{selectedAgents.length}</div>
            <p className="text-xs text-gray-500">AI Analysts Selected</p>
          </CardContent>
        </Card>

        <Card className="bg-white shadow-sm border-gray-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-700">Tracked Stocks</CardTitle>
            <TrendingUp className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{tickers.split(',').filter(t => t.trim()).length}</div>
            <p className="text-xs text-gray-500">Securities in Portfolio</p>
          </CardContent>
        </Card>

        <Card className="bg-white shadow-sm border-gray-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-700">Status</CardTitle>
            <Activity className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">
              {loading ? (
                <Badge variant="secondary" className="bg-blue-100 text-blue-800">Running</Badge>
              ) : (
                <Badge variant="outline" className="border-gray-300 text-gray-700">Ready</Badge>
              )}
            </div>
            <p className="text-xs text-gray-500">{activeTab} Mode</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Configuration Panel */}
        <Card className="col-span-4 bg-white shadow-sm border-gray-200">
          <CardHeader>
            <CardTitle className="text-gray-900">Configuration</CardTitle>
            <CardDescription className="text-gray-600">
              Set up your {activeTab} parameters and select AI agents
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Portfolio Configuration */}
            <div className="space-y-4">
              <div>
                <Label htmlFor="tickers" className="text-gray-700 font-medium">Stock Tickers</Label>
                <Input
                  id="tickers"
                  value={tickers}
                  onChange={(e) => setTickers(e.target.value)}
                  placeholder="AAPL,MSFT,GOOGL,TSLA"
                  className="mt-1 bg-white border-gray-300 text-gray-900 focus:border-blue-500 focus:ring-blue-500"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Enter stock symbols separated by commas
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="cash" className="text-gray-700 font-medium">Initial Capital</Label>
                  <Input
                    id="cash"
                    type="number"
                    value={initialCash}
                    onChange={(e) => setInitialCash(Number(e.target.value))}
                    className="mt-1 bg-white border-gray-300 text-gray-900 focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <Label htmlFor="margin" className="text-gray-700 font-medium">Margin Requirement</Label>
                  <Input
                    id="margin"
                    type="number"
                    step="0.01"
                    value={marginRequirement}
                    onChange={(e) => setMarginRequirement(Number(e.target.value))}
                    className="mt-1 bg-white border-gray-300 text-gray-900 focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="startDate" className="text-gray-700 font-medium">Start Date</Label>
                  <Input
                    id="startDate"
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="mt-1 bg-white border-gray-300 text-gray-900 focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <Label htmlFor="endDate" className="text-gray-700 font-medium">End Date</Label>
                  <Input
                    id="endDate"
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="mt-1 bg-white border-gray-300 text-gray-900 focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            <Separator className="bg-gray-200" />

            {/* AI Configuration */}
            <div className="space-y-4">
              <div>
                <Label className="text-gray-700 font-medium">AI Model</Label>
                <Select value={selectedModel} onValueChange={handleModelChange}>
                  <SelectTrigger className="mt-1 bg-white border-gray-300 text-gray-900 focus:border-blue-500 focus:ring-blue-500">
                    <SelectValue placeholder="Select an AI model" />
                  </SelectTrigger>
                  <SelectContent className="bg-white border-gray-300">
                    {models.map((model, index) => (
                      <SelectItem key={`${model.provider}-${model.model_name}-${index}`} value={model.model_name} className="text-gray-900">
                        <div className="flex items-center">
                          <Badge variant="outline" className="mr-2 text-xs border-gray-300 text-gray-600">
                            {model.provider}
                          </Badge>
                          {model.display_name}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label className="text-gray-700 font-medium">AI Analysts ({selectedAgents.length} selected)</Label>
                <div className="grid grid-cols-2 gap-2 mt-2 max-h-40 overflow-y-auto">
                  {agents.map(agent => (
                    <div key={agent.id} className="flex items-center space-x-2 p-2 border border-gray-200 rounded bg-white hover:bg-gray-50">
                      <input
                        type="checkbox"
                        id={agent.id}
                        checked={selectedAgents.includes(agent.id)}
                        onChange={() => toggleAgent(agent.id)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <Label htmlFor={agent.id} className="text-sm flex-1 cursor-pointer text-gray-700">
                        {agent.name}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <Separator className="bg-gray-200" />

            {/* Action Section */}
            <div className="space-y-4">
              <Button
                onClick={activeTab === 'analysis' ? runAnalysis : runBacktest}
                disabled={loading || selectedAgents.length === 0 || !tickers.trim()}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white border-0"
                size="lg"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Running {activeTab}...
                  </>
                ) : (
                  <>
                    {activeTab === 'analysis' ? <BarChart3 className="mr-2 h-4 w-4" /> : <Activity className="mr-2 h-4 w-4" />}
                    Run {activeTab === 'analysis' ? 'Analysis' : 'Backtest'}
                  </>
                )}
              </Button>

              {error && (
                <Alert className="border-red-300 bg-red-50">
                  <AlertDescription className="text-red-700">
                    {error}
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Results Panel */}
        <Card className="col-span-3 bg-white shadow-sm border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center text-gray-900">
              {activeTab === 'analysis' ? 'Trading Decisions' : 'Performance Results'}
              {loading && <div className="ml-2 animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>}
            </CardTitle>
            <CardDescription className="text-gray-600">
              {activeTab === 'analysis' 
                ? 'AI-generated buy/sell/hold recommendations' 
                : 'Historical performance metrics and analysis'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            {activeTab === 'analysis' && result && (
              <div className="space-y-4">
                {Object.entries(result.decisions).map(([ticker, decision]: [string, any]) => (
                  <Card key={ticker} className="p-4 bg-white border-gray-200 shadow-sm">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-semibold text-lg text-gray-900">{ticker}</h4>
                        <Badge 
                          variant={
                            decision.action === 'buy' ? 'default' :
                            decision.action === 'sell' ? 'destructive' : 'secondary'
                          }
                          className={`flex items-center ${
                            decision.action === 'buy' ? 'bg-green-100 text-green-800 border-green-200' :
                            decision.action === 'sell' ? 'bg-red-100 text-red-800 border-red-200' :
                            'bg-gray-100 text-gray-800 border-gray-200'
                          }`}
                        >
                          {decision.action === 'buy' ? <TrendingUp className="mr-1 h-3 w-3" /> :
                           decision.action === 'sell' ? <TrendingDown className="mr-1 h-3 w-3" /> :
                           <Minus className="mr-1 h-3 w-3" />}
                          {decision.action?.toUpperCase()}
                        </Badge>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-500">Confidence</div>
                        <div className="font-semibold text-gray-900">{(decision.confidence * 100).toFixed(1)}%</div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500">Quantity:</span>
                        <span className="font-medium text-gray-900">{decision.quantity}</span>
                      </div>
                      <Separator className="bg-gray-200" />
                      <p className="text-sm text-gray-600 leading-relaxed">
                        {decision.reasoning}
                      </p>
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {activeTab === 'backtest' && backtestResult && (
              <div className="space-y-4">
                {backtestResult.performance_metrics && (
                  <div className="grid grid-cols-1 gap-4">
                    <Card className="p-4 bg-white border-gray-200 shadow-sm">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-500">Total Return</p>
                          <p className="text-2xl font-bold text-gray-900 flex items-center">
                            {backtestResult.performance_metrics.total_return > 0 ? (
                              <TrendingUp className="mr-1 h-5 w-5 text-green-600" />
                            ) : (
                              <TrendingDown className="mr-1 h-5 w-5 text-red-600" />
                            )}
                            {backtestResult.performance_metrics.total_return?.toFixed(2)}%
                          </p>
                        </div>
                      </div>
                    </Card>
                    
                    <Card className="p-4 bg-white border-gray-200">
                      <div>
                        <p className="text-sm text-gray-500">Final Portfolio Value</p>
                        <p className="text-2xl font-bold text-gray-900">
                          ${backtestResult.performance_metrics.final_value?.toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-500">
                          Initial: ${backtestResult.performance_metrics.initial_capital?.toLocaleString()}
                        </p>
                      </div>
                    </Card>

                    {backtestResult.performance_metrics.sharpe_ratio && (
                      <div className="grid grid-cols-2 gap-4">
                        <Card className="p-4 bg-white border-gray-200">
                          <p className="text-sm text-gray-500">Sharpe Ratio</p>
                          <p className="text-xl font-bold text-gray-900">
                            {backtestResult.performance_metrics.sharpe_ratio.toFixed(3)}
                          </p>
                        </Card>
                        
                        {backtestResult.performance_metrics.max_drawdown && (
                          <Card className="p-4 bg-white border-gray-200">
                            <p className="text-sm text-gray-500">Max Drawdown</p>
                            <p className="text-xl font-bold text-red-600">
                              -{(Math.abs(backtestResult.performance_metrics.max_drawdown) * 100).toFixed(2)}%
                            </p>
                          </Card>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {!result && !backtestResult && !loading && (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <div className="rounded-full bg-gray-100 p-6 mb-4">
                  {activeTab === 'analysis' ? (
                    <BarChart3 className="h-12 w-12 text-gray-400" />
                  ) : (
                    <Activity className="h-12 w-12 text-gray-400" />
                  )}
                </div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900">No Results Yet</h3>
                <p className="text-gray-500 mb-4">
                  Configure your parameters and run {activeTab} to see results
                </p>
                <Badge variant="outline" className="border-gray-300 text-gray-600">Ready to Start</Badge>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 