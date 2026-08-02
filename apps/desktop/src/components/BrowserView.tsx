import React, { useState } from 'react';
import { ArrowLeft, ArrowRight, RotateCw, Search, X, Globe, Menu, Shield } from 'lucide-react';

export const BrowserView: React.FC = () => {
  const [url, setUrl] = useState('https://google.com');
  const [inputValue, setInputValue] = useState('google.com');

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      let finalUrl = inputValue;
      if (!finalUrl.startsWith('http')) {
        finalUrl = 'https://' + finalUrl;
      }
      setUrl(finalUrl);
      setInputValue(finalUrl.replace('https://', ''));
    }
  };

  return (
    <div className="flex-1 h-full flex flex-col bg-white overflow-hidden">
      {/* Browser Tabs */}
      <div className="h-[32px] flex items-center bg-[var(--color-bg-background)] border-b border-[var(--color-border-subtle)] shrink-0 px-2 pt-1 gap-1">
         <div className="flex items-center h-full px-3 gap-2 bg-[var(--color-bg-panel)] border-t border-l border-r border-[var(--color-border-subtle)] rounded-t-md min-w-[150px] max-w-[200px] cursor-pointer group">
            <Globe size={14} className="text-[var(--color-accent)]" />
            <span className="text-[12px] truncate flex-1 text-[var(--color-text-primary)]">Google</span>
            <button className="p-0.5 rounded opacity-0 group-hover:opacity-100 hover:bg-[var(--color-bg-hover)] text-[var(--color-text-secondary)] hover:text-white">
              <X size={12} />
            </button>
         </div>
         <div className="flex items-center h-full px-3 gap-2 hover:bg-[var(--color-bg-hover)] rounded-t-md min-w-[150px] max-w-[200px] cursor-pointer group">
            <Globe size={14} className="text-[var(--color-text-tertiary)]" />
            <span className="text-[12px] truncate flex-1 text-[var(--color-text-secondary)]">GitHub</span>
         </div>
      </div>

      {/* Browser Navbar */}
      <div className="h-[40px] flex items-center bg-[var(--color-bg-panel)] border-b border-[var(--color-border-subtle)] px-2 gap-2 shrink-0">
        <div className="flex items-center gap-1">
           <button className="w-7 h-7 flex items-center justify-center rounded hover:bg-[var(--color-bg-hover)] text-[var(--color-text-secondary)]">
             <ArrowLeft size={16} />
           </button>
           <button className="w-7 h-7 flex items-center justify-center rounded hover:bg-[var(--color-bg-hover)] text-[var(--color-text-secondary)] opacity-50 cursor-not-allowed">
             <ArrowRight size={16} />
           </button>
           <button className="w-7 h-7 flex items-center justify-center rounded hover:bg-[var(--color-bg-hover)] text-[var(--color-text-secondary)]">
             <RotateCw size={14} />
           </button>
        </div>

        {/* Address Bar */}
        <div className="flex-1 max-w-3xl flex items-center bg-[var(--color-bg-background)] border border-[var(--color-border-subtle)] rounded-full h-7 px-3 gap-2 group focus-within:border-[var(--color-accent)] focus-within:ring-1 focus-within:ring-[var(--color-accent)]">
           <Shield size={14} className="text-green-500" />
           <input 
             type="text" 
             value={inputValue}
             onChange={(e) => setInputValue(e.target.value)}
             onKeyDown={handleKeyDown}
             className="flex-1 bg-transparent border-none outline-none text-[13px] text-[var(--color-text-primary)] font-mono"
             placeholder="Search or enter web address"
           />
        </div>

        <div className="flex items-center gap-1 ml-auto">
           <button className="w-7 h-7 flex items-center justify-center rounded hover:bg-[var(--color-bg-hover)] text-[var(--color-text-secondary)]">
             <Menu size={16} />
           </button>
        </div>
      </div>
      
      {/* Agent Status Bar (Optional, for demo) */}
      <div className="h-8 bg-[#00A8E8]/10 border-b border-[#00A8E8]/30 flex items-center px-4 gap-2 shrink-0">
         <span className="w-2 h-2 rounded-full bg-[var(--color-accent)] animate-pulse" />
         <span className="text-[12px] font-medium text-[var(--color-text-primary)]">Agent Navigating...</span>
         <span className="text-[12px] text-[var(--color-text-secondary)] ml-2">Currently inspecting search results</span>
         
         <div className="ml-auto flex items-center gap-2">
            <button className="px-2 py-1 bg-[var(--color-bg-hover)] text-[11px] rounded border border-[var(--color-border-subtle)] hover:bg-[var(--color-bg-selected)] text-[var(--color-text-primary)] transition-colors">
              Pause
            </button>
            <button className="px-2 py-1 bg-[var(--color-danger-transparent)] text-[11px] rounded border border-red-900/30 text-[var(--color-danger)] hover:bg-red-900/40 transition-colors">
              Stop
            </button>
         </div>
      </div>

      {/* Browser Viewport */}
      <div className="flex-1 relative bg-white">
         <iframe 
           src={url}
           title="Browser Viewport"
           className="w-full h-full border-none"
           sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
           onError={(e) => console.log('Iframe load error', e)}
         />
      </div>
    </div>
  );
};
