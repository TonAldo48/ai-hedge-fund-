import { useState, useCallback, useRef } from 'react';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  reasoning?: string[];
  toolCalls?: Array<{
    toolName: string;
    args: any;
  }>;
}

interface AgentChatConfig {
  agentName: string;
  apiKey: string;
  baseUrl?: string;
}

interface StreamEvent {
  type: string;
  data: any;
}

export function useAgentChat({ agentName, apiKey, baseUrl = '' }: AgentChatConfig) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    setIsLoading(true);
    setError(null);

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
    };
    
    setMessages(prev => [...prev, userMessage]);

    // Create assistant message placeholder
    const assistantId = (Date.now() + 1).toString();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      reasoning: [],
      toolCalls: [],
    };
    
    setMessages(prev => [...prev, assistantMessage]);

    try {
      // Use streaming endpoint
      const url = baseUrl ? `${baseUrl}/api/agents/${agentName}/analyze-streaming` : `/api/agents/${agentName}/analyze-streaming`;
      
      abortControllerRef.current = new AbortController();
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`,
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          message: content,
          chat_history: messages.map(m => ({
            role: m.role,
            content: m.content,
          })),
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) {
        throw new Error('No response body');
      }

      let buffer = '';
      let fullContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Keep the last incomplete line in the buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim() === '') continue;
          
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            if (data === '[DONE]') {
              break;
            }
            
            try {
              const event = JSON.parse(data);
              
              // Update assistant message based on event type
              setMessages(prev => prev.map(msg => {
                if (msg.id === assistantId) {
                  if (event.type === 'text-delta') {
                    fullContent += event.textDelta;
                    return { ...msg, content: fullContent };
                  } else if (event.type === 'llm_thinking' || event.type === 'agent_action' || event.type === 'tool_start') {
                    // Add reasoning steps
                    const message = event.data?.message || '';
                    if (message && !msg.reasoning?.includes(message)) {
                      return { 
                        ...msg, 
                        reasoning: [...(msg.reasoning || []), message] 
                      };
                    }
                  }
                }
                return msg;
              }));
            } catch (e) {
              console.error('Error parsing SSE data:', data, e);
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log('Request was aborted');
      } else {
        setError(err instanceof Error ? err.message : 'An error occurred');
        // Remove the empty assistant message if error
        setMessages(prev => prev.filter(msg => msg.id !== assistantId));
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [agentName, apiKey, baseUrl, messages]);

  const stop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    stop,
  };
} 