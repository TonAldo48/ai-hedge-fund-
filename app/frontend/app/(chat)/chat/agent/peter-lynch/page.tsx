import { AgentChatUI } from '@/components/agent-chat-ui';

const agentData = {
  name: 'Peter Lynch',
  description: 'Growth at a reasonable price (GARP) investing expert',
  expertise: ['Growth Stocks', 'PEG Ratio', 'Retail Investing', 'Ten-Baggers'],
  icon: '📈',
};

export default function PeterLynchPage() {
  return <AgentChatUI agentId="peter_lynch" agentData={agentData} />;
} 