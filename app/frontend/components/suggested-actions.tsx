'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { memo } from 'react';
import type { UseChatHelpers } from '@ai-sdk/react';
import type { VisibilityType } from './visibility-selector';
import { useRouter, usePathname } from 'next/navigation';

interface SuggestedActionsProps {
  chatId: string;
  append: UseChatHelpers['append'];
  selectedVisibilityType: VisibilityType;
}

function PureSuggestedActions({
  chatId,
  append,
  selectedVisibilityType,
}: SuggestedActionsProps) {
  const router = useRouter();
  const pathname = usePathname();
  
  // Determine which agent we're talking to based on the route
  const getAgentFromPath = (path: string): string => {
    const match = path.match(/\/chat\/agent\/([^/]+)/);
    return match ? match[1] : 'default';
  };
  
  const agent = getAgentFromPath(pathname);
  
  // Define agent-specific suggestions based on their actual analytical functions
  const agentSuggestions: Record<string, Array<{action: string, description: string, label: string}>> = {
    'warren-buffett': [
      {
        action: 'Analyze fundamentals',
        description: 'Analyze fundamentals (ROE, debt, margins, liquidity) for AAPL',
        label: 'Fundamentals Analysis'
      },
      {
        action: 'Evaluate moat',
        description: 'Evaluate competitive moat and durable advantages for MSFT',
        label: 'Moat Analysis'
      },
      {
        action: 'Check consistency',
        description: 'Analyze earnings consistency and growth trends for BRK.B',
        label: 'Consistency Check'
      },
      {
        action: 'Calculate intrinsic value',
        description: 'Calculate intrinsic value and margin of safety for KO',
        label: 'Intrinsic Value'
      }
    ],
    'charlie-munger': [
      {
        action: 'Analyze moat strength',
        description: 'Evaluate competitive advantages and moat durability for COST',
        label: 'Moat Strength'
      },
      {
        action: 'Assess management',
        description: 'Analyze management quality and capital allocation for BRK.B',
        label: 'Management Quality'
      },
      {
        action: 'Check predictability',
        description: 'Evaluate business predictability and earnings stability for JNJ',
        label: 'Business Predictability'
      },
      {
        action: 'Full analysis',
        description: 'Perform complete Munger-style analysis on WFC',
        label: 'Complete Analysis'
      }
    ],
    'peter-lynch': [
      {
        action: 'Analyze growth',
        description: 'Analyze revenue and earnings growth patterns for AMD',
        label: 'Growth Analysis'
      },
      {
        action: 'Check valuation',
        description: 'Calculate PEG ratio and relative valuation for NVDA',
        label: 'Valuation Check'
      },
      {
        action: 'Evaluate fundamentals',
        description: 'Assess business fundamentals and financial health for TGT',
        label: 'Fundamentals'
      },
      {
        action: 'Sentiment analysis',
        description: 'Analyze news sentiment and insider activity for TSLA',
        label: 'Market Sentiment'
      }
    ],
    'ben-graham': [
      {
        action: 'Check earnings stability',
        description: 'Analyze earnings stability over 10 years for IBM',
        label: 'Earnings Stability'
      },
      {
        action: 'Assess financial strength',
        description: 'Evaluate debt levels and liquidity position for GE',
        label: 'Financial Strength'
      },
      {
        action: 'Calculate Graham value',
        description: 'Calculate Graham Number and net-net value for F',
        label: 'Graham Valuation'
      },
      {
        action: 'Margin of safety',
        description: 'Determine margin of safety for value investment in BAC',
        label: 'Safety Margin'
      }
    ],
    'michael-burry': [
      {
        action: 'Deep value scan',
        description: 'Find deep value with FCF yield and EV/EBIT for META',
        label: 'Value Metrics'
      },
      {
        action: 'Balance sheet analysis',
        description: 'Analyze leverage and liquidity position for GOOGL',
        label: 'Balance Sheet'
      },
      {
        action: 'Insider activity',
        description: 'Check insider buying as hard catalyst for PYPL',
        label: 'Insider Trades'
      },
      {
        action: 'Contrarian opportunity',
        description: 'Find contrarian value in hated stocks like COIN',
        label: 'Contrarian Play'
      }
    ],
    'bill-ackman': [
      {
        action: 'Business quality',
        description: 'Evaluate business quality and franchise value for CMG',
        label: 'Quality Analysis'
      },
      {
        action: 'Financial discipline',
        description: 'Assess capital allocation and financial discipline for CP',
        label: 'Capital Discipline'
      },
      {
        action: 'Activism potential',
        description: 'Identify activism opportunities and unlock value in DIS',
        label: 'Activism Potential'
      },
      {
        action: 'Valuation analysis',
        description: 'Calculate intrinsic value with margin of safety for HLT',
        label: 'Value Assessment'
      }
    ],
    'cathie-wood': [
      {
        action: 'Disruptive potential',
        description: 'Analyze disruptive innovation potential in TSLA',
        label: 'Disruption Score'
      },
      {
        action: 'Innovation growth',
        description: 'Evaluate innovation-driven growth metrics for ROKU',
        label: 'Innovation Growth'
      },
      {
        action: 'Technology valuation',
        description: 'Assess future valuation for exponential growth in SQ',
        label: 'Tech Valuation'
      },
      {
        action: 'ARK portfolio',
        description: 'Analyze top ARK-style opportunities in genomics and AI',
        label: 'Portfolio Ideas'
      }
    ],
    'phil-fisher': [
      {
        action: 'Growth quality',
        description: 'Evaluate sustainable growth and quality metrics for MSFT',
        label: 'Quality Growth'
      },
      {
        action: 'Margin stability',
        description: 'Analyze operating margin trends and stability for ADBE',
        label: 'Margins Analysis'
      },
      {
        action: 'Management efficiency',
        description: 'Assess management and R&D effectiveness for AAPL',
        label: 'Management'
      },
      {
        action: 'Long-term potential',
        description: 'Evaluate 10-year growth potential for innovative companies',
        label: 'Growth Potential'
      }
    ],
    'stanley-druckenmiller': [
      {
        action: 'Momentum analysis',
        description: 'Analyze price and earnings momentum for NVDA',
        label: 'Momentum Signals'
      },
      {
        action: 'Risk-reward setup',
        description: 'Evaluate risk-reward and position sizing for SPY',
        label: 'Risk/Reward'
      },
      {
        action: 'Market sentiment',
        description: 'Assess market sentiment and positioning in QQQ',
        label: 'Sentiment Check'
      },
      {
        action: 'Macro overlay',
        description: 'Apply macro analysis to sector rotation opportunities',
        label: 'Macro View'
      }
    ],
    'aswath-damodaran': [
      {
        action: 'DCF valuation',
        description: 'Calculate intrinsic value using FCFF DCF model for AMZN',
        label: 'DCF Analysis'
      },
      {
        action: 'Growth reinvestment',
        description: 'Analyze growth rates and reinvestment efficiency for GOOGL',
        label: 'Growth & ROIC'
      },
      {
        action: 'Risk profile',
        description: 'Evaluate beta, leverage, and cost of equity for AAPL',
        label: 'Risk Assessment'
      },
      {
        action: 'Relative valuation',
        description: 'Compare valuation multiples to history and peers for META',
        label: 'Relative Value'
      }
    ],
    'technical-analyst': [
      {
        action: 'Trend analysis',
        description: 'Analyze trend signals and moving averages for SPY',
        label: 'Trend Following'
      },
      {
        action: 'Momentum indicators',
        description: 'Check RSI, MACD, and momentum signals for TSLA',
        label: 'Momentum'
      },
      {
        action: 'Support resistance',
        description: 'Identify key support and resistance levels for BTC',
        label: 'Price Levels'
      },
      {
        action: 'Chart patterns',
        description: 'Detect breakout patterns and trading setups in QQQ',
        label: 'Patterns'
      }
    ],
    'fundamentals-analyst': [
      {
        action: 'Profitability metrics',
        description: 'Analyze ROE, margins, and profitability trends for AAPL',
        label: 'Profitability'
      },
      {
        action: 'Growth analysis',
        description: 'Evaluate revenue and earnings growth rates for MSFT',
        label: 'Growth Metrics'
      },
      {
        action: 'Financial health',
        description: 'Assess balance sheet strength and cash flow for JNJ',
        label: 'Financial Health'
      },
      {
        action: 'Peer comparison',
        description: 'Compare fundamental metrics across tech sector',
        label: 'Sector Analysis'
      }
    ],
    'sentiment-analyst': [
      {
        action: 'News sentiment',
        description: 'Analyze recent news sentiment and media coverage for TSLA',
        label: 'News Analysis'
      },
      {
        action: 'Insider trades',
        description: 'Track insider buying and selling activity for NVDA',
        label: 'Insider Activity'
      },
      {
        action: 'Social sentiment',
        description: 'Gauge market sentiment from social signals for GME',
        label: 'Social Signals'
      },
      {
        action: 'Sentiment shifts',
        description: 'Identify major sentiment changes in the market',
        label: 'Sentiment Trends'
      }
    ],
    'valuation-analyst': [
      {
        action: 'Multiple methods',
        description: 'Calculate value using DCF, multiples, and assets for AAPL',
        label: 'Valuation Models'
      },
      {
        action: 'Relative valuation',
        description: 'Compare P/E, EV/EBITDA to industry peers for MSFT',
        label: 'Peer Multiples'
      },
      {
        action: 'Asset valuation',
        description: 'Evaluate book value and tangible assets for BAC',
        label: 'Asset-Based'
      },
      {
        action: 'Valuation gaps',
        description: 'Find stocks with largest valuation discrepancies',
        label: 'Value Gaps'
      }
    ],
    'hedge-fund': [
      {
        action: 'Multi-agent analysis',
        description: 'Run full hedge fund analysis on AAPL with all agents',
        label: 'Full Analysis'
      },
      {
        action: 'Portfolio construction',
        description: 'Build optimal portfolio from S&P 500 components',
        label: 'Portfolio Build'
      },
      {
        action: 'Risk assessment',
        description: 'Comprehensive risk analysis across multiple positions',
        label: 'Risk Analysis'
      },
      {
        action: 'Market opportunities',
        description: 'Find best opportunities using ensemble approach',
        label: 'Top Ideas'
      }
    ],
    'portfolio-manager': [
      {
        action: 'Portfolio optimization',
        description: 'Optimize weights for risk-adjusted returns',
        label: 'Optimize Portfolio'
      },
      {
        action: 'Risk management',
        description: 'Analyze portfolio risk and suggest hedges',
        label: 'Risk Management'
      },
      {
        action: 'Rebalancing',
        description: 'Recommend rebalancing based on market conditions',
        label: 'Rebalance'
      },
      {
        action: 'Performance attribution',
        description: 'Analyze portfolio performance and factor exposures',
        label: 'Performance'
      }
    ],
    'default': [
      {
        action: 'Stock analysis',
        description: 'Analyze any stock ticker comprehensively',
        label: 'Analyze Stock'
      },
      {
        action: 'Market overview',
        description: 'Get current market conditions and opportunities',
        label: 'Market View'
      },
      {
        action: 'Investment advice',
        description: 'Get personalized investment recommendations',
        label: 'Get Advice'
      },
      {
        action: 'Learn investing',
        description: 'Learn about value investing principles',
        label: 'Learn More'
      }
    ]
  };

  const suggestedActions = agentSuggestions[agent];

  return (
    <div
      data-testid="suggested-actions"
      className="grid sm:grid-cols-2 gap-3 w-full max-w-4xl mx-auto"
    >
      {suggestedActions.map((suggestedAction, index) => (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          transition={{ delay: 0.05 * index }}
          key={`suggested-action-${suggestedAction.action}-${index}`}
          className={index > 1 ? 'hidden sm:block' : 'block'}
        >
          <Button
            variant="ghost"
            onClick={async () => {
              window.history.replaceState({}, '', `/chat/${chatId}`);

              append({
                role: 'user',
                content: suggestedAction.description,
              });
            }}
            className={`text-left border rounded-xl px-4 py-3.5 text-sm flex flex-col gap-1.5 w-full min-h-fit justify-start items-start ${
              // Famous Investors
              agent === 'warren-buffett' ? 'hover:border-blue-500/50 hover:bg-blue-50/10' :
              agent === 'charlie-munger' ? 'hover:border-indigo-500/50 hover:bg-indigo-50/10' :
              agent === 'peter-lynch' ? 'hover:border-green-500/50 hover:bg-green-50/10' :
              agent === 'ben-graham' ? 'hover:border-slate-500/50 hover:bg-slate-50/10' :
              agent === 'michael-burry' ? 'hover:border-red-500/50 hover:bg-red-50/10' :
              agent === 'bill-ackman' ? 'hover:border-orange-500/50 hover:bg-orange-50/10' :
              agent === 'cathie-wood' ? 'hover:border-pink-500/50 hover:bg-pink-50/10' :
              agent === 'phil-fisher' ? 'hover:border-teal-500/50 hover:bg-teal-50/10' :
              agent === 'stanley-druckenmiller' ? 'hover:border-yellow-500/50 hover:bg-yellow-50/10' :
              agent === 'aswath-damodaran' ? 'hover:border-violet-500/50 hover:bg-violet-50/10' :
              // Analytical Agents
              agent === 'technical-analyst' ? 'hover:border-cyan-500/50 hover:bg-cyan-50/10' :
              agent === 'fundamentals-analyst' ? 'hover:border-emerald-500/50 hover:bg-emerald-50/10' :
              agent === 'sentiment-analyst' ? 'hover:border-rose-500/50 hover:bg-rose-50/10' :
              agent === 'valuation-analyst' ? 'hover:border-sky-500/50 hover:bg-sky-50/10' :
              // Multi-Agent
              agent === 'hedge-fund' ? 'hover:border-purple-500/50 hover:bg-purple-50/10' :
              agent === 'portfolio-manager' ? 'hover:border-amber-500/50 hover:bg-amber-50/10' :
              ''
            }`}
          >
            <span className="font-medium w-full">{suggestedAction.label}</span>
            <span className="text-muted-foreground w-full text-xs sm:text-sm whitespace-normal break-words">
              {suggestedAction.description}
            </span>
          </Button>
        </motion.div>
      ))}
    </div>
  );
}

export const SuggestedActions = memo(
  PureSuggestedActions,
  (prevProps, nextProps) => {
    if (prevProps.chatId !== nextProps.chatId) return false;
    if (prevProps.selectedVisibilityType !== nextProps.selectedVisibilityType)
      return false;

    return true;
  },
);
