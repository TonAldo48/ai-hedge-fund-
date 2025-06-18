import { cookies } from 'next/headers';
import { notFound, redirect } from 'next/navigation';

import { auth } from '@/app/(auth)/auth';
import { Chat } from '@/components/chat';
import { getChatById, getMessagesByChatId } from '@/lib/db/queries';
import { DataStreamHandler } from '@/components/data-stream-handler';
import { DEFAULT_CHAT_MODEL } from '@/lib/ai/models';
import type { DBMessage } from '@/lib/db/schema';
import type { Attachment, UIMessage } from 'ai';
import type { Session } from 'next-auth';

export default async function Page(props: { params: Promise<{ id: string }> }) {
  const params = await props.params;
  const { id } = params;
  let chat: Awaited<ReturnType<typeof getChatById>> | null = null;

  try {
    chat = await getChatById({ id });
  } catch (error) {
    /*
     * A database error can occur here if the supplied ID is not a valid UUID or
     * the database connection is temporarily unavailable.  In that scenario we
     * fall back to treating the chat as a brand-new one so that the page still
     * renders and the first user message will create the chat record via the
     * /api/chat route.
     */
    chat = null;
  }

  const session = await auth();

  if (!session) {
    redirect('/api/auth/guest');
  }

  if (chat && chat.visibility === 'private') {
    if (!session.user) {
      return notFound();
    }

    if (session.user.id !== chat.userId) {
      return notFound();
    }
  }

  const messagesFromDb = chat ? await getMessagesByChatId({ id }) : [];

  function convertToUIMessages(messages: Array<DBMessage>): Array<UIMessage> {
    return messages.map((message) => ({
      id: message.id,
      parts: message.parts as UIMessage['parts'],
      role: message.role as UIMessage['role'],
      // Note: content will soon be deprecated in @ai-sdk/react
      content: '',
      createdAt: message.createdAt,
      experimental_attachments:
        (message.attachments as Array<Attachment>) ?? [],
    }));
  }

  // Determine the correct model based on agentType from database
  const getChatModel = () => {
    // If this is a Warren Buffett chat, always use warren-buffett model
    if (chat && chat.agentType === 'warren-buffett') {
      return 'warren-buffett';
    }
    
    // Retrieve cookie store (API is synchronous in current Next.js version).
    // Cast to any to avoid type issues across Next.js versions.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const cookieStore = cookies() as any;
    const chatModelFromCookie = cookieStore.get?.('chat-model');
    return chatModelFromCookie?.value || DEFAULT_CHAT_MODEL;
  };

  const chatModel = getChatModel();

  /*
   * If the chat does not exist yet we render the UI anyway (similar to the root
   * /chat page).  When the user sends the first message the API route will
   * create the corresponding database record.
   */
  if (!chat) {
    return (
      <>
        <Chat
          id={id}
          initialMessages={[]}
          initialChatModel={DEFAULT_CHAT_MODEL}
          initialVisibilityType="private"
          isReadonly={false}
          session={session as Session}
          autoResume={false}
        />
        <DataStreamHandler id={id} />
      </>
    );
  }

  return (
    <>
      <Chat
        id={chat.id}
        initialMessages={convertToUIMessages(messagesFromDb)}
        initialChatModel={chatModel}
        initialVisibilityType={chat.visibility}
        isReadonly={session?.user?.id !== chat.userId}
        session={session as Session}
        autoResume={true}
      />
      <DataStreamHandler id={id} />
    </>
  );
}
