import React, { useEffect, useRef } from 'react';
import { useStore } from '../store/useStore';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, TerminalSquare, Database, Globe, PackageOpen } from 'lucide-react';

export const Conversation: React.FC = () => {
  const { events, isExecuting } = useStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  const getIconForCapability = (action: string) => {
    switch (action) {
      case 'filesystem': return <Database size={16} />;
      case 'command': return <TerminalSquare size={16} />;
      case 'browser': return <Globe size={16} />;
      default: return <PackageOpen size={16} />;
    }
  };

  return (
    <div className="flex-1 h-full flex flex-col relative overflow-hidden bg-[#0B0B0D]">
      <div className="flex-1 overflow-y-auto pt-8 pb-32 px-12 flex flex-col items-center">
        <div className="w-full max-w-[860px] flex flex-col gap-6">
          
          {events.length === 0 && !isExecuting && (
            <motion.div 
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }} 
              transition={{ delay: 0.2 }}
              className="mt-32 flex flex-col items-center text-center gap-4"
            >
              <div className="w-16 h-16 rounded-2xl bg-[#E5E7EB]/10 flex items-center justify-center border border-[#E5E7EB]/20 shadow-[0_0_40px_rgba(255,255,255,0.05)]">
                 <Sparkles className="text-[#E5E7EB]" size={32} strokeWidth={1.5} />
              </div>
              <h1 className="text-2xl font-medium text-white tracking-tight mt-4">Your AI Operating System</h1>
              <p className="text-[#A6A6A6] text-[15px]">Files. Browser. Terminal. Memory. Plugins. All in one place.</p>
            </motion.div>
          )}

          <AnimatePresence initial={false}>
            {events.map((ev, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className={`w-full flex ${ev.type === 'user_prompt' ? 'justify-end' : 'justify-start'}`}
              >
                {ev.type === 'user_prompt' && (
                  <div className="bg-[#17181B] text-white px-5 py-3.5 rounded-[22px] rounded-br-[8px] max-w-[80%] text-[15px] border border-[#ffffff0d] shadow-sm">
                    {ev.content}
                  </div>
                )}
                
                {ev.type === 'thought' && (
                  <div className="flex items-center gap-3 text-[#A6A6A6] text-sm ml-2">
                     <span className="flex items-center gap-1.5"><Sparkles size={14} className="text-[#E5E7EB]" /> {ev.content}</span>
                  </div>
                )}
                
                {ev.type === 'action' && (
                  <div className="flex flex-col gap-2 w-full ml-6">
                    <div className="flex items-center gap-2 text-[13px] font-medium text-[#A6A6A6]">
                      {getIconForCapability(ev.action || '')}
                      <span className="capitalize">{ev.action}</span>
                      <span className="w-1.5 h-1.5 rounded-full bg-[#E5E7EB] animate-pulse ml-2" />
                      <span className="text-[#666]">Running</span>
                    </div>
                  </div>
                )}

                {ev.type === 'observation' && (
                  <div className="ml-6 mt-1 w-full max-w-[600px]">
                    <div className="bg-[#111214] border border-[#ffffff0d] rounded-xl p-3 max-h-[200px] overflow-y-auto no-select text-[13px] text-[#A6A6A6] font-mono leading-relaxed shadow-sm">
                      <pre>{ev.content}</pre>
                    </div>
                  </div>
                )}
                
                {ev.type === 'error' && (
                  <div className="ml-2 text-red-500 text-sm flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-red-500" />
                    Error: {ev.error}
                  </div>
                )}

                {ev.type === 'finish' && (
                  <div className="ml-2 text-green-500 text-sm flex items-center gap-2 mt-4">
                    <span className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
                    Completed
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={bottomRef} className="h-4" />
        </div>
      </div>
    </div>
  );
};
