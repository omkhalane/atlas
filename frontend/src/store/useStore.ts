import { create } from 'zustand';

interface AgentEvent {
  type: string;
  content?: string;
  action?: string;
  parameters?: any;
  result?: any;
  error?: string;
  current_task_idx?: number;
}

interface FileMeta {
  name: string;
  path: string;
}

interface AppState {
  // Agent Execution
  taskInput: string;
  setTaskInput: (val: string) => void;
  isExecuting: boolean;
  setIsExecuting: (val: boolean) => void;
  execId: string | null;
  setExecId: (id: string | null) => void;
  
  events: AgentEvent[];
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

export const useStore = create<AppState>((set) => ({
  taskInput: '',
  setTaskInput: (val) => set({ taskInput: val }),
  
  isExecuting: false,
  setIsExecuting: (val) => set({ isExecuting: val }),
  
  execId: null,
  setExecId: (id) => set({ execId: id }),
  
  events: [],
  addEvent: (event) => set((state) => ({ events: [...state.events, event] })),
  clearEvents: () => set({ events: [] }),
  
  planTasks: [],
  setPlanTasks: (tasks) => set({ planTasks: tasks }),
  
  currentTaskIdx: -1,
  setCurrentTaskIdx: (idx) => set({ currentTaskIdx: idx }),
  
  visibleTabs: ['files', 'terminal', 'logs', 'memory'],
  setVisibleTabs: (tabs) => set({ visibleTabs: tabs }),
  ensureTabVisible: (tab) => set((state) => ({ 
      visibleTabs: state.visibleTabs.includes(tab) ? state.visibleTabs : [...state.visibleTabs, tab],
      activeWorkspaceTab: tab
  })),
  
  activeWorkspaceTab: 'files',
  setActiveWorkspaceTab: (tab) => set({ activeWorkspaceTab: tab }),
  
  files: [],
  addFile: (file) => set((state) => ({
    files: state.files.find(f => f.path === file.path) ? state.files : [...state.files, file]
  })),
  
  securityHalt: null,
  setSecurityHalt: (halt) => set({ securityHalt: halt }),
}));
