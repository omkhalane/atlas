import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, ChevronDown, Folder, File, FileText, FileJson, FileCode2, Image } from 'lucide-react';
import type { TreeNode } from '../App';

function getIconForFile(filename: string) {
  const ext = filename.split('.').pop()?.toLowerCase();
  switch (ext) {
    case 'json': return <FileJson size={14} className="text-yellow-500" />;
    case 'md':
    case 'txt': return <FileText size={14} className="text-blue-400" />;
    case 'js':
    case 'ts':
    case 'jsx':
    case 'tsx':
    case 'py':
    case 'go':
    case 'rs':
    case 'java':
    case 'c':
    case 'cpp': return <FileCode2 size={14} className="text-green-400" />;
    case 'png':
    case 'jpg':
    case 'svg': return <Image size={14} className="text-purple-400" />;
    default: return <File size={14} className="text-atlas-muted" />;
  }
}

function TreeItem({ node, depth = 0 }: { node: TreeNode; depth?: number }) {
  const [isOpen, setIsOpen] = useState(depth < 1); // Expand root folders by default
  const location = useLocation();
  const isActive = location.pathname === `/file/${node.path}`;

  if (node.type === 'dir') {
    return (
      <div className="select-none">
        <div 
          className="flex items-center gap-1.5 py-1 px-2 hover:bg-atlas-border rounded cursor-pointer text-sm text-atlas-text"
          style={{ paddingLeft: `${depth * 12 + 8}px` }}
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? <ChevronDown size={14} className="text-atlas-muted shrink-0" /> : <ChevronRight size={14} className="text-atlas-muted shrink-0" />}
          <Folder size={14} className="text-atlas-accent shrink-0" />
          <span className="truncate">{node.name}</span>
        </div>
        {isOpen && node.children && (
          <div>
            {node.children.map((child, idx) => (
              <TreeItem key={`${child.path}-${idx}`} node={child} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <Link 
      to={`/file/${node.path}`}
      className={`flex items-center gap-1.5 py-1 px-2 hover:bg-atlas-border rounded cursor-pointer text-sm transition-colors ${isActive ? 'bg-atlas-selection text-atlas-accent font-medium' : 'text-atlas-text'}`}
      style={{ paddingLeft: `${depth * 12 + 24}px` }}
    >
      <span className="shrink-0">{getIconForFile(node.name)}</span>
      <span className="truncate">{node.name}</span>
    </Link>
  );
}

export default function Sidebar({ nodes }: { nodes: TreeNode[] }) {
  return (
    <div className="pb-4">
      {nodes.map((node, idx) => (
        <TreeItem key={`${node.path}-${idx}`} node={node} />
      ))}
    </div>
  );
}
