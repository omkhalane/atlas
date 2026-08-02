# Command Palette Specification

## Purpose & Mental Model

The Command Palette is the "spotlight" of Atlas—the universal access point for every action, view, file, and feature in the application. It's the most powerful navigation tool and should feel instant and discoverable.

### Guiding Principle

"Everything at your fingertips, one keystroke away."

---

## Activation

### Keyboard Shortcut

- **Linux**: Ctrl+P
- **Bind**: System-wide if possible (respect OS conflicts)
- **Always Available**: Even in dialogs (closes dialog first)

### Alternative Access

- **Menu**: Tools → Command Palette
- **Toolbar**: Button in status bar (rarely used)

### Modal Appearance

```
┌──────────────────────────────────────────────────┐
│ > search text                           [Ctrl+P] │ Dismiss
├──────────────────────────────────────────────────┤
│ ▪ Command Name                        Ctrl+Shift+Q
│   Description of what this command does
│
│ ▪ Another Command                          Alt+K
│   What this does and when to use it
│
│ ▪ Third Command                            Ctrl+G
│   More details and information
│
└──────────────────────────────────────────────────┘
```

### Dimensions

- **Width**: 520px (centered on screen)
- **Max Height**: 600px (scroll if more items)
- **Top Margin**: 80px from window top
- **Backdrop**: Translucent dark overlay (opacity: 40%)

---

## Search & Filtering

### Fuzzy Search Algorithm

- Matches partial text anywhere in command name/description
- Prioritizes prefix matches over anywhere matches
- Case-insensitive by default
- Scoring:
  1. Exact match (lowest score, highest priority)
  2. Prefix match (command starts with search)
  3. Word boundary match (after space or punctuation)
  4. Substring match (anywhere in name)
  5. Description match (lowest priority)

### Search Examples

| Query       | Matches                              | Score                     |
| ----------- | ------------------------------------ | ------------------------- |
| `oef`       | Open File                            | High (prefix match)       |
| `file`      | Open File, Recent Files, Delete File | High (all contain "file") |
| `sss`       | Save Session Snapshot                | Low (fuzzy substring)     |
| `agent run` | Run Agent, Stop Agent Running        | High (multi-term match)   |

### Real-Time Filtering

- Results update as user types
- Show count: "Showing 3 of 15 commands"
- Highlighted matching text in results
- Results ordered by relevance score

### Keyboard Search Modifiers

#### Prefix Filtering

- `file:` - Show only file-related commands
- `agent:` - Show only agent commands
- `plugin:` - Show only plugin commands
- `settings:` - Show only settings

#### Type Filtering

- `@function` - Show only executable commands
- `@file` - Show files in current workspace
- `@memory` - Show memory facts and items
- `@recent` - Show recent commands/files

#### Sorting Options (Type `>`)

- `>recent` - Sort by most recent use
- `>frequent` - Sort by frequency (how often used)
- `>alpha` - Sort alphabetically
- `>score` - Sort by search relevance (default)

### Clear Search

- Esc: Clear and close
- Ctrl+U: Clear search term only, keep palette open
- Backspace: Delete one character (delete key works normally)

---

## Result Categories & Organization

### Pinned Commands (Top)

```
▪ [PIN ICON] Run Current Agent         Ctrl+Enter
  Execute the active agent immediately
```

Commands explicitly pinned by user appear first. Up to 5 pinned. Ctrl+Star to pin/unpin.

### Recent Commands

```
Recent (Used in last 24 hours)
▪ Deploy to Production                 Ctrl+Shift+D
  Ship built artifacts to prod server

▪ View Memory Timeline                 Ctrl+K M
  Open the memory browser timeline
```

Commands user has executed recently (auto-sorted by usage time).

### Agent Commands

```
Agent (Run, control, manage)
▪ Run Agent                            Ctrl+Enter
  Start the active agent with current plan

▪ Cancel Agent                         Ctrl+Shift+C
  Stop running agent immediately

▪ Approve Agent Action                 Ctrl+Y
  Approve pending agent request

▪ Pause Agent                          Ctrl+Shift+Space
  Pause agent execution

▪ View Agent Logs                      Ctrl+K L
  Open agent execution logs
```

Commands that affect agent execution.

### File Commands

```
Files (Open, search, manage)
▪ Open File                            Ctrl+O
  Browse and open file in editor

▪ Recent Files                         Ctrl+R
  List 10 most recently opened files

▪ Search Files                         Ctrl+Shift+F
  Full-text search in workspace

▪ New File                             Ctrl+Alt+N
  Create new file
```

### View Commands

```
Views (Navigate, organize)
▪ Toggle Chat View                     Ctrl+'
  Show/hide chat panel

▪ Toggle File Explorer                 Ctrl+E
  Show/hide file explorer

▪ Focus Chat                           Ctrl+Shift+C
  Bring chat panel to focus

▪ Split View Horizontal                Ctrl+Shift+\ (depends on context)
  Split current panel horizontally
```

### Plugin Commands

```
Plugins (Install, manage, configure)
▪ Install Plugin                       (none)
  Browse and install from plugin marketplace

▪ Manage Installed Plugins             Ctrl+P P
  View, update, configure plugins

▪ Reload Plugins                       Ctrl+Shift+P
  Reload all installed plugins
```

### Settings & Preferences

```
Settings (Configure, customize)
▪ Open Settings                        Ctrl+,
  Edit application preferences

▪ Themes                               (none)
  Browse and select theme

▪ Keyboard Shortcuts                   Ctrl+K Ctrl+S
  View and edit keyboard shortcuts

▪ Configure MCP Servers                (none)
  Set up Model Context Protocol servers
```

### Help & Documentation

```
Help (Learn, support)
▪ Keyboard Shortcuts Reference         Ctrl+?
  Show complete shortcut list

▪ API Documentation                    (none)
  Open Atlas API documentation

▪ Report Bug                           (none)
  Open bug report form

▪ About Atlas                          (none)
  Show version and copyright info
```

### Workspace & File Navigation

```
[Divider]
recent_project.md
src/components/Button.tsx
config.json
.env.example
```

Recent files appear at bottom, sorted by access time. Click to open.

---

## Keyboard Navigation

### Arrow Keys

- **Up**: Select previous command
- **Down**: Select next command
- **Page Up**: Scroll up 5 items
- **Page Down**: Scroll down 5 items
- **Home**: Select first command
- **End**: Select last command

### Selection Actions

- **Enter**: Execute selected command
- **Ctrl+Enter**: Execute selected command and keep palette open
- **Tab**: Preview selected command (show details/help)
- **Escape**: Close palette

### Pin/Unpin

- **Ctrl+Star** (or Ctrl+;): Pin/unpin selected command
- Shows confirmation toast

### Copy Command Name

- **Ctrl+C**: Copy selected command name or path to clipboard
- Shows "Copied!" toast

---

## Command Details & Preview

When user tabs onto a command, show details:

```
┌──────────────────────────────────────────────────┐
│ > search text                                    │
├──────────────────────────────────────────────────┤
│ ▪ Run Agent                              Ctrl+Enter
│   Start the active agent with current plan
│
│   Details:
│   Category: Agent Control
│   Keyboard: Ctrl+Enter
│   Last Used: 15 minutes ago (2 times today)
│
│   When Running:
│   • Agent switches to "Executing" state
│   • Timeline updates with execution info
│   • Browser/Terminal output streamed to panels
│
└──────────────────────────────────────────────────┘
```

### Detail Sections

- **Category**: Which category command belongs to
- **Keyboard**: Current keyboard shortcut (editable)
- **Last Used**: When user last executed this
- **Usage Count**: Total times executed today
- **Description**: Full help text

---

## Command Types

### Execute Commands (Callable)

```
▪ Run Agent
  Execute/invoke a function with no arguments
```

- Standard action commands
- Immediately executable
- No input required

### File Commands (Navigation)

```
▪ recent_project.md
  Open: /home/user/projects/atlas/docs/recent_project.md
```

- File path shown in description
- Press Enter to open
- Shows file size, modified date

### Workspace Commands

```
▪ Switch Workspace: production
  Switch to production workspace configuration
```

- Navigate to different workspace
- Show workspace details on hover

### Settings Commands

```
▪ Theme: Dracula
  Currently: System Default
```

- Configure application settings
- Show current value

---

## Command Palette States

### Initial State (Just Opened)

- Empty search
- Show pinned commands
- Show recent commands (last 10)
- Show command categories
- Focus on search input

### With Results

- Matching commands listed
- Grouped by category
- Sorted by relevance
- Best match highlighted
- Result count shown

### No Results

```
┌──────────────────────────────────────────────────┐
│ > impossible search term                         │
├──────────────────────────────────────────────────┤
│ No commands match "impossible search term"
│
│ Tips:
│ • Did you mean: "create test"?
│ • Try simpler keywords
│ • Press Ctrl+? for help
│
└──────────────────────────────────────────────────┘
```

### Loading State

If search involves async operations (file indexing, etc.):

```
┌──────────────────────────────────────────────────┐
│ > search                                         │
├──────────────────────────────────────────────────┤
│ ⟳ Searching... (showing 5 of 12+ results)
│
│ [Results shown as they load...]
│
└──────────────────────────────────────────────────┘
```

---

## Customization & Settings

### Remapping Shortcuts

**Settings → Keyboard → Command Palette**

```
Command Palette Shortcuts:
  Ctrl+P   → Open Command Palette (primary)
  Ctrl+Shift+P → Open Command Palette (alternative)
  F1 → Open Command Palette (alternative)

Quick Filter Hotkeys:
  @file  → Search files only
  @agent → Agent commands only
  >recent → Sort by recent usage
```

### Custom Commands

**Settings → Custom Commands**

Users can create custom commands that appear in palette:

- Bash aliases
- Script shortcuts
- Agent templates
- File shortcuts

### Workspace-Specific Commands

Commands filtered based on current workspace:

- Some commands only available in specific workspaces
- Example: "Deploy to Production" only in prod workspace

---

## Accessibility

### Screen Reader

- Palette announced as "Command Palette, modal dialog"
- Search box label: "Search commands"
- Each result: "[Number]. [Command name]. [Shortcut]. [Description]"
- Currently selected: "Selected" announced on change

### High Contrast

- Commands remain readable on dark background
- Focus indicator visible (blue highlight)
- Text contrast ≥7:1

### Keyboard Only

- All functions accessible without mouse
- Tab order: Search → Results → Execute
- Escape closes palette

### Reduced Motion

- No animation on open/close (instant)
- Scrolling not animated
- Transitions disabled

---

## Performance & Optimization

### Search Optimization

- Results returned within 50ms (max)
- Debounce search input 100ms before filtering
- Cache recent searches (10-item limit)
- Virtual scrolling for 100+ results

### Indexing

- Command index built on application start
- Incremental updates when plugins loaded
- Caches index to disk for fast reload
- Rebuild index on demand (Settings → Rebuild Command Index)

### Memory Management

- Keep last 5 searches in memory
- LRU cache for command history
- Unload detailed command info until previewed
- 50MB max palette data in memory

---

## Integration with Other Features

### Agent Integration

When agent is running:

- "Approve Agent Action" command available
- "Stop Agent" command available
- "View Agent Logs" command prominent
- Recent agent commands at top

### File Context

When in Files panel:

- "New File" command available
- "Delete File" command available
- "Search Files" command available
- Recent files of current type shown

### Terminal Context

When Terminal is focused:

- "New Terminal Tab" command available
- "Run Command" command prominent
- Recent commands shown
- SSH sessions listed

---

## Animation Specifications

### Open/Close

- **Duration**: Instant (no animation)
- **Fade-in**: Backdrop fades in 100ms
- **Scale**: Modal appears at full scale
- **Accessibility**: Instant, no delay for reduced-motion users

### Result Updates

- **Duration**: 100ms
- **Transition**: Fade between result sets
- **Highlight**: Selected item gets subtle blue glow

### Command Execution

- **Duration**: 200ms fade-out
- **Callback**: Command executes after palette closes
- **Feedback**: Toast confirmation for some commands

---

## Mobile/Touch (Future)

Phase 1 is keyboard/mouse. But architecture allows:

- Swipe to switch categories
- Long-press to pin command
- Tap to execute

---

## Troubleshooting & Help

### Common Issues

| Issue                   | Solution                                 |
| ----------------------- | ---------------------------------------- |
| Commands not showing    | Rebuild command index: Settings → System |
| Shortcut not working    | Check if another app captured it         |
| Slow search             | Reduce open files, rebuild index         |
| Plugin commands missing | Reload plugins: Ctrl+Shift+R             |

### Help Resources

- **Ctrl+?**: Show keyboard shortcuts
- **Tab on command**: View full help text
- **Settings → Help**: Official documentation links
- **Bug report**: Tools → Report Issue

---

**Command Palette Specification Version**: 1.0  
**Last Updated**: August 2, 2026

This specification defines the complete behavior and UX of the Command Palette. All command discovery and execution must follow this design.
