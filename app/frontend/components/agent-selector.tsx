'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useSidebar } from '@/components/ui/sidebar';
import { ChevronDown } from 'lucide-react';
import { useState } from 'react';

interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  expertise: string[];
  available: boolean;
}

// These agents have been implemented with chat interfaces
const AVAILABLE_AGENTS = [
  'warren-buffett',
  'peter-lynch',
  'charlie-munger',
  'ben-graham',
  'technical-analyst'
];

const AGENTS: Agent[] = [
  // Available Famous Investors
  {
    id: 'warren-buffett',
    name: 'Warren Buffett',
    description: 'Value investing & fundamentals',
    icon: '🎩',
    expertise: ['Value Investing', 'Fundamentals', 'Competitive Moats'],
    available: true
  },
  {
    id: 'peter-lynch',
    name: 'Peter Lynch', 
    description: 'Growth investing & PEG analysis',
    icon: '📈',
    expertise: ['Growth Investing', 'PEG Ratio', 'Consumer Trends'],
    available: true
  },
  {
    id: 'charlie-munger',
    name: 'Charlie Munger',
    description: 'Mental models & quality businesses',
    icon: '🧠',
    expertise: ['Mental Models', 'Business Moats', 'Predictability'],
    available: true
  },
  {
    id: 'ben-graham',
    name: 'Ben Graham',
    description: 'Deep value & margin of safety',
    icon: '📚',
    expertise: ['Margin of Safety', 'Intrinsic Value', 'Financial Strength'],
    available: true
  },
  // Available Analytical Agent
  {
    id: 'technical-analyst',
    name: 'Technical Analyst',
    description: 'Chart patterns & technical indicators',
    icon: '📊',
    expertise: ['Chart Analysis', 'Technical Indicators', 'Price Patterns'],
    available: true
  },
  // Coming Soon - Famous Investors
  {
    id: 'michael-burry',
    name: 'Michael Burry',
    description: 'Contrarian value & market inefficiencies',
    icon: '🔍',
    expertise: ['Contrarian Investing', 'Deep Value', 'Market Bubbles'],
    available: false
  },
  {
    id: 'bill-ackman',
    name: 'Bill Ackman',
    description: 'Activist investing & operational improvement',
    icon: '📢',
    expertise: ['Activist Investing', 'Corporate Governance', 'Operational Fixes'],
    available: false
  },
  {
    id: 'cathie-wood',
    name: 'Cathie Wood',
    description: 'Disruptive innovation & technology',
    icon: '🚀',
    expertise: ['Innovation', 'Disruptive Tech', 'Exponential Growth'],
    available: false
  },
  {
    id: 'phil-fisher',
    name: 'Phil Fisher',
    description: 'Quality growth & scuttlebutt method',
    icon: '🔬',
    expertise: ['Quality Growth', 'Management Quality', 'Research Methods'],
    available: false
  },
  {
    id: 'stanley-druckenmiller',
    name: 'Stanley Druckenmiller',
    description: 'Macro trading & market timing',
    icon: '⏰',
    expertise: ['Macro Trading', 'Market Timing', 'Risk/Reward'],
    available: false
  },
  {
    id: 'aswath-damodaran',
    name: 'Aswath Damodaran',
    description: 'Academic valuation & story vs numbers',
    icon: '🎓',
    expertise: ['Valuation Models', 'Academic Rigor', 'Story vs Numbers'],
    available: false
  },
  // Coming Soon - Analytical Agents
  {
    id: 'fundamentals-analyst',
    name: 'Fundamentals Analyst',
    description: 'Financial analysis & business metrics',
    icon: '💼',
    expertise: ['Financial Analysis', 'Profitability', 'Growth Metrics'],
    available: false
  },
  {
    id: 'sentiment-analyst',
    name: 'Sentiment Analyst',
    description: 'Market psychology & insider activity',
    icon: '🎭',
    expertise: ['Market Sentiment', 'Insider Trading', 'News Analysis'],
    available: false
  },
  {
    id: 'valuation-analyst',
    name: 'Valuation Analyst',
    description: 'Multiple valuation models & fair value',
    icon: '🧮',
    expertise: ['DCF Analysis', 'Relative Valuation', 'Price Targets'],
    available: false
  },
  // Coming Soon - Multi-Agent
  {
    id: 'hedge-fund',
    name: 'Multi-Agent Analysis',
    description: 'Comprehensive portfolio analysis',
    icon: '🏛️',
    expertise: ['Portfolio Analysis', 'Risk Management', 'Asset Allocation'],
    available: false
  },
  {
    id: 'portfolio-manager',
    name: 'Portfolio Manager',
    description: 'Portfolio optimization & rebalancing',
    icon: '⚖️',
    expertise: ['Portfolio Optimization', 'Risk Assessment', 'Rebalancing'],
    available: false
  }
];

export function AgentSelector() {
  const router = useRouter();
  const { setOpenMobile } = useSidebar();
  const [showComingSoon, setShowComingSoon] = useState(false);

  const handleAgentSelect = (agentId: string, available: boolean) => {
    if (!available) return;
    setOpenMobile(false);
    router.push(`/chat/agent/${agentId}`);
  };

  const availableAgents = AGENTS.filter(agent => agent.available);
  const comingSoonAgents = AGENTS.filter(agent => !agent.available);

  return (
    <div className="space-y-3">
      {/* Available Agents Section */}
      <div className="space-y-1">
        {/* <h3 className="text-xs font-medium text-muted-foreground px-3 mb-2">
          Available Agents
        </h3> */}
        {availableAgents.map((agent) => (
          <Card 
            key={agent.id} 
            className="cursor-pointer hover:bg-muted/50 transition-colors border-0 bg-transparent"
            onClick={() => handleAgentSelect(agent.id, agent.available)}
          >
            <CardContent className="p-3">
              <div className="flex items-start gap-3">
                <div className="text-2xl">{agent.icon}</div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm leading-tight">
                    {agent.name}
                  </h4>
                  <p className="text-xs text-muted-foreground mt-1">
                    {agent.description}
                  </p>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {agent.expertise.slice(0, 2).map((skill) => (
                      <span 
                        key={skill}
                        className="text-xs bg-muted px-1.5 py-0.5 rounded text-muted-foreground"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Coming Soon Section */}
      <div className="border-t pt-3">
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-between px-3 h-8"
          onClick={() => setShowComingSoon(!showComingSoon)}
        >
          <span className="text-xs font-medium text-muted-foreground">
            Coming Soon ({comingSoonAgents.length})
          </span>
          <ChevronDown 
            className={`h-3 w-3 transition-transform ${
              showComingSoon ? 'rotate-180' : ''
            }`}
          />
        </Button>
        
        {showComingSoon && (
          <div className="mt-2 space-y-1">
            {comingSoonAgents.map((agent) => (
              <Card 
                key={agent.id} 
                className="opacity-50 cursor-not-allowed border-0 bg-transparent"
              >
                <CardContent className="p-3">
                  <div className="flex items-start gap-3">
                    <div className="text-2xl grayscale">{agent.icon}</div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-sm leading-tight text-muted-foreground">
                        {agent.name}
                      </h4>
                      <p className="text-xs text-muted-foreground/70 mt-1">
                        {agent.description}
                      </p>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {agent.expertise.slice(0, 2).map((skill) => (
                          <span 
                            key={skill}
                            className="text-xs bg-muted/50 px-1.5 py-0.5 rounded text-muted-foreground/70"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 