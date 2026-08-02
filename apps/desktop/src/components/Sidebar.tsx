import React, { useState } from 'react';
import { 
  MessageSquarePlus, 
  Settings, 
  Folder as FolderIcon, 
  ChevronRight, 
  ChevronDown,
  Hash,
  Search,
  Plus,
  Trash2,
  FolderPlus,
  FileText,
  XSquare,
  Globe,
  Terminal
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useStore } from '../store/useStore';
import type { Conversation } from '../store/useStore';
import { SettingsModal } from './SettingsModal';
import { FileTree } from './FileTree';

export const Sidebar: React.FC = () => {
  const { 
    folders, 
    conversations, 
    createConversation, 
    createFolder, 
    deleteFolder, 
    deleteConversation, 
    setActiveConversation, 
    activeConversationId,
    activitySidebarSelection
  } = useStore();
  
  const [expandedFolders, setExpandedFolders] = useState<Record<string, boolean>>({});
  const [settingsOpen, setSettingsOpen] = useState(false);

  const toggleFolder = (id: string) => setExpandedFolders(prev => ({ ...prev, [id]: !prev[id] }));

  const handleNewConversation = () => createConversation(null);
  const handleNewFolder = () => {
    const name = prompt("Enter folder name:");
    if (name) createFolder(name);
  };

  const rootConversations = conversations.filter(c => !c.folderId);

  return (
    <>
      <div className="w-[250px] h-full bg-[var(--color-bg-panel)] flex flex-col border-r border-[var(--color-border-subtle)] flex-shrink-0 z-40 select-none">
        
        {/* Header - Dynamic based on activeWorkspaceTab */}
        <div className="px-3 py-2 border-b border-[var(--color-border-subtle)] flex items-center justify-between">
           <div className="flex items-center gap-2 text-[var(--color-text-primary)]">
              {activitySidebarSelection === 'chat' && <MessageSquarePlus size={16} />}
              {activitySidebarSelection === 'files' && <FolderIcon size={16} />}
              {activitySidebarSelection === 'browser' && <Globe size={16} />}
              {activitySidebarSelection === 'terminal' && <Terminal size={16} />}
              <span className="text-[13px] font-medium capitalize">
                 {activitySidebarSelection === 'chat' ? 'Conversations' : activitySidebarSelection}
              </span>
           </div>
           <div className="flex items-center gap-1">
              <button className="p-1 text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-hover)] rounded">
                 <XSquare size={14} />
              </button>
           </div>
        </div>

        {/* Search Bar */}
        <div className="px-3 py-2 border-b border-[var(--color-border-subtle)] bg-[var(--color-bg-background)]">
          <div className="relative group flex items-center">
            <Search size={14} className="absolute left-2.5 text-[var(--color-text-tertiary)] group-focus-within:text-[var(--color-text-primary)] transition-colors" />
            <input 
              type="text" 
              placeholder={`Search ${activitySidebarSelection}...`}
              className="w-full bg-transparent border-none focus:outline-none py-1 pl-8 pr-2 text-[12px] text-[var(--color-text-primary)] placeholder-[var(--color-text-tertiary)]"
            />
          </div>
        </div>

        {/* List (Scrollable) */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-2">
          
          {activitySidebarSelection === 'chat' && (
             <>
              <div className="mb-2">
                 <button 
                   onClick={handleNewConversation}
                   className="flex items-center gap-2 w-full text-left px-2 py-1.5 text-[12px] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-hover)] hover:text-[var(--color-text-primary)] rounded transition-colors"
                 >
                   <Plus size={14} /> New Conversation
                 </button>
              </div>
              
              {/* Folders */}
              {folders.map(folder => (
                <div key={folder.id} className="mb-1">
                  <div 
                    className="flex items-center justify-between px-2 py-1.5 rounded-md hover:bg-[var(--color-bg-hover)] cursor-pointer group transition-colors"
                    onClick={() => toggleFolder(folder.id)}
                  >
                    <div className="flex items-center gap-1.5 overflow-hidden">
                      <motion.div initial={false} animate={{ rotate: expandedFolders[folder.id] ? 90 : 0 }}>
                        <ChevronRight size={14} className="text-[var(--color-text-tertiary)] group-hover:text-[var(--color-text-secondary)] transition-colors shrink-0" />
                      </motion.div>
                      <FolderIcon size={14} className="text-[var(--color-text-tertiary)] shrink-0" />
                      <span className="text-[12px] font-medium text-[var(--color-text-secondary)] truncate">{folder.name}</span>
                    </div>
                    
                    <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
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
                        className="overflow-hidden pl-6"
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
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ))}

              {/* Root Conversations */}
              <div className="mt-2 pt-2 border-t border-[var(--color-border-subtle)]">
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
             </>
          )}

          {activitySidebarSelection === 'files' && (
             <FileTree />
          )}
          
          {['browser', 'terminal'].includes(activitySidebarSelection) && (
             <div className="text-[12px] text-[var(--color-text-tertiary)] px-2 py-4 italic text-center">
                Select a tab or session...
             </div>
          )}

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
        <span className={`text-[12px] truncate ${isActive ? 'text-[var(--color-text-primary)] font-medium' : 'text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-primary)]'}`}>
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
