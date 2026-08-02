import React, { useState } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Shield, Terminal, Globe, Database, Cpu, HardDrive, Settings } from 'lucide-react';

const permissions = [
  { id: 'fs', name: 'Filesystem', description: 'Allow Atlas to read and write files in your workspace.', icon: HardDrive, active: true },
  { id: 'term', name: 'Terminal', description: 'Allow Atlas to execute shell commands.', icon: Terminal, active: true },
  { id: 'net', name: 'Network', description: 'Allow Atlas to make HTTP requests.', icon: Globe, active: false },
  { id: 'mcp', name: 'MCP Servers', description: 'Connect to external Model Context Protocol servers.', icon: Database, active: true },
  { id: 'ext', name: 'Extensions', description: 'Enable third-party agent plugins.', icon: Cpu, active: false },
];

export const SettingsModal: React.FC<{ open: boolean; onOpenChange: (open: boolean) => void }> = ({ open, onOpenChange }) => {
  const [activeTab, setActiveTab] = useState('appearance');
  
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {open && (
          <Dialog.Portal forceMount>
            <Dialog.Overlay asChild>
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="fixed inset-0 z-[200] bg-black/60 backdrop-blur-sm"
              />
            </Dialog.Overlay>
            <Dialog.Content asChild>
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 10 }}
                transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
                className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-[200] w-full max-w-[800px] h-[600px] bg-[var(--color-bg-modal)] rounded-2xl shadow-[0_20px_60px_rgba(0,0,0,0.8)] border border-[var(--color-border-subtle)] flex overflow-hidden outline-none"
              >
                {/* Sidebar */}
                <div className="w-[220px] bg-[var(--color-bg-panel)] border-r border-[var(--color-border-subtle)] flex flex-col pt-6">
                  <div className="px-5 mb-4">
                    <h2 className="text-[13px] font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">Settings</h2>
                  </div>
                  <nav className="flex-1 px-3 space-y-1">
                    {['Appearance', 'Behavior', 'Keyboard', 'Advanced'].map(tab => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab.toLowerCase())}
                        className={`w-full text-left px-3 py-2 rounded-lg text-[13px] transition-colors outline-none ${
                          activeTab === tab.toLowerCase() 
                            ? 'bg-[var(--color-bg-selected)] text-[var(--color-text-primary)] font-medium' 
                            : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-hover)] hover:text-[var(--color-text-primary)]'
                        }`}
                      >
                        {tab}
                      </button>
                    ))}
                  </nav>
                </div>
                
                {/* Content */}
                <div className="flex-1 flex flex-col bg-[var(--color-bg-background)] relative">
                  <div className="h-14 flex items-center justify-between px-6 border-b border-[var(--color-border-subtle)] shrink-0 sticky top-0 bg-[var(--color-bg-background)]/80 backdrop-blur-md z-10">
                    <Dialog.Title className="text-[15px] font-medium text-[var(--color-text-primary)] capitalize">
                      {activeTab}
                    </Dialog.Title>
                    <Dialog.Close asChild>
                      <button className="w-8 h-8 flex items-center justify-center rounded-lg text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-hover)] transition-colors outline-none">
                        <X size={18} />
                      </button>
                    </Dialog.Close>
                  </div>
                  
                  <div className="flex-1 overflow-y-auto p-6 scrollbar-thin">
                    {activeTab === 'appearance' && (
                      <div className="space-y-6">
                         <div className="grid gap-3">
                           <div className="flex items-center justify-between p-4 rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)]">
                             <div>
                               <h4 className="text-[14px] font-medium text-[var(--color-text-primary)]">Dark Mode (Always)</h4>
                               <p className="text-[12px] text-[var(--color-text-tertiary)] mt-0.5">Force dark theme across the application.</p>
                             </div>
                             <button className="w-11 h-6 rounded-full bg-[var(--color-success)] transition-colors relative shrink-0">
                               <span className="absolute top-1 left-1 bg-white w-4 h-4 rounded-full translate-x-5 transition-transform" />
                             </button>
                           </div>
                           <div className="flex items-center justify-between p-4 rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)]">
                             <div>
                               <h4 className="text-[14px] font-medium text-[var(--color-text-primary)]">Font Size</h4>
                               <p className="text-[12px] text-[var(--color-text-tertiary)] mt-0.5">Base font size for the editor and terminal.</p>
                             </div>
                             <div className="flex items-center gap-2">
                                <button className="w-6 h-6 flex items-center justify-center rounded bg-[var(--color-bg-hover)] text-[var(--color-text-primary)]">-</button>
                                <span className="text-[13px] font-mono text-[var(--color-text-primary)] w-8 text-center">12px</span>
                                <button className="w-6 h-6 flex items-center justify-center rounded bg-[var(--color-bg-hover)] text-[var(--color-text-primary)]">+</button>
                             </div>
                           </div>
                           <div className="flex items-center justify-between p-4 rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)]">
                             <div>
                               <h4 className="text-[14px] font-medium text-[var(--color-text-primary)]">Sync Theme with System</h4>
                               <p className="text-[12px] text-[var(--color-text-tertiary)] mt-0.5">Automatically switch based on OS settings.</p>
                             </div>
                             <button className="w-11 h-6 rounded-full bg-[var(--color-bg-hover)] border border-[var(--color-border-subtle)] transition-colors relative shrink-0">
                               <span className="absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform" />
                             </button>
                           </div>
                         </div>
                      </div>
                    )}
                    
                    {activeTab === 'behavior' && (
                      <div className="space-y-6">
                         <div className="grid gap-3">
                           <div className="flex items-center justify-between p-4 rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)]">
                             <div>
                               <h4 className="text-[14px] font-medium text-[var(--color-text-primary)]">Confirm on Quit</h4>
                               <p className="text-[12px] text-[var(--color-text-tertiary)] mt-0.5">Ask for confirmation before exiting Atlas.</p>
                             </div>
                             <button className="w-11 h-6 rounded-full bg-[var(--color-success)] transition-colors relative shrink-0">
                               <span className="absolute top-1 left-1 bg-white w-4 h-4 rounded-full translate-x-5 transition-transform" />
                             </button>
                           </div>
                           <div className="flex items-center justify-between p-4 rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)]">
                             <div>
                               <h4 className="text-[14px] font-medium text-[var(--color-text-primary)]">Show Notifications</h4>
                               <p className="text-[12px] text-[var(--color-text-tertiary)] mt-0.5">Display toast notifications for agent actions.</p>
                             </div>
                             <button className="w-11 h-6 rounded-full bg-[var(--color-success)] transition-colors relative shrink-0">
                               <span className="absolute top-1 left-1 bg-white w-4 h-4 rounded-full translate-x-5 transition-transform" />
                             </button>
                           </div>
                           <div className="flex items-center justify-between p-4 rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)]">
                             <div>
                               <h4 className="text-[14px] font-medium text-[var(--color-text-primary)]">Agent Timeout</h4>
                               <p className="text-[12px] text-[var(--color-text-tertiary)] mt-0.5">Maximum time an agent can run without input.</p>
                             </div>
                             <select className="bg-[var(--color-bg-hover)] border border-[var(--color-border-subtle)] text-[13px] text-[var(--color-text-primary)] rounded px-2 py-1 outline-none">
                                <option>5 min</option>
                                <option>15 min</option>
                                <option>30 min</option>
                             </select>
                           </div>
                         </div>
                      </div>
                    )}

                    {['keyboard', 'advanced'].includes(activeTab) && (
                      <div className="flex flex-col items-center justify-center h-full text-[var(--color-text-tertiary)] gap-4 pb-12">
                        <Settings size={32} />
                        <p className="text-[14px]">Settings for {activeTab} are coming soon.</p>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            </Dialog.Content>
          </Dialog.Portal>
        )}
      </AnimatePresence>
    </Dialog.Root>
  );
};
