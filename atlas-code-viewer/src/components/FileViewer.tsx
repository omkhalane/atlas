import { useState, useEffect } from 'react';
import { createHighlighter, type Highlighter } from 'shiki';

let highlighterInstance: Highlighter | null = null;

async function getShiki() {
  if (!highlighterInstance) {
    highlighterInstance = await createHighlighter({
      themes: ['dark-plus'],
      langs: ['javascript', 'typescript', 'tsx', 'jsx', 'python', 'java', 'c', 'cpp', 'rust', 'go', 'json', 'yaml', 'markdown', 'css', 'html', 'bash', 'sql']
    });
  }
  return highlighterInstance;
}

function getLangFromExt(ext: string) {
  switch (ext) {
    case 'ts': return 'typescript';
    case 'tsx': return 'tsx';
    case 'js': return 'javascript';
    case 'jsx': return 'jsx';
    case 'py': return 'python';
    case 'go': return 'go';
    case 'rs': return 'rust';
    case 'json': return 'json';
    case 'yml':
    case 'yaml': return 'yaml';
    case 'md': return 'markdown';
    case 'css': return 'css';
    case 'html': return 'html';
    case 'sh': return 'bash';
    case 'sql': return 'sql';
    case 'java': return 'java';
    case 'c': return 'c';
    case 'cpp': return 'cpp';
    default: return 'text';
  }
}

export default function FileViewer({ path }: { path: string }) {
  const [content, setContent] = useState<string>('');
  const [html, setHtml] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const ext = path.split('.').pop()?.toLowerCase() || '';
  const lang = getLangFromExt(ext);
  const size = new Blob([content]).size;

  useEffect(() => {
    setLoading(true);
    setError(null);
    setHtml('');
    
    fetch(`${import.meta.env.BASE_URL}repository/${encodeURI(path)}`)
      .then(res => {
        if (!res.ok) throw new Error('File not found');
        return res.text();
      })
      .then(async text => {
        setContent(text);
        try {
          const shiki = await getShiki();
          const highlighted = shiki ? shiki.codeToHtml(text, {
            lang: lang === 'text' ? 'text' : lang,
            theme: 'dark-plus'
          }) : '';
          setHtml(highlighted);
        } catch (e) {
          // Fallback if language not loaded
          setHtml(`<pre><code>${text.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>`);
        }
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [path, lang]);

  return (
    <div className="flex flex-col h-full bg-[#0d1117] overflow-hidden">
      {/* File Header */}
      <div className="h-10 border-b border-atlas-border bg-atlas-bg flex items-center px-4 shrink-0 text-sm font-medium text-atlas-muted justify-between">
        <div className="flex items-center gap-2">
          <span>{path}</span>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <span>{loading ? '...' : `${(size / 1024).toFixed(2)} KB`}</span>
          <span className="uppercase">{lang}</span>
        </div>
      </div>
      
      {/* File Content */}
      <div className="flex-1 overflow-auto relative">
        {loading ? (
          <div className="p-4 text-atlas-muted">Loading file...</div>
        ) : error ? (
          <div className="p-4 text-red-400">{error}</div>
        ) : (
          <div className="flex text-[13px] leading-relaxed font-mono">
            {/* Line Numbers */}
            <div className="flex flex-col text-right py-4 px-3 select-none text-[#6e7681] border-r border-[#30363d] bg-[#0d1117] shrink-0 sticky left-0 min-w-[3rem]">
              {content.split('\\n').map((_, i) => (
                <div key={i} className="h-[21px] leading-[21px]">{i + 1}</div>
              ))}
            </div>
            {/* Code */}
            <div 
              className="py-4 px-4 overflow-x-auto min-w-max"
              dangerouslySetInnerHTML={{ __html: html.replace(/<pre[^>]*>/, '<pre style="background: transparent !important; margin: 0; padding: 0;">').replace(/<code[^>]*>/, '<code style="background: transparent !important;">') }} 
            />
          </div>
        )}
      </div>
    </div>
  );
}
