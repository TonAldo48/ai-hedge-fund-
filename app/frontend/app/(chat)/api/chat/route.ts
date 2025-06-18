import {
  appendClientMessage,
  appendResponseMessages,
  createDataStream,
  smoothStream,
  streamText,
} from 'ai';
import { auth, type UserType } from '@/app/(auth)/auth';
import { type RequestHints, systemPrompt } from '@/lib/ai/prompts';
import {
  createStreamId,
  deleteChatById,
  getChatById,
  getMessageCountByUserId,
  getMessagesByChatId,
  getStreamIdsByChatId,
  saveChat,
  saveMessages,
} from '@/lib/db/queries';
import { generateUUID, getTrailingMessageId } from '@/lib/utils';
import { generateTitleFromUserMessage } from '../../actions';
import { createDocument } from '@/lib/ai/tools/create-document';
import { updateDocument } from '@/lib/ai/tools/update-document';
import { requestSuggestions } from '@/lib/ai/tools/request-suggestions';
import { getWeather } from '@/lib/ai/tools/get-weather';
import { isProductionEnvironment } from '@/lib/constants';
import { myProvider } from '@/lib/ai/providers';
import { entitlementsByUserType } from '@/lib/ai/entitlements';
import { postRequestBodySchema, type PostRequestBody } from './schema';
import { geolocation } from '@vercel/functions';
import {
  createResumableStreamContext,
  type ResumableStreamContext,
} from 'resumable-stream';
import { after } from 'next/server';
import type { Chat } from '@/lib/db/schema';
import { differenceInSeconds } from 'date-fns';
import { ChatSDKError } from '@/lib/errors';

export const maxDuration = 60;

let globalStreamContext: ResumableStreamContext | null = null;

function getStreamContext() {
  if (!globalStreamContext) {
    try {
      globalStreamContext = createResumableStreamContext({
        waitUntil: after,
      });
    } catch (error: any) {
      if (error.message.includes('REDIS_URL')) {
        console.log(
          ' > Resumable streams are disabled due to missing REDIS_URL',
        );
      } else {
        console.error(error);
      }
    }
  }

  return globalStreamContext;
}

export async function POST(request: Request) {
  let requestBody: PostRequestBody;

  try {
    const json = await request.json();
    requestBody = postRequestBodySchema.parse(json);
  } catch (_) {
    return new ChatSDKError('bad_request:api').toResponse();
  }

  try {
    const { id, message, selectedChatModel, selectedVisibilityType, agentId } =
      requestBody;

    const session = await auth();

    if (!session?.user) {
      return new ChatSDKError('unauthorized:chat').toResponse();
    }

    // If agentId is provided, route to the backend agent API
    if (agentId) {
      try {
        // Ensure chat exists
        const chat = await getChatById({ id });
        if (!chat) {
          const title = `Chat with ${agentId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`;
          
          // Map agentId to agentType
          const agentTypeMap: Record<string, any> = {
            'warren_buffett': 'warren-buffett',
            'peter_lynch': 'peter-lynch',
            'charlie_munger': 'charlie-munger',
            'ben_graham': 'ben-graham',
            'technical_analyst': 'technical-analyst'
          };
          
          await saveChat({
            id,
            userId: session.user.id,
            title,
            visibility: selectedVisibilityType,
            agentType: agentTypeMap[agentId] || 'general',
          });
        }

        // Get previous messages for context
        const previousMessages = await getMessagesByChatId({ id });
        
        // Extract message content properly
        const messageContent = typeof message.content === 'string' 
          ? message.content 
          : message.parts?.[0]?.text || '';
        
        // Save the user message first
        await saveMessages({
          messages: [
            {
              chatId: id,
              id: message.id,
              role: 'user',
              parts: message.parts || [{ type: 'text', text: messageContent }],
              attachments: message.experimental_attachments ?? [],
              createdAt: new Date(),
            },
          ],
        });
        
        // Call the backend agent API with streaming
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const apiKey = process.env.API_KEY || 'Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw';
        
        console.log(`Calling agent API: ${backendUrl}/api/agents/${agentId}/analyze-streaming`);
        
        const response = await fetch(`${backendUrl}/api/agents/${agentId}/analyze-streaming`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`,
            'Accept': 'text/event-stream',
          },
          body: JSON.stringify({
            message: messageContent,
            chat_history: previousMessages.map((msg: any) => ({
              role: msg.role,
              content: msg.content || msg.parts?.[0]?.text || '',
            })).slice(-10), // Send last 10 messages for context
          }),
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error(`Backend API error: ${response.status} ${response.statusText}`, errorText);
          throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
        }

        // Create a data stream that processes the backend SSE response
        const stream = createDataStream({
          execute: async (dataStream) => {
            const reader = response.body?.getReader();
            const decoder = new TextDecoder();
            
            if (!reader) {
              throw new Error('No response body');
            }

            let assistantId = generateUUID();
            let assistantMessage = '';
            let buffer = '';
            let messageStarted = false;

            try {
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
                      
                      // Handle different event types from our adapter
                      if (event.type === 'message-start') {
                        assistantId = event.id || generateUUID();
                        messageStarted = true;
                        // Forward the event to the client
                        dataStream.writeData(event);
                      } else if (event.type === 'text-delta') {
                        assistantMessage += event.textDelta;
                        // Forward the event to the client
                        dataStream.writeData(event);
                      } else if (event.type === 'message-end') {
                        // Forward the event to the client
                        dataStream.writeData(event);
                      } else if (event.type === 'error') {
                        // Forward error events
                        dataStream.writeData(event);
                      } else {
                        // Forward any other events (tool calls, etc.)
                        dataStream.writeData(event);
                      }
                    } catch (e) {
                      console.error('Error parsing SSE data:', data, e);
                    }
                  }
                }
              }

              // Save the assistant message after streaming completes
              if (assistantMessage && messageStarted) {
                await saveMessages({
                  messages: [
                    {
                      id: assistantId,
                      chatId: id,
                      role: 'assistant',
                      parts: [{ type: 'text', text: assistantMessage }],
                      attachments: [],
                      createdAt: new Date(),
                    },
                  ],
                });
              }
            } catch (error) {
              console.error('Error processing stream:', error);
              throw error;
            }
          },
          onError: (error) => {
            console.error('Stream error:', error);
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            return `An error occurred while processing your request: ${errorMessage}. Please try again.`;
          },
        });

        return new Response(stream);
      } catch (error) {
        console.error('Agent API error:', error);
        return new ChatSDKError('offline:chat').toResponse();
      }
    }

    // Original flow for non-agent chats
    const userType: UserType = session.user.type;

    const messageCount = await getMessageCountByUserId({
      id: session.user.id,
      differenceInHours: 24,
    });

    if (messageCount > entitlementsByUserType[userType].maxMessagesPerDay) {
      return new ChatSDKError('rate_limit:chat').toResponse();
    }

    const chat = await getChatById({ id });

    if (!chat) {
      const title = await generateTitleFromUserMessage({
        message,
      });

      await saveChat({
        id,
        userId: session.user.id,
        title,
        visibility: selectedVisibilityType,
        agentType: 'general',
      });
    } else {
      if (chat.userId !== session.user.id) {
        return new ChatSDKError('forbidden:chat').toResponse();
      }
    }

    const previousMessages = await getMessagesByChatId({ id });

    const messages = appendClientMessage({
      // @ts-expect-error: todo add type conversion from DBMessage[] to UIMessage[]
      messages: previousMessages,
      message,
    });

    const { longitude, latitude, city, country } = geolocation(request);

    const requestHints: RequestHints = {
      longitude,
      latitude,
      city,
      country,
    };

    await saveMessages({
      messages: [
        {
          chatId: id,
          id: message.id,
          role: 'user',
          parts: message.parts,
          attachments: message.experimental_attachments ?? [],
          createdAt: new Date(),
        },
      ],
    });

    const streamId = generateUUID();
    await createStreamId({ streamId, chatId: id });

    const stream = createDataStream({
      execute: (dataStream) => {
        const result = streamText({
          model: myProvider.languageModel(selectedChatModel),
          system: systemPrompt({ selectedChatModel, requestHints }),
          messages,
          maxSteps: 5,
          experimental_activeTools:
            selectedChatModel === 'chat-model-reasoning'
              ? []
              : [
                  'getWeather',
                  'createDocument',
                  'updateDocument',
                  'requestSuggestions',
                ],
          experimental_transform: smoothStream({ chunking: 'word' }),
          experimental_generateMessageId: generateUUID,
          tools: {
            getWeather,
            createDocument: createDocument({ session, dataStream }),
            updateDocument: updateDocument({ session, dataStream }),
            requestSuggestions: requestSuggestions({
              session,
              dataStream,
            }),
          },
          onFinish: async ({ response }) => {
            if (session.user?.id) {
              try {
                const assistantId = getTrailingMessageId({
                  messages: response.messages.filter(
                    (message) => message.role === 'assistant',
                  ),
                });

                if (!assistantId) {
                  throw new Error('No assistant message found!');
                }

                const [, assistantMessage] = appendResponseMessages({
                  messages: [message],
                  responseMessages: response.messages,
                });

                await saveMessages({
                  messages: [
                    {
                      id: assistantId,
                      chatId: id,
                      role: assistantMessage.role,
                      parts: assistantMessage.parts,
                      attachments:
                        assistantMessage.experimental_attachments ?? [],
                      createdAt: new Date(),
                    },
                  ],
                });
              } catch (_) {
                console.error('Failed to save chat');
              }
            }
          },
          experimental_telemetry: {
            isEnabled: isProductionEnvironment,
            functionId: 'stream-text',
          },
        });

        result.consumeStream();

        result.mergeIntoDataStream(dataStream, {
          sendReasoning: true,
        });
      },
      onError: () => {
        return 'Oops, an error occurred!';
      },
    });

    const streamContext = getStreamContext();

    if (streamContext) {
      return new Response(
        await streamContext.resumableStream(streamId, () => stream),
      );
    } else {
      return new Response(stream);
    }
  } catch (error) {
    if (error instanceof ChatSDKError) {
      return error.toResponse();
    }
  }
}

export async function GET(request: Request) {
  const streamContext = getStreamContext();
  const resumeRequestedAt = new Date();

  if (!streamContext) {
    return new Response(null, { status: 204 });
  }

  const { searchParams } = new URL(request.url);
  const chatId = searchParams.get('chatId');

  if (!chatId) {
    return new ChatSDKError('bad_request:api').toResponse();
  }

  const session = await auth();

  if (!session?.user) {
    return new ChatSDKError('unauthorized:chat').toResponse();
  }

  let chat: Chat;

  try {
    chat = await getChatById({ id: chatId });
  } catch {
    return new ChatSDKError('not_found:chat').toResponse();
  }

  if (!chat) {
    return new ChatSDKError('not_found:chat').toResponse();
  }

  if (chat.visibility === 'private' && chat.userId !== session.user.id) {
    return new ChatSDKError('forbidden:chat').toResponse();
  }

  const streamIds = await getStreamIdsByChatId({ chatId });

  if (!streamIds.length) {
    return new ChatSDKError('not_found:stream').toResponse();
  }

  const recentStreamId = streamIds.at(-1);

  if (!recentStreamId) {
    return new ChatSDKError('not_found:stream').toResponse();
  }

  const emptyDataStream = createDataStream({
    execute: () => {},
  });

  const stream = await streamContext.resumableStream(
    recentStreamId,
    () => emptyDataStream,
  );

  /*
   * For when the generation is streaming during SSR
   * but the resumable stream has concluded at this point.
   */
  if (!stream) {
    const messages = await getMessagesByChatId({ id: chatId });
    const mostRecentMessage = messages.at(-1);

    if (!mostRecentMessage) {
      return new Response(emptyDataStream, { status: 200 });
    }

    if (mostRecentMessage.role !== 'assistant') {
      return new Response(emptyDataStream, { status: 200 });
    }

    const messageCreatedAt = new Date(mostRecentMessage.createdAt);

    if (differenceInSeconds(resumeRequestedAt, messageCreatedAt) > 15) {
      return new Response(emptyDataStream, { status: 200 });
    }

    const restoredStream = createDataStream({
      execute: (buffer) => {
        buffer.writeData({
          type: 'append-message',
          message: JSON.stringify(mostRecentMessage),
        });
      },
    });

    return new Response(restoredStream, { status: 200 });
  }

  return new Response(stream, { status: 200 });
}

export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');

  if (!id) {
    return new ChatSDKError('bad_request:api').toResponse();
  }

  const session = await auth();

  if (!session?.user) {
    return new ChatSDKError('unauthorized:chat').toResponse();
  }

  const chat = await getChatById({ id });

  if (chat.userId !== session.user.id) {
    return new ChatSDKError('forbidden:chat').toResponse();
  }

  const deletedChat = await deleteChatById({ id });

  return Response.json(deletedChat, { status: 200 });
}
