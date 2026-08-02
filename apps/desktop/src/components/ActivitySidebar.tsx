import React from 'react';
import { MessageSquare, Folder, Terminal, Globe, BrainCircuit, PlaySquare } from 'lucide-react';
import { useStore } from '../store/useStore';

export const ActivitySidebar: React.FC = () => {
  const { activitySidebarSelection, setActivitySidebarSelection, workspaceOpen, setWorkspaceOpen } = useStore();

  const handleSelect = (id: string) => {
    if (activitySidebarSelection === id && workspaceOpen) {
      setWorkspaceOpen(false);
    } else {
      setActivitySidebarSelection(id);
      setWorkspaceOpen(true);
    }
  };

  return (
    <div className="w-[48px] h-full bg-[var(--color-bg-background)] border-r border-[var(--color-border-subtle)] flex flex-col items-center py-2 gap-4 shrink-0 z-50">
      <SidebarIcon id="chat" onClick={() => handleSelect('chat')} icon={<MessageSquare size={24} />} active={activitySidebarSelection === 'chat'} tooltip="Chat" />
      <SidebarIcon id="files" onClick={() => handleSelect('files')} icon={<Folder size={24} />} active={activitySidebarSelection === 'files'} tooltip="Files" />
      <SidebarIcon id="browser" onClick={() => handleSelect('browser')} icon={<Globe size={24} />} active={activitySidebarSelection === 'browser'} tooltip="Browser" />
      <SidebarIcon id="terminal" onClick={() => handleSelect('terminal')} icon={<Terminal size={24} />} active={activitySidebarSelection === 'terminal'} tooltip="Terminal" />
      <SidebarIcon id="memory" onClick={() => handleSelect('memory')} icon={<BrainCircuit size={24} />} active={activitySidebarSelection === 'memory'} tooltip="Memory" />
      <div className="flex-1" />
      <SidebarIcon id="agents" onClick={() => handleSelect('agents')} icon={<PlaySquare size={24} />} active={activitySidebarSelection === 'agents'} tooltip="Agents" />
    </div>
  );
};

const SidebarIcon: React.FC<{ id: string, icon: React.ReactNode, active?: boolean, tooltip: string, onClick: () => void }> = ({ icon, active, tooltip, onClick }) => {
  return (
    <div className="relative group flex items-center justify-center w-full">
      <div className={`w-[2px] h-8 absolute left-0 transition-colors ${active ? 'bg-[var(--color-accent)]' : 'bg-transparent'}`} />
      <button onClick={onClick} className={`w-10 h-10 flex items-center justify-center rounded-lg transition-colors ${active ? 'text-[var(--color-text-primary)]' : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-hover)]'}`}>
        {icon}
      </button>
      {/* Tooltip */}
      <div className="absolute left-[54px] top-1/2 -translate-y-1/2 bg-[var(--color-bg-tooltip)] text-[var(--color-text-primary)] text-[11px] px-2 py-1 rounded shadow-lg border border-[var(--color-border-active)] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
        {tooltip}
      </div>
    </div>
  );
};
