import React from 'react';
import { useStore } from '../store/useStore';
import { X, FileText, Clock, User, Shield, Image, Hash } from 'lucide-react';

export const InfoSidebar: React.FC = () => {
  const { activitySidebarSelection, setWorkspaceOpen } = useStore();

  return (
    <div className="w-full h-full bg-[var(--color-bg-panel)] flex flex-col border-l border-[var(--color-border-subtle)] overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-[var(--color-border-subtle)] shrink-0">
        <div className="flex items-center gap-2 text-[var(--color-text-primary)]">
          {activitySidebarSelection === 'files' ? <FileText size={16} /> : <Hash size={16} />}
          <span className="text-[13px] font-medium capitalize">{activitySidebarSelection} Properties</span>
        </div>
        <button 
          onClick={() => setWorkspaceOpen(false)}
          className="w-6 h-6 flex items-center justify-center rounded hover:bg-[var(--color-bg-hover)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
        >
          <X size={14} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-hidden p-3 scrollbar-thin flex flex-col gap-4">
        {/* Metadata Section */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between text-[12px]">
            <span className="text-[var(--color-text-tertiary)] font-mono">Type:</span>
            <span className="text-[var(--color-text-secondary)] capitalize">{activitySidebarSelection}</span>
          </div>
          <div className="flex items-center justify-between text-[12px]">
            <span className="text-[var(--color-text-tertiary)] font-mono flex items-center gap-1"><Clock size={12}/> Modified:</span>
            <span className="text-[var(--color-text-secondary)]">Just now</span>
          </div>
          <div className="flex items-center justify-between text-[12px]">
            <span className="text-[var(--color-text-tertiary)] font-mono flex items-center gap-1"><User size={12}/> Owner:</span>
            <span className="text-[var(--color-text-secondary)]">current_user</span>
          </div>
        </div>

        <div className="w-full h-px bg-[var(--color-border-subtle)]" />

        {/* Details Section */}
        <div className="flex flex-col gap-2">
          <h4 className="text-[12px] font-medium text-[var(--color-text-primary)] uppercase tracking-wider mb-1">Details</h4>
          <div className="bg-[var(--color-bg-background)] border border-[var(--color-border-subtle)] rounded-lg p-2 flex flex-col gap-1">
            {activitySidebarSelection === 'chat' && (
              <>
                <span className="text-[11px] text-[var(--color-text-secondary)]">Model: Claude 3.5 Sonnet</span>
                <span className="text-[11px] text-[var(--color-text-secondary)]">Tokens: ~1.2K</span>
              </>
            )}
            {activitySidebarSelection === 'files' && (
              <>
                <span className="text-[11px] text-[var(--color-text-secondary)] flex items-center gap-1"><Shield size={10}/> Permissions: rw-r--r--</span>
                <span className="text-[11px] text-[var(--color-text-secondary)] flex items-center gap-1"><FileText size={10}/> Size: 1.2 KB</span>
              </>
            )}
            {activitySidebarSelection === 'terminal' && (
              <>
                <span className="text-[11px] text-[var(--color-text-secondary)]">PID: 1234 (bash)</span>
                <span className="text-[11px] text-[var(--color-text-secondary)]">Status: Running</span>
              </>
            )}
            {activitySidebarSelection === 'browser' && (
              <>
                <span className="text-[11px] text-[var(--color-text-secondary)]">URL: https://google.com</span>
                <span className="text-[11px] text-[var(--color-success)] flex items-center gap-1"><Shield size={10}/> Secure Connection</span>
              </>
            )}
            {!['chat', 'files', 'terminal', 'browser'].includes(activitySidebarSelection) && (
              <span className="text-[11px] text-[var(--color-text-secondary)]">No specific details available.</span>
            )}
          </div>
        </div>

        <div className="w-full h-px bg-[var(--color-border-subtle)]" />

        {/* Related Items */}
        <div className="flex flex-col gap-2">
          <h4 className="text-[12px] font-medium text-[var(--color-text-primary)] uppercase tracking-wider mb-1">Related Items</h4>
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2 text-[12px] text-[var(--color-accent)] hover:underline cursor-pointer group">
              <span className="text-[10px] text-[var(--color-text-tertiary)] group-hover:text-[var(--color-accent)]">▶</span> Files (2)
            </div>
            <div className="flex items-center gap-2 text-[12px] text-[var(--color-accent)] hover:underline cursor-pointer group">
              <span className="text-[10px] text-[var(--color-text-tertiary)] group-hover:text-[var(--color-accent)]">▶</span> Tasks (1)
            </div>
          </div>
        </div>

        <div className="w-full h-px bg-[var(--color-border-subtle)]" />

        {/* Actions */}
        <div className="flex flex-col gap-2 mt-auto">
          <button className="w-full py-1.5 bg-[var(--color-bg-hover)] hover:bg-[var(--color-bg-selected)] text-[var(--color-text-primary)] text-[12px] rounded border border-[var(--color-border-subtle)] transition-colors">
            Export Data
          </button>
          <button className="w-full py-1.5 bg-[var(--color-danger-transparent)] hover:bg-red-900/40 text-[var(--color-danger)] text-[12px] rounded border border-red-900/30 transition-colors">
            Delete Item
          </button>
        </div>
      </div>
    </div>
  );
};
