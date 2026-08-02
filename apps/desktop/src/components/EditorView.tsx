import React from 'react';
import Editor from '@monaco-editor/react';
import { useStore } from '../store/useStore';
import type { Tab } from '../store/useStore';

export const EditorView: React.FC<{ tab?: Tab }> = ({ tab }) => {
  const code = tab?.data?.code || `// No content for ${tab?.title || 'Unknown File'}`;

  const language = tab?.title?.endsWith('.ts') || tab?.title?.endsWith('.tsx') ? 'typescript' : 
                   tab?.title?.endsWith('.js') ? 'javascript' :
                   tab?.title?.endsWith('.json') ? 'json' :
                   tab?.title?.endsWith('.md') ? 'markdown' :
                   tab?.title?.endsWith('.css') ? 'css' : 'plaintext';

  return (
    <div className="flex-1 h-full flex flex-col bg-[#1E1E1E] overflow-hidden">
      <div className="flex-1 w-full pt-2">
        <Editor
          height="100%"
          defaultLanguage={language}
          language={language}
          theme="vs-dark"
          value={code}
          options={{
            minimap: { enabled: true },
            fontSize: 13,
            fontFamily: '"JetBrains Mono", monospace',
            wordWrap: 'on',
            padding: { top: 16 }
          }}
        />
      </div>
    </div>
  );
};
