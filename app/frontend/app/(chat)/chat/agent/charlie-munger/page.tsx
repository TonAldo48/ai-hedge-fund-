import { AgentChat } from '@/components/agent-chat';
import type { Session } from 'next-auth';
import { auth } from '../../../../(auth)/auth';
import { generateUUID } from '@/lib/utils';

export default async function CharlieMungerChatPage() {
  const session = await auth() as Session;
  const id = generateUUID();

  // Start with empty messages so the greeting shows
  const initialMessages: any[] = [];

  return (
    <AgentChat
      id={id}
      agentType="charlie-munger"
      initialMessages={initialMessages}
      initialVisibilityType="private"
      isReadonly={false}
      session={session}
      autoResume={false}
    />
  );
} 