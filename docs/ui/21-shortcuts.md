# Keyboard Shortcuts Specification

## Global Shortcuts (All Contexts)

### Application Control

```
Ctrl+Q          Quit Atlas
Ctrl+,          Open Settings
Ctrl+?          Show Keyboard Shortcuts Reference
Ctrl+K Ctrl+S   Edit Keyboard Shortcuts
F1              Open Help
```

### View Navigation

```
Ctrl+'          Focus Chat (apostrophe key)
Ctrl+B          Focus Browser
Ctrl+E          Focus Files
Ctrl+J          Focus Terminal
Ctrl+M          Focus Memory
Ctrl+A          Focus Agents
Ctrl+L          Focus Planner
Ctrl+H          Focus Home

Ctrl+Tab        Next Tab
Ctrl+Shift+Tab  Previous Tab
Ctrl+W          Close Current Tab
Ctrl+Shift+T    Reopen Last Closed Tab

Alt+1-8         Jump to Tab 1-8 in Current Panel
```

### Sidebar Toggle

```
Ctrl+Shift+P    Toggle Info Sidebar
Ctrl+Shift+E    Toggle Explorer Sidebar
Ctrl+K Ctrl+X   Toggle Activity Sidebar
Ctrl+`          Toggle Bottom Panel

F11             Toggle Fullscreen
Ctrl+K Z        Toggle Zen Mode (hide all sidebars)
```

### Panel Management

```
Ctrl+Shift+S    Create Split View
Ctrl+Shift+D    Detach Panel as Floating Window
Ctrl+Shift+M    Minimize Panel to Sidebar
Ctrl+0          Reset Panel Layout
Ctrl+Shift+L    Restore Last Layout
```

### Universal Search & Navigation

```
Ctrl+P          Open Command Palette
Ctrl+Shift+F    Global Search (Files, Memory, History)
Ctrl+F          Search in Current Context
Ctrl+G          Go to Line (in text/code)
Ctrl+K Ctrl+G   Go to File in Project
```

### Selection & Editing

```
Ctrl+A          Select All
Ctrl+C          Copy
Ctrl+X          Cut
Ctrl+V          Paste
Ctrl+Z          Undo
Ctrl+Shift+Z    Redo
Ctrl+D          Duplicate Line/Item
Ctrl+/          Toggle Comment (in code)
```

### Agent Control

```
Ctrl+Enter      Run Current Agent
Ctrl+Shift+C    Cancel Agent
Ctrl+Y          Approve Agent Action
Ctrl+N          Deny Agent Action
Ctrl+Shift+Space Pause Agent
Ctrl+Shift+R    Restart Agent
Ctrl+K L        View Agent Logs
```

---

## Context-Specific Shortcuts

### Chat Panel

#### Navigation

```
Ctrl+F          Search Messages
Ctrl+Shift+F    Full-Text Search
Ctrl+Home       Jump to First Message
Ctrl+End        Jump to Last Message
```

#### Composition

```
Shift+Enter     New Line in Message
Ctrl+Enter      Send Message
Ctrl+Z          Undo Message Composition
Tab             Auto-Complete
```

#### Message Interaction

```
Ctrl+C          Copy Selected Text
Ctrl+K Ctrl+C   Copy Code Block
Ctrl+B          Bold Text (if composing)
Ctrl+I          Italic Text (if composing)
Alt+C           Copy Entire Message
```

#### Agent Feedback

```
Ctrl+Y          Approve Agent's Proposed Action
Ctrl+N          Deny Agent's Action
Ctrl+?          Show More Details on Task
```

---

### Browser Panel

#### Navigation

```
Ctrl+T          New Tab
Ctrl+W          Close Tab
Ctrl+N          New Window
Ctrl+L          Focus URL Bar
Ctrl+Tab        Next Tab
Ctrl+Shift+Tab  Previous Tab
Ctrl+Shift+M    Mute Tab
```

#### Page Navigation

```
Alt+Left        Back
Alt+Right       Forward
Ctrl+R          Reload
Ctrl+Shift+R    Hard Reload (clear cache)
Ctrl+H          History
Ctrl+Y          Downloads
Ctrl+B          Bookmarks
Ctrl+D          Bookmark Current Page
```

#### Page Interaction

```
Ctrl+F          Find on Page
Ctrl+G          Find Next Match
Ctrl+Shift+G    Find Previous Match
Ctrl+P          Print
Ctrl+S          Save Page
Ctrl+,          Page Settings
Ctrl+Shift+I    Developer Inspector (if enabled)
```

#### Zoom & Display

```
Ctrl++          Zoom In
Ctrl+-          Zoom Out
Ctrl+0          Reset Zoom
Ctrl+U          View Page Source
```

---

### Files Panel

#### Navigation & Selection

```
Ctrl+F          Search Files
Ctrl+K Ctrl+O   Open File
Ctrl+Enter      Open in Split View
Ctrl+Home       Jump to First File
Ctrl+End        Jump to Last File

Arrow Up        Previous Item
Arrow Down      Next Item
Left            Collapse Folder
Right           Expand Folder
```

#### File Operations

```
Ctrl+N          New File
Ctrl+Shift+N    New Folder
Ctrl+D          Delete File/Folder
F2              Rename File
Ctrl+C          Copy File Path
Ctrl+X          Cut File
Ctrl+V          Paste File
Ctrl+D          Duplicate File
```

#### File Comparison

```
Ctrl+K Ctrl+D   Show Diff
Ctrl+K D        Quick Diff
Ctrl+Shift+C    Copy Relative Path
```

#### Source Control (Git)

```
Ctrl+K G        Show Git Status
Ctrl+K Ctrl+G   Git Commands Menu
Ctrl+K B        Show Git Blame
Ctrl+K L        Show Commit Log
```

---

### Terminal Panel

#### Tab Management

```
Ctrl+Shift+`    New Terminal Tab
Ctrl+W          Close Terminal
Ctrl+Tab        Next Terminal
Ctrl+Shift+Tab  Previous Terminal
Ctrl+Shift+;    Terminal Settings
```

#### Terminal Input

```
Ctrl+C          Send SIGINT (interrupt)
Ctrl+Z          Send SIGSTOP (suspend)
Ctrl+\          Send SIGQUIT
Ctrl+D          Send EOF (if no text)
Shift+Insert    Paste (if Ctrl+V doesn't work)
```

#### Terminal Output

```
Ctrl+F          Search Terminal Output
Ctrl+L          Clear Screen
Ctrl+A Home     Go to Line Start
Ctrl+E End      Go to Line End
Page Up         Scroll Up
Page Down       Scroll Down
```

#### Copy & Selection

```
Ctrl+C          Copy Selected Text
Shift+Select    Extend Selection
Double-Click    Select Word
Triple-Click    Select Line
```

---

### Memory Panel

#### Navigation

```
Ctrl+F          Search Facts
Ctrl+Home       First Fact
Ctrl+End        Last Fact
Arrow Keys      Navigate Facts
```

#### Fact Operations

```
Ctrl+N          New Fact
Ctrl+E          Edit Selected Fact
Ctrl+D          Delete Fact
Ctrl+S          Save Fact
Ctrl+P          Pin/Star Fact
```

#### Display

```
Ctrl+K V        Show Graph View
Ctrl+K L        Show Timeline View
Ctrl+K T        Show Tree View
```

---

### Terminal Commands (Shell Aliases)

Users can set custom shell aliases that appear in command palette:

```bash
# Common patterns
Ctrl+Shift+B    npm build / make build
Ctrl+Shift+T    npm test / make test
Ctrl+Shift+R    npm run / ./run.sh
Ctrl+Shift+D    npm dev / npm start
```

---

## Keyboard Layouts

### Linux Default (QWERTY)

All shortcuts above assume QWERTY layout. Alt key = Option on macOS (Phase 2).

### Key Notation

- `Ctrl` = Control key (Linux, Windows)
- `Shift` = Shift key
- `Alt` = Alt key (not Option)
- `+` = Pressed together
- `→` = Then (sequence)
- `|` = Or (alternative)

### Non-ASCII Keys

- `` ` `` = Backtick / Grave accent (top-left)
- `'` = Apostrophe / Single quote
- `;` = Semicolon
- `\` = Backslash
- `/` = Forward slash
- `=` = Equals
- `-` = Minus / Hyphen

---

## Shortcut Customization

### User-Defined Shortcuts

Users can remap any built-in shortcut:

**Settings → Keyboard → Shortcuts**

```
Command Name                    Current Shortcut    Custom
────────────────────────────────────────────────────────────
Run Current Agent               Ctrl+Enter          [Edit]
Open Command Palette            Ctrl+P              [Edit]
Focus Chat                      Ctrl+'              [Edit]
```

### Remapping Process

1. Click [Edit] next to command
2. Press desired key combination
3. Conflicts are detected: "This shortcut conflicts with 'Copy'"
4. Press Enter to confirm or Esc to cancel
5. Changes saved immediately

### Revert to Defaults

**Settings → Keyboard → Reset All Shortcuts to Defaults**

---

## Accessible Shortcuts

### Single-Key Access (Not Using Modifier)

Avoid single-key shortcuts to prevent conflicts with input fields:

- ❌ `E` to open explorer (conflicts with typing)
- ✓ `Ctrl+E` to open explorer

### Modifier-Only Shortcuts

Never require only modifier keys (confusing):

- ❌ `Ctrl` alone to open menu
- ✓ `Ctrl+M` to open menu

### Avoid Web Conflicts

Avoid shortcuts that interfere with web browser when browsing:

- ⚠️ `Ctrl+S` (save) - safe in Atlas, conflicts in web pages
- ⚠️ `Ctrl+W` (close tab) - same as browser
- ✓ Use `Ctrl+Shift+` for browser-specific to minimize conflicts

### Dvorak & Alternative Layouts

- Shortcuts work on physical key position, not character
- `Ctrl+E` moves to the same physical key on Dvorak
- Linux respects layout switching automatically

---

## Keyboard Shortcut Reference Card

### Quick Print Card (Trifold)

**Panel Focus**

```
Ctrl+' Chat    Ctrl+B Browser  Ctrl+E Files
Ctrl+J Terminal  Ctrl+M Memory  Ctrl+A Agents
```

**Essential Actions**

```
Ctrl+P Command Palette       Ctrl+Z Undo
Ctrl+F Search              Ctrl+Shift+F Global Search
```

**Agent Control**

```
Ctrl+Enter Run          Ctrl+Shift+C Cancel
Ctrl+Y Approve          Ctrl+N Deny
```

**Editing**

```
Ctrl+C Copy             Ctrl+X Cut
Ctrl+V Paste            Ctrl+A Select All
```

**Views**

```
Ctrl+Shift+P Info Sidebar    Ctrl+K Z Zen Mode
Ctrl+Shift+S Split View      F11 Fullscreen
```

---

## Help System Integration

### In-App Shortcut Display

All buttons and menu items show shortcuts:

```
File
├─ New Agent .................... Ctrl+Shift+N
├─ Open Agent ................... Ctrl+O
├─ Save ......................... Ctrl+S
└─ Quit ......................... Ctrl+Q
```

### Keyboard Shortcut Reference (Ctrl+?)

Accessible anywhere, shows all shortcuts grouped by category:

- Panel Navigation
- File Operations
- Agent Control
- Search & Selection
- View Management
- Custom Shortcuts

### Contextual Help

- Hover over button: Tooltip shows shortcut
- Press Alt: Show all shortcuts in current view
- Unavailable: Shortcuts shown but disabled (grayed out)

---

## Accessibility Requirements

### Screen Reader Compatibility

- Shortcuts announced in tooltips
- Help text includes shortcut info
- Ctrl+? opens accessible reference

### Keyboard Navigation

- Every feature accessible without mouse
- Tab order logical and predictable
- No keyboard traps

### Custom Shortcuts Accessibility

- All custom shortcuts announced
- Conflicts clearly listed with explanations
- Easy reset to defaults

---

## Performance Considerations

### Shortcut Registry

- Maximum 500 shortcuts (OS limitation)
- Currently using ~80 built-in
- ~200 available for plugins/custom
- Performance: <1ms lookup time

### Conflict Resolution

- Atlas shortcuts take priority
- Plugin shortcuts next
- User custom shortcuts last
- First match wins

---

## Mobile/Touch (Future Phase)

While Phase 1 is keyboard/mouse:

- Consider gesture equivalents (Ctrl+S → swipe-left-then-down)
- Long-press for shortcuts menu
- On-screen keyboard with suggestion bar

---

## Keyboard Shortcut Versioning

**Current Version**: 1.0  
**Added in v1.0**: All shortcuts listed above

### Future Changes

- Additional shortcuts added in minor versions
- Breaking changes in major versions (rare)
- User preferences preserve across updates

---

**Keyboard Shortcuts Specification Version**: 1.0  
**Last Updated**: August 2, 2026

All keyboard shortcuts must be documented here. No hidden or undocumented shortcuts.
