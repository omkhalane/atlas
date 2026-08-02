import React, { useState, useEffect, useRef } from 'react';
import { Search, Terminal, Folder, Settings, Globe, Play, Square, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useStore } from '../store/useStore';

interface Command {
  id: string;
  name: string;
  description: string;
  shortcut?: string;
  icon: React.FC<any>;
  category: string;
  action: () => void;
}

export const CommandPalette: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const { openTab } = useStore();

  const commands: Command[] = [
    {
      id: 'cmd-chat',
      name: 'Toggle Chat View',
      description: 'Open a chat panel',
      shortcut: "Ctrl+'",
      icon: Terminal,
      category: 'Views',
      action: () => openTab({ type: 'chat', title: 'Chat' })
    },
    {
      id: 'cmd-files',
      name: 'Toggle File Explorer',
      description: 'Show file explorer',
      shortcut: 'Ctrl+E',
      icon: Folder,
      category: 'Views',
      action: () => openTab({ type: 'file', title: 'Explorer' })
    },
    {
      id: 'cmd-browser',
      name: 'Open Browser',
      description: 'Switch to integrated web browser',
      shortcut: 'Ctrl+B',
      icon: Globe,
      category: 'Views',
      action: () => openTab({ type: 'browser', title: 'Browser' })
    },
    {
      id: 'cmd-settings',
      name: 'Open Settings',
      description: 'Edit application preferences',
      shortcut: 'Ctrl+,',
      icon: Settings,
      category: 'Settings',
      action: () => console.log('Open Settings')
    },
    {
      id: 'cmd-run-agent',
      name: 'Run Agent',
      description: 'Start the active agent',
      shortcut: 'Ctrl+Enter',
      icon: Play,
      category: 'Agent',
      action: () => console.log('Run Agent')
    },
    {
      id: 'cmd-stop-agent',
      name: 'Cancel Agent',
      description: 'Stop running agent immediately',
      shortcut: 'Ctrl+Shift+C',
      icon: Square,
      category: 'Agent',
      action: () => console.log('Stop Agent')
    },
    {
      id: 'cmd-new-file',
      name: 'New File',
      description: 'Create new file',
      shortcut: 'Ctrl+Alt+N',
      icon: FileText,
      category: 'Files',
      action: () => console.log('New File')
    }
  ];

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'p') {
        e.preventDefault();
        setIsOpen(true);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
      setSearch('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  const filteredCommands = commands.filter(cmd => 
    cmd.name.toLowerCase().includes(search.toLowerCase()) || 
    cmd.description.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    setSelectedIndex(0);
  }, [search]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, filteredCommands.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredCommands[selectedIndex]) {
        filteredCommands[selectedIndex].action();
        setIsOpen(false);
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[1000] flex items-start justify-center pt-[80px]">
      <motion.div 
        initial={{ opacity: 0 }} 
        animate={{ opacity: 1 }} 
        exit={{ opacity: 0 }} 
        transition={{ duration: 0.1 }}
        className="absolute inset-0 bg-black/40 backdrop-blur-sm" 
        onClick={() => setIsOpen(false)} 
      />
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.98, y: -10 }} 
        animate={{ opacity: 1, scale: 1, y: 0 }} 
        exit={{ opacity: 0, scale: 0.98, y: -10 }}
        transition={{ duration: 0.15, ease: "easeOut" }}
        className="relative w-full max-w-[520px] bg-[var(--color-bg-panel)] rounded-xl shadow-2xl border border-[var(--color-border-active)] overflow-hidden flex flex-col max-h-[600px]"
      >
        <div className="flex items-center px-4 py-3 border-b border-[var(--color-border-subtle)] bg-[var(--color-bg-background)]">
          <Search size={16} className="text-[var(--color-text-tertiary)] mr-3 shrink-0" />
          <input 
            ref={inputRef}
            value={search}
            onChange={e => setSearch(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a command or search..."
            className="flex-1 bg-transparent border-none outline-none text-[var(--color-text-primary)] text-[14px] placeholder-[var(--color-text-tertiary)]"
          />
          <span className="text-[10px] text-[var(--color-text-tertiary)] font-mono ml-3 border border-[var(--color-border-subtle)] px-1.5 py-0.5 rounded">ESC</span>
        </div>

        <div className="flex-1 overflow-y-auto py-2">
          {filteredCommands.length > 0 ? (
            filteredCommands.map((cmd, i) => (
              <div 
                key={cmd.id} 
                onClick={() => { cmd.action(); setIsOpen(false); }}
                className={`flex items-center justify-between px-4 py-2 cursor-pointer transition-colors ${i === selectedIndex ? 'bg-[var(--color-bg-hover)]' : 'hover:bg-[#ffffff05]'}`}
                onMouseEnter={() => setSelectedIndex(i)}
              >
                <div className="flex items-start gap-3 overflow-hidden">
                  <div className={`mt-0.5 ${i === selectedIndex ? 'text-[var(--color-accent)]' : 'text-[var(--color-text-secondary)]'}`}>
                    <cmd.icon size={16} />
                  </div>
                  <div className="flex flex-col overflow-hidden">
                    <span className={`text-[13px] font-medium truncate ${i === selectedIndex ? 'text-[var(--color-text-primary)]' : 'text-[var(--color-text-secondary)]'}`}>
                      {cmd.name}
                    </span>
                    <span className="text-[11px] text-[var(--color-text-tertiary)] truncate">
                      {cmd.description}
                    </span>
                  </div>
                </div>
                {cmd.shortcut && (
                  <span className="text-[11px] font-mono text-[var(--color-text-tertiary)] shrink-0 ml-4">
                    {cmd.shortcut}
                  </span>
                )}
              </div>
            ))
          ) : (
            <div className="px-4 py-8 text-center flex flex-col items-center gap-2">
              <Search size={24} className="text-[var(--color-text-tertiary)] opacity-50" />
              <span className="text-[13px] text-[var(--color-text-secondary)]">No commands found</span>
              <span className="text-[11px] text-[var(--color-text-tertiary)]">Try a different search term</span>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};
