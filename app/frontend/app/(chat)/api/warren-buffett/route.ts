import {
  createDataStream,
} from 'ai';
import { auth } from '@/app/(auth)/auth';
import { generateUUID } from '@/lib/utils';
import { 
  getChatById,
  saveChat,
  saveMessages,
  getMessagesByChatIdAndAgentType,
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
    parts: Array<{type: 'text'; text: string}>;
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
        agentType: 'warren-buffett',
      });
    } else {
      if (chat.userId !== session.user.id) {
        return new ChatSDKError('forbidden:chat').toResponse();
      }
      
      // Ensure this is a Warren Buffett chat
      if (chat.agentType !== 'warren-buffett') {
        return new ChatSDKError('bad_request:chat', 'Chat is not a Warren Buffett conversation').toResponse();
      }
    }

    // Get previous Warren Buffett messages only
    const previousMessages = await getMessagesByChatIdAndAgentType({ 
      id, 
      agentType: 'warren-buffett' 
    });
    
    console.log('Warren Buffett previous messages count:', previousMessages.length);
    console.log('Warren Buffett chat history being sent:', previousMessages.map(msg => ({
      role: msg.role,
      content: Array.isArray(msg.parts) && msg.parts.length > 0 && 'text' in msg.parts[0] 
        ? (msg.parts[0] as any).text?.substring(0, 50) + '...' 
        : '',
    })));

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
              'X-API-Key': 'Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw',
            },
            body: JSON.stringify({
              query: message.content,
              chat_history: previousMessages.map(msg => ({
                role: msg.role,
                content: Array.isArray(msg.parts) && msg.parts.length > 0 && 'text' in msg.parts[0]
                  ? (msg.parts[0] as any).text || ''
                  : '',
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
                    let finalResponse = data.data.output || data.data.response || '';
                    
                    // Clean up trailing markdown
                    if (finalResponse.endsWith('```')) {
                      finalResponse = finalResponse.slice(0, -3).trim();
                    }

                    // Append the complete message to the stream
                    dataStream.writeData({
                      type: 'append-message',
                      message: JSON.stringify({
                        id: assistantId,
                        role: 'assistant',
                        parts: [{ type: 'text', text: finalResponse }],
                        createdAt: new Date().toISOString(),
                      }),
                    });
                    
                    // Save the assistant message
                    try {
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
                    } catch (saveError) {
                      console.error('Failed to save Warren Buffett assistant message:', {
                        error: saveError,
                        assistantId,
                        chatId: id,
                        messageLength: finalResponse.length,
                      });
                      // Don't fail the whole response if save fails
                    }
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