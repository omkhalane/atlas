import React, { useState } from 'react';
import { 
  MessageSquarePlus, 
  Settings, 
  Folder as FolderIcon, 
  ChevronRight, 
  Hash,
  Search,
  Plus,
  Trash2,
  FolderPlus
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useStore } from '../store/useStore';
import type { Conversation } from '../store/useStore';
import { SettingsModal } from './SettingsModal';

export const Sidebar: React.FC = () => {
  const { folders, conversations, createConversation, createFolder, deleteFolder, deleteConversation, setActiveConversation, activeConversationId } = useStore();
  
  const [expandedFolders, setExpandedFolders] = useState<Record<string, boolean>>({});
  const [settingsOpen, setSettingsOpen] = useState(false);

  const toggleFolder = (id: string) => setExpandedFolders(prev => ({ ...prev, [id]: !prev[id] }));

  const handleNewConversation = () => {
    createConversation(null);
  };

  const handleNewFolder = () => {
    const name = prompt("Enter folder name:");
    if (name) {
      createFolder(name);
    }
  };

  const rootConversations = conversations.filter(c => !c.folderId);

  return (
    <>
      <div className="w-[280px] h-full bg-[var(--color-bg-sidebar)] flex flex-col border-r border-[var(--color-border-subtle)] flex-shrink-0 z-40 select-none">
        
        {/* Top Action Bar */}
        <div className="px-4 py-4 flex flex-col gap-3">
          <button 
            onClick={handleNewConversation}
            className="flex items-center justify-center gap-2 w-full bg-[var(--color-bg-hover)] hover:bg-[var(--color-bg-selected)] text-[var(--color-text-primary)] py-2 rounded-lg transition-colors border border-[var(--color-border-subtle)] shadow-sm"
          >
            <MessageSquarePlus size={16} />
            <span className="text-[13px] font-medium">New Conversation</span>
          </button>
          
          <div className="relative group flex gap-2">
            <div className="relative flex-1">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)] group-focus-within:text-[var(--color-text-primary)] transition-colors" />
              <input 
                type="text" 
                placeholder="Search..." 
                className="w-full bg-[var(--color-bg-background)] border border-[var(--color-border-subtle)] focus:border-[var(--color-border-active)] rounded-lg py-1.5 pl-9 pr-3 text-[13px] text-[var(--color-text-primary)] placeholder-[var(--color-text-tertiary)] outline-none transition-all shadow-inner"
              />
            </div>
            <button 
              onClick={handleNewFolder}
              className="w-[34px] h-[34px] flex items-center justify-center rounded-lg bg-[var(--color-bg-background)] border border-[var(--color-border-subtle)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:border-[var(--color-border-active)] transition-colors shrink-0"
              title="New Folder"
            >
              <FolderPlus size={16} />
            </button>
          </div>
        </div>

        {/* List (Scrollable) */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden px-2 pb-4">
          
          {/* Folders */}
          {folders.map(folder => (
            <div key={folder.id} className="mb-2">
              <div 
                className="flex items-center justify-between px-2 py-1.5 rounded-md hover:bg-[var(--color-bg-hover)] cursor-pointer group transition-colors"
                onClick={() => toggleFolder(folder.id)}
              >
                <div className="flex items-center gap-1.5 overflow-hidden">
                  <motion.div initial={false} animate={{ rotate: expandedFolders[folder.id] ? 90 : 0 }}>
                    <ChevronRight size={14} className="text-[var(--color-text-tertiary)] group-hover:text-[var(--color-text-secondary)] transition-colors shrink-0" />
                  </motion.div>
                  <FolderIcon size={14} className="text-[var(--color-text-tertiary)] shrink-0" />
                  <span className="text-[13px] font-medium text-[var(--color-text-secondary)] truncate">{folder.name}</span>
                </div>
                
                <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <button 
                    onClick={(e) => { e.stopPropagation(); createConversation(folder.id); }}
                    className="p-1 hover:bg-[var(--color-bg-selected)] rounded text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
                  >
                    <Plus size={14} />
                  </button>
                  <button 
                    onClick={(e) => { e.stopPropagation(); deleteFolder(folder.id); }}
                    className="p-1 hover:bg-[var(--color-danger-transparent)] hover:text-[var(--color-danger)] rounded text-[var(--color-text-secondary)] transition-colors"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>

              <AnimatePresence initial={false}>
                {expandedFolders[folder.id] && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.22, ease: [0.4, 0, 0.2, 1] }}
                    className="overflow-hidden pl-7"
                  >
                    {conversations.filter(c => c.folderId === folder.id).map(conv => (
                      <ConversationItem 
                        key={conv.id} 
                        conv={conv} 
                        isActive={activeConversationId === conv.id}
                        onSelect={() => setActiveConversation(conv.id)}
                        onDelete={() => deleteConversation(conv.id)}
                      />
                    ))}
                    {conversations.filter(c => c.folderId === folder.id).length === 0 && (
                      <div className="text-[11px] text-[var(--color-text-tertiary)] px-2 py-1 italic">Empty folder</div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}

          {/* Root Conversations */}
          {folders.length > 0 && rootConversations.length > 0 && (
            <div className="my-3 border-t border-[var(--color-border-subtle)] opacity-50" />
          )}

          <div className="pl-2 pr-1">
            {rootConversations.map(conv => (
              <ConversationItem 
                key={conv.id} 
                conv={conv} 
                isActive={activeConversationId === conv.id}
                onSelect={() => setActiveConversation(conv.id)}
                onDelete={() => deleteConversation(conv.id)}
              />
            ))}
          </div>
        </div>

        {/* Bottom Settings */}
        <div className="p-3 border-t border-[var(--color-border-subtle)]">
          <button 
            className="flex items-center gap-3 w-full px-3 py-2 rounded-lg hover:bg-[var(--color-bg-hover)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors group"
            onClick={() => setSettingsOpen(true)}
          >
            <Settings size={16} className="group-hover:rotate-45 transition-transform duration-300" />
            <span className="text-[13px] font-medium">Settings</span>
          </button>
        </div>
      </div>

      <SettingsModal open={settingsOpen} onOpenChange={setSettingsOpen} />
    </>
  );
};

const ConversationItem: React.FC<{ conv: Conversation, isActive: boolean, onSelect: () => void, onDelete: () => void }> = ({ conv, isActive, onSelect, onDelete }) => {
  return (
    <div 
      onClick={onSelect}
      className={`flex items-center justify-between px-2 py-1.5 rounded-md cursor-pointer group transition-colors mt-0.5 ${isActive ? 'bg-[var(--color-bg-selected)]' : 'hover:bg-[var(--color-bg-hover)]'}`}
    >
      <div className="flex items-center gap-2 overflow-hidden flex-1">
        {isActive ? (
          <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-accent)] shrink-0" />
        ) : (
          <Hash size={13} className="text-[var(--color-text-tertiary)] shrink-0" />
        )}
        <span className={`text-[13px] truncate ${isActive ? 'text-[var(--color-text-primary)] font-medium' : 'text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-primary)]'}`}>
          {conv.title}
        </span>
      </div>
      
      <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity ml-2 shrink-0">
         <button 
           onClick={(e) => { e.stopPropagation(); onDelete(); }}
           className="p-1 hover:bg-[var(--color-danger-transparent)] hover:text-[var(--color-danger)] rounded text-[var(--color-text-secondary)] transition-colors"
         >
           <Trash2 size={13} />
         </button>
      </div>
    </div>
  );
};
