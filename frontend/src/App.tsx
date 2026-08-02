import { useEffect, useState } from 'react';
import { Group as PanelGroup, Panel, Separator as PanelResizeHandle } from 'react-resizable-panels';
import { Sidebar } from './components/Sidebar';
import { Conversation } from './components/Conversation';
import { Workspace } from './components/Workspace';
import { PromptBox } from './components/PromptBox';
import { useStore } from './store/useStore';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert } from 'lucide-react';

function App() {
  const { execId, addEvent, setIsExecuting, securityHalt, setSecurityHalt, addFile, setPlanTasks, setCurrentTaskIdx, ensureTabVisible } = useStore();
  const [showSplash, setShowSplash] = useState(true);

  // Splash screen transition
  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 800);
    return () => clearTimeout(timer);
  }, []);

  // SSE streaming logic
  useEffect(() => {
    if (!execId) return;
    
    const es = new EventSource(`http://localhost:8000/api/stream/${execId}`);
    
    es.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        
        if (msg.type === "security_halt") {
          setSecurityHalt(msg);
          return;
        }
        if (msg.type === "file_written") {
          addFile({name: msg.name, path: msg.path});
          return;
        }
        if (msg.type === "plan") {
           setPlanTasks(msg.tasks || []);
           return;
        }
        if (msg.type === "thought" && msg.current_task_idx !== undefined) {
           setCurrentTaskIdx(msg.current_task_idx);
        }
        
        if (msg.type === "action" && ['browser', 'docker', 'git'].includes(msg.action)) {
           ensureTabVisible(msg.action);
        }
        
        addEvent(msg); // Add event to store
        
        if (msg.type === "finish" || msg.type === "error") {
          setIsExecuting(false);
          es.close();
        }
      } catch (e) {
        console.error("Failed to parse SSE message", e);
      }
    };
    
    es.onerror = () => es.close();
    return () => es.close();
  }, [execId]);

  const handleApprove = async () => {
    if (!execId) return;
    try {
      await fetch(`http://localhost:8000/api/approve/${execId}`, { method: 'POST' });
      setSecurityHalt(null);
    } catch (err) {}
  };

  return (
    <div className="w-screen h-screen bg-[#0B0B0D] text-white flex overflow-hidden font-primary select-none">
      <AnimatePresence>
        {showSplash && (
          <motion.div 
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            className="absolute inset-0 z-50 bg-[#0B0B0D] flex items-center justify-center"
          >
            <motion.img 
               initial={{ scale: 0.9, opacity: 0 }}
               animate={{ scale: 1, opacity: 1 }}
               transition={{ duration: 0.5, type: 'spring' }}
               src="/favicon.png" 
               alt="Atlas Logo" 
               className="w-24 h-24 drop-shadow-[0_0_30px_rgba(255,255,255,0.1)]"
               onError={(e) => {
                   e.currentTarget.src = '';
                   e.currentTarget.className = "w-24 h-24 rounded-2xl bg-[#E5E7EB] shadow-[0_0_40px_rgba(255,255,255,0.1)]";
               }}
            />
          </motion.div>
        )}
      </AnimatePresence>

      <Sidebar />

      <PanelGroup orientation="horizontal" className="flex-1 w-full h-full">
        <Panel defaultSize={60} minSize={40} className="relative h-full">
           <Conversation />
           <PromptBox />
        </Panel>
        
        <PanelResizeHandle className="w-1 bg-[#ffffff05] hover:bg-[#ffffff20] transition-colors cursor-col-resize active:bg-[#ffffff30]" />
        
        <Panel defaultSize={40} minSize={25}>
           <Workspace />
        </Panel>
      </PanelGroup>

      {/* Security Modal */}
      <AnimatePresence>
        {securityHalt && (
          <motion.div 
             initial={{ opacity: 0 }}
             animate={{ opacity: 1 }}
             exit={{ opacity: 0 }}
             className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-center justify-center"
          >
            <motion.div 
               initial={{ scale: 0.95, y: 20 }}
               animate={{ scale: 1, y: 0 }}
               className="bg-[#17181B] border border-[#ffffff0d] rounded-2xl w-full max-w-md p-6 shadow-2xl"
            >
              <div className="flex items-center gap-3 text-yellow-500 mb-4">
                <ShieldAlert size={24} />
                <h3 className="text-lg font-medium text-white tracking-tight">Human Approval Required</h3>
              </div>
              <p className="text-[#A6A6A6] text-[15px] mb-4 leading-relaxed">{securityHalt.detail}</p>
              
              <div className="bg-[#0B0B0D] rounded-xl p-3 border border-[#ffffff0d] font-mono text-[13px] text-[#A6A6A6] mb-6 overflow-x-auto">
                {securityHalt.data?.path || 'N/A'}
              </div>
              
              <div className="flex justify-end gap-3">
                <button 
                  onClick={() => setSecurityHalt(null)} 
                  className="px-5 py-2.5 rounded-xl text-[#A6A6A6] hover:bg-[#ffffff0d] hover:text-white transition-colors text-[14px] font-medium"
                >
                  Deny
                </button>
                <button 
                  onClick={handleApprove} 
                  className="px-5 py-2.5 rounded-xl bg-[#E5E7EB] text-black hover:bg-white transition-colors text-[14px] font-medium shadow-[0_0_20px_rgba(255,255,255,0.1)]"
                >
                  Approve Execution
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
