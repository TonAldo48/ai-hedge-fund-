-- Add new agent types to the Chat table
ALTER TABLE "Chat" 
ALTER COLUMN "agentType" TYPE varchar 
CHECK ("agentType" IN ('general', 'warren-buffett', 'peter-lynch', 'charlie-munger', 'ben-graham', 'technical-analyst')); 