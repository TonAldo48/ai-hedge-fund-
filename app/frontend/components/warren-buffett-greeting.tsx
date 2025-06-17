export function WarrenBuffettGreeting() {
  return (
    <div className="w-full mx-auto max-w-3xl px-4 mt-12">
      <div className="rounded-lg border bg-card p-8">
        <h2 className="text-2xl font-semibold mb-4">
          Welcome to Warren Buffett Investment Analysis
        </h2>
        
        <p className="text-muted-foreground mb-6">
          I'm here to help you analyze investments through the lens of Warren Buffett's 
          time-tested value investing principles.
        </p>

        <div className="space-y-4">
          <div>
            <h3 className="font-medium mb-2">I can help you evaluate companies based on:</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
              <li><strong>Fundamental Analysis</strong>: ROE, debt levels, operating margins, and liquidity</li>
              <li><strong>Competitive Moat</strong>: Durable competitive advantages and pricing power</li>
              <li><strong>Earnings Consistency</strong>: Stability and growth trends over time</li>
              <li><strong>Management Quality</strong>: Capital allocation and shareholder orientation</li>
              <li><strong>Intrinsic Value</strong>: DCF valuation with margin of safety</li>
            </ul>
          </div>

          <div>
            <h3 className="font-medium mb-2">Example questions you can ask:</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
              <li>"What do you think about Apple's competitive moat?"</li>
              <li>"How strong are Microsoft's fundamentals?"</li>
              <li>"What's Tesla's intrinsic value and margin of safety?"</li>
              <li>"Should I invest in NVDA based on value investing principles?"</li>
              <li>"How does Amazon's management allocate capital?"</li>
            </ul>
          </div>
        </div>

        <p className="mt-6 text-sm text-muted-foreground">
          💡 <strong>Tip:</strong> Ask about any publicly traded company, and I'll analyze it using 
          Warren Buffett's investment philosophy!
        </p>
      </div>
    </div>
  );
} 