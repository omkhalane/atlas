import React from 'react';
import { useStore } from '../store/useStore';
import type { Pane, Tab } from '../store/useStore';
import { X, MessageSquare, Terminal, Globe, FileCode2, BrainCircuit, Columns } from 'lucide-react';
import { motion } from 'framer-motion';

const getTabIcon = (type: string) => {
  switch (type) {
    case 'chat': return <MessageSquare size={13} />;
    case 'terminal': return <Terminal size={13} />;
    case 'browser': return <Globe size={13} />;
    case 'file': return <FileCode2 size={13} />;
    case 'memory': return <BrainCircuit size={13} />;
    default: return <FileCode2 size={13} />;
  }
};

export const TabSystem: React.FC<{ pane: Pane }> = ({ pane }) => {
  const { activePaneId, setActivePaneId, closeTab, splitPane } = useStore();
  const isActivePane = activePaneId === pane.id;

  return (
    <div 
      className={`flex flex-col h-full bg-[var(--color-bg-background)] ${isActivePane ? 'ring-1 ring-inset ring-[var(--color-border-active)]' : ''}`}
      onClick={() => !isActivePane && setActivePaneId(pane.id)}
    >
      <div className="flex items-center h-[36px] bg-[var(--color-bg-panel)] border-b border-[var(--color-border-subtle)] overflow-x-auto overflow-y-hidden shrink-0 pl-1 pr-2">
        {pane.tabs.map((tab: Tab) => {
          const isActive = pane.activeTabId === tab.id;
          return (
            <div
              key={tab.id}
              onClick={() => {
                const panes = useStore.getState().panes;
                const newPanes = panes.map(p => p.id === pane.id ? { ...p, activeTabId: tab.id } : p);
                const updates: any = { panes: newPanes, activePaneId: pane.id };
                if (tab.type === 'chat' && tab.data?.convId) {
                  updates.activeConversationId = tab.data.convId;
                }
                useStore.setState(updates);
              }}
              className={`group flex items-center h-[28px] min-w-[120px] max-w-[200px] px-3 mt-2 mx-0.5 rounded-t-lg cursor-pointer transition-colors relative ${
                isActive 
                  ? 'bg-[var(--color-bg-background)] text-[var(--color-text-primary)] border-t border-l border-r border-[var(--color-border-subtle)] border-b-transparent z-10' 
                  : 'bg-transparent text-[var(--color-text-secondary)] hover:bg-[#ffffff08] border border-transparent'
              }`}
            >
              <div className={`mr-2 ${isActive ? 'text-[var(--color-accent)]' : 'text-[var(--color-text-tertiary)] group-hover:text-[var(--color-text-secondary)]'}`}>
                {getTabIcon(tab.type)}
              </div>
              <span className="text-[12px] font-medium truncate flex-1 select-none">{tab.title}</span>
              <button 
                onClick={(e) => { e.stopPropagation(); closeTab(pane.id, tab.id); }}
                className={`ml-2 p-0.5 rounded transition-colors ${isActive ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'} hover:bg-[var(--color-bg-hover)] hover:text-[var(--color-danger)] text-[var(--color-text-tertiary)]`}
              >
                <X size={12} />
              </button>
            </div>
          );
        })}
        
        {pane.tabs.length === 0 && (
           <div className="text-[11px] text-[var(--color-text-tertiary)] italic px-3 select-none">Empty pane</div>
        )}

        <div className="flex-1" />
        
        {/* Pane Actions */}
        <div className="flex items-center gap-1 opacity-50 hover:opacity-100 transition-opacity">
           <button 
             onClick={(e) => { e.stopPropagation(); splitPane(pane.id, 'horizontal'); }}
             className="p-1.5 rounded hover:bg-[var(--color-bg-hover)] text-[var(--color-text-secondary)] tooltip-trigger"
             title="Split Right"
           >
             <Columns size={13} />
           </button>
        </div>
      </div>
      
      {/* Pane Content */}
      <div className="flex-1 relative overflow-hidden bg-[var(--color-bg-background)]">
        {pane.tabs.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-[var(--color-text-tertiary)] text-[13px]">
            Press Ctrl+P to open a command or select an item from the sidebar.
          </div>
        ) : (
          pane.tabs.map(tab => {
            const isActive = tab.id === pane.activeTabId;
            return (
              <div 
                key={tab.id} 
                className={`absolute inset-0 transition-opacity duration-200 ${isActive ? 'opacity-100 pointer-events-auto z-10' : 'opacity-0 pointer-events-none z-0'}`}
              >
                {/* Dynamically render content based on tab type */}
                {tab.type === 'chat' && <ChatWrapper tab={tab} />}
                {tab.type === 'terminal' && <TerminalWrapper tab={tab} />}
                {tab.type === 'browser' && <BrowserWrapper tab={tab} />}
                {tab.type === 'file' && <EditorWrapper tab={tab} />}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

// Quick wrappers to avoid circular deps with existing components
import { Conversation } from './Conversation';
import { PromptBox } from './PromptBox';
import { TerminalView } from './TerminalView';
import { BrowserView } from './BrowserView';
import { EditorView } from './EditorView';

const ChatWrapper: React.FC<{tab: Tab}> = ({ tab }) => {
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-hidden relative">
        <Conversation convId={tab.data?.convId} />
      </div>
      <PromptBox convId={tab.data?.convId} />
    </div>
  );
};

const TerminalWrapper: React.FC<{tab: Tab}> = ({ tab }) => {
  return <TerminalView />;
};

const BrowserWrapper: React.FC<{tab: Tab}> = ({ tab }) => {
  return <BrowserView />;
};

const EditorWrapper: React.FC<{tab: Tab}> = ({ tab }) => {
  return <EditorView />;
};
