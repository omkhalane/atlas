# Sidebar Specifications

## Activity Sidebar (Left, 48px Fixed)

### Purpose

Primary mode switcher and workspace navigation. Always visible. Provides quick access to all major features without taking up much space.

### Dimensions

- **Width**: 48px (fixed, not resizable)
- **Height**: Full window height minus top and bottom bars
- **Background**: #0A0E27 (darkest color)
- **Border**: 1px right, #1A1F3A
- **Padding**: 8px vertical, 0px horizontal

### Icon Grid

- **Container Width**: 32px (48px - 16px padding)
- **Icon Size**: 24×24px
- **Spacing Between Icons**: 8px (vertically)
- **Icon Groups**: Separated by 12px visual gap

### Icon Set & Behavior

#### Group 1: Navigation

```
🏠 Home         (Alt+H)        - Default/recent view
💬 Chat         (Ctrl+')       - Agent conversation
🌐 Browser      (Ctrl+B)       - Web browsing
📁 Files        (Ctrl+E)       - File explorer
⌨️  Terminal      (Ctrl+J)       - Command line
```

#### Group 2: Context

```
🧠 Memory       (Ctrl+M)       - Knowledge browser
🤖 Agents       (Ctrl+A)       - Agent management
📊 Planner      (Ctrl+L)       - Task planning
```

#### Group 3: System

```
🔧 Settings     (Ctrl+,)       - Preferences
🔌 Plugins      (Ctrl+Shift+P) - Plugin manager
```

### Visual States

#### Idle State

- Icon: #7A8BA0 (medium gray)
- Background: Transparent
- Border: None

#### Hover State

- Icon: #E0E0E0 (light gray)
- Background: #1A1F3A (subtle highlight)
- Border: None
- Tooltip appears (100ms delay)

#### Active State (Current View)

- Icon: #00A8E8 (electric blue)
- Background: #1A2F4A (darker blue tint)
- Border: 2px left, #00A8E8
- Animate: 100ms fade-in of accent

#### Click Response

- Immediate visual feedback (click animation)
- Switch to view (instant)
- Content area updates
- Smooth focus transition

### Tooltips

- **Activation**: Hover for 100ms
- **Position**: Appear to the right, vertically centered
- **Width**: 120px max
- **Content**: View name + keyboard shortcut
- **Fade-out**: 100ms after mouse leaves

### Right-Click Context Menu

```
+ Split Right        (Ctrl+Shift+S)
- Close
- Detach             (Ctrl+Shift+D)
- Full Screen        (F11)
- Reset Layout
```

### Animation Specifications

#### Icon Transition

- **Duration**: 100ms
- **Curve**: ease-out
- **Properties**: color, background-color
- **No Motion**: Respected when `prefers-reduced-motion` enabled

#### Active Indicator

- **Type**: Left border slide-in
- **Duration**: 150ms
- **Curve**: ease-out
- **Direction**: Fade + slide from 0-2px

---

## Explorer Sidebar (Left Variable, Appears in Main Panel Header)

### Terminology

The explorer sidebar is **not** a separate sidebar like activity. It's the left subsection of the main panel, containing context-specific navigation.

### Dimensions

- **Width**: 250px default, resizable 150-400px
- **Height**: Full height of main content area
- **Background**: #0F1229
- **Border**: 1px right, #1A1F3A
- **Resizable**: Right edge draggable
- **Collapsible**: Click header collapse button to hide

### Components (Varies by Panel)

#### Chat Panel - Conversations Explorer

```
┌────────────────────────────────┐
│ 💬 Conversations        [×][⊡] │  Header: 32px
├────────────────────────────────┤
│ [🔍 Search conversations...]  │  Search: 32px
├────────────────────────────────┤
│ 📌 Pinned                      │  Section Header
│  • Task: Build API             │  Item: 32px height
│  • Memory: Architecture         │
│                                │
│ 📅 Today                       │
│  • Chat: Getting started        │
│  • Chat: Error handling         │
│                                │
│ 📅 Yesterday                   │
│  • Chat: Architecture review    │
│  • Chat: Performance tuning     │
│                                │
│ 🗂️  Archive (12 items)         │  Collapsed section
└────────────────────────────────┘
```

**Interaction**:

- Click item to open
- Right-click for options: pin, delete, export, archive
- Drag to reorder recent
- Search filters in real-time
- Scroll for more items

#### Files Panel - Directory Tree

```
┌────────────────────────────────┐
│ 📁 Project          [×][⊡]     │  Header
├────────────────────────────────┤
│ [🔍 Search files...]           │  Search (sticky)
├────────────────────────────────┤
│ ⭐ Favorites                   │  Section
│  • ./src/main.ts               │
│  • ./package.json              │
│                                │
│ ▼ Project Root (/)             │  Expandable
│  ▼ src/                        │  (Blue chevron = open)
│   ▶ components/                │  (Gray chevron = closed)
│   ▶ utils/                     │
│   ▶ services/                  │
│   📄 index.ts                  │
│   📄 config.ts                 │
│  ▶ tests/                      │
│  ▶ docs/                       │
│  📄 README.md                  │
│  📄 package.json               │
│                                │
│ [+] New File      [-] Delete   │  Action buttons
└────────────────────────────────┘
```

**Interaction**:

- Click chevron to expand/collapse folders
- Click file to preview/open (in main panel)
- Double-click file to open in split
- Right-click file for options: rename, delete, copy path, git commands
- Drag file to move (with visual feedback)
- Type to search/filter tree

#### Terminal Panel - Sessions

```
┌────────────────────────────────┐
│ 🖥️  Terminals          [×][⊡]   │
├────────────────────────────────┤
│ [🔍 Search commands...]        │
├────────────────────────────────┤
│ ▼ Main (0)                     │  Sessions
│  └ Ready                       │  (Number = unread count)
│
│ ▼ SSH: prod-01                 │
│  └ Connected                   │
│
│ ▶ Build                        │
│  └ Running: npm build          │
│
│ Recent Commands                │
│  $ npm run dev                 │
│  $ git status                  │
│  $ npm test                    │
│
│ [+] New Session                │
└────────────────────────────────┘
```

**Interaction**:

- Click session to switch
- Right-click session: rename, close, duplicate
- Click command to re-run
- Double-click to open in split terminal

#### Browser Panel - Tabs & Bookmarks

```
┌────────────────────────────────┐
│ 🌐 Browser            [×][⊡]   │
├────────────────────────────────┤
│ [🔍 Search history...]         │
├────────────────────────────────┤
│ ▶ Open Tabs (3)                │
│  ▼ google.com                  │
│  ▼ github.com                  │
│   ▶ Settings                   │
│   ▶ Notifications              │
│  ▶ stackoverflow.com           │
│
│ ▶ History (Today)              │
│  • docs.python.org             │
│  • npmjs.com                   │
│  • mdn.org                     │
│
│ ▼ Bookmarks                    │
│  ▶ Documentation               │
│  ▶ Tools                       │
│  • MDN Web Docs                │
│
│ [+] New Tab                    │
└────────────────────────────────┘
```

**Interaction**:

- Click tab to switch
- Right-click tab: close, close others, bookmark
- Click history item to load
- Drag items to organize
- Search filters all sections

#### Memory Panel - Facts & Timeline

```
┌────────────────────────────────┐
│ 🧠 Memory             [×][⊡]   │
├────────────────────────────────┤
│ [🔍 Search facts...]           │
├────────────────────────────────┤
│ ▼ Pinned (5)                   │
│  • Architecture: MVC pattern   │
│  • User: John's preferences    │
│  • Config: Database URL        │
│
│ ▼ Timeline                     │
│ 📍 20 min ago                  │
│  • Created fact: API design    │
│ 📍 1 hour ago                  │
│  • Updated: User context       │
│ 📍 Yesterday                   │
│  • Imported: Knowledge base    │
│
│ ▼ By Type                      │
│  ▶ Facts (24)                  │
│  ▶ Relationships (8)           │
│  ▶ Events (156)                │
│
│ [+] New Fact                   │
└────────────────────────────────┘
```

**Interaction**:

- Click fact to view details
- Pin/unpin with star icon
- Timeline events scrollable
- Search filters facts
- Right-click for export/delete

### Search Behavior

#### Real-time Filtering

- As user types, filter results immediately
- Highlights matching text
- Shows result count: "3 / 12 items"
- Escape to clear search

#### Search Scope

- **Case Sensitive**: Off by default, toggle with `Aa` button
- **Regex**: Toggle with `.*` button
- **Fuzzy**: Enabled by default
- **Whole Word**: Toggle with `W` button

#### No Results State

Shows icon and message:

```
🔍
No items match "impossible-search"
Suggestions:
• Check spelling
• Try different keywords
• Clear filters (X)
```

### Section Collapsing

Each section in explorer has a chevron to expand/collapse:

- **Chevron Left**: Section collapsed, items hidden
- **Chevron Down**: Section expanded, items visible
- **Click**: Toggle state
- **State Persistence**: Remember for session

### Scrolling Behavior

#### Scrollbar

- Always visible (not hidden on non-hover)
- 6px wide, dark gray (#3A4A5A)
- Highlight on hover (lighter gray)
- Click and drag to scroll

#### Virtual Scrolling (Large Lists)

- Only render visible items
- Smooth scrolling 60 FPS
- Placeholder content for off-screen items
- Memory efficient for 1000s of items

#### Keyboard Scrolling

- Arrow Up/Down: Scroll one item
- Page Up/Down: Scroll full viewport
- Home/End: Jump to start/end

### Context Menu (Right-Click)

#### Files Context Menu

```
🔖 Bookmark
✂️  Cut               (Ctrl+X)
📋 Copy              (Ctrl+C)
📌 Copy Path         (Ctrl+Shift+C)
✏️  Rename            (F2)
🗑️  Delete            (Delete)
─────────────────
📊 Properties        (Alt+Enter)
🔄 Show in Folder
📈 Git Status
📖 Recent Versions
```

#### Chat Context Menu

```
✏️  Rename            (F2)
⭐ Pin               (Ctrl+P)
🔗 Copy Link         (Ctrl+Shift+C)
📊 Statistics
🗑️  Delete            (Delete)
📦 Export            (Ctrl+E)
🔄 Duplicate         (Ctrl+D)
```

### Styling Details

#### Item Styling

- **Height**: 32px
- **Padding**: 8px left, 8px right
- **Font Size**: 12px
- **Color**: #A0A0A0 (normal), #E0E0E0 (hover/focused)

#### Folder Icons

- **Closed**: ▶ (dark gray)
- **Open**: ▼ (blue when hovered)
- **Width**: 16px (includes click zone)

#### File Icons

- Specific to file type (detailed in icons specification)
- 16×16px
- Left of file name

#### Hierarchy Indentation

- Each nesting level: +16px left margin
- Maintains visual tree structure
- Maximum 8 levels deep

### Keyboard Navigation

#### Arrow Keys

- **Up**: Move to previous item
- **Down**: Move to next item
- **Left**: Collapse current folder
- **Right**: Expand current folder, then move into first child

#### Enter/Return

- Open selected item

#### Spacebar

- Toggle expand/collapse folder

#### Delete

- Delete selected item (with confirmation)

#### F2

- Rename selected item

#### Ctrl+C/V/X

- Copy/Paste/Cut selected item

---

## Info Sidebar (Right, 300px Variable)

### Purpose

Context-specific details panel. Shows properties, metadata, related items, and secondary information about the currently selected item.

### Dimensions

- **Width**: 300px default, resizable 200-400px
- **Height**: Full content area
- **Background**: #0F1229
- **Border**: 1px left, #1A1F3A
- **Position**: Always right side
- **Collapsible**: Ctrl+Shift+P to toggle

### Resizing

- Left edge draggable
- Snap points at 250px, 300px, 350px
- Double-click to toggle expand/collapse
- Minimum width: 200px, Maximum: 400px

### Content Areas

#### Heading

- **Icon**: Context-specific
- **Title**: Name of selected item
- **Close Button**: X (same as collapse)

#### Metadata Section

- **Item Type**: Label (File, Conversation, Memory, etc.)
- **Created**: Timestamp
- **Modified**: Timestamp
- **Size/Count**: If applicable
- **Status**: Current state (running, completed, error, etc.)

#### Details Section

Varies by context:

- **File**: Permissions, owner, size, git status
- **Chat**: Model, duration, tokens, participants
- **Terminal**: PID, status, command, exit code
- **Browser**: URL, SSL info, performance metrics
- **Memory**: Type, last accessed, relationships

#### Related Items Section

```
Related Items
▶ Files (2)
  • src/api.ts
  • src/types.ts
▶ Conversations (1)
  • Architecture Discussion
▶ Tasks (3)
  • Implement API
  • Test Coverage
  • Code Review
```

Click to navigate to related item.

#### Preview Section

- **Type-specific Preview**: Code, markdown, image, etc.
- **Height**: Dynamic (max 200px)
- **Scrollable**: If content exceeds max height
- **Copy Button**: Ctrl+C to copy contents

#### Actions Section

- **Primary Actions**: Save, Export, Delete (contextual)
- **Secondary Actions**: More options menu (⋮)
- **Button Size**: 32px height
- **Spacing**: 8px between buttons

### Styling

#### Text Hierarchy

- **Titles**: 14px, #E0E0E0 (bold)
- **Labels**: 11px, #7A8BA0 (monospace for tech data)
- **Values**: 12px, #A0A0A0
- **Links**: 12px, #00A8E8 (clickable items)

#### Sections

- **Separator**: 1px top border, #1A1F3A
- **Padding**: 12px top/bottom, 12px left/right
- **First Section**: No top border

#### Copy-to-Clipboard

- **Interaction**: Click value to copy
- **Feedback**: "Copied!" toast (1 second)
- **Keyboard**: Ctrl+C in focused value field

### Dynamic Content Loading

#### Lazy Loading

- Expand section to load details
- Show spinner while loading (max 1 second)
- Fallback to partial data if full load fails

#### Refresh Capability

- Refresh button (🔄) next to title
- Re-fetch current item details
- Update timestamp shows when last refreshed

### Accessibility

#### Keyboard Access

- Tab: Move through sections
- Enter: Expand/collapse section
- Arrow keys: Navigate within lists
- Copy shortcut shows in hover

#### Screen Reader Support

- Section headers marked as headings
- Relationships marked as lists
- Actions marked as buttons

### Empty State

When no item selected:

```
No Selection
Select an item to view details
```

---

## Sidebar Persistence

### Remember State

- **Visibility**: Explorer/Info sidebar open/closed
- **Widths**: Explorer width, Info sidebar width
- **Collapsed Sections**: Which sections were expanded/collapsed
- **Search Queries**: Last search in each explorer

### Storage

`~/.atlas/workspaces/{workspace-name}/sidebar-state.json`

### Restoration

- On workspace open: Restore sidebar layout
- On panel switch: Load that panel's explorer state
- Per workspace: Each workspace has independent sidebar state

---

**Sidebar Specifications Version**: 1.0  
**Last Updated**: August 2, 2026
