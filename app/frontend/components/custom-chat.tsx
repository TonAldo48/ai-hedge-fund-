'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Send, Loader2, User, Bot } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

interface Agent {
  id: string;
  name: string;
  endpoint: string;
  description: string;
}

const AGENTS: Agent[] = [
  {
    id: 'warren-buffett',
    name: 'Warren Buffett',
    endpoint: '/warren-buffett/analyze-streaming',
    description: 'Value investing analysis using Warren Buffett\'s principles'
  },
  // Add more agents here as needed
];

interface CustomChatProps {
  apiKey?: string;
  backendUrl?: string;
  defaultAgent?: string;
  className?: string;
}

export function CustomChat({ 
  apiKey = 'Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw',
  backendUrl = 'http://localhost:8000',
  defaultAgent = 'warren-buffett',
  className = ''
}: CustomChatProps) {
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

    const assistantMessage: Message = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    };

    setMessages(prev => [...prev, assistantMessage]);

    try {
      // Create abort controller for cancellation
      abortControllerRef.current = new AbortController();
      
      const agent = AGENTS.find(a => a.id === selectedAgent);
      if (!agent) throw new Error('Agent not found');

      const response = await fetch(`${backendUrl}${agent.endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          query: userMessage.content,
          chat_history: messages.map(msg => ({
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
              
              // Handle different event types
              if (data.type === 'agent_finish' || data.type === 'complete') {
                const finalContent = data.data.output || data.data.response || accumulatedContent;
                setMessages(prev => prev.map(msg => 
                  msg.id === assistantMessage.id 
                    ? { ...msg, content: finalContent, isStreaming: false }
                    : msg
                ));
                accumulatedContent = finalContent;
              } else if (data.type === 'token' || data.type === 'chunk') {
                // Handle streaming tokens if your backend supports it
                accumulatedContent += data.data.token || data.data.chunk || '';
                setMessages(prev => prev.map(msg => 
                  msg.id === assistantMessage.id 
                    ? { ...msg, content: accumulatedContent }
                    : msg
                ));
              } else if (data.type === 'error') {
                throw new Error(data.data.error || 'Unknown error');
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
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

  return (
    <Card className={`flex flex-col h-[600px] w-full max-w-4xl mx-auto ${className}`}>
      {/* Header */}
      <div className="border-b p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">AI Hedge Fund Chat</h2>
          <Select value={selectedAgent} onValueChange={setSelectedAgent}>
            <SelectTrigger className="w-[200px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {AGENTS.map(agent => (
                <SelectItem key={agent.id} value={agent.id}>
                  {agent.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          {AGENTS.find(a => a.id === selectedAgent)?.description}
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-muted-foreground py-8">
            <p>Start a conversation by asking about stocks or investment strategies!</p>
          </div>
        )}
        
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5" />
              </div>
            )}
            
            <div
              className={`max-w-[70%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              {message.isStreaming && (
                <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1" />
              )}
            </div>
            
            {message.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                <User className="w-5 h-5 text-primary-foreground" />
              </div>
            )}
          </div>
        ))}
        
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
            placeholder="Ask about stocks, investment strategies, or market analysis..."
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