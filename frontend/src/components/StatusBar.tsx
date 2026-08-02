import React from 'react';
import { CheckCircle2, Activity, HardDrive, Database, Box } from 'lucide-react';

export const StatusBar: React.FC = () => {
  return (
    <div className="h-8 bg-[#050505] border-t border-[#ffffff04] flex items-center justify-between px-4 shrink-0 text-[11px] font-mono text-[#525252] select-none z-50">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 hover:text-[#F5F5F5] transition-colors cursor-pointer">
          <CheckCircle2 size={12} className="text-green-500/70" />
          <span>Ready</span>
        </div>
        
        <div className="flex items-center gap-1.5 hover:text-[#F5F5F5] transition-colors cursor-pointer">
          <Database size={12} />
          <span>Memory OK</span>
        </div>
        
        <div className="flex items-center gap-1.5 hover:text-[#F5F5F5] transition-colors cursor-pointer">
          <Box size={12} />
          <span>MCP: 3 active</span>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 hover:text-[#F5F5F5] transition-colors cursor-pointer">
          <HardDrive size={12} />
          <span>Workspace: Local</span>
        </div>
        
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-sm bg-[#121212] border border-[#ffffff08] hover:border-[#ffffff15] text-[#8C8C8C] transition-colors cursor-pointer">
          <Activity size={12} className="text-orange-500/70" />
          <span>Gemini 3.1 Pro</span>
        </div>
      </div>
    </div>
  );
};
