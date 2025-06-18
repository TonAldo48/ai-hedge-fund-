// @ts-nocheck
// @ts-ignore – external "ai" SDK may not ship type declarations in the monorepo
import {
  customProvider,
  extractReasoningMiddleware,
  wrapLanguageModel,
} from 'ai';
// @ts-ignore – external "@ai-sdk/xai" SDK may not ship type declarations in the monorepo
import { xai } from '@ai-sdk/xai';
import { isTestEnvironment } from '../constants';
import {
  artifactModel,
  chatModel,
  reasoningModel,
  titleModel,
} from './models.test';

export const myProvider = isTestEnvironment
  ? customProvider({
      languageModels: {
        'chat-model': chatModel,
        'chat-model-reasoning': reasoningModel,
        'title-model': titleModel,
        'artifact-model': artifactModel,
      },
    })
  : customProvider({
      languageModels: {
        'chat-model': xai('grok-2-vision-1212'),
        'chat-model-reasoning': wrapLanguageModel({
          model: xai('grok-3-mini-beta'),
          middleware: extractReasoningMiddleware({ tagName: 'think' }),
        }),
        'title-model': xai('grok-2-1212'),
        'artifact-model': xai('grok-2-1212'),
      },
      imageModels: {
        'small-model': xai.image('grok-2-image'),
      },
    });

// Helper function to extract text from prompt messages
function extractTextFromPrompt(prompt: any): string {
  // This variant of the provider is only used in the experimental `frontend` package.
  // We do not rely on it for hedge-fund agent queries, but we still need a valid
  // implementation to satisfy the type checker.
  if (typeof prompt === 'string') return prompt;
  if (prompt?.type === 'messages' && Array.isArray(prompt.messages)) {
    const last = prompt.messages[prompt.messages.length - 1];
    if (typeof last?.content === 'string') return last.content;
  }
  return '';
}
