'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useSidebar } from '@/components/ui/sidebar';

interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  expertise: string[];
}

const AGENTS: Agent[] = [
  // Famous Investors
  {
    id: 'warren-buffett',
    name: 'Warren Buffett',
    description: 'Value investing & fundamentals',
    icon: '🎩',
    expertise: ['Value Investing', 'Fundamentals', 'Competitive Moats']
  },
  {
    id: 'charlie-munger',
    name: 'Charlie Munger',
    description: 'Mental models & quality businesses',
    icon: '🧠',
    expertise: ['Mental Models', 'Business Moats', 'Predictability']
  },
  {
    id: 'peter-lynch',
    name: 'Peter Lynch', 
    description: 'Growth investing & PEG analysis',
    icon: '📈',
    expertise: ['Growth Investing', 'PEG Ratio', 'Consumer Trends']
  },
  {
    id: 'ben-graham',
    name: 'Ben Graham',
    description: 'Deep value & margin of safety',
    icon: '📚',
    expertise: ['Margin of Safety', 'Intrinsic Value', 'Financial Strength']
  },
  {
    id: 'michael-burry',
    name: 'Michael Burry',
    description: 'Contrarian value & market inefficiencies',
    icon: '🔍',
    expertise: ['Contrarian Investing', 'Deep Value', 'Market Bubbles']
  },
  {
    id: 'bill-ackman',
    name: 'Bill Ackman',
    description: 'Activist investing & operational improvement',
    icon: '📢',
    expertise: ['Activist Investing', 'Corporate Governance', 'Operational Fixes']
  },
  {
    id: 'cathie-wood',
    name: 'Cathie Wood',
    description: 'Disruptive innovation & technology',
    icon: '🚀',
    expertise: ['Innovation', 'Disruptive Tech', 'Exponential Growth']
  },
  {
    id: 'phil-fisher',
    name: 'Phil Fisher',
    description: 'Quality growth & scuttlebutt method',
    icon: '🔬',
    expertise: ['Quality Growth', 'Management Quality', 'Research Methods']
  },
  {
    id: 'stanley-druckenmiller',
    name: 'Stanley Druckenmiller',
    description: 'Macro trading & market timing',
    icon: '⏰',
    expertise: ['Macro Trading', 'Market Timing', 'Risk/Reward']
  },
  {
    id: 'aswath-damodaran',
    name: 'Aswath Damodaran',
    description: 'Academic valuation & story vs numbers',
    icon: '🎓',
    expertise: ['Valuation Models', 'Academic Rigor', 'Story vs Numbers']
  },
  // Analytical Agents
  {
    id: 'technical-analyst',
    name: 'Technical Analyst',
    description: 'Chart patterns & technical indicators',
    icon: '📊',
    expertise: ['Chart Analysis', 'Technical Indicators', 'Price Patterns']
  },
  {
    id: 'fundamentals-analyst',
    name: 'Fundamentals Analyst',
    description: 'Financial analysis & business metrics',
    icon: '💼',
    expertise: ['Financial Analysis', 'Profitability', 'Growth Metrics']
  },
  {
    id: 'sentiment-analyst',
    name: 'Sentiment Analyst',
    description: 'Market psychology & insider activity',
    icon: '🎭',
    expertise: ['Market Sentiment', 'Insider Trading', 'News Analysis']
  },
  {
    id: 'valuation-analyst',
    name: 'Valuation Analyst',
    description: 'Multiple valuation models & fair value',
    icon: '🧮',
    expertise: ['DCF Analysis', 'Relative Valuation', 'Price Targets']
  },
  // Multi-Agent
  {
    id: 'hedge-fund',
    name: 'Multi-Agent Analysis',
    description: 'Comprehensive portfolio analysis',
    icon: '🏛️',
    expertise: ['Portfolio Analysis', 'Risk Management', 'Asset Allocation']
  },
  {
    id: 'portfolio-manager',
    name: 'Portfolio Manager',
    description: 'Portfolio optimization & rebalancing',
    icon: '⚖️',
    expertise: ['Portfolio Optimization', 'Risk Assessment', 'Rebalancing']
  }
];

export function AgentSelector() {
  const router = useRouter();
  const { setOpenMobile } = useSidebar();

  const handleAgentSelect = (agentId: string) => {
    setOpenMobile(false);
    router.push(`/chat/agent/${agentId}`);
  };

  return (
    <div className="space-y-3">
      {AGENTS.map((agent) => (
        <Card 
          key={agent.id} 
          className="cursor-pointer hover:bg-muted/50 transition-colors border-0 bg-transparent"
          onClick={() => handleAgentSelect(agent.id)}
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
  );
} 