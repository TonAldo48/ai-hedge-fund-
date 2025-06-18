import { AgentChat } from '@/components/agent-chat';

const technicalAnalystData = {
  name: 'Technical Analyst',
  description: 'Chart and technical pattern expert focused on price action and market indicators',
  expertise: ['Chart Patterns', 'Technical Indicators', 'Trend Analysis', 'Support/Resistance', 'Volume Analysis'],
  icon: '📊'
};

export default function TechnicalAnalystChatPage() {
  return (
    <div className="h-screen flex flex-col">
      <AgentChat 
        agentId="technical_analyst" 
        agentData={technicalAnalystData}
      />
    </div>
  );
}
