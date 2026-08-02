import React from 'react';
import { Minus, Square, X } from 'lucide-react';

export const Titlebar: React.FC = () => {
  const handleMinimize = () => (window as any).electronAPI?.windowMinimize();
  const handleMaximize = () => (window as any).electronAPI?.windowMaximize();
  const handleClose = () => (window as any).electronAPI?.windowClose();

  return (
    <div 
      className="h-8 bg-[var(--color-bg-background)] flex items-center justify-between px-2 select-none app-drag-region z-50 shrink-0"
      onDoubleClick={handleMaximize}
    >
      <div className="flex items-center gap-2 px-2">
        <div className="w-5 h-5 rounded-md bg-[#1a1a1a] flex items-center justify-center border border-[#ffffff0a] shadow-[0_0_10px_rgba(255,255,255,0.05)]">
          <img src="/favicon.svg" alt="Atlas" className="w-3.5 h-3.5 opacity-90 drop-shadow-[0_0_10px_rgba(255,255,255,0.2)]" />
        </div>
        <span className="text-[12px] font-medium text-[var(--color-text-secondary)] tracking-wide">ATLAS</span>
      </div>
      
      <div className="flex items-center gap-0 app-no-drag">
        <button onClick={handleMinimize} className="w-8 h-8 flex items-center justify-center rounded text-[var(--color-text-secondary)] hover:text-white hover:bg-[var(--color-bg-hover)] transition-colors">
          <Minus size={14} strokeWidth={2} />
        </button>
        <button onClick={handleMaximize} className="w-8 h-8 flex items-center justify-center rounded text-[var(--color-text-secondary)] hover:text-white hover:bg-[var(--color-bg-hover)] transition-colors">
          <Square size={12} strokeWidth={2} />
        </button>
        <button onClick={handleClose} className="w-8 h-8 flex items-center justify-center rounded text-[var(--color-text-secondary)] hover:text-white hover:bg-red-500 transition-colors">
          <X size={14} strokeWidth={2} />
        </button>
      </div>
    </div>
  );
};
