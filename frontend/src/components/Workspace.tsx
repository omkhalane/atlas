import React, { useEffect, useRef } from 'react';
import { useStore } from '../store/useStore';
import { Globe, Folder, TerminalSquare, Activity, Brain, Box, GitBranch } from 'lucide-react';
import { Terminal } from '@xterm/xterm';
import '@xterm/xterm/css/xterm.css';

export const Workspace: React.FC = () => {
  const { activeWorkspaceTab, setActiveWorkspaceTab, files, visibleTabs } = useStore();
  const terminalRef = useRef<HTMLDivElement>(null);

  const allTabs = [
    { id: 'browser', icon: Globe, label: 'Browser' },
    { id: 'files', icon: Folder, label: `Files (${files.length})` },
    { id: 'terminal', icon: TerminalSquare, label: 'Terminal' },
    { id: 'logs', icon: Activity, label: 'Logs' },
    { id: 'memory', icon: Brain, label: 'Memory' },
    { id: 'docker', icon: Box, label: 'Docker' },
    { id: 'git', icon: GitBranch, label: 'Git' }
  ];

  const displayedTabs = allTabs.filter(t => visibleTabs.includes(t.id));

  useEffect(() => {
    if (activeWorkspaceTab === 'terminal' && terminalRef.current) {
      const term = new Terminal({
        theme: { background: '#17181B', foreground: '#E5E7EB' },
        fontFamily: '"JetBrains Mono", monospace',
        fontSize: 13,
      });
      term.open(terminalRef.current);
      term.write('Atlas Agentic Terminal v1.0.0\r\n$ ');
      
      return () => {
        term.dispose();
      };
    }
  }, [activeWorkspaceTab]);

  return (
    <div className="w-full h-full bg-[#111214] flex flex-col border-l border-[#ffffff0d]">
      <div className="flex px-4 py-3 gap-2 overflow-x-auto border-b border-[#ffffff0d] no-scrollbar">
        {displayedTabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveWorkspaceTab(tab.id)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-[13px] font-medium transition-colors outline-none whitespace-nowrap ${
              activeWorkspaceTab === tab.id 
                ? 'bg-[#17181B] text-white border border-[#ffffff0d] shadow-sm' 
                : 'text-[#A6A6A6] hover:text-white hover:bg-[#ffffff05]'
            }`}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-hidden relative">
        {activeWorkspaceTab === 'browser' && (
          <div className="absolute inset-0">
             {/* Full screen browser, locked mode */}
             <img 
                  src={`http://localhost:8000/api/browser_screenshot?t=${new Date().getTime()}`} 
                  className="w-full h-full object-cover"
                  alt="Live Browser"
                  onError={(e) => {
                      e.currentTarget.style.display = 'none';
                  }}
               />
          </div>
        )}
        
        {activeWorkspaceTab === 'files' && (
          <div className="absolute inset-0 p-4 overflow-y-auto bg-[#0B0B0D]">
             <div className="space-y-1">
                {files.map((f, i) => (
                   <div key={i} className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-[#ffffff05] text-[13px] text-[#A6A6A6] cursor-pointer group">
                      <div className="flex items-center gap-3">
                         <Folder size={16} className="text-blue-400" />
                         <span className="group-hover:text-white transition-colors">{f.name}</span>
                      </div>
                      <span className="text-[11px] opacity-50">Just now</span>
                   </div>
                ))}
                {files.length === 0 && (
                   <div className="text-center text-[#A6A6A6] text-[13px] mt-10">
                      No files modified yet.
                   </div>
                )}
             </div>
          </div>
        )}

        {activeWorkspaceTab === 'terminal' && (
          <div className="absolute inset-0 p-4 bg-[#17181B]">
             <div ref={terminalRef} className="w-full h-full" />
          </div>
        )}

        {activeWorkspaceTab === 'logs' && (
          <div className="absolute inset-0 p-4 bg-[#0B0B0D] overflow-y-auto font-mono text-[12px] text-[#A6A6A6]">
             <div>[SYSTEM] Atlas Execution Engine Started.</div>
             <div>[SYSTEM] Listening on port 8000...</div>
          </div>
        )}

        {activeWorkspaceTab === 'memory' && (
          <div className="absolute inset-0 p-4 bg-[#0B0B0D] overflow-y-auto text-[13px] text-[#A6A6A6]">
             <div className="border border-[#ffffff0d] rounded-lg p-3 bg-[#17181B] mb-2">
                <strong>Project Goal:</strong> Build a premium AI desktop UI.
             </div>
          </div>
        )}

        {['docker', 'git'].includes(activeWorkspaceTab) && (
          <div className="absolute inset-0 flex items-center justify-center text-[#A6A6A6] text-sm font-mono bg-[#0B0B0D]">
             {activeWorkspaceTab} module loading...
          </div>
        )}
      </div>
    </div>
  );
};
