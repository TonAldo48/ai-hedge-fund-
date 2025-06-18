import { AgentChatUI } from '@/components/agent-chat-ui';

const agentData = {
  name: 'Warren Buffett',
  description: 'Value investing sage focused on economic moats and long-term growth',
  expertise: ['Value Investing', 'Economic Moats', 'Management Quality', 'Long-term Strategy'],
  icon: '🦉',
};

export default function WarrenBuffettPage() {
  return <AgentChatUI agentId="warren_buffett" agentData={agentData} />;
} 