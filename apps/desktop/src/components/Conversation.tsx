import React, { useEffect, useRef, useState } from 'react';
import { useStore } from '../store/useStore';
import { motion } from 'framer-motion';
import { Sparkles, TerminalSquare, Database, Globe, PackageOpen, Check, Copy } from 'lucide-react';
import { Virtuoso } from 'react-virtuoso';
import type { VirtuosoHandle } from 'react-virtuoso';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const CodeBlock = ({ node, inline, className, children, ...props }: any) => {
  const match = /language-(\w+)/.exec(className || '');
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(String(children).replace(/\n$/, ''));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!inline && match) {
    return (
      <div className="relative group rounded-xl overflow-hidden my-4 border border-[var(--color-border-subtle)] bg-[var(--color-bg-card)]">
        <div className="flex items-center justify-between px-4 py-2 bg-[var(--color-bg-panel)] border-b border-[var(--color-border-subtle)]">
          <span className="text-xs font-mono text-[var(--color-text-secondary)] uppercase">{match[1]}</span>
          <button 
            onClick={handleCopy}
            className="text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] transition-colors p-1 rounded"
          >
            {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
          </button>
        </div>
        <SyntaxHighlighter
          style={vscDarkPlus as any}
          language={match[1]}
          PreTag="div"
          customStyle={{ margin: 0, padding: '1rem', background: 'transparent', fontSize: '13px' }}
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      </div>
    );
  }
  return (
    <code className="bg-[var(--color-bg-hover)] text-[var(--color-text-primary)] px-1.5 py-0.5 rounded-md font-mono text-[13px]" {...props}>
      {children}
    </code>
  );
};

export const Conversation: React.FC<{ convId?: string }> = ({ convId }) => {
  const { conversations, activeConversationId, isExecuting } = useStore();
  const idToUse = convId || activeConversationId;
  const activeConv = conversations.find(c => c.id === idToUse);
  const events = activeConv ? activeConv.events : [];
  const virtuosoRef = useRef<VirtuosoHandle>(null);

  useEffect(() => {
    if (events.length > 0) {
      setTimeout(() => {
        virtuosoRef.current?.scrollToIndex({ index: events.length - 1, align: 'end', behavior: 'smooth' });
      }, 50);
    }
  }, [events.length]);

  const getIconForCapability = (action: string) => {
    switch (action) {
      case 'filesystem': return <Database size={16} />;
      case 'command': return <TerminalSquare size={16} />;
      case 'browser': return <Globe size={16} />;
      default: return <PackageOpen size={16} />;
    }
  };

  const renderItem = (_index: number, ev: any) => {
    return (
      <div className={`w-full flex ${ev.type === 'user_prompt' ? 'justify-end' : 'justify-start'} py-2`}>
        <div className="max-w-[800px] w-full flex flex-col">
          {ev.type === 'user_prompt' && (
            <div className="self-end bg-[var(--color-bg-hover)] text-[var(--color-text-primary)] px-5 py-3.5 rounded-[4px] max-w-[70%] text-[15px] border-l border-[var(--color-accent)] shadow-sm flex flex-col gap-1">
              <div className="flex justify-between items-center w-full mb-1">
                 <span className="text-[12px] font-medium text-white">User</span>
                 <span className="text-[10px] text-[var(--color-text-tertiary)]">Just now</span>
              </div>
              <div className="text-left leading-relaxed">
                {ev.content}
              </div>
            </div>
          )}
          
          {ev.type === 'thought' && (
            <div className="flex flex-col border border-[var(--color-border-subtle)] bg-[var(--color-bg-card)] rounded-lg my-2 max-w-[85%] ml-4 overflow-hidden">
               <div className="flex items-center gap-2 px-3 py-2 bg-[var(--color-bg-panel)] border-b border-[var(--color-border-subtle)] cursor-pointer hover:bg-[var(--color-bg-hover)]">
                 <Sparkles size={14} className="text-[var(--color-accent)]" /> 
                 <span className="text-[12px] font-medium text-[var(--color-text-secondary)]">Thinking...</span>
               </div>
               <div className="p-3 text-[13px] text-[var(--color-text-secondary)] leading-relaxed prose prose-invert max-w-none">
                 <ReactMarkdown>{ev.content}</ReactMarkdown>
               </div>
            </div>
          )}
          
          {ev.type === 'action' && (
            <div className="flex flex-col border border-[var(--color-border-subtle)] bg-[var(--color-bg-panel)] rounded-lg my-2 max-w-[85%] ml-4 overflow-hidden">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-[var(--color-border-subtle)]">
                {getIconForCapability(ev.action || '')}
                <span className="text-[13px] font-medium text-[var(--color-text-primary)] capitalize">Task: {ev.action}</span>
                <div className="ml-auto flex items-center gap-2">
                   <span className="text-[11px] text-[var(--color-accent)]">Running</span>
                   <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-accent)] animate-pulse" />
                </div>
              </div>
            </div>
          )}

          {ev.type === 'observation' && (
            <div className="ml-10 w-full max-w-[700px] my-1">
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border-subtle)] rounded-xl p-4 max-h-[250px] overflow-y-auto text-[12px] text-[var(--color-text-secondary)] font-mono leading-relaxed shadow-sm scrollbar-thin">
                <pre className="whitespace-pre-wrap">{ev.content}</pre>
              </div>
            </div>
          )}
          
          {ev.type === 'error' && (
            <div className="ml-10 text-[var(--color-danger)] text-sm flex items-center gap-2 bg-red-950/20 px-4 py-3 rounded-xl border border-red-900/30 w-max my-2">
              <span className="w-2 h-2 rounded-full bg-[var(--color-danger)] shrink-0" />
              <span className="font-mono text-[13px]">{ev.error}</span>
            </div>
          )}

          {ev.type === 'finish' && (
            <div className="flex flex-col border border-[var(--color-border-subtle)] bg-[var(--color-bg-panel)] rounded-lg my-4 max-w-[85%] ml-4 overflow-hidden">
               <div className="flex items-center gap-2 px-3 py-2 border-b border-[var(--color-border-subtle)] bg-[var(--color-bg-card)]">
                  <Check size={14} className="text-[var(--color-success)]" />
                  <span className="text-[12px] font-medium text-white uppercase tracking-wider">Task Complete</span>
               </div>
               <div className="px-4 py-3 flex flex-col gap-2">
                  <div className="text-[13px] text-[var(--color-text-secondary)]">The agent has successfully completed the requested task.</div>
                  <div className="flex gap-2 mt-2">
                     <button className="px-3 py-1.5 bg-[var(--color-bg-hover)] hover:bg-[var(--color-bg-selected)] text-[var(--color-text-primary)] text-[12px] rounded border border-[var(--color-border-subtle)] transition-colors">
                       View Changes
                     </button>
                  </div>
               </div>
            </div>
          )}
          
          {/* Default markdown for normal assistant responses (if any) */}
          {ev.type === 'message' && (
            <div className="flex flex-col gap-1 ml-4 mt-2">
              <div className="flex items-center gap-2 text-[12px] text-[var(--color-text-tertiary)] mb-1">
                 <span className="font-medium text-[var(--color-text-secondary)]">Agent (Claude 3.5)</span>
                 <span>Just now</span>
              </div>
              <div className="prose prose-invert max-w-none text-[14px] leading-relaxed prose-pre:bg-transparent prose-pre:p-0 prose-pre:m-0 text-[var(--color-text-primary)]">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={{ code: CodeBlock }}>
                  {ev.content}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="flex-1 h-full flex flex-col relative overflow-hidden bg-[var(--color-bg-background)]">
      {events.length === 0 && !isExecuting ? (
        <div className="flex-1 flex flex-col items-center justify-center -mt-20">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }} 
            animate={{ opacity: 1, scale: 1 }} 
            transition={{ delay: 0.1, duration: 0.4 }}
            className="flex flex-col items-center text-center gap-5"
          >
            <div className="w-20 h-20 rounded-[24px] bg-[var(--color-bg-panel)] flex items-center justify-center border border-[var(--color-border-subtle)] shadow-[0_10px_40px_rgba(0,0,0,0.5)]">
               <Sparkles className="text-[var(--color-text-primary)]" size={32} strokeWidth={1.5} />
            </div>
            <h1 className="text-[28px] font-medium text-[var(--color-text-primary)] tracking-tight">Your AI Operating System</h1>
            <p className="text-[var(--color-text-secondary)] text-[16px] max-w-md">Files. Browser. Terminal. Memory. Plugins. All in one place.</p>
          </motion.div>
        </div>
      ) : (
        <Virtuoso
          ref={virtuosoRef}
          data={events}
          itemContent={renderItem}
          className="w-full h-full pb-32 pt-8 px-8 lg:px-20"
          followOutput="smooth"
        />
      )}
    </div>
  );
};
