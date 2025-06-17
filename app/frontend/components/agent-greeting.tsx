import { motion } from 'framer-motion';

interface AgentGreetingProps {
  name: string;
  description: string;
  expertise: string[];
  icon: string;
}

export const AgentGreeting = ({ name, description, expertise, icon }: AgentGreetingProps) => {
  return (
    <div
      key="agent-overview"
      className="max-w-3xl mx-auto md:mt-20 px-8 size-full flex flex-col justify-center"
    >
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        transition={{ delay: 0.3 }}
        className="flex items-center gap-4 mb-6"
      >
        <span className="text-5xl">{icon}</span>
        <h1 className="text-3xl font-semibold">{name}</h1>
      </motion.div>
      
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        transition={{ delay: 0.4 }}
        className="text-xl text-zinc-600 dark:text-zinc-400 mb-6"
      >
        {description}
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        transition={{ delay: 0.5 }}
        className="mb-4"
      >
        <h3 className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
          Areas of Expertise:
        </h3>
        <div className="flex flex-wrap gap-2">
          {expertise.map((skill, index) => (
            <motion.span
              key={skill}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6 + index * 0.1 }}
              className="px-3 py-1 bg-zinc-100 dark:bg-zinc-800 rounded-full text-sm text-zinc-700 dark:text-zinc-300"
            >
              {skill}
            </motion.span>
          ))}
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        transition={{ delay: 0.8 }}
        className="text-lg text-zinc-500 mt-4"
      >
        How can I help you with your investment analysis today?
      </motion.div>
    </div>
  );
}; 