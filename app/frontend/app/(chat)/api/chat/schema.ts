import { z } from 'zod';

const textPartSchema = z.object({
  text: z.string().min(1).max(2000),
  type: z.enum(['text']),
});

export const postRequestBodySchema = z.object({
  id: z.string(),
  message: z.any(),
  selectedChatModel: z.string(),
  selectedVisibilityType: z.enum(['public', 'private']),
  agentId: z.string().optional(),
});

export type PostRequestBody = z.infer<typeof postRequestBodySchema>;
