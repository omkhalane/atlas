import React from 'react';
import { Minus, Square, X } from 'lucide-react';

export const Titlebar: React.FC = () => {
  return (
    <div 
      className="h-10 bg-black flex items-center justify-between px-3 select-none app-drag-region border-b border-[#ffffff04] z-50 shrink-0"
      onDoubleClick={() => {/* Toggle maximize if native API available */}}
    >
      <div className="flex items-center gap-2 px-2">
        <div className="w-5 h-5 rounded-md bg-[#1a1a1a] flex items-center justify-center border border-[#ffffff0a] shadow-[0_0_10px_rgba(255,255,255,0.05)]">
          <img src="/favicon.svg" alt="Atlas" className="w-3.5 h-3.5 opacity-90 drop-shadow-[0_0_10px_rgba(255,255,255,0.2)]" />
        </div>
        <span className="text-[12px] font-medium text-[var(--color-text-secondary)] tracking-wide">ATLAS</span>
      </div>
      
      <div className="flex items-center gap-1 app-no-drag">
        <button className="w-8 h-8 flex items-center justify-center rounded-md text-[#525252] hover:text-[#F5F5F5] hover:bg-[#121212] transition-colors">
          <Minus size={14} strokeWidth={2} />
        </button>
        <button className="w-8 h-8 flex items-center justify-center rounded-md text-[#525252] hover:text-[#F5F5F5] hover:bg-[#121212] transition-colors">
          <Square size={12} strokeWidth={2} />
        </button>
        <button className="w-8 h-8 flex items-center justify-center rounded-md text-[#525252] hover:text-white hover:bg-red-500/90 transition-colors">
          <X size={14} strokeWidth={2} />
        </button>
      </div>
    </div>
  );
};
