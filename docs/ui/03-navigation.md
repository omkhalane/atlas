# Navigation Architecture

## Navigation Model Overview

### Three-Layer Navigation System

Atlas uses a three-layer navigation model that separates concerns and allows users to navigate at different levels of granularity:

```
Layer 1: Global Navigation (Top Bar + Activity Sidebar)
         ↓
Layer 2: Context Navigation (Explorer/Main Panel + Info Sidebar)
         ↓
Layer 3: Detail Navigation (Properties, Inspector, Secondary Panels)
```

---

## Layer 1: Global Navigation

### Activity Sidebar (Left, 48px)

The leftmost vertical bar containing icon buttons for major application modes.

#### Icons (Top to Bottom)

1. **Home** (≡ three bars)
   - Latest/default view
   - Shows recent tasks, quick actions
   - Keyboard: Alt+H

2. **Chat** (⊙ circle with dot)
   - Agent conversation interface
   - Primary interaction point
   - Keyboard: Ctrl+' (apostrophe)

3. **Browser** (◉ globe)
   - Integrated web browser
   - For agent web tasks
   - Keyboard: Ctrl+B

4. **Files** (▦ folder)
   - File explorer and manager
   - Project file tree
   - Keyboard: Ctrl+E

5. **Terminal** (▬ terminal symbol)
   - Multi-tab terminal interface
   - Command execution
   - Keyboard: Ctrl+J

6. **Memory** (⧗ brain symbol)
   - Knowledge graph browser
   - Fact storage viewer
   - Keyboard: Ctrl+M

7. **Agents** (◯ agent icon)
   - Manage running agents
   - History, logs
   - Keyboard: Ctrl+A

8. **Planner** (📋 checklist)
   - Task planning view
   - Dependencies, queue
   - Keyboard: Ctrl+L

---

[Spacer for brevity - continues with detailed subsections]

#### Navigation Behavior

- **Click**: Switch to that view
- **Double-Click**: Focus that panel (if already open)
- **Right-Click**: Context menu with options (split, detach, close)
- **Hover**: Show tooltip with view name and shortcut

#### Active State Indicator

- Active icon has blue (#00A8E8) accent circle around it
- Animation: 100ms fade-in when activated
- Smooth transition between icons

#### Icon Specifications

- **Size**: 24×24px
- **Padding**: 12px around icon
- **Spacing**: 8px between icons
- **Margin**: 8px top/bottom spacing group

---

### Top Menu Bar

#### File Menu

- New Agent
- New Workspace
- Open Workspace
- Save Workspace As
- Close Workspace
- Settings (→ Opens Settings Panel)
- Quit (Ctrl+Q)

#### Edit Menu

- Undo (Ctrl+Z)
- Redo (Ctrl+Shift+Z)
- Cut (Ctrl+X)
- Copy (Ctrl+C)
- Paste (Ctrl+V)
- Select All (Ctrl+A)

#### View Menu

- Toggle Activity Sidebar (Ctrl+B)
- Toggle Info Sidebar (Ctrl+Shift+P)
- Toggle Bottom Panel (Ctrl+`)
- Fullscreen (F11)
- Zoom In (Ctrl++)
- Zoom Out (Ctrl+-)
- Reset Zoom (Ctrl+0)
- Toggle Zen Mode (Ctrl+K Z)

#### Tools Menu

- Command Palette (Ctrl+P)
- Plugin Manager
- MCP Manager
- Preferences
- Extensions Gallery

#### Help Menu

- Keyboard Shortcuts (Ctrl+?)
- API Documentation
- Report Bug (⌘ Bug Report)
- About Atlas

#### Menu Behavior

- Accessible via Alt key (Alt+F for File, etc.)
- Shows keyboard shortcuts inline
- Submenus on hover
- Keyboard navigation with arrow keys

---

## Layer 2: Context Navigation

### Main Panel Navigation

#### Panel Header

```
[Icon] Panel Title          [Search] [≡ Menu]
```

Each panel has a header containing:

- **Icon**: Visual identifier (folder for files, chat bubble for chat, etc.)
- **Title**: Current context name
- **Search**: Quick search/filter (if applicable)
- **Menu**: Panel-specific options

#### Panel Tab System

Tabs appear below header for multiple open items:

```
[🗂️ Project] [📄 Document] [🌐 Browser Tab] [✕]
```

- **Tab Format**: Icon + name
- **Active Tab**: Blue accent color
- **Close Button**: X on rightmost tab
- **Right-Click**: Close, close others, close to right
- **Drag Tab**: Reorder or move to different panel

#### Keyboard Navigation

- **Ctrl+Tab**: Next tab
- **Ctrl+Shift+Tab**: Previous tab
- **Ctrl+W**: Close current tab
- **Ctrl+Shift+T**: Reopen last closed tab
- **Ctrl+1-8**: Jump to specific tab

---

### Explorer Sidebar (Dynamic)

The left sidebar content changes based on current panel:

#### Chat Panel - Recent Conversations

```
Recents
  • Today
    - Task: Build API
    - Task: Review PR
  • Yesterday
    - Memory: User preferences
    - Memory: Project structure
Favorites ⭐
Archived
Search...
```

Navigation:

- Click item to open
- Right-click for options (pin, delete, archive)
- Drag to reorder
- Search filters list

#### Files Panel - Directory Tree

```
Project Root (/)
  📁 src/
     📁 components/
        📄 Button.tsx
        📄 Modal.tsx
     📁 utils/
        📄 helpers.ts
  📁 tests/
  📄 README.md
```

Navigation:

- Click folder to expand/collapse
- Click file to preview/open
- Drag files to move
- Right-click for context menu (copy, delete, rename)

#### Browser Panel - Tabs & History

```
Open Tabs
  • Google (google.com)
  • GitHub (github.com) [active]
  • Stack Overflow
History (last 7 days)
  • docs.python.org
  • npmjs.com
Bookmarks
```

Navigation:

- Click tab to switch
- Click history item to reload
- Right-click for options

#### Terminal Panel - Sessions & Commands

```
Sessions
  • Main Terminal [1]
  • SSH: prod-server
Commands (recent)
  • npm run build
  • git commit -m "..."
  • python test.py
```

Navigation:

- Click session to switch
- Click command to re-run
- Right-click session for options (rename, close, etc.)

---

## Layer 3: Detail Navigation

### Info Sidebar (Right)

The right panel shows context-specific information:

#### Properties Panel (Files)

```
File Properties
📄 app.jsx
Size: 4.2 KB
Modified: 2 days ago
Owner: user
Permissions: 644

Preview
[Image/code preview]

Recent Versions
• version-2 (1 day ago)
• version-1 (3 days ago)
```

Keyboard:

- Tab between sections
- Ctrl+Shift+P to close sidebar

#### Properties Panel (Chat)

```
Conversation Properties
Created: Aug 1, 2026
Duration: 2h 15m
Token Usage: 45K / 100K
Model: Claude 3.5
Status: Complete

Related Items
• File: src/api.js
• Task: API Review
• Memory: Architecture

Export
[Export buttons]
```

#### Inspector Panel (Browser)

When browser is focused, inspector shows:

```
DOM Inspector
<div class="container">
  <div class="header">
    <h1>Title</h1>
  </div>
</div>

Styles
.container {
  padding: 16px;
  display: flex;
}

Performance
DOM Nodes: 1,245
Memory: 24 MB
Time to Interactive: 1.2s
```

Keyboard:

- Ctrl+Shift+I to toggle inspector
- Arrow keys to navigate DOM tree
- Click element to select in page

---

## Command Palette (Global)

### Activation

- **Keyboard**: Ctrl+P
- **Menu**: Tools → Command Palette
- **Button**: Visible in status bar

### Interface

```
┌──────────────────────────────────┐
│ > search term                    │ [Close: Esc]
├──────────────────────────────────┤
│ [Pin] Command Name ... Ctrl+Shift+Q
│       Description of what command does
│
│ [Pin] Another Command ... Ctrl+K X
│       Description ...
│
│ Recent Commands
│   > Last command run
│   > Previous command
└──────────────────────────────────┘
```

### Features

- **Fuzzy Search**: Type partial text to find commands
- **Pinned Commands**: Show starred commands at top
- **Recent Commands**: Show recently used
- **Keyboard Navigation**:
  - Arrow Up/Down: Navigate results
  - Enter: Execute selected command
  - Tab: Focus on command (show details)
  - Esc: Close palette
  - ⭐: Pin command (Ctrl+Star)

### Command Categories

- **Agent Commands** (Run, Plan, Cancel, Approve)
- **File Commands** (Open, Save, Search, Compare)
- **Terminal Commands** (Run Command, New Tab, SSH)
- **Browser Commands** (New Tab, Bookmark, Inspector)
- **View Commands** (Toggle Panel, Split, Fullscreen)
- **Plugin Commands** (Install, Configure, Update)
- **Settings Commands** (Open Settings, Preferences)
- **Help Commands** (Shortcuts, Documentation, Report)

---

## Keyboard Navigation Hierarchy

### Global Navigation (Any Context)

```
Ctrl+P     : Command Palette
Alt+F/E/V/T/H : Menu access
Ctrl+1-8   : Jump to tab in current panel
Ctrl+Tab   : Next tab
Ctrl+Shift+Tab : Previous tab
Ctrl+W     : Close current tab
Ctrl+Q     : Quit application
```

### Panel Focus Navigation

```
Ctrl+'     : Focus Chat
Ctrl+B     : Focus Browser
Ctrl+E     : Focus Files
Ctrl+J     : Focus Terminal
Ctrl+M     : Focus Memory
Ctrl+A     : Focus Agents
Ctrl+L     : Focus Planner
Ctrl+H     : Focus Home
```

### Sidebar Toggle

```
Ctrl+Shift+P : Toggle Info Sidebar
Ctrl+Shift+E : Toggle Explorer (in Files panel)
Ctrl+K Ctrl+X : Toggle Activity Sidebar
```

### Zen Mode (Distraction-Free)

```
Ctrl+K Z   : Toggle Zen Mode (hides all sidebars, status bar)
Esc        : Exit Zen Mode
```

---

## Focus Management

### Focus Order (Tab Key)

1. Activity Sidebar icons
2. Main Panel (current tab content)
3. Info Sidebar
4. Status Bar buttons
5. (Cycle back to Activity Sidebar)

### Focus Indicators

- **2px Blue Border**: #00A8E8, all edges
- **High Contrast**: Works on all backgrounds
- **Outset**: Focus ring outside element boundary
- **Animation**: 100ms fade-in when focused

### Focus Trap Behavior

- **Dialogs**: Focus trapped within dialog
- **Context Menus**: Focus released when closed
- **Panels**: Focus released on click outside

### Keyboard Shortcuts for Focus

- **Ctrl+0**: Reset focus to main panel
- **Ctrl+H**: Home (help/default view)
- **Tab**: Move to next focusable element
- **Shift+Tab**: Move to previous focusable element

---

## Search & Quick Access

### Global Search (Ctrl+Shift+F)

Search across all content types:

- Files and directories
- Memory facts
- Browser history
- Terminal history
- Agent conversations
- Plugins and extensions

Results grouped by type, keyboard navigation between groups.

### File Search (Ctrl+F in Files panel)

Filters file tree in real-time:

- Case sensitive toggle
- Regex support
- Exclude patterns

### Memory Search (Ctrl+F in Memory panel)

Searches facts and relationships:

- Full-text search
- Filter by type (fact, relationship, event)
- Timeline filtering

### Terminal Search (Ctrl+F in Terminal)

Searches command output and history:

- Case sensitive toggle
- Regex support
- Highlight all matches

---

## Breadcrumb Navigation

### File Breadcrumb

```
Project Root / src / components / Button.tsx
```

**Interaction**:

- Click segment to navigate to parent
- Shows folder contents on hover
- Right-click for context menu

### Chat Breadcrumb

```
Conversations / Today / Build API Task
```

**Interaction**:

- Click to navigate history
- Shows related conversations on hover

### Browser Breadcrumb

```
Google / Search / "atlas runtime"
```

**Interaction**:

- Click to go back
- Shows history dropdown

---

## Navigation State Persistence

### What's Remembered

- Active panel (Chat, Files, Browser, etc.)
- Open tabs and their order
- Expanded/collapsed tree nodes
- Search query (if applicable)
- Scroll position in lists
- Sidebar widths
- Floating window positions
- Recent visited items

### Storage Location

`~/.atlas/workspaces/{workspace-name}/navigation-state.json`

### Restoration

- On application launch: Restore to previous state
- On workspace switch: Apply workspace-specific navigation
- On panel close/open: Remember last state before close

### Clear Navigation State

**Option**: Edit → Clear Navigation State (resets to defaults)

---

## Navigation Error Handling

### Broken Links / Dead Items

- Show error indicator (red dot)
- Display reason (file deleted, agent stopped, etc.)
- Offer quick fixes (remove from history, re-index)

### Circular Navigation Prevention

- Don't allow navigation that creates loops
- Show warning before action

### Navigation Timeout

- If navigation takes >5 seconds, show loading indicator
- Allow cancellation
- Offer retry after timeout

---

## Accessibility Considerations

### Screen Reader Support

- All navigation items have descriptive labels
- Current location announced
- Navigation structure clear from outline (Ctrl+?)
- Skip links available (Ctrl+Shift+K)

### High Contrast Mode

- All focus indicators visible
- Text contrast ≥7:1
- Color not used alone to indicate state

### Reduced Motion

- Disable navigation animations
- Show changes instantly
- Respect `prefers-reduced-motion` CSS media query

### Keyboard Only Navigation

- Every navigation action accessible via keyboard
- No click-drag requirements
- Tab order logical and predictable

---

## Mobile/Touch Considerations (Future)

Phase 1 is desktop-only, but architecture allows for:

- Swipe navigation (left/right to switch panels)
- Tap-and-hold for context menus
- Long-press for quick actions
- Touch gestures on resizable panels

---

**Navigation Architecture Version**: 1.0  
**Last Updated**: August 2, 2026

This specification defines the complete navigation model for Atlas. All UI interactions must follow this hierarchy and keyboard shortcut scheme.
