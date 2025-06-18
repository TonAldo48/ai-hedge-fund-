import {
  createDataStream,
} from 'ai';
import { auth } from '@/app/(auth)/auth';
import { generateUUID } from '@/lib/utils';
import { 
  getChatById,
  saveChat,
  saveMessages,
  getMessagesByChatId,
  createStreamId,
} from '@/lib/db/queries';
import { generateTitleFromUserMessage } from '../../actions';
import { ChatSDKError } from '@/lib/errors';

export const maxDuration = 60;

interface WarrenBuffettRequest {
  id: string;
  message: {
    id: string;
    role: 'user';
    content: string;
    parts?: Array<{type: string; text: string}>;
    createdAt: Date;
  };
  selectedVisibilityType: 'private' | 'public';
}

// Main POST handler
export async function POST(request: Request) {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return new ChatSDKError('unauthorized:chat').toResponse();
    }

    const { id, message, selectedVisibilityType } = await request.json() as WarrenBuffettRequest;

    // Check if chat exists, create if not
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
      });
    } else {
      if (chat.userId !== session.user.id) {
        return new ChatSDKError('forbidden:chat').toResponse();
      }
    }

    // Get previous messages
    const previousMessages = await getMessagesByChatId({ id });

    // Save user message
    await saveMessages({
      messages: [
        {
          chatId: id,
          id: message.id,
          role: 'user',
          parts: [{ type: 'text', text: message.content }],
          attachments: [],
          createdAt: new Date(),
        },
      ],
    });

    // Create stream ID
    const streamId = generateUUID();
    await createStreamId({ streamId, chatId: id });

    // Stream the response from Warren Buffett backend
    const stream = createDataStream({
      execute: async (dataStream) => {
        try {
          // Call Warren Buffett backend
          const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
          
          const response = await fetch(`${backendUrl}/warren-buffett/analyze-streaming`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw',
            },
            body: JSON.stringify({
              query: message.content,
              chat_history: previousMessages.map(msg => ({
                role: msg.role,
                content: msg.parts?.[0]?.text || '',
                timestamp: msg.createdAt,
              })),
            }),
          });

          if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
          }

          const reader = response.body!.getReader();
          const decoder = new TextDecoder();
          let finalResponse = '';
          const assistantId = generateUUID();

          // Process Server-Sent Events
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  console.log('Received event:', data.type, data);
                  
                  if (data.type === 'agent_finish' || data.type === 'complete') {
                    // Extract the final response
                    finalResponse = data.data.output || data.data.response || '';
                    
                    // Append the complete message to the stream
                    dataStream.writeData({
                      type: 'append-message',
                      message: JSON.stringify({
                        id: assistantId,
                        role: 'assistant',
                        content: finalResponse,
                        createdAt: new Date().toISOString(),
                      }),
                    });
                    
                    // Save the assistant message
                    await saveMessages({
                      messages: [
                        {
                          id: assistantId,
                          chatId: id,
                          role: 'assistant',
                          parts: [{ type: 'text', text: finalResponse }],
                          attachments: [],
                          createdAt: new Date(),
                        },
                      ],
                    });
                  }
                } catch (e) {
                  console.error('Error parsing SSE data:', e);
                }
              }
            }
          }
        } catch (error) {
          console.error('Warren Buffett API error:', error);
          dataStream.writeData({
            type: 'error',
            error: error instanceof Error ? error.message : 'Unknown error occurred',
          });
        }
      },
      onError: () => {
        return 'Sorry, I encountered an error while analyzing. Please try again.';
      },
    });

    return new Response(stream);
  } catch (error) {
    if (error instanceof ChatSDKError) {
      return error.toResponse();
    }
    return new Response('Internal Server Error', { status: 500 });
  }
} 