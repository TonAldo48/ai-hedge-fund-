import { AgentChatUI } from '@/components/agent-chat-ui';

const agentData = {
  name: 'Ben Graham',
  description: 'Father of value investing and margin of safety principles',
  expertise: ['Value Investing', 'Margin of Safety', 'Fundamental Analysis', 'Conservative Investing'],
  icon: '📊',
};

export default function BenGrahamPage() {
  return <AgentChatUI agentId="ben_graham" agentData={agentData} />;
}
