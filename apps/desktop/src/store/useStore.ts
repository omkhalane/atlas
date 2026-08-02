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

export interface Tab {
  id: string;
  type: 'chat' | 'file' | 'browser' | 'terminal' | 'memory' | 'plugins' | 'planner';
  title: string;
  data?: any;
}

export interface Pane {
  id: string;
  tabs: Tab[];
  activeTabId: string | null;
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

  // Agent Execution
  taskInput: string;
  setTaskInput: (val: string | ((prev: string) => string)) => void;
  isExecuting: boolean;
  setIsExecuting: (val: boolean) => void;
  execId: string | null;
  setExecId: (id: string | null) => void;
  
  addEvent: (event: AgentEvent, convId?: string) => void;
  clearEvents: () => void;
  
  // Execution Plan
  planTasks: string[];
  setPlanTasks: (tasks: string[]) => void;
  currentTaskIdx: number;
  setCurrentTaskIdx: (idx: number) => void;
  
  // Layout Engine
  activitySidebarSelection: string;
  setActivitySidebarSelection: (selection: string) => void;

  panes: Pane[];
  activePaneId: string;
  setActivePaneId: (paneId: string) => void;
  openTab: (tab: Omit<Tab, 'id'> & { id?: string }, targetPaneId?: string) => void;
  closeTab: (paneId: string, tabId: string) => void;
  splitPane: (sourcePaneId: string, direction: 'horizontal' | 'vertical') => void;
  closePane: (paneId: string) => void;

  ensureTabVisible: (tabType: string) => void;
  
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
        set((state) => {
          // Auto-open this conversation in a tab
          const newTab: Tab = { id: `chat-${id}`, type: 'chat', title: 'New Conversation', data: { convId: id } };
          const panes = [...state.panes];
          if (panes.length === 0) {
            panes.push({ id: 'pane-1', tabs: [newTab], activeTabId: newTab.id });
          } else {
            const activePane = panes.find(p => p.id === state.activePaneId) || panes[0];
            if (!activePane.tabs.find(t => t.id === newTab.id)) {
              activePane.tabs.push(newTab);
            }
            activePane.activeTabId = newTab.id;
          }

          return {
            conversations: [newConv, ...state.conversations],
            activeConversationId: id,
            workspaceOpen: false,
            planTasks: [],
            files: [],
            taskInput: '',
            execId: null,
            panes
          };
        });
        return id;
      },

      deleteConversation: (id) => set((state) => ({
        conversations: state.conversations.filter(c => c.id !== id),
        activeConversationId: state.activeConversationId === id ? null : state.activeConversationId
      })),

      setActiveConversation: (id) => set((state) => {
        const tabId = `chat-${id}`;
        let panes = [...state.panes];
        if (panes.length === 0) {
          panes = [{ id: 'pane-1', tabs: [], activeTabId: null }];
        }
        const activePane = panes.find(p => p.id === state.activePaneId) || panes[0];
        
        // Ensure it's in the pane
        if (!activePane.tabs.find(t => t.id === tabId)) {
          const conv = state.conversations.find(c => c.id === id);
          activePane.tabs.push({ id: tabId, type: 'chat', title: conv?.title || 'Chat', data: { convId: id } });
        }
        activePane.activeTabId = tabId;

        return { 
          activeConversationId: id,
          workspaceOpen: false,
          planTasks: [],
          execId: null,
          panes,
          activePaneId: activePane.id
        };
      }),

      updateConversationTitle: (id, title) => set((state) => {
        const panes = state.panes.map(pane => ({
          ...pane,
          tabs: pane.tabs.map(tab => 
            tab.type === 'chat' && tab.data?.convId === id ? { ...tab, title } : tab
          )
        }));
        return {
          conversations: state.conversations.map(c => c.id === id ? { ...c, title, updatedAt: Date.now() } : c),
          panes
        };
      }),

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
      
      addEvent: (event, convId) => set((state) => {
        const targetId = convId || state.activeConversationId;
        if (!targetId) return state;
        return {
          conversations: state.conversations.map(c => 
            c.id === targetId 
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
      
      activitySidebarSelection: 'chat',
      setActivitySidebarSelection: (sel) => set({ activitySidebarSelection: sel }),

      panes: [{ id: 'pane-1', tabs: [], activeTabId: null }],
      activePaneId: 'pane-1',
      setActivePaneId: (paneId) => set({ activePaneId: paneId }),

      openTab: (tabData, targetPaneId) => set((state) => {
        const tab: Tab = { ...tabData, id: tabData.id || `${tabData.type}-${Date.now()}` };
        const panes = [...state.panes];
        if (panes.length === 0) {
          panes.push({ id: 'pane-1', tabs: [], activeTabId: null });
        }
        
        let targetPane = panes.find(p => p.id === (targetPaneId || state.activePaneId));
        if (!targetPane) targetPane = panes[0];

        // Check if tab exists anywhere
        let found = false;
        panes.forEach(p => {
          if (p.tabs.find(t => t.id === tab.id)) {
            p.activeTabId = tab.id;
            found = true;
          }
        });

        if (!found) {
          targetPane.tabs.push(tab);
          targetPane.activeTabId = tab.id;
        }

        return { panes, activePaneId: targetPane.id };
      }),

      closeTab: (paneId, tabId) => set((state) => {
        const panes = state.panes.map(pane => {
          if (pane.id !== paneId) return pane;
          const newTabs = pane.tabs.filter(t => t.id !== tabId);
          let newActive = pane.activeTabId;
          if (newActive === tabId) {
            newActive = newTabs.length > 0 ? newTabs[newTabs.length - 1].id : null;
          }
          return { ...pane, tabs: newTabs, activeTabId: newActive };
        });
        return { panes };
      }),

      splitPane: (sourcePaneId, direction) => set((state) => {
        const sourcePane = state.panes.find(p => p.id === sourcePaneId);
        if (!sourcePane) return state;

        const newPane: Pane = {
          id: `pane-${Date.now()}`,
          tabs: [],
          activeTabId: null
        };
        
        const sourceIndex = state.panes.findIndex(p => p.id === sourcePaneId);
        const newPanes = [...state.panes];
        newPanes.splice(sourceIndex + 1, 0, newPane);

        return { panes: newPanes, activePaneId: newPane.id };
      }),

      closePane: (paneId) => set((state) => {
        if (state.panes.length <= 1) return state;
        const newPanes = state.panes.filter(p => p.id !== paneId);
        let active = state.activePaneId;
        if (active === paneId) {
          active = newPanes[0].id;
        }
        return { panes: newPanes, activePaneId: active };
      }),

      ensureTabVisible: (tabType) => set((state) => {
        const panes = [...state.panes];
        let found = false;
        
        // Check if tab of this type is already visible
        for (const pane of panes) {
          if (pane.activeTabId) {
            const activeTab = pane.tabs.find(t => t.id === pane.activeTabId);
            if (activeTab?.type === tabType) {
              found = true;
              break;
            }
          }
        }
        
        if (!found) {
          // Open or focus an existing tab of this type
          let targetTab = null;
          for (const pane of panes) {
            targetTab = pane.tabs.find(t => t.type === tabType);
            if (targetTab) {
              pane.activeTabId = targetTab.id;
              found = true;
              break;
            }
          }
          
          if (!found) {
             const activePane = panes.find(p => p.id === state.activePaneId) || panes[0];
             const newTab: Tab = { id: `${tabType}-1`, type: tabType as any, title: tabType };
             activePane.tabs.push(newTab);
             activePane.activeTabId = newTab.id;
          }
        }
        return { panes };
      }),
      
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
        activeConversationId: state.activeConversationId,
        panes: state.panes
      }),
    }
  )
);
