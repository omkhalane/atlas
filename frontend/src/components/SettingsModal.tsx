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
  const [activeTab, setActiveTab] = useState('permissions');
  
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
                    {['General', 'Permissions', 'Models', 'Appearance', 'Advanced'].map(tab => (
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
                    {activeTab === 'permissions' && (
                      <div className="space-y-6">
                        <div className="flex items-center gap-3 text-[var(--color-text-secondary)] bg-[var(--color-bg-panel)] p-4 rounded-xl border border-[var(--color-border-subtle)]">
                          <Shield className="text-[var(--color-warning)]" size={24} />
                          <div>
                            <h3 className="text-[14px] font-medium text-[var(--color-text-primary)]">Security Controls</h3>
                            <p className="text-[13px] mt-0.5">Manage what Atlas is allowed to do on your machine.</p>
                          </div>
                        </div>

                        <div className="grid gap-3">
                          {permissions.map(perm => (
                            <div key={perm.id} className="flex items-center justify-between p-4 rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)] hover:border-[var(--color-border-active)] transition-colors group cursor-pointer">
                              <div className="flex items-center gap-4">
                                <div className="w-10 h-10 rounded-lg bg-[var(--color-bg-hover)] flex items-center justify-center group-hover:bg-[var(--color-bg-selected)] transition-colors">
                                  <perm.icon size={18} className="text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-primary)]" />
                                </div>
                                <div>
                                  <h4 className="text-[14px] font-medium text-[var(--color-text-primary)]">{perm.name}</h4>
                                  <p className="text-[12px] text-[var(--color-text-tertiary)] mt-0.5">{perm.description}</p>
                                </div>
                              </div>
                              <button 
                                className={`w-11 h-6 rounded-full transition-colors relative shrink-0 ${perm.active ? 'bg-[var(--color-success)]' : 'bg-[var(--color-bg-hover)] border border-[var(--color-border-subtle)]'}`}
                              >
                                <span className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${perm.active ? 'translate-x-5' : 'translate-x-0'}`} />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {activeTab !== 'permissions' && (
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
