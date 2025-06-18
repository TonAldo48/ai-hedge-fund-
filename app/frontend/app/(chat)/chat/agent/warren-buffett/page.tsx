import { Chat } from '@/components/chat';
import type { Session } from 'next-auth';
import { auth } from '../../../../(auth)/auth';
import { generateUUID } from '@/lib/utils';
import { DataStreamHandler } from '@/components/data-stream-handler';

export default async function WarrenBuffettPage() {
  const session = await auth() as Session;
  const id = generateUUID();

  return (
    <>
      <Chat
        id={id}
        initialMessages={[]}
        initialChatModel="warren-buffett"
        initialVisibilityType="private"
        isReadonly={false}
        session={session}
        autoResume={false}
        agentId="warren_buffett"
      />
      <DataStreamHandler id={id} />
    </>
  );
} 