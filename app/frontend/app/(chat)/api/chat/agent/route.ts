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
  getChatById,
  getMessageCountByUserId,
  getMessagesByChatId,
  saveChat,
  saveMessages,
} from '@/lib/db/queries';
import { generateUUID, getTrailingMessageId } from '@/lib/utils';
import { generateTitleFromUserMessage } from '../../../actions';
import { isProductionEnvironment } from '@/lib/constants';
import { entitlementsByUserType } from '@/lib/ai/entitlements';
import { z } from 'zod';
import { geolocation } from '@vercel/functions';
import {
  createResumableStreamContext,
  type ResumableStreamContext,
} from 'resumable-stream';
import { after } from 'next/server';
import { ChatSDKError } from '@/lib/errors';

export const maxDuration = 60;

const requestSchema = z.object({
  id: z.string(),
  message: z.object({
    id: z.string(),
    role: z.enum(['user', 'assistant']),
    content: z.string(),
    parts: z.array(z.any()).optional(),
    experimental_attachments: z.array(z.any()).optional(),
  }),
  selectedChatModel: z.string(),
  selectedVisibilityType: z.enum(['private', 'public']),
  agentType: z.enum([
    'warren-buffett', 'peter-lynch', 'charlie-munger', 'ben-graham', 'technical-analyst',
    'michael-burry', 'bill-ackman', 'cathie-wood', 'phil-fisher', 'stanley-druckenmiller',
    'aswath-damodaran', 'fundamentals-analyst', 'sentiment-analyst', 'valuation-analyst',
    'hedge-fund', 'portfolio-manager'
  ]),
});

// Map frontend agent types to backend API names
const AGENT_API_MAPPING: Record<string, string> = {
  'warren-buffett': 'warren_buffett',
  'peter-lynch': 'peter_lynch',
  'charlie-munger': 'charlie_munger',
  'ben-graham': 'ben_graham',
  'technical-analyst': 'technical_analyst',
  // Add more mappings as backend supports them
};

export async function POST(request: Request) {
  let requestBody: z.infer<typeof requestSchema>;

  try {
    const json = await request.json();
    requestBody = requestSchema.parse(json);
  } catch (_) {
    return new ChatSDKError('bad_request:api').toResponse();
  }

  try {
    const { id, message, selectedChatModel, selectedVisibilityType, agentType } = requestBody;

    const session = await auth();

    if (!session?.user) {
      return new ChatSDKError('unauthorized:chat').toResponse();
    }

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
        agentType: agentType as any,
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

    await saveMessages({
      messages: [
        {
          chatId: id,
          id: message.id,
          role: 'user',
          parts: message.parts || [],
          attachments: message.experimental_attachments ?? [],
          createdAt: new Date(),
        },
      ],
    });

    const streamId = generateUUID();
    await createStreamId({ streamId, chatId: id });

    // Get the backend API agent name
    const backendAgentName = AGENT_API_MAPPING[agentType];
    
    if (!backendAgentName) {
      return new ChatSDKError('bad_request:api', `Agent ${agentType} not yet supported`).toResponse();
    }

    const stream = createDataStream({
      execute: async (dataStream) => {
        try {
          // Call the backend agent API using the memory-stored API key
          const apiKey = 'Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw';
          const backendUrl = 'http://localhost:8000';
          
          const response = await fetch(`${backendUrl}/api/agents/${backendAgentName}/analyze-streaming`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${apiKey}`,
            },
            body: JSON.stringify({
              query: message.content,
              chat_history: previousMessages.map(msg => ({
                role: msg.role,
                content: typeof msg.parts === 'string' ? msg.parts : JSON.stringify(msg.parts),
              })),
            }),
          });

          if (!response.ok) {
            throw new Error(`Backend error: ${response.status}`);
          }

          const reader = response.body?.getReader();
          if (!reader) {
            throw new Error('No response body');
          }

          const decoder = new TextDecoder();
          let assistantMessage = '';
          let assistantId = generateUUID();

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') continue;

                try {
                  const event = JSON.parse(data);
                  
                  if (event.type === 'step') {
                    // Send reasoning step
                    dataStream.writeData({
                      type: 'reasoning',
                      content: event.content || event.description || '',
                    });
                  } else if (event.type === 'final_response' || event.type === 'response') {
                    // Accumulate the assistant message
                    assistantMessage = event.content || '';
                    
                    // Send the message chunk
                    dataStream.writeData({
                      type: 'text-delta',
                      textDelta: assistantMessage,
                    });
                  } else if (event.type === 'content') {
                    // Handle streaming content
                    dataStream.writeData({
                      type: 'text-delta',
                      textDelta: event.content || '',
                    });
                    assistantMessage += event.content || '';
                  }
                } catch (e) {
                  console.error('Error parsing event:', e);
                }
              }
            }
          }

          // Save the assistant message
          if (assistantMessage) {
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
          console.error('Agent API error:', error);
          dataStream.writeData({
            type: 'error',
            error: 'Failed to get response from agent',
          });
        }
      },
      onError: () => {
        return 'Oops, an error occurred!';
      },
    });

    return new Response(stream);
  } catch (error) {
    if (error instanceof ChatSDKError) {
      return error.toResponse();
    }
    
    return new ChatSDKError('bad_request:api', 'Failed to process request').toResponse();
  }
} 