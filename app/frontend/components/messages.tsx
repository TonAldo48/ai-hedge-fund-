import type { UIMessage } from 'ai';
import { PreviewMessage, ThinkingMessage } from './message';
import { Greeting } from './greeting';
import { AgentGreeting } from './agent-greeting';
import { memo } from 'react';
import type { Vote } from '@/lib/db/schema';
import equal from 'fast-deep-equal';
import type { UseChatHelpers } from '@ai-sdk/react';
import { motion } from 'framer-motion';
import { useMessages } from '@/hooks/use-messages';
import { usePathname } from 'next/navigation';

interface MessagesProps {
  chatId: string;
  status: UseChatHelpers['status'];
  votes: Array<Vote> | undefined;
  messages: Array<UIMessage>;
  setMessages: UseChatHelpers['setMessages'];
  reload: UseChatHelpers['reload'];
  isReadonly: boolean;
  isArtifactVisible: boolean;
}

function PureMessages({
  chatId,
  status,
  votes,
  messages,
  setMessages,
  reload,
  isReadonly,
}: MessagesProps) {
  const pathname = usePathname();
  
  const {
    containerRef: messagesContainerRef,
    endRef: messagesEndRef,
    onViewportEnter,
    onViewportLeave,
    hasSentMessage,
  } = useMessages({
    chatId,
    status,
  });

  // Agent data for different investment agents
  const agentData = {
    // Famous Investors
    'warren-buffett': {
      name: 'Warren Buffett',
      description: 'Value investing legend focused on fundamental analysis and long-term wealth creation',
      expertise: ['Value Investing', 'Fundamental Analysis', 'Competitive Moats', 'Capital Allocation', 'Long-term Thinking'],
      icon: '🎩'
    },
    'charlie-munger': {
      name: 'Charlie Munger',
      description: 'Philosopher investor focused on mental models, quality businesses, and long-term thinking',
      expertise: ['Mental Models', 'Business Moats', 'Predictability', 'Psychology', 'Decision Making'],
      icon: '🧠'
    },
    'peter-lynch': {
      name: 'Peter Lynch',
      description: 'Growth investing expert known for finding "tenbaggers" and investing in what you know',
      expertise: ['Growth Investing', 'PEG Ratio Analysis', 'Consumer Trends', 'Company Research', 'Market Psychology'],
      icon: '📈'
    },
    'ben-graham': {
      name: 'Ben Graham',
      description: 'The father of value investing, focused on margin of safety and intrinsic value',
      expertise: ['Margin of Safety', 'Intrinsic Value', 'Financial Strength', 'Risk Management', 'Value Investing'],
      icon: '📚'
    },
    'michael-burry': {
      name: 'Michael Burry',
      description: 'Contrarian investor known for finding deep value and predicting market inefficiencies',
      expertise: ['Contrarian Investing', 'Deep Value Analysis', 'Market Bubbles', 'Crisis Investing', 'Balance Sheet Analysis'],
      icon: '🔍'
    },
    'bill-ackman': {
      name: 'Bill Ackman',
      description: 'Activist investor focused on operational improvements and corporate governance',
      expertise: ['Activist Investing', 'Corporate Governance', 'Operational Turnaround', 'Catalyst Events', 'Value Creation'],
      icon: '📢'
    },
    'cathie-wood': {
      name: 'Cathie Wood',
      description: 'Innovation investor focused on disruptive technologies and exponential growth',
      expertise: ['Disruptive Innovation', 'Technology Trends', 'Exponential Growth', 'Future Technologies', 'ARK Invest Strategy'],
      icon: '🚀'
    },
    'phil-fisher': {
      name: 'Phil Fisher',
      description: 'Quality growth investor known for thorough research and the "scuttlebutt" method',
      expertise: ['Quality Growth', 'Management Assessment', 'Scuttlebutt Method', 'Long-term Holdings', 'Innovation Focus'],
      icon: '🔬'
    },
    'stanley-druckenmiller': {
      name: 'Stanley Druckenmiller',
      description: 'Macro trader focused on market timing, momentum, and asymmetric risk/reward',
      expertise: ['Macro Trading', 'Market Timing', 'Risk/Reward Analysis', 'Position Sizing', 'Momentum Trading'],
      icon: '⏰'
    },
    'aswath-damodaran': {
      name: 'Aswath Damodaran',
      description: 'The "Dean of Valuation" combining academic rigor with practical valuation methods',
      expertise: ['Valuation Models', 'Academic Analysis', 'Story vs Numbers', 'Risk Assessment', 'Market Pricing'],
      icon: '🎓'
    },
    // Analytical Agents
    'technical-analyst': {
      name: 'Technical Analyst',
      description: 'Chart and technical pattern expert focused on price action and market indicators',
      expertise: ['Chart Patterns', 'Technical Indicators', 'Trend Analysis', 'Support/Resistance', 'Volume Analysis'],
      icon: '📊'
    },
    'fundamentals-analyst': {
      name: 'Fundamentals Analyst',
      description: 'Financial statement expert analyzing business metrics and company health',
      expertise: ['Financial Analysis', 'Profitability Metrics', 'Growth Analysis', 'Cash Flow', 'Business Quality'],
      icon: '💼'
    },
    'sentiment-analyst': {
      name: 'Sentiment Analyst',
      description: 'Market psychology expert tracking insider activity and market sentiment',
      expertise: ['Market Sentiment', 'Insider Trading', 'News Analysis', 'Social Sentiment', 'Contrarian Signals'],
      icon: '🎭'
    },
    'valuation-analyst': {
      name: 'Valuation Analyst',
      description: 'Multi-model valuation expert calculating fair value and price targets',
      expertise: ['DCF Analysis', 'Relative Valuation', 'Fair Value', 'Price Targets', 'Multiple Models'],
      icon: '🧮'
    },
    // Multi-Agent
    'hedge-fund': {
      name: 'Multi-Agent Analyst',
      description: 'Comprehensive portfolio analysis combining insights from multiple investment experts',
      expertise: ['Portfolio Analysis', 'Risk Management', 'Asset Allocation', 'Market Timing', 'Diversification'],
      icon: '🏛️'
    },
    'portfolio-manager': {
      name: 'Portfolio Manager',
      description: 'Professional portfolio optimization and strategic asset management',
      expertise: ['Portfolio Optimization', 'Risk Assessment', 'Rebalancing', 'Tax Efficiency', 'Performance Tracking'],
      icon: '⚖️'
    }
  };

  // Check if we're in an agent chat
  const getAgentFromPath = () => {
    const match = pathname.match(/\/chat\/agent\/([^\/]+)/);
    return match ? match[1] : null;
  };

  const currentAgent = getAgentFromPath();

  return (
    <div
      ref={messagesContainerRef}
      className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4 relative"
    >
      {messages.length === 0 && (
        currentAgent && agentData[currentAgent as keyof typeof agentData] ? (
          <AgentGreeting {...agentData[currentAgent as keyof typeof agentData]} />
        ) : (
          <Greeting />
        )
      )}

      {messages.map((message, index) => (
        <PreviewMessage
          key={message.id}
          chatId={chatId}
          message={message}
          isLoading={status === 'streaming' && messages.length - 1 === index}
          vote={
            votes
              ? votes.find((vote) => vote.messageId === message.id)
              : undefined
          }
          setMessages={setMessages}
          reload={reload}
          isReadonly={isReadonly}
          requiresScrollPadding={
            hasSentMessage && index === messages.length - 1
          }
        />
      ))}

      {status === 'submitted' &&
        messages.length > 0 &&
        messages[messages.length - 1].role === 'user' && <ThinkingMessage />}

      <motion.div
        ref={messagesEndRef}
        className="shrink-0 min-w-[24px] min-h-[24px]"
        onViewportLeave={onViewportLeave}
        onViewportEnter={onViewportEnter}
      />
    </div>
  );
}

export const Messages = memo(PureMessages, (prevProps, nextProps) => {
  if (prevProps.isArtifactVisible && nextProps.isArtifactVisible) return true;

  if (prevProps.status !== nextProps.status) return false;
  if (prevProps.status && nextProps.status) return false;
  if (prevProps.messages.length !== nextProps.messages.length) return false;
  if (!equal(prevProps.messages, nextProps.messages)) return false;
  if (!equal(prevProps.votes, nextProps.votes)) return false;

  return true;
});
