import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface AgentEvent {
  type: string;
  content?: string;
  action?: string;
  parameters?: any;
  result?: any;
  error?: string;
  current_task_idx?: number;
}

export interface FileMeta {
  name: string;
  path: string;
}

export interface Conversation {
  id: string;
  title: string;
  folderId: string | null;
  updatedAt: number;
  events: AgentEvent[];
}

export interface Folder {
  id: string;
  name: string;
}

interface AppState {
  // Global Layout
  workspaceOpen: boolean;
  setWorkspaceOpen: (val: boolean) => void;

  // Conversations & Folders (Persisted)
  conversations: Conversation[];
  folders: Folder[];
  activeConversationId: string | null;
  
  createConversation: (folderId: string | null) => string;
  deleteConversation: (id: string) => void;
  setActiveConversation: (id: string | null) => void;
  updateConversationTitle: (id: string, title: string) => void;
  
  createFolder: (name: string) => void;
  deleteFolder: (id: string) => void;
  moveConversation: (convId: string, folderId: string | null) => void;

  // Agent Execution (Current active conversation context)
  taskInput: string;
  setTaskInput: (val: string | ((prev: string) => string)) => void;
  isExecuting: boolean;
  setIsExecuting: (val: boolean) => void;
  execId: string | null;
  setExecId: (id: string | null) => void;
  
  addEvent: (event: AgentEvent) => void;
  clearEvents: () => void;
  
  // Execution Plan & Tasks
  planTasks: string[];
  setPlanTasks: (tasks: string[]) => void;
  currentTaskIdx: number;
  setCurrentTaskIdx: (idx: number) => void;
  
  // Workspace State
  visibleTabs: string[];
  setVisibleTabs: (tabs: string[]) => void;
  ensureTabVisible: (tab: string) => void;
  activeWorkspaceTab: string; // 'browser', 'files', 'terminal', 'memory', 'docker', 'git'
  setActiveWorkspaceTab: (tab: string) => void;
  
  files: FileMeta[];
  addFile: (file: FileMeta) => void;
  
  securityHalt: any;
  setSecurityHalt: (halt: any) => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      workspaceOpen: false,
      setWorkspaceOpen: (val) => set({ workspaceOpen: val }),

      conversations: [],
      folders: [],
      activeConversationId: null,

      createConversation: (folderId) => {
        const id = `conv-${Date.now()}`;
        const newConv: Conversation = {
          id,
          title: 'New Conversation',
          folderId,
          updatedAt: Date.now(),
          events: []
        };
        set((state) => ({
          conversations: [newConv, ...state.conversations],
          activeConversationId: id,
          workspaceOpen: false, // Start with closed workspace for new chats
          planTasks: [],
          files: [],
          taskInput: '',
          execId: null
        }));
        return id;
      },

      deleteConversation: (id) => set((state) => ({
        conversations: state.conversations.filter(c => c.id !== id),
        activeConversationId: state.activeConversationId === id ? null : state.activeConversationId
      })),

      setActiveConversation: (id) => set(() => {
        // Find the conversation to optionally restore some UI state, though most state is in the conv obj
        return { 
          activeConversationId: id,
          workspaceOpen: false, // Close workspace on switch to keep it clean, or keep it open if you want
          planTasks: [], // Reset current UI state for tasks
          execId: null
        };
      }),

      updateConversationTitle: (id, title) => set((state) => ({
        conversations: state.conversations.map(c => c.id === id ? { ...c, title, updatedAt: Date.now() } : c)
      })),

      createFolder: (name) => set((state) => ({
        folders: [...state.folders, { id: `folder-${Date.now()}`, name }]
      })),

      deleteFolder: (id) => set((state) => ({
        folders: state.folders.filter(f => f.id !== id),
        conversations: state.conversations.map(c => c.folderId === id ? { ...c, folderId: null } : c)
      })),

      moveConversation: (convId, folderId) => set((state) => ({
        conversations: state.conversations.map(c => c.id === convId ? { ...c, folderId } : c)
      })),

      taskInput: '',
      setTaskInput: (val) => set((state) => ({ taskInput: typeof val === 'function' ? val(state.taskInput) : val })),
      
      isExecuting: false,
      setIsExecuting: (val) => set({ isExecuting: val }),
      
      execId: null,
      setExecId: (id) => set({ execId: id }),
      
      addEvent: (event) => set((state) => {
        if (!state.activeConversationId) return state;
        return {
          conversations: state.conversations.map(c => 
            c.id === state.activeConversationId 
              ? { ...c, events: [...c.events, event], updatedAt: Date.now() } 
              : c
          )
        };
      }),

      clearEvents: () => set((state) => {
        if (!state.activeConversationId) return state;
        return {
          conversations: state.conversations.map(c => 
            c.id === state.activeConversationId 
              ? { ...c, events: [], updatedAt: Date.now() } 
              : c
          )
        };
      }),
      
      planTasks: [],
      setPlanTasks: (tasks) => set({ planTasks: tasks }),
      
      currentTaskIdx: -1,
      setCurrentTaskIdx: (idx) => set({ currentTaskIdx: idx }),
      
      visibleTabs: ['files', 'terminal', 'logs', 'memory'],
      setVisibleTabs: (tabs) => set({ visibleTabs: tabs }),
      ensureTabVisible: (tab) => set((state) => ({ 
          visibleTabs: state.visibleTabs.includes(tab) ? state.visibleTabs : [...state.visibleTabs, tab],
          activeWorkspaceTab: tab,
          workspaceOpen: true // Auto-open workspace when a tool is used
      })),
      
      activeWorkspaceTab: 'files',
      setActiveWorkspaceTab: (tab) => set({ activeWorkspaceTab: tab }),
      
      files: [],
      addFile: (file) => set((state) => ({
        files: state.files.find(f => f.path === file.path) ? state.files : [...state.files, file]
      })),
      
      securityHalt: null,
      setSecurityHalt: (halt) => set({ securityHalt: halt }),
    }),
    {
      name: 'atlas-storage',
      partialize: (state) => ({ 
        conversations: state.conversations, 
        folders: state.folders, 
        activeConversationId: state.activeConversationId 
      }), // Only persist these fields
    }
  )
);
