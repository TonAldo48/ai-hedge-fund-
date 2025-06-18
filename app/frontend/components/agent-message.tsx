'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import { ChevronDown, ChevronRight, Brain, Target, TrendingUp, Search } from 'lucide-react';
import { Button } from './ui/button';
import { Markdown } from './markdown';

interface ReasoningStep {
  type: 'step' | 'analysis' | 'calculation' | 'conclusion';
  content: string;
  timestamp?: string;
}

interface AgentMessageProps {
  content: string;
  reasoningSteps?: ReasoningStep[];
  agentType: string;
  isLoading?: boolean;
}

const agentIcons: Record<string, React.ReactNode> = {
  'warren-buffett': '🎩',
  'charlie-munger': '🧠',
  'peter-lynch': '📈',
  'ben-graham': '📚',
  'technical-analyst': '📊',
  // Add more agents as needed
};

const stepIcons: Record<string, React.ReactNode> = {
  step: <Search className="w-4 h-4" />,
  analysis: <Brain className="w-4 h-4" />,
  calculation: <TrendingUp className="w-4 h-4" />,
  conclusion: <Target className="w-4 h-4" />,
};

export function AgentMessage({ content, reasoningSteps, agentType, isLoading }: AgentMessageProps) {
  const [showReasoning, setShowReasoning] = useState(false);

  return (
    <div className="flex gap-3 w-full max-w-4xl mx-auto">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center text-lg">
        {agentIcons[agentType] || '🤖'}
      </div>
      
      <div className="flex-1 space-y-2">
        {/* Reasoning Steps */}
        {reasoningSteps && reasoningSteps.length > 0 && (
          <div className="mb-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowReasoning(!showReasoning)}
              className="text-muted-foreground hover:text-foreground mb-2"
            >
              {showReasoning ? <ChevronDown className="w-4 h-4 mr-1" /> : <ChevronRight className="w-4 h-4 mr-1" />}
              {showReasoning ? 'Hide' : 'Show'} reasoning ({reasoningSteps.length} steps)
            </Button>
            
            {showReasoning && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-2 border-l-2 border-muted pl-4 ml-2"
              >
                {reasoningSteps.map((step, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={cn(
                      "flex gap-2 items-start p-2 rounded-lg",
                      "bg-muted/30 hover:bg-muted/50 transition-colors"
                    )}
                  >
                    <div className="flex-shrink-0 mt-0.5 text-muted-foreground">
                      {stepIcons[step.type] || stepIcons.step}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground">{step.content}</p>
                      {step.timestamp && (
                        <p className="text-xs text-muted-foreground/60 mt-1">{step.timestamp}</p>
                      )}
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </div>
        )}
        
        {/* Main Response */}
        <div className={cn(
          "prose prose-sm dark:prose-invert max-w-none",
          isLoading && "animate-pulse"
        )}>
          <Markdown>{content}</Markdown>
        </div>
      </div>
    </div>
  );
} 