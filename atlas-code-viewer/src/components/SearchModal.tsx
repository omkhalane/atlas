import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, File as FileIcon, X } from 'lucide-react';

type SearchResult = {
  path: string;
  line: number;
  contentSnippet: string;
};

type SearchIndexEntry = {
  path: string;
  content: string;
};

export default function SearchModal({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [index, setIndex] = useState<SearchIndexEntry[] | null>(null);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      
      // Lazy load index
      if (!index && !loading) {
        setLoading(true);
        fetch(`${import.meta.env.BASE_URL}repository/search-index.json`)
          .then(res => res.json())
          .then(data => {
            setIndex(data);
            setLoading(false);
          })
          .catch(() => setLoading(false));
      }
    }
  }, [isOpen, index, loading]);

  useEffect(() => {
    if (!query.trim() || !index) {
      setResults([]);
      return;
    }

    const q = query.toLowerCase();
    const hits: SearchResult[] = [];

    // Simple search implementation
    for (const file of index) {
      if (hits.length > 50) break; // Limit results

      const lines = file.content.split('\\n');
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (line.toLowerCase().includes(q) || file.path.toLowerCase().includes(q)) {
          hits.push({
            path: file.path,
            line: i + 1,
            contentSnippet: line.trim()
          });
          if (hits.length > 50) break;
        }
      }
    }
    
    setResults(hits);
  }, [query, index]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[10vh] bg-black/50 backdrop-blur-sm" onClick={onClose}>
      <div 
        className="w-full max-w-2xl bg-atlas-bg-subtle border border-atlas-border rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center border-b border-atlas-border px-4 py-3">
          <Search size={20} className="text-atlas-muted mr-3" />
          <input
            ref={inputRef}
            type="text"
            className="flex-1 bg-transparent border-none outline-none text-atlas-text placeholder-atlas-muted text-lg"
            placeholder="Search code or files..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Escape') onClose();
            }}
          />
          <button onClick={onClose} className="text-atlas-muted hover:text-atlas-text p-1">
            <X size={20} />
          </button>
        </div>

        <div className="overflow-y-auto flex-1">
          {loading && <div className="p-8 text-center text-atlas-muted">Loading search index...</div>}
          
          {!loading && query && results.length === 0 && (
            <div className="p-8 text-center text-atlas-muted">No results found for "{query}"</div>
          )}

          {!loading && results.map((res, i) => (
            <div 
              key={`${res.path}-${res.line}-${i}`}
              className="px-4 py-3 border-b border-atlas-border hover:bg-atlas-selection cursor-pointer group"
              onClick={() => {
                navigate(`/file/${res.path}`);
                onClose();
              }}
            >
              <div className="flex items-center text-sm text-atlas-text font-medium mb-1">
                <FileIcon size={14} className="mr-2 text-atlas-muted" />
                {res.path} <span className="text-atlas-muted ml-2">Line {res.line}</span>
              </div>
              <div className="text-xs font-mono text-atlas-muted truncate group-hover:text-atlas-text">
                {res.contentSnippet}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
