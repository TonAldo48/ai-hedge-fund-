import { auth } from '@/app/(auth)/auth';
import { saveChat } from '@/lib/db/queries';
import { ChatSDKError } from '@/lib/errors';
import { z } from 'zod';

const requestSchema = z.object({
  id: z.string(),
  agentType: z.enum([
    'warren-buffett', 'peter-lynch', 'charlie-munger', 'ben-graham', 'technical-analyst',
    'michael-burry', 'bill-ackman', 'cathie-wood', 'phil-fisher', 'stanley-druckenmiller',
    'aswath-damodaran', 'fundamentals-analyst', 'sentiment-analyst', 'valuation-analyst',
    'hedge-fund', 'portfolio-manager'
  ]),
  userId: z.string(),
  visibility: z.enum(['private', 'public']).optional().default('private'),
});

export async function POST(request: Request) {
  try {
    const session = await auth();

    if (!session?.user) {
      return new ChatSDKError('unauthorized:chat').toResponse();
    }

    const json = await request.json();
    const body = requestSchema.parse(json);

    // Verify the userId matches the session
    if (body.userId !== session.user.id) {
      return new ChatSDKError('forbidden:chat').toResponse();
    }

    // Generate a title based on the agent type
    const agentTitles: Record<string, string> = {
      'warren-buffett': 'Warren Buffett Investment Analysis',
      'peter-lynch': 'Peter Lynch Growth Investing',
      'charlie-munger': 'Charlie Munger Business Analysis',
      'ben-graham': 'Ben Graham Value Investing',
      'technical-analyst': 'Technical Analysis',
      'michael-burry': 'Michael Burry Deep Value',
      'bill-ackman': 'Bill Ackman Activist Investing',
      'cathie-wood': 'Cathie Wood Innovation Investing',
      'phil-fisher': 'Phil Fisher Quality Growth',
      'stanley-druckenmiller': 'Stanley Druckenmiller Macro Trading',
      'aswath-damodaran': 'Aswath Damodaran Valuation',
      'fundamentals-analyst': 'Fundamental Analysis',
      'sentiment-analyst': 'Market Sentiment Analysis',
      'valuation-analyst': 'Valuation Analysis',
      'hedge-fund': 'Multi-Agent Hedge Fund Analysis',
      'portfolio-manager': 'Portfolio Management',
    };

    const title = agentTitles[body.agentType] || 'Investment Analysis';

    await saveChat({
      id: body.id,
      userId: session.user.id,
      title,
      visibility: body.visibility,
      agentType: body.agentType as any, // Cast to match the expected type
    });

    return Response.json({ success: true });
  } catch (error) {
    console.error('Error initializing agent chat:', error);
    
    if (error instanceof z.ZodError) {
      return new ChatSDKError('bad_request:api').toResponse();
    }
    
    if (error instanceof ChatSDKError) {
      return error.toResponse();
    }

    return new ChatSDKError('bad_request:database', 'Failed to initialize agent chat').toResponse();
  }
} 