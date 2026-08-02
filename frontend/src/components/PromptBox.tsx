import React, { useRef, useEffect } from 'react';
import { Paperclip, Mic, ArrowUp, BrainCircuit } from 'lucide-react';
import { useStore } from '../store/useStore';
import { motion } from 'framer-motion';

export const PromptBox: React.FC = () => {
  const { taskInput, setTaskInput, isExecuting, setIsExecuting, setExecId } = useStore();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleExecute = async () => {
    if (!taskInput.trim() || isExecuting) return;
    
    setIsExecuting(true);
    // Real implementation would interact with API here. For mock, just delay.
    // Let's call the actual API
    try {
      const res = await fetch('http://localhost:8000/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal: taskInput })
      });
      const data = await res.json();
      setExecId(data.exec_id);
      setTaskInput('');
    } catch (err) {
      console.error(err);
      setIsExecuting(false);
    }
  };

  return (
    <motion.div 
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="absolute bottom-8 left-1/2 -translate-x-1/2 w-full max-w-[860px] px-4 z-40"
    >
      <div className="h-[68px] bg-[#17181B] rounded-[22px] shadow-[0_4px_30px_rgba(0,0,0,0.4)] border border-[#ffffff0d] flex items-center px-6 gap-4">
        
        <button className="text-[#A6A6A6] hover:text-white transition-colors outline-none">
          <Paperclip size={20} strokeWidth={2} />
        </button>
        
        <button className="text-[#A6A6A6] hover:text-white transition-colors outline-none flex items-center gap-2 bg-[#222327] px-3 py-1.5 rounded-full text-sm font-medium">
          <BrainCircuit size={16} className="text-[#E5E7EB]" />
          <span>Atlas Auto</span>
        </button>

        <input 
          ref={inputRef}
          type="text"
          value={taskInput}
          onChange={(e) => setTaskInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleExecute()}
          placeholder="Ask Atlas to do anything..."
          className="flex-1 bg-transparent border-none outline-none text-white text-[15px] placeholder-[#666666] font-primary"
          autoFocus
        />

        <button className="text-[#A6A6A6] hover:text-white transition-colors outline-none">
          <Mic size={20} strokeWidth={2} />
        </button>

        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleExecute}
          className={`w-9 h-9 flex items-center justify-center rounded-full transition-colors ${
            taskInput.trim() ? 'bg-[#E5E7EB] text-black' : 'bg-[#222327] text-[#666666]'
          }`}
        >
          {isExecuting ? (
            <div className="w-3 h-3 bg-white rounded-sm animate-pulse" /> // Stop square
          ) : (
            <ArrowUp size={18} strokeWidth={2.5} />
          )}
        </motion.button>
      </div>
    </motion.div>
  );
};
