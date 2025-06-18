'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Send, Loader2, User, Bot, TrendingUp, Brain, DollarSign, Shield, BarChart3 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agent?: string;
  isStreaming?: boolean;
}

interface Agent {
  id: string;
  name: string;
  endpoint: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

const AGENTS: Agent[] = [
  {
    id: 'warren-buffett',
    name: 'Warren Buffett',
    endpoint: '/warren-buffett/analyze-streaming',
    description: 'Value investing analysis using Warren Buffett\'s principles',
    icon: DollarSign,
    color: 'text-green-600'
  },
  {
    id: 'portfolio-manager',
    name: 'Portfolio Manager',
    endpoint: '/api/agents/portfolio_manager/analyze',
    description: 'Portfolio optimization and asset allocation strategies',
    icon: BarChart3,
    color: 'text-blue-600'
  },
  {
    id: 'risk-manager',
    name: 'Risk Manager',
    endpoint: '/api/agents/risk_manager/analyze',
    description: 'Risk assessment and mitigation strategies',
    icon: Shield,
    color: 'text-red-600'
  },
  {
    id: 'sentiment-analyzer',
    name: 'Sentiment Analyzer',
    endpoint: '/api/agents/sentiment_analyzer/analyze',
    description: 'Market sentiment and news analysis',
    icon: Brain,
    color: 'text-purple-600'
  },
  {
    id: 'technical-analyst',
    name: 'Technical Analyst',
    endpoint: '/api/agents/technical_analyst/analyze',
    description: 'Technical indicators and chart patterns',
    icon: TrendingUp,
    color: 'text-orange-600'
  }
];

interface MultiAgentChatProps {
  apiKey?: string;
  backendUrl?: string;
  defaultAgent?: string;
  className?: string;
  showAgentBadge?: boolean;
}

export function MultiAgentChat({ 
  apiKey = 'Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw',
  backendUrl = 'http://localhost:8000',
  defaultAgent = 'warren-buffett',
  className = '',
  showAgentBadge = true
}: MultiAgentChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(defaultAgent);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const agent = AGENTS.find(a => a.id === selectedAgent);
    if (!agent) {
      console.error('Agent not found');
      setIsLoading(false);
      return;
    }

    const assistantMessage: Message = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      agent: agent.name,
      isStreaming: true
    };

    setMessages(prev => [...prev, assistantMessage]);

    try {
      abortControllerRef.current = new AbortController();
      
      // Handle streaming endpoints
      if (agent.endpoint.includes('streaming')) {
        const response = await fetch(`${backendUrl}${agent.endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`,
          },
          body: JSON.stringify({
            query: userMessage.content,
            chat_history: messages.filter(m => m.agent === agent.name).map(msg => ({
              role: msg.role,
              content: msg.content,
              timestamp: msg.timestamp.toISOString()
            }))
          }),
          signal: abortControllerRef.current.signal
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.statusText}`);
        }

        const reader = response.body!.getReader();
        const decoder = new TextDecoder();
        let accumulatedContent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'agent_finish' || data.type === 'complete') {
                  const finalContent = data.data.output || data.data.response || accumulatedContent;
                  setMessages(prev => prev.map(msg => 
                    msg.id === assistantMessage.id 
                      ? { ...msg, content: finalContent, isStreaming: false }
                      : msg
                  ));
                  accumulatedContent = finalContent;
                } else if (data.type === 'token' || data.type === 'chunk') {
                  accumulatedContent += data.data.token || data.data.chunk || '';
                  setMessages(prev => prev.map(msg => 
                    msg.id === assistantMessage.id 
                      ? { ...msg, content: accumulatedContent }
                      : msg
                  ));
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e);
              }
            }
          }
        }
      } else {
        // Handle non-streaming endpoints
        const response = await fetch(`${backendUrl}${agent.endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`,
          },
          body: JSON.stringify({
            query: userMessage.content
          }),
          signal: abortControllerRef.current.signal
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.statusText}`);
        }

        const data = await response.json();
        const content = data.response || data.output || 'No response received';
        
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessage.id 
            ? { ...msg, content, isStreaming: false }
            : msg
        ));
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request cancelled');
      } else {
        console.error('Chat error:', error);
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMessage.id 
            ? { 
                ...msg, 
                content: `Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`,
                isStreaming: false 
              }
            : msg
        ));
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const cancelStream = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
    }
  };

  const currentAgent = AGENTS.find(a => a.id === selectedAgent);
  const AgentIcon = currentAgent?.icon || Bot;

  return (
    <Card className={cn("flex flex-col h-[700px] w-full max-w-5xl mx-auto", className)}>
      {/* Header */}
      <div className="border-b p-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-2xl font-semibold">AI Hedge Fund Analysis</h2>
          <Select value={selectedAgent} onValueChange={setSelectedAgent}>
            <SelectTrigger className="w-[250px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {AGENTS.map(agent => (
                <SelectItem key={agent.id} value={agent.id}>
                  <div className="flex items-center gap-2">
                    <agent.icon className={cn("w-4 h-4", agent.color)} />
                    <span>{agent.name}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <p className="text-sm text-muted-foreground flex items-center gap-2">
          <AgentIcon className={cn("w-4 h-4", currentAgent?.color)} />
          {currentAgent?.description}
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-muted-foreground py-12">
            <AgentIcon className={cn("w-12 h-12 mx-auto mb-4", currentAgent?.color)} />
            <p className="text-lg mb-2">Welcome to AI Hedge Fund Analysis</p>
            <p className="text-sm max-w-md mx-auto">
              Ask {currentAgent?.name} about stocks, investment strategies, or market analysis. 
              Switch between different agents for specialized insights.
            </p>
          </div>
        )}
        
        {messages.map((message) => {
          const messageAgent = message.agent ? AGENTS.find(a => a.name === message.agent) : null;
          const MessageIcon = messageAgent?.icon || Bot;
          
          return (
            <div
              key={message.id}
              className={cn(
                "flex gap-3",
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              {message.role === 'assistant' && (
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <MessageIcon className={cn("w-6 h-6", messageAgent?.color)} />
                </div>
              )}
              
              <div
                className={cn(
                  "max-w-[75%] rounded-lg px-4 py-3",
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                )}
              >
                {showAgentBadge && message.agent && message.role === 'assistant' && (
                  <div className="text-xs font-medium mb-1 opacity-70">
                    {message.agent}
                  </div>
                )}
                <p className="whitespace-pre-wrap">{message.content}</p>
                {message.isStreaming && (
                  <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1" />
                )}
              </div>
              
              {message.role === 'user' && (
                <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                  <User className="w-6 h-6 text-primary-foreground" />
                </div>
              )}
            </div>
          );
        })}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder={`Ask ${currentAgent?.name} about stocks, investment strategies, or market analysis...`}
            className="min-h-[60px] resize-none"
            disabled={isLoading}
          />
          
          {isLoading ? (
            <Button
              type="button"
              onClick={cancelStream}
              variant="secondary"
              size="icon"
              className="h-[60px] w-[60px]"
            >
              <Loader2 className="w-5 h-5 animate-spin" />
            </Button>
          ) : (
            <Button
              type="submit"
              size="icon"
              className="h-[60px] w-[60px]"
              disabled={!input.trim()}
            >
              <Send className="w-5 h-5" />
            </Button>
          )}
        </div>
      </form>
    </Card>
  );
} 