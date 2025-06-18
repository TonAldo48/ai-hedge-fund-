'use client';

import type { Attachment, UIMessage } from 'ai';
import { useChat } from '@ai-sdk/react';
import { useEffect, useState, useCallback } from 'react';
import useSWR, { useSWRConfig } from 'swr';
import { ChatHeader } from '@/components/chat-header';
import type { Vote } from '@/lib/db/schema';
import { fetcher, fetchWithErrorHandlers, generateUUID } from '@/lib/utils';
import { Artifact } from './artifact';
import { MultimodalInput } from './multimodal-input';
import { Messages } from './messages';
import type { VisibilityType } from './visibility-selector';
import { useArtifactSelector } from '@/hooks/use-artifact';
import { unstable_serialize } from 'swr/infinite';
import { getChatHistoryPaginationKey } from './sidebar-history';
import { toast } from './toast';
import type { Session } from 'next-auth';
import { useSearchParams } from 'next/navigation';
import { useChatVisibility } from '@/hooks/use-chat-visibility';
import { useAutoResume } from '@/hooks/use-auto-resume';
import { ChatSDKError } from '@/lib/errors';

export type AgentType = 'warren-buffett' | 'peter-lynch' | 'charlie-munger' | 'ben-graham' | 'technical-analyst' | 
  'michael-burry' | 'bill-ackman' | 'cathie-wood' | 'phil-fisher' | 'stanley-druckenmiller' | 
  'aswath-damodaran' | 'fundamentals-analyst' | 'sentiment-analyst' | 'valuation-analyst' | 
  'hedge-fund' | 'portfolio-manager';

interface AgentChatProps {
  id: string;
  agentType: AgentType;
  initialMessages: Array<UIMessage>;
  initialVisibilityType: VisibilityType;
  isReadonly: boolean;
  session: Session;
  autoResume: boolean;
}

export function AgentChat({
  id,
  agentType,
  initialMessages,
  initialVisibilityType,
  isReadonly,
  session,
  autoResume,
}: AgentChatProps) {
  const { mutate } = useSWRConfig();
  const [hasInitialized, setHasInitialized] = useState(false);

  const { visibilityType } = useChatVisibility({
    chatId: id,
    initialVisibilityType,
  });

  // Map agent types to appropriate models
  const getAgentModel = (agent: AgentType): string => {
    // For now, all agents use gpt-4o, but this can be customized per agent
    return 'gpt-4o';
  };

  const agentModel = getAgentModel(agentType);

  const {
    messages,
    setMessages,
    handleSubmit,
    input,
    setInput,
    append,
    status,
    stop,
    reload,
    experimental_resume,
    data,
  } = useChat({
    id,
    initialMessages,
    experimental_throttle: 100,
    sendExtraMessageFields: true,
    generateId: generateUUID,
    fetch: fetchWithErrorHandlers,
    api: '/api/chat/agent',
    experimental_prepareRequestBody: (body) => ({
      id,
      message: body.messages.at(-1),
      selectedChatModel: agentModel,
      selectedVisibilityType: visibilityType,
      agentType, // Include agent type in the request
    }),
    onFinish: () => {
      mutate(unstable_serialize(getChatHistoryPaginationKey));
    },
    onError: (error) => {
      if (error instanceof ChatSDKError) {
        toast({
          type: 'error',
          description: error.message,
        });
      }
    },
  });

  // Initialize chat in database with agent type
  const initializeAgentChat = useCallback(async () => {
    if (!hasInitialized && messages.length === 0) {
      try {
        const response = await fetch('/api/chat/agent/initialize', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            id,
            agentType,
            userId: session.user.id,
            visibility: visibilityType,
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to initialize agent chat');
        }

        setHasInitialized(true);
      } catch (error) {
        console.error('Error initializing agent chat:', error);
        toast({
          type: 'error',
          description: 'Failed to initialize chat. Please refresh the page.',
        });
      }
    }
  }, [id, agentType, session.user.id, visibilityType, hasInitialized, messages.length]);

  useEffect(() => {
    initializeAgentChat();
  }, [initializeAgentChat]);

  const searchParams = useSearchParams();
  const query = searchParams.get('query');

  const [hasAppendedQuery, setHasAppendedQuery] = useState(false);

  useEffect(() => {
    if (query && !hasAppendedQuery) {
      append({
        role: 'user',
        content: query,
      });

      setHasAppendedQuery(true);
      window.history.replaceState({}, '', `/chat/${id}`);
    }
  }, [query, append, hasAppendedQuery, id]);

  const { data: votes } = useSWR<Array<Vote>>(
    messages.length >= 2 ? `/api/vote?chatId=${id}` : null,
    fetcher,
  );

  const [attachments, setAttachments] = useState<Array<Attachment>>([]);
  const isArtifactVisible = useArtifactSelector((state) => state.isVisible);

  useAutoResume({
    autoResume,
    initialMessages,
    experimental_resume,
    data,
    setMessages,
  });

  return (
    <>
      <div className="flex flex-col min-w-0 h-dvh bg-background">
        <ChatHeader
          chatId={id}
          selectedModelId={agentModel}
          selectedVisibilityType={initialVisibilityType}
          isReadonly={isReadonly}
          session={session}
        />

        <Messages
          chatId={id}
          status={status}
          votes={votes}
          messages={messages}
          setMessages={setMessages}
          reload={reload}
          isReadonly={isReadonly}
          isArtifactVisible={isArtifactVisible}
        />

        <form className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
          {!isReadonly && (
            <MultimodalInput
              chatId={id}
              input={input}
              setInput={setInput}
              handleSubmit={handleSubmit}
              status={status}
              stop={stop}
              attachments={attachments}
              setAttachments={setAttachments}
              messages={messages}
              setMessages={setMessages}
              append={append}
              selectedVisibilityType={visibilityType}
            />
          )}
        </form>
      </div>

      <Artifact
        chatId={id}
        input={input}
        setInput={setInput}
        handleSubmit={handleSubmit}
        status={status}
        stop={stop}
        attachments={attachments}
        setAttachments={setAttachments}
        append={append}
        messages={messages}
        setMessages={setMessages}
        reload={reload}
        votes={votes}
        isReadonly={isReadonly}
        selectedVisibilityType={visibilityType}
      />
    </>
  );
} 