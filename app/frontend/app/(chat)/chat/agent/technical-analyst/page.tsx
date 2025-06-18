import { AgentChatUI } from '@/components/agent-chat-ui';

const agentData = {
  name: 'Technical Analyst',
  description: 'Chart patterns and technical indicators expert',
  expertise: ['Chart Analysis', 'Technical Indicators', 'Support/Resistance', 'Trading Patterns'],
  icon: '📉',
};

export default function TechnicalAnalystPage() {
  return <AgentChatUI agentId="technical_analyst" agentData={agentData} />;
}
