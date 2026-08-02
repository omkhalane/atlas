import React, { useState } from 'react';
import { ChevronDown, ChevronRight, FileText, Folder, Trash2, Edit2, FilePlus, FolderPlus } from 'lucide-react';

interface FileNode {
  name: string;
  type: 'file' | 'folder';
  children?: FileNode[];
  isOpen?: boolean;
}

export const FileTree: React.FC = () => {
  const [tree, setTree] = useState<FileNode[]>([
    {
      name: 'src',
      type: 'folder',
      isOpen: true,
      children: [
        { name: 'App.tsx', type: 'file' },
        { name: 'index.css', type: 'file' },
        {
          name: 'components',
          type: 'folder',
          isOpen: false,
          children: [
            { name: 'Button.tsx', type: 'file' },
            { name: 'Modal.tsx', type: 'file' }
          ]
        }
      ]
    },
    {
      name: 'tests',
      type: 'folder',
      isOpen: false,
      children: [{ name: 'App.test.tsx', type: 'file' }]
    },
    { name: 'package.json', type: 'file' },
    { name: 'README.md', type: 'file' }
  ]);

  const toggleFolder = (node: FileNode) => {
    node.isOpen = !node.isOpen;
    setTree([...tree]); // simple re-render
  };

  const renderTree = (nodes: FileNode[], depth = 0) => {
    return nodes.map((node, i) => (
      <div key={node.name + i} className="flex flex-col">
        <div 
          className="flex items-center justify-between px-2 py-1.5 hover:bg-[var(--color-bg-hover)] cursor-pointer group transition-colors select-none"
          style={{ paddingLeft: `${depth * 12 + 8}px` }}
          onClick={() => node.type === 'folder' && toggleFolder(node)}
        >
          <div className="flex items-center gap-1.5 overflow-hidden">
            {node.type === 'folder' ? (
              <>
                {node.isOpen ? (
                   <ChevronDown size={14} className="text-[var(--color-accent)] shrink-0" />
                ) : (
                   <ChevronRight size={14} className="text-[var(--color-text-tertiary)] group-hover:text-[var(--color-text-secondary)] shrink-0" />
                )}
                <Folder size={14} className={node.isOpen ? 'text-[var(--color-accent)]' : 'text-[var(--color-text-tertiary)]'} />
              </>
            ) : (
              <>
                <div className="w-3 shrink-0" /> {/* Spacer for file alignment */}
                <FileText size={14} className="text-[var(--color-text-tertiary)] shrink-0" />
              </>
            )}
            <span className={`text-[12px] truncate ${node.isOpen ? 'text-[var(--color-text-primary)] font-medium' : 'text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-primary)]'}`}>
              {node.name}
            </span>
          </div>

          <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity gap-0.5">
             {node.type === 'folder' && (
                <>
                  <button className="p-1 hover:bg-[var(--color-bg-selected)] rounded text-[var(--color-text-secondary)]" title="New File"><FilePlus size={12} /></button>
                  <button className="p-1 hover:bg-[var(--color-bg-selected)] rounded text-[var(--color-text-secondary)]" title="New Folder"><FolderPlus size={12} /></button>
                </>
             )}
             <button className="p-1 hover:bg-[var(--color-bg-selected)] rounded text-[var(--color-text-secondary)]" title="Rename"><Edit2 size={12} /></button>
             <button className="p-1 hover:bg-[var(--color-danger-transparent)] hover:text-[var(--color-danger)] rounded text-[var(--color-text-secondary)]" title="Delete"><Trash2 size={12} /></button>
          </div>
        </div>
        
        {node.type === 'folder' && node.isOpen && node.children && (
          <div className="flex flex-col">
            {renderTree(node.children, depth + 1)}
          </div>
        )}
      </div>
    ));
  };

  return (
    <div className="flex flex-col gap-2 w-full pt-2">
      <div className="text-[11px] font-medium text-[var(--color-text-tertiary)] uppercase tracking-wider px-3 flex items-center justify-between">
         <span>⭐ Favorites</span>
      </div>
      <div className="flex flex-col gap-0.5 mb-2">
         <div className="flex items-center gap-2 px-3 py-1.5 text-[12px] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-hover)] cursor-pointer">
            <div className="w-3 shrink-0" />
            <FileText size={14} className="text-[var(--color-text-tertiary)]" /> src/main.ts
         </div>
      </div>

      <div className="text-[11px] font-medium text-[var(--color-text-tertiary)] uppercase tracking-wider px-3 flex items-center justify-between mb-1 border-t border-[var(--color-border-subtle)] pt-3">
         <span>▼ Project Root</span>
         <div className="flex items-center gap-1">
            <button className="p-1 hover:bg-[var(--color-bg-hover)] rounded text-[var(--color-text-secondary)]" title="New File"><FilePlus size={12} /></button>
            <button className="p-1 hover:bg-[var(--color-bg-hover)] rounded text-[var(--color-text-secondary)]" title="New Folder"><FolderPlus size={12} /></button>
         </div>
      </div>
      
      <div className="flex flex-col pb-4">
        {renderTree(tree)}
      </div>
    </div>
  );
};
