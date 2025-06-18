'use client';

import { useAgentChat } from '@/hooks/use-agent-chat';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { AgentGreeting } from './agent-greeting';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { ArrowUpIcon, LoaderIcon } from './icons';
import { cn } from '@/lib/utils';

const API_KEY = 'Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw';

interface AgentChatProps {
  agentId: string;
  agentData: {
    name: string;
    description: string;
    expertise: string[];
    icon: string;
  };
}

export function AgentChat({ agentId, agentData }: AgentChatProps) {
  const [input, setInput] = useState('');
  const { messages, isLoading, error, sendMessage } = useAgentChat({
    agentName: agentId,
    apiKey: API_KEY,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const message = input.trim();
    setInput('');
    await sendMessage(message);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Agent Header */}
      <div className="border-b px-4 py-3 bg-background/95 backdrop-blur">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{agentData.icon}</span>
          <div>
            <h2 className="font-semibold">{agentData.name}</h2>
            <p className="text-sm text-muted-foreground">
              {agentData.description}
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {messages.length === 0 ? (
          <AgentGreeting {...agentData} />
        ) : (
          <div className="space-y-4 max-w-3xl mx-auto">
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn(
                  'flex',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                <div
                  className={cn(
                    'max-w-[80%] rounded-lg px-4 py-2',
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  )}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              </motion.div>
            ))}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="bg-muted rounded-lg px-4 py-2">
                  <div className="animate-spin">
                    <LoaderIcon size={16} />
                  </div>
                </div>
              </motion.div>
            )}
            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center text-sm text-destructive"
              >
                {error}
              </motion.div>
            )}
          </div>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex gap-2 max-w-3xl mx-auto">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder={`Ask ${agentData.name} about investments...`}
            className="min-h-[60px] resize-none"
            disabled={isLoading}
          />
          <Button
            type="submit"
            size="icon"
            disabled={!input.trim() || isLoading}
            className="h-[60px] w-[60px]"
          >
            {isLoading ? (
              <div className="animate-spin">
                <LoaderIcon size={16} />
              </div>
            ) : (
              <ArrowUpIcon size={16} />
            )}
          </Button>
        </div>
      </form>
    </div>
  );
} 