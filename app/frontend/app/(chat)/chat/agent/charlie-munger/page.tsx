import { AgentChat } from '@/components/agent-chat';

const charlieMungerData = {
  name: 'Charlie Munger',
  description: 'Philosopher investor focused on mental models, quality businesses, and long-term thinking',
  expertise: ['Mental Models', 'Business Moats', 'Predictability', 'Psychology', 'Decision Making'],
  icon: '🧠'
};

export default function CharlieMungerChatPage() {
  return (
    <div className="h-screen flex flex-col">
      <AgentChat 
        agentId="charlie_munger" 
        agentData={charlieMungerData}
      />
    </div>
  );
} 