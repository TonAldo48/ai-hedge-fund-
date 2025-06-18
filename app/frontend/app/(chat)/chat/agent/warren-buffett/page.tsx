import { AgentChat } from '@/components/agent-chat';

const warrenBuffettData = {
  name: 'Warren Buffett',
  description: 'Value investing legend focused on fundamental analysis and long-term wealth creation',
  expertise: ['Value Investing', 'Fundamental Analysis', 'Competitive Moats', 'Capital Allocation', 'Long-term Thinking'],
  icon: '🎩'
};

export default function WarrenBuffettChatPage() {
  return (
    <div className="h-screen flex flex-col">
      <AgentChat 
        agentId="warren_buffett" 
        agentData={warrenBuffettData}
      />
    </div>
  );
} 