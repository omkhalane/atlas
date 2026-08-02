import React, { useEffect, useRef, useState } from 'react';
import { Terminal } from 'xterm';
import 'xterm/css/xterm.css';
import { useStore } from '../store/useStore';
import { Terminal as TerminalIcon, X, Plus, Play, Square, SplitSquareHorizontal } from 'lucide-react';

export const TerminalView: React.FC = () => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<Terminal | null>(null);
  const [tabs, setTabs] = useState([{ id: '1', name: 'Main' }, { id: '2', name: 'Build' }]);
  const [activeTab, setActiveTab] = useState('1');

  useEffect(() => {
    if (!terminalRef.current) return;

    const term = new Terminal({
      theme: {
        background: '#0F1229',
        foreground: '#E0E0E0',
        cursor: '#00A8E8',
        selectionBackground: 'rgba(0, 168, 232, 0.3)',
      },
      fontFamily: '"JetBrains Mono", monospace',
      fontSize: 13,
      cursorBlink: true
    });

    term.open(terminalRef.current);
    term.write('\x1b[1;36mAtlas Terminal v1.0\x1b[0m\r\n');
    term.write('$ npm run build\r\n');
    term.write('\x1b[32m> Compiling...\x1b[0m\r\n');
    term.write('\x1b[32m> Done! (2.3s)\x1b[0m\r\n');
    term.write('$ ');

    term.onData(data => {
      // Basic echo for demo purposes
      if (data === '\r') {
        term.write('\r\n$ ');
      } else if (data === '\x7f') {
        term.write('\b \b');
      } else {
        term.write(data);
      }
    });

    xtermRef.current = term;

    return () => {
      term.dispose();
    };
  }, [activeTab]);

  return (
    <div className="flex-1 h-full flex flex-col bg-[var(--color-bg-panel)] overflow-hidden">
      {/* Terminal Header */}
      <div className="h-[32px] flex items-center bg-[var(--color-bg-background)] border-b border-[var(--color-border-subtle)] shrink-0 px-2 overflow-x-auto scrollbar-none">
        <div className="flex items-center h-full">
          {tabs.map((tab) => (
            <div 
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center h-full px-3 gap-2 border-r border-[var(--color-border-subtle)] cursor-pointer group select-none min-w-[120px] max-w-[200px] transition-colors ${
                activeTab === tab.id 
                  ? 'bg-[var(--color-bg-panel)] border-t-2 border-t-[var(--color-accent)]' 
                  : 'bg-transparent border-t-2 border-t-transparent hover:bg-[var(--color-bg-hover)]'
              }`}
            >
              <TerminalIcon size={14} className={activeTab === tab.id ? 'text-[var(--color-accent)]' : 'text-[var(--color-text-tertiary)]'} />
              <span className={`text-[12px] truncate flex-1 ${activeTab === tab.id ? 'text-[var(--color-text-primary)]' : 'text-[var(--color-text-secondary)]'}`}>
                {tab.name}
              </span>
              <button 
                className={`p-0.5 rounded opacity-0 group-hover:opacity-100 hover:bg-[var(--color-bg-hover)] ${activeTab === tab.id ? 'text-[var(--color-text-secondary)] hover:text-white' : 'text-[var(--color-text-tertiary)]'}`}
                onClick={(e) => {
                  e.stopPropagation();
                  setTabs(tabs.filter(t => t.id !== tab.id));
                }}
              >
                <X size={12} />
              </button>
            </div>
          ))}
          <button 
            className="w-8 h-full flex items-center justify-center text-[var(--color-text-tertiary)] hover:bg-[var(--color-bg-hover)] hover:text-[var(--color-text-primary)] transition-colors"
            onClick={() => setTabs([...tabs, { id: Date.now().toString(), name: 'bash' }])}
          >
            <Plus size={14} />
          </button>
        </div>

        <div className="ml-auto flex items-center gap-1 pr-2">
           <button className="p-1.5 text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-hover)] rounded transition-colors" title="Split Terminal">
             <SplitSquareHorizontal size={14} />
           </button>
        </div>
      </div>

      {/* Terminal Content */}
      <div className="flex-1 w-full bg-[#0F1229] relative p-1" ref={terminalRef}>
         {/* xterm.js will mount here */}
      </div>
      
      {/* Background Processes Sidebar (Mock) */}
      <div className="h-40 border-t border-[var(--color-border-subtle)] bg-[var(--color-bg-panel)] flex flex-col shrink-0">
         <div className="px-3 py-1.5 border-b border-[var(--color-border-subtle)] text-[11px] font-medium text-[var(--color-text-tertiary)] uppercase tracking-wider bg-[var(--color-bg-background)]">
            Running Processes
         </div>
         <div className="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
            <div className="flex items-center justify-between px-2 py-1.5 hover:bg-[var(--color-bg-hover)] rounded group text-[12px] text-[var(--color-text-secondary)]">
               <div className="flex items-center gap-2">
                 <Play size={12} className="text-[var(--color-success)]" />
                 <span className="font-mono">npm run dev</span>
                 <span className="text-[var(--color-text-tertiary)] text-[10px] ml-2">PID 1234</span>
               </div>
               <button className="opacity-0 group-hover:opacity-100 text-[10px] px-2 py-0.5 bg-[var(--color-danger-transparent)] text-[var(--color-danger)] rounded border border-red-900/30 hover:bg-red-900/40">
                 Kill
               </button>
            </div>
         </div>
      </div>
    </div>
  );
};
