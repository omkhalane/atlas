import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

const resolvePath = (basePath: string, relativePath: string) => {
  if (!relativePath || relativePath.startsWith('http://') || relativePath.startsWith('https://') || relativePath.startsWith('data:')) {
    return relativePath;
  }
  
  const parts = basePath.split('/');
  parts.pop(); // remove filename
  const dir = parts.join('/');
  
  // handle relative paths (e.g. ./assets/logo.png or ../assets/logo.png)
  let joined = dir ? `${dir}/${relativePath}` : relativePath;
  joined = joined.replace(/\.\//g, '').replace(/\/{2,}/g, '/');
  
  return `${import.meta.env.BASE_URL}repository/${encodeURI(joined)}`;
};

export default function MarkdownViewer({ path }: { path: string }) {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    
    fetch(`${import.meta.env.BASE_URL}repository/${encodeURI(path)}`)
      .then(res => {
        if (!res.ok) throw new Error('File not found');
        return res.text();
      })
      .then(text => {
        setContent(text);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [path]);

  return (
    <div className="flex flex-col h-full bg-atlas-bg overflow-hidden">
      <div className="h-10 border-b border-atlas-border bg-atlas-bg flex items-center px-4 shrink-0 text-sm font-medium text-atlas-muted">
        {path}
      </div>
      <div className="flex-1 overflow-auto p-8">
        <div className="max-w-4xl mx-auto bg-atlas-bg-subtle border border-atlas-border rounded-lg p-8">
          {loading ? (
            <div className="text-atlas-muted">Loading markdown...</div>
          ) : error ? (
            <div className="text-red-400">{error}</div>
          ) : (
            <div className="markdown-body">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw]}
                components={{
                  img: ({node, src, ...props}) => (
                    <img src={resolvePath(path, src || '')} {...props} style={{maxWidth: '100%'}} />
                  )
                }}
              >
                {content}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
