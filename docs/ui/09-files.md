# File Explorer Specification

## Purpose

File browser for exploring project structure, previewing files, managing versions, and integrating with git.

## Layout

```
┌─ Files Header ──────────────────────────┐ 32px
│ [🗂️] Project          [🔍] [⋮] [×]     │
├──────────────────────────────────────────┤
│ [Search files...]                        │ Search: 32px
├──────────────────────────────────────────┤
│ ⭐ Favorites                            │
│  • ./src/main.ts                        │
│  • ./package.json                       │
│                                         │
│ ▼ Project Root (/)                     │ File Tree
│  ▶ src/                                │ Resizable
│  ▶ tests/                              │
│  ▶ docs/                               │
│  📄 README.md                          │
│  📄 package.json                       │
│                                         │
└──────────────────────────────────────────┘
```

## Features

### File Tree

- **Expand/Collapse**: Click chevron
- **Open**: Click file to preview
- **Double-click**: Open in split view
- **Right-click**: Context menu (rename, delete, etc.)
- **Drag**: Move files/folders
- **Keyboard Navigation**: Arrow keys, Enter to open

### Search

- **Real-time Filter**: Type to search files
- **Fuzzy Match**: Partial matching
- **Regex**: Toggle regex mode
- **Case Sensitive**: Optional toggle
- **Exclude**: Patterns to exclude

### Preview

- **Code**: Syntax-highlighted preview
- **Images**: Thumbnail preview with zoom
- **Markdown**: Rendered preview
- **JSON**: Formatted display
- **Binary**: Show hex dump or "binary file"

### Git Integration

- **Status Icons**: Modified (●), staged (✓), untracked (?), conflict (×)
- **Blame**: Show last commit per line (Ctrl+K G)
- **Diff**: Compare with last commit (Ctrl+K D)
- **History**: View file history (Ctrl+K L)

### Diff Viewer

```
src/main.ts
─────────────────────────
- OLD: function oldName() {  | + NEW: function newName() {
- OLD: return 42;            | + NEW: return 100;
─────────────────────────
```

- **Side-by-side**: Two versions
- **Inline**: Changes highlighted inline
- **Word Diff**: Show word-level changes
- **Context**: Show surrounding lines

### Version History

- **Timeline**: Show versions over time
- **Diff**: View changes between versions
- **Restore**: Rollback to previous version
- **Branch**: Show version from different branch

## Keyboard Shortcuts

```
Ctrl+F          Search Files
Ctrl+N          New File
Ctrl+Shift+N    New Folder
F2              Rename
Delete          Delete File
Ctrl+X          Cut
Ctrl+C          Copy
Ctrl+V          Paste
Ctrl+D          Duplicate

Ctrl+K G        Git Status
Ctrl+K D        Show Diff
Ctrl+K L        Show History
```

## Right-Click Context Menu

```
✏️  Rename
🗑️  Delete
✂️  Cut
📋 Copy
📌 Copy Path
───────────
📊 Properties
🔄 Show in Folder
📈 Git Status
📖 Recent Versions
───────────
🔖 Bookmark
👁️  Preview
```

## Settings

```
Files Preferences
├─ ☑ Show Hidden Files
├─ ☑ Show Git Status
├─ Exclude Pattern: node_modules/, .git/
├─ Sort By: [Name ▼]
└─ ☑ Expand Folders on Click
```

---

**Files Specification Version**: 1.0  
**Last Updated**: August 2, 2026
