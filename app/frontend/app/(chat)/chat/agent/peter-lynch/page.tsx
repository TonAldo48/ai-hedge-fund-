import { AgentChat } from '@/components/agent-chat';

const peterLynchData = {
  name: 'Peter Lynch',
  description: 'Growth investing expert known for finding "tenbaggers" and investing in what you know',
  expertise: ['Growth Investing', 'PEG Ratio Analysis', 'Consumer Trends', 'Company Research', 'Market Psychology'],
  icon: '📈'
};

export default function PeterLynchChatPage() {
  return (
    <div className="h-screen flex flex-col">
      <AgentChat 
        agentId="peter_lynch" 
        agentData={peterLynchData}
      />
    </div>
  );
} 