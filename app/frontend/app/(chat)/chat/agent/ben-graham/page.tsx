import { AgentChat } from '@/components/agent-chat';

const benGrahamData = {
  name: 'Ben Graham',
  description: 'The father of value investing, focused on margin of safety and intrinsic value',
  expertise: ['Margin of Safety', 'Intrinsic Value', 'Financial Strength', 'Risk Management', 'Value Investing'],
  icon: '📚'
};

export default function BenGrahamChatPage() {
  return (
    <div className="h-screen flex flex-col">
      <AgentChat 
        agentId="ben_graham" 
        agentData={benGrahamData}
      />
    </div>
  );
}
