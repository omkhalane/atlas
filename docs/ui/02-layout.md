# Layout Architecture - Physical Organization

## Core Layout Structure

### Window Anatomy (1920×1080 Primary)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ ▮ Atlas  [File]  [Edit]  [View]  [Tools]  [Help]  ________________  _ ⊡ ✕ │  Height: 32px
├──────┬──────────────────────────────────────────────────────────────┬──────┤
│      │                                                              │      │
│ Act  │  Main Content Area (Chat, Browser, Terminal, Files)         │ Info │
│ Side │                                                              │ Side │
│ bar  │  ┌─────────────────────────────┬─────────────────────────┐  │ bar  │
│      │  │  Secondary Panel 1          │  Secondary Panel 2      │  │      │
│  32px│  │  (Browser / Terminal)       │  (Output / Logs)        │  │ 300px│
│      │  │                             │                         │  │      │
│      │  │                             │                         │  │      │
│      │  │                             │                         │  │      │
│      │  │                             │                         │  │      │
│      │  │                             │                         │  │      │
│      │  │                             │                         │  │      │
│      │  └─────────────────────────────┴─────────────────────────┘  │      │
│      │  ┌────────────────────────────────────────────────────────┐  │      │
│      │  │  Tertiary Panel (Timeline, Logs, Memory)              │  │      │
│      │  │                                                        │  │      │
│      │  └────────────────────────────────────────────────────────┘  │      │
├──────┴──────────────────────────────────────────────────────────────┴──────┤
│ Agent: Idle  ◯ GPU On  ⚙ Settings  🔔 1  🔗 Plugins  🧠 Memory  📊 Timeline│  Height: 28px
└────────────────────────────────────────────────────────────────────────────┘
```

### Component Dimensions

#### Top Bar / Title Bar

- **Height**: 32px
- **Padding**: 8px left/right, 4px top/bottom
- **Contains**:
  - Window control (8px left margin)
  - App title "Atlas"
  - Menu bar (File, Edit, View, Tools, Help)
  - Spacer (flex)
  - Window controls (minimize, maximize, close)

#### Activity Sidebar (Left)

- **Width**: 48px fixed
- **Background**: #0A0E27
- **Border**: 1px right, #1A1F3A
- **Contains**: Vertically stacked icons
- **Icon Size**: 24px
- **Padding**: 8px top/bottom, 12px sides
- **Interactive**: Click to switch views, right-click for context menu

#### Main Content Area

- **Flex**: Takes available space
- **Min Width**: 800px (below this, switch to single-column layout)
- **Resizable**: Divider between left panel and center
- **Resizable**: Dividers between center panels
- **Resizable**: Divider between center and right

#### Info Sidebar (Right)

- **Width**: 300px default, resizable 200-400px
- **Background**: #0F1229
- **Border**: 1px left, #1A1F3A
- **Contains**: Properties, details, secondary info
- **Collapsible**: Click sidebar handle to collapse/expand

#### Status Bar / Footer

- **Height**: 28px
- **Padding**: 4px
- **Background**: #0A0E27
- **Border**: 1px top, #1A1F3A
- **Contains**: Status indicators, quick actions, notifications

---

## Panel System & Resizing

### Primary Panel (Left-Center)

- **Default Content**: Chat or Files or Browser
- **Resizable**: Right edge draggable, minimum 400px
- **State**: Can be collapsed to icon-only view
- **Tabs**: Multiple tabs for recent items
- **Shortcuts**:
  - Ctrl+B: Focus browser
  - Ctrl+E: Focus files
  - Ctrl+J: Focus terminal
  - Ctrl+': Focus chat

### Secondary Panels (Right side of center)

- **Layout**: Stacked vertically or side-by-side (user configurable)
- **Resizable**: Dividers between them
- **Contents**: Terminal, Browser Preview, Logs, Output
- **Collapsible**: Hide secondary panels for focus mode

### Info Sidebar (Right)

- **Always On Right**: Properties, details, context
- **Collapsible**: Ctrl+Shift+P to toggle
- **Dynamic Content**: Changes based on selected item
- **Resizable**: Drag left border to adjust width

### Bottom Panels (Contextual)

- **Timeline**: Show execution history, can be docked or floating
- **Memory**: Knowledge graph and facts browser
- **Logs**: System and application logs

---

## Layout Configurations

### Full-Spread Layout (1920×1080 - DEFAULT)

```
┌──────┬─────────────────────────┬─────────┐
│      │                         │         │
│ Act  │   Chat (Main)           │ Info    │
│ Side │   + Browser Split       │ Panel   │
│      │   + Terminal Split      │         │
│      │   + Output Split        │         │
│      ├─────────────────────────┤         │
│      │   Timeline (Bottom)     │         │
└──────┴─────────────────────────┴─────────┘
```

**Usage**: Best for multi-task workflows. User can watch agent, see browser, terminal, and logs simultaneously.

### Focus Layout (1920×1080)

```
┌──────┬──────────────────────────────────────┐
│      │                                      │
│ Act  │        Chat (Full Width)             │
│ Side │                                      │
│      │                                      │
└──────┴──────────────────────────────────────┘
```

**How to Enter**: Collapse info sidebar (Ctrl+Shift+P), minimize secondary panels

### Two-Column Layout (2560×1440)

```
┌──────┬─────────────┬──────────────┬─────────┐
│      │             │              │         │
│ Act  │   Chat      │   Browser    │ Info    │
│ Side │             │   Terminal   │ Panel   │
│      │   Timeline  │   Logs       │         │
└──────┴─────────────┴──────────────┴─────────┘
```

**Usage**: Wide monitors, side-by-side comparison tasks, parallel workflows.

### Minimal Layout (1366×768)

```
┌──────┬────────────────────────────┐
│      │                            │
│ Act  │   Chat / Browser /Files    │
│ Side │   (Tab Switching)          │
│      │                            │
│      ├────────────────────────────┤
│      │   Terminal                 │
└──────┴────────────────────────────┘
```

**Usage**: Smaller monitors. Secondary content hidden or tabbed.

---

## Panel Resizing Mechanics

### Resize Handles

- **Visual**: 1px line, 2px active zone (more forgiving)
- **Color**: #1A1F3A, brightens to #2A3F5A on hover
- **Cursor**: Changes to `resize-x` or `resize-y` on hover
- **Min/Max**: Each panel has minimum and maximum width

### Resize Constraints

- **Activity Sidebar**: Fixed at 48px, not resizable
- **Left Panel**: Min 400px, Max 75% of window
- **Info Sidebar**: Min 200px, Max 400px
- **Secondary Panels**: Min 200px each

### Resize Animation

- **Duration**: Instant (no delay)
- **Feedback**: Live preview as dragging
- **Momentum**: No momentum/snap
- **Persistence**: User's layout saved to workspace config

### Double-Click Resize

- **Left Edge**: Double-click to toggle collapse/expand
- **Width**: Expands to last saved width or default
- **Animation**: 200ms ease-out slide

---

## Grid & Alignment System

### 8px Base Grid

- All elements align to 8px multiples
- Exceptions: Text baseline, some borders (1px)
- Tools should enforce grid constraints

### Container Widths (Content Area)

- **Default**: Full flex (respects window width)
- **Max Width**: None (full to edges)
- **Responsive**: Recalculate layout below 1366px width

### Padding & Margins

- **Panel Padding**: 12px all sides
- **Section Padding**: 12px between major sections
- **Component Gap**: 8px between components
- **Text Area Padding**: 12px top/bottom, 16px left/right

### Spacing Scale

Applied consistently throughout:

```
4px  - Minimum spacing (icons to text)
8px  - Default component gap
12px - Section separation, dialog padding
16px - Large content padding
24px - Major section break
32px - Large break (rare)
48px - Between major panels (rare)
64px - Empty states (vertical breathing room)
```

---

## Responsive Behavior

### Breakpoint Strategy

Responsive design is minimal—focus on primary resolution.

#### Below 1366px (Minimal Layout)

- Info sidebar hides by default (Ctrl+Shift+P to show)
- Secondary panels stack vertically
- Panels become tabbed where possible
- Menu bar compresses to hamburger (File, Edit → ≡)

#### 1366-1920px (Standard)

- All panels visible
- Single layout mode
- Full functionality

#### 1920px+ (Full-Spread)

- All panels visible
- Multiple layout options
- Triple-column possible

### Dynamic Panel Hiding

- User can collapse any panel
- UI remembers last state
- Quick toggle buttons in top bar and status bar
- Keyboard shortcuts available

---

## Z-Index Strategy

### Layer Hierarchy

```
1000 - Floating windows, Picture-in-Picture
900  - Floating panels (when detached)
800  - Dialogs and modals
700  - Context menus and popovers
600  - Tooltips
500  - Notifications (toasts)
200  - Sidebars (activity + info)
100  - Main panels (chat, browser, files)
50   - Panel dividers
0    - Window background
```

### Focus Management

- Only one panel has focus at a time
- Focus ring shows active panel (blue border accent)
- Tab order: Left sidebar → Main panel → Right sidebar → Status bar

---

## Window States

### Normal

- All panels visible and docked
- Dividers show resize handles
- Full functionality available

### Fullscreen

- Selected panel expanded to full window
- Escape to exit fullscreen
- Window controls still visible
- Quick access to other panels via Ctrl+key

### Floating Panel

- Panel detached as separate window
- Can be moved, resized independently
- Stays on top of main window
- Click back to dock it
- Shortcut: Ctrl+Shift+D to detach focused panel

### Picture-in-Picture

- Browser panel floats in corner
- Semi-transparent (80% opacity)
- Draggable, resizable (min 400×300)
- Click through when not focused
- Exit with close button or Esc

### Minimized

- Panel minimized to icon in activity sidebar
- Quick preview on hover
- Click to restore
- Memory: Last state before minimize is restored

---

## Resizable Panel Example: Chat vs Browser

### Initial State (1920×1080)

```
Left Panel (60%):     1000px - Chat interface
Middle Panel (30%):    600px - Browser preview
Right Sidebar (10%):   300px - Info panel
```

### User Drags Left Divider Right (+200px)

```
Left Panel (70%):     1200px - Chat interface (expanded)
Middle Panel (20%):    400px - Browser preview (compressed)
Right Sidebar (10%):   300px - Info panel (unchanged)
```

### Animation

- 0ms: Panel sizes change immediately
- Mouse tracking continues
- Content reflows in real-time
- No lag or jumpiness

---

## Panel Switching & Navigation

### Keyboard Shortcuts for Panels

- **Ctrl+1**: Focus primary panel
- **Ctrl+2**: Focus secondary left
- **Ctrl+3**: Focus secondary right
- **Ctrl+4**: Focus info sidebar
- **Ctrl+5**: Focus status bar / command palette

### Mouse Switching

- Click on any panel to focus
- Click on tab to switch tabs
- Click on icon in sidebar to switch views

### Visual Feedback on Switch

- Previous panel: Normal opacity
- New panel: Blue accent border (2px, #00A8E8)
- Animation: 100ms fade of accent on entry

---

## Split View System

### Creating Splits

- Drag panel divider to open split
- Or: Right-click panel header → "Split Right/Down"
- Or: Keyboard Ctrl+Shift+S in panel

### Split Configurations

- **Vertical Split**: Two panels side-by-side
- **Horizontal Split**: Two panels stacked
- **Multiple Splits**: Up to 4 panels in 2×2 grid

### Unsplitting

- Double-click divider to remove split
- Or: Right-click panel → "Remove Split"
- Or: Click X on tab bar

### Split Memory

- Last split configuration remembered
- Restored on app relaunch
- Per workspace (different workspaces = different splits)

---

## Minimizing to Sidebar

### Collapsed State

- Panel minimized to icon in activity sidebar
- Icon shows a preview on hover (tooltip-style)
- Click icon to restore at previous size

### Restoration

- Animated expansion from sidebar location
- Slides open 300ms ease-out
- Content position smooth
- Focus shifts to restored panel

### Keyboard

- Minimize focused panel: Alt+M
- Restore from sidebar: Click or Alt+number

---

## Status Bar Layout

### Left Section (Status)

- Agent state icon (circle: idle, spinning: planning, working)
- Agent name/ID
- CPU/GPU usage (if visible)
- Task progress (if executing)

### Middle Section (Info)

- Current file or workspace name
- Line/column if in editor context
- Selection info if applicable

### Right Section (Actions & Indicators)

- GPU indicator (⚙ GPU On/Off)
- Settings button
- Notification center (🔔 with badge count)
- Plugin indicator (🔗 count)
- Memory indicator (🧠 with fact count)
- Timeline button (📊 with event count)

### Responsive Behavior

- Below 1400px: Hide non-essential info
- Below 1200px: Compress to icons only
- Hover icon to see label

---

## Accessibility Considerations

### Keyboard Navigation

- Tab order: Left → Center → Right → Bottom
- Shift+Tab reverses order
- Arrow keys within panel for navigation
- Enter to select/activate

### Focus Ring

- 2px blue (#00A8E8) border
- High contrast against any background
- Visible on all interactive elements
- Never hidden or invisible

### Resize Handle Accessibility

- Keyboard resizing: Ctrl+Left/Right arrows
- 10px increments per keypress
- Shortcuts shown in tooltip

### High Contrast

- Borders used instead of color alone
- Text contrast ≥7:1 WCAG AAA
- Hover/active states use borders + color

---

## Performance Considerations

### Lazy Rendering

- Panels off-screen don't render (hidden tabs)
- Content in hidden sidebars isn't rendered
- Rerendered only on focus/activation

### Virtual Scrolling

- Large lists in panels use virtual scrolling
- Only visible rows rendered
- Smooth scroll with placeholder content

### Panel Splitting Impact

- Each split uses separate renderer
- GPU acceleration for smooth rendering
- Memory limit: Max 4 splits (safety limit)
- Close unused splits to free memory

---

## Layout Versioning & Migrations

### Layout Persistence Format

Stored in workspace config (`~/.atlas/workspaces/{name}/layout.json`):

```json
{
  "primaryPanel": {
    "width": 1200,
    "type": "chat",
    "tabs": ["chat-main", "chat-history"]
  },
  "secondaryPanels": {
    "layout": "stacked",
    "panels": [
      { "width": 400, "height": 300, "type": "browser" },
      { "width": 400, "height": 200, "type": "terminal" }
    ]
  },
  "infoPanelOpen": true,
  "infoPanelWidth": 300
}
```

### Migration Strategy

- v1.0 to v1.1: Auto-convert old layout format
- User notified of layout changes
- Rollback available via Edit menu

---

## Layout Specification Summary

| Component        | Width | Height | Min   | Max   | Resizable |
| ---------------- | ----- | ------ | ----- | ----- | --------- |
| Activity Sidebar | 48px  | Full   | N/A   | N/A   | No        |
| Left Panel       | Flex  | Full   | 400px | 75%   | Yes       |
| Secondary Panels | Flex  | Flex   | 200px | 100%  | Yes       |
| Info Sidebar     | 300px | Full   | 200px | 400px | Yes       |
| Top Bar          | Full  | 32px   | N/A   | N/A   | No        |
| Status Bar       | Full  | 28px   | N/A   | N/A   | No        |

---

**Layout Specification Version**: 1.0  
**Last Updated**: August 2, 2026

Implement this layout specification exactly as documented. Any deviations require design review approval.
