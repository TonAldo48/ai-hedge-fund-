import { AgentChatUI } from '@/components/agent-chat-ui';

const agentData = {
  name: 'Charlie Munger',
  description: 'Mental models and quality business advocate',
  expertise: ['Mental Models', 'Quality Businesses', 'Psychology', 'Long-term Thinking'],
  icon: '🧠',
};

export default function CharlieMungerPage() {
  return <AgentChatUI agentId="charlie_munger" agentData={agentData} />;
} 