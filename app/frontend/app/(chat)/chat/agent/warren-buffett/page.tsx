import { Chat } from '@/components/chat';
import type { Session } from 'next-auth';
import { auth } from '../../../../(auth)/auth';
import { generateUUID } from '@/lib/utils';

export default async function WarrenBuffettChatPage() {
  const session = await auth() as Session;
  const id = generateUUID();

  // Start with empty messages so the greeting shows
  const initialMessages: any[] = [];

  return (
    <Chat
      id={id}
      initialMessages={initialMessages}
      initialChatModel="gpt-4o"
      initialVisibilityType="private"
      isReadonly={false}
      session={session}
      autoResume={false}
    />
  );
} 