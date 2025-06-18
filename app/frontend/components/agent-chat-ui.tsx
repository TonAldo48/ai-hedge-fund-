'use client';

import { useAgentChat, type ChatMessage } from '@/hooks/use-agent-chat';
import { useState, useRef } from 'react';
import { ChatHeader } from './chat-header';
import { MultimodalInput } from './multimodal-input';
import { PreviewMessage, ThinkingMessage } from './message';
import { useScrollToBottom } from '@/hooks/use-scroll-to-bottom';
import { AnimatePresence, motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import type { Attachment } from 'ai';
import { AgentGreeting } from './agent-greeting';

const API_KEY = process.env.NEXT_PUBLIC_API_KEY || 'Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface AgentChatUIProps {
  chatId: string;
  agentId: string;
  agentData: {
    name: string;
    description: string;
    expertise: string[];
    icon: string;
  };
}

// Convert our simple messages to the UI format expected by PreviewMessage
function convertToUIMessage(message: ChatMessage): any {
  return {
    id: message.id,
    role: message.role,
    content: message.content,
    parts: [
      {
        type: 'text',
        text: message.content
      }
    ],
    // Add reasoning as a special part if present
    ...(message.reasoning && message.reasoning.length > 0 && {
      reasoning: message.reasoning
    })
  };
}

export function AgentChatUI({ chatId, agentId, agentData }: AgentChatUIProps) {
  const [input, setInput] = useState('');
  const [attachments, setAttachments] = useState<Array<Attachment>>([]);
  const { messages, isLoading, error, sendMessage, stop } = useAgentChat({
    chatId,
    agentName: agentId,
    apiKey: API_KEY,
    baseUrl: API_URL,
  });

  const { 
    containerRef: messagesContainerRef, 
    endRef: messagesEndRef,
    scrollToBottom 
  } = useScrollToBottom();

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const message = input.trim();
    setInput('');
    await sendMessage(message);
    
    // Scroll to bottom after sending
    setTimeout(() => scrollToBottom(), 100);
  };



  // Convert messages to UI format
  const uiMessages = messages.map(convertToUIMessage);

  // Mock append function to satisfy the type requirements
  const mockAppend = async (message: { role: string; content: string }) => {
    // For agent chats, we use sendMessage instead of append
    if (message.role === 'user' && message.content) {
      setInput(message.content);
      await sendMessage(message.content);
    }
    return null;
  };

  // Wrapper for handleSubmit to match expected type
  const wrappedHandleSubmit = (event?: { preventDefault?: () => void }) => {
    event?.preventDefault?.();
    handleSubmit();
  };

  return (
    <div className="flex flex-col min-w-0 h-dvh bg-background">
      <ChatHeader
        chatId={chatId}
        selectedModelId={agentData.name}
        selectedVisibilityType="private"
        isReadonly={false}
        session={{ user: { id: 'agent-user', email: '', type: 'regular' }, expires: '' }}
      />

      <div
        ref={messagesContainerRef}
        className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4"
      >
        {messages.length === 0 && (
          <AgentGreeting {...agentData} />
        )}

        <AnimatePresence>
          {uiMessages.map((message, index) => (
            <motion.div
              key={message.id}
              className={cn(
                'w-full mx-auto max-w-3xl px-4',
                message.role === 'assistant' && index === messages.length - 1 && isLoading && 'min-h-96'
              )}
              initial={{ y: 5, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
            >
              {/* Show reasoning steps if available */}
              {message.role === 'assistant' && message.reasoning && message.reasoning.length > 0 && (
                <div className="mb-2 space-y-1">
                  {message.reasoning.map((step: string, idx: number) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className="text-xs text-muted-foreground flex items-center gap-2"
                    >
                      <span className="animate-pulse">⚡</span>
                      <span>{step}</span>
                    </motion.div>
                  ))}
                </div>
              )}
              
              <PreviewMessage
                chatId={chatId}
                message={message}
                vote={undefined}
                isLoading={false}
                setMessages={() => {}}
                reload={() => {}}
                isReadonly={false}
                requiresScrollPadding={false}
              />
            </motion.div>
          ))}

          {isLoading && messages[messages.length - 1]?.role === 'user' && (
            <ThinkingMessage />
          )}
        </AnimatePresence>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mx-auto max-w-3xl w-full px-4"
          >
            <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-4 text-sm text-destructive">
              {error}
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} className="shrink-0 min-w-[24px] min-h-[24px]" />
      </div>

      <form className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
        <MultimodalInput
          chatId={chatId}
          input={input}
          setInput={setInput}
          handleSubmit={wrappedHandleSubmit}
          status={isLoading ? 'submitted' : 'ready'}
          stop={stop}
          attachments={attachments}
          setAttachments={setAttachments}
          messages={uiMessages}
          setMessages={() => {}}
          append={mockAppend}
          selectedVisibilityType="private"
        />
      </form>
    </div>
  );
} 