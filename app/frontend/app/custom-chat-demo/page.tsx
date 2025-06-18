'use client';

import { useState } from 'react';
import { CustomChat } from '@/components/custom-chat';
import { MultiAgentChat } from '@/components/multi-agent-chat';
import { Button } from '@/components/ui/button';

export default function CustomChatDemo() {
  const [activeView, setActiveView] = useState<'simple' | 'multi'>('simple');

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold text-center mb-4 mt-8">
          AI Hedge Fund Custom Chat Components
        </h1>
        
        <div className="flex justify-center gap-4 mb-8">
          <Button 
            variant={activeView === 'simple' ? 'default' : 'outline'}
            onClick={() => setActiveView('simple')}
          >
            Simple Chat
          </Button>
          <Button 
            variant={activeView === 'multi' ? 'default' : 'outline'}
            onClick={() => setActiveView('multi')}
          >
            Multi-Agent Chat
          </Button>
        </div>
        
        {activeView === 'simple' ? (
          <div>
            <p className="text-center text-muted-foreground mb-6">
              Basic chat component with Warren Buffett agent
            </p>
            <CustomChat />
          </div>
        ) : (
          <div>
            <p className="text-center text-muted-foreground mb-6">
              Advanced chat with multiple AI agents
            </p>
            <MultiAgentChat />
          </div>
        )}

        <div className="mt-12 max-w-3xl mx-auto">
          <h2 className="text-xl font-semibold mb-4">Integration Guide</h2>
          <div className="space-y-4 text-sm">
            <div className="bg-muted p-4 rounded-lg">
              <h3 className="font-medium mb-2">Basic Usage:</h3>
              <pre className="text-xs overflow-x-auto">
{`import { CustomChat } from '@/components/custom-chat';

<CustomChat />`}
              </pre>
            </div>
            
            <div className="bg-muted p-4 rounded-lg">
              <h3 className="font-medium mb-2">With Custom Props:</h3>
              <pre className="text-xs overflow-x-auto">
{`<CustomChat 
  apiKey="your-api-key"
  backendUrl="https://your-backend.com"
  defaultAgent="warren-buffett"
  className="shadow-lg"
/>`}
              </pre>
            </div>
            
            <div className="bg-muted p-4 rounded-lg">
              <h3 className="font-medium mb-2">Multi-Agent Chat:</h3>
              <pre className="text-xs overflow-x-auto">
{`import { MultiAgentChat } from '@/components/multi-agent-chat';

<MultiAgentChat 
  showAgentBadge={true}
  defaultAgent="portfolio-manager"
/>`}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 