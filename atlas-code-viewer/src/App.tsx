import { useState, useEffect } from 'react';
import { HashRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Search, Lock, Menu, X } from 'lucide-react';
import Sidebar from './components/Sidebar';
import FileViewer from './components/FileViewer';
import MarkdownViewer from './components/MarkdownViewer';
import SearchModal from './components/SearchModal';

export type TreeNode = {
  name: string;
  path: string;
  type: 'file' | 'dir';
  size?: number;
  children?: TreeNode[];
};

function Layout() {
  const [tree, setTree] = useState<TreeNode[]>([]);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}repository/tree.json`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load repository tree.');
        return res.json();
      })
      .then((data) => {
        setTree(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsSearchOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="flex flex-col h-screen bg-atlas-bg text-atlas-text overflow-hidden font-sans">
      {/* Header */}
      <header className="h-14 border-b border-atlas-border bg-atlas-bg-subtle flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 hover:bg-atlas-border rounded md:hidden"
          >
            <Menu size={20} />
          </button>
          <div className="font-bold text-lg flex items-center gap-2">
            <span className="text-atlas-accent">ATLAS</span>
            <span className="text-sm font-normal text-atlas-muted hidden sm:inline-block">AI-NATIVE BROWSER RUNTIME</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button 
            onClick={() => setIsSearchOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-atlas-bg border border-atlas-border rounded-md hover:border-atlas-muted transition-colors text-atlas-muted"
          >
            <Search size={14} />
            <span className="hidden sm:inline-block">Search code...</span>
            <kbd className="hidden sm:inline-block ml-2 px-1.5 py-0.5 text-xs border border-atlas-border rounded bg-atlas-bg-subtle">⌘K</kbd>
          </button>
          <div className="flex items-center gap-1.5 text-sm font-medium text-atlas-muted bg-atlas-bg border border-atlas-border px-2.5 py-1 rounded-md">
            <Lock size={14} />
            READ ONLY
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Sidebar */}
        <div className={`
          absolute md:static z-20 h-full bg-atlas-bg-subtle border-r border-atlas-border flex-col transition-all duration-200
          ${sidebarOpen ? 'w-72 flex' : 'w-0 hidden'}
        `}>
          <div className="p-3 border-b border-atlas-border font-semibold text-sm flex justify-between items-center">
            EXPLORER
            <button className="md:hidden" onClick={() => setSidebarOpen(false)}>
              <X size={16} />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {loading ? (
              <div className="text-sm text-atlas-muted">Loading...</div>
            ) : error ? (
              <div className="text-sm text-red-400">{error}</div>
            ) : (
              <Sidebar nodes={tree} />
            )}
          </div>
        </div>

        {/* Content Area */}
        <main className="flex-1 overflow-hidden bg-atlas-bg flex flex-col min-w-0">
          <Routes>
            <Route path="/" element={<HomeViewer tree={tree} />} />
            <Route path="/file/*" element={<ContentRouter />} />
          </Routes>
        </main>
      </div>

      <SearchModal 
        isOpen={isSearchOpen} 
        onClose={() => setIsSearchOpen(false)} 
      />
    </div>
  );
}

function HomeViewer({ tree }: { tree: TreeNode[] }) {
  // If root has README.md, render it
  const hasReadme = tree.some(n => n.name.toLowerCase() === 'readme.md');
  return hasReadme ? (
    <MarkdownViewer path="README.md" />
  ) : (
    <div className="flex-1 flex items-center justify-center text-atlas-muted flex-col gap-2">
      <div className="text-2xl text-atlas-text">ATLAS Repository Snapshot</div>
      <div>Select a file from the explorer to view its contents.</div>
    </div>
  );
}

function ContentRouter() {
  const location = useLocation();
  // location.pathname is like /file/apps/runtime/main.py
  const filePath = location.pathname.replace(/^\/file\//, '');
  
  if (!filePath) return <div className="p-4">Select a file</div>;

  const ext = filePath.split('.').pop()?.toLowerCase();
  
  if (ext === 'md' || ext === 'mdx') {
    return <MarkdownViewer path={filePath} />;
  }

  // Common image extensions
  if (['png', 'jpg', 'jpeg', 'gif', 'svg', 'ico', 'webp'].includes(ext || '')) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#0d1117] p-8 overflow-auto">
        <img src={`${import.meta.env.BASE_URL}repository/${filePath}`} alt={filePath} className="max-w-full max-h-full object-contain" />
      </div>
    );
  }

  return <FileViewer path={filePath} />;
}

export default function App() {
  return (
    <Router>
      <Layout />
    </Router>
  );
}
