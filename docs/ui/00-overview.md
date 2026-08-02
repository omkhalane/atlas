# Atlas Desktop Application - UI/UX Overview

## Executive Summary

Atlas is an AI Operating Runtime—a desktop application that allows AI agents to reliably and safely interact with the user's computer through browsers, filesystems, terminals, memory systems, MCP plugins, external applications, and workflows. The UI must communicate that an AI agent is actually working _inside_ the user's machine, not merely chatting about tasks.

This specification defines the complete desktop experience for Atlas Phase 1, targeting Linux Desktop environments with a professional, minimal, and technically-focused design language inspired by modern developer tools.

---

## Platform & Specifications

### Target Environment

- **Platform**: Linux Desktop (Wayland and X11 support)
- **Theme**: Dark Mode Only
- **Primary Resolution**: 1920×1080 (Full HD)
- **Secondary Resolution**: 2560×1440 (2K)
- **Minimum Resolution**: 1366×768
- **Display Philosophy**: Desktop First, Large Screen Optimized
- **Input Methods**: Keyboard First, Mouse Friendly
- **Performance Target**: 60 FPS, Low Latency
- **Experience Type**: Native Desktop Application

### Design Principles Applied

The application embodies these core principles:

- **Professional**: Enterprise-grade, no gamification, serious tooling
- **Minimal**: Every visual element serves a purpose; no decoration
- **Technical**: Exposes complexity appropriately for power users
- **Fast**: Responsive feedback, instant perceived performance
- **Trustworthy**: Clear agent actions, visible reasoning, full transparency
- **Powerful**: Advanced capabilities surface naturally through keyboard
- **Modern**: Contemporary design language, AI-native interactions
- **AI Native**: Agent actions are first-class UI citizens, not an afterthought

### Design Inspiration (Philosophy, Not Copy)

- **Google Antigravity 2.0 IDE**: Complex multi-panel layouts with clear information hierarchy
- **Cursor**: AI-first code editor with streaming artifacts and execution
- **VS Code**: Keyboard-driven, command palette architecture, extensible
- **Linear**: Clean, data-dense lists with contextual detail panels
- **Figma**: Canvas-based spatial reasoning, multiplayer awareness
- **Docker Desktop**: System resource visualization, clear state indicators
- **Claude Desktop**: Conversational integration with file system context
- **Raycast**: Command-first interface, instant search, productivity tools
- **Arc Browser**: Contextual workspaces, relationship-aware navigation
- **Warp Terminal**: Modern terminal with structured command history
- **Notion**: Flexible content organization, inline previews, full-text search
- **Obsidian**: Knowledge graphs, bidirectional linking, local-first philosophy

**What We're NOT**:

- Not ChatGPT (no conversation-only interface)
- Not an IDE (no code editor built-in)
- Not a browser (browser is integrated tool, not primary product)
- Not VS Code (not an editor, broader runtime scope)
- Not another AI assistant (operating system layer)

---

## Core Metaphor & Mental Model

### The Desk Metaphor

Atlas presents the user's computer as an active _desk_ where an intelligent agent works alongside them:

```
┌─────────────────────────────────────────────────┐
│  Atlas Desktop - The Agent's Workspace          │
├──────┬────────────────────────────────┬─────────┤
│ 🎯   │  What the agent is doing       │ 📊 Info │
│ Tasks│  (Chat, Browser, Files, Term)  │ Panel   │
│      │                                │         │
│      │                                │         │
│      │                                │         │
│      │                                │         │
│      │                                │         │
└──────┴────────────────────────────────┴─────────┘
```

The user can:

- Watch the agent work in real-time
- Intervene at any moment
- Understand what's happening
- Undo/rollback actions
- Take manual control

### Key Difference from Chat Interfaces

Traditional chat interfaces show conversation. Atlas shows **execution**. The conversation is secondary; the agent's actual interaction with the system is primary.

---

## Visual Language

### Color Philosophy

- **Dark Mode Foundation**: OLED-optimized dark grays and blacks
- **Accent Color**: Electric blue for AI actions, controls, and focus states
- **Status Colors**: Green (success), amber (warning), red (error), cyan (info)
- **Text**: High contrast white on dark, with reduced opacity for secondary text
- **Dividers**: Minimal, 1px, low-opacity borders

### Typography

- **Primary Font**: Inter (sans-serif, open-source)
- **Code Font**: JetBrains Mono (monospace, technical)
- **Scale**: 11px to 32px, with specific sizes for each component type

### Spacing System

- **Base Unit**: 4px
- **Scale**: 4, 8, 12, 16, 24, 32, 48, 64, 96
- **Padding**: 8-12px for compact elements, 16px for primary content
- **Gap**: 8px between most components, 12px for section separation

### Corner Radius

- **None**: Raw technical elements (terminal, code blocks)
- **2px**: Small buttons, input fields, badges
- **4px**: Medium panels, dialogs, cards
- **8px**: Large containers, main panels
- **12px**: Dialog backgrounds, drawer panels

### Shadows & Elevation

- **No shadows** on dark backgrounds (use opacity instead)
- **Border-based hierarchy**: 1px borders for separation
- **Opacity layers**: 5%, 10%, 20% white overlay for depth

---

## Layout Grid & Constraints

### Primary Grid System

- **Type**: 8px base grid
- **Container Width**: Flexible, respects window bounds
- **Panel Gaps**: 12px consistent separation
- **Responsive Breakpoints**:
  - **1366×768**: Single-column layouts, stacked panels
  - **1920×1080**: Multi-column, side-by-side panels (PRIMARY)
  - **2560×1440**: Full layout with triple columns possible

### Safe Area & Margins

- **Top**: 12px from window edge (below title bar)
- **Sides**: 12px from window edges
- **Bottom**: 12px from status bar
- **Between Panels**: 12px gap

---

## Navigation Architecture

### Three-Layer Navigation Model

1. **Global Navigation** (Top bar + Activity Sidebar)
   - Workspace switcher
   - Global status
   - Quick actions

2. **Context Navigation** (Explorer Sidebar)
   - File structure, agent list, memory browser
   - Context-dependent on active view
   - Resizable, collapsible

3. **Detail Navigation** (Properties Panel)
   - Item details, configuration
   - Right panel, collapsible
   - Context-aware content

### Command Palette

The "Spotlight" for Atlas—⌘P (Ctrl+P on Linux) opens fuzzy search across:

- Commands
- Files
- Agents
- Memory items
- Plugins
- Recent actions
- Browser tabs
- Terminal sessions

---

## Core Views & Their Purposes

### Agent Chat View (Primary)

- Main conversation interface with the AI agent
- Shows streaming responses, artifacts, task cards
- Real-time execution feedback
- Agent reasoning and planning visible

### Browser Panel

- Integrated web browsing for agent tasks
- Screenshots, DOM inspection, network logs
- Keyboard/mouse control toggle
- Session history and bookmarks

### Terminal Panel

- Multiple split terminals
- Syntax highlighting, command history
- Task tracking, background processes
- SSH and Docker support

### File Explorer

- Directory tree with Git status
- Quick preview, diff viewer
- Recent files, favorites
- Search with full-text and regex

### Memory Browser

- Facts, workspace state, recent interactions
- Timeline view of events
- Knowledge graph visualization
- Search and relationships

### Planner View

- Agent's planning/thinking visualization
- Task queue and dependencies
- Execution graph
- Parallel task tracking

### Timeline View

- Complete execution history
- Event log with timestamps
- Rollback points marked
- Context recovery

---

## Interaction Model Principles

### Keyboard First, Mouse Friendly

Every function accessible via keyboard, but mouse is smooth and efficient for pointing tasks:

- **Global Shortcuts**: ⌘/Ctrl for global commands
- **Panel Shortcuts**: Ctx+Key for context-specific actions
- **Focus Management**: Tab/Shift+Tab for navigation
- **Selection**: Click, Shift+Click, Ctrl+Click for multi-select
- **Dragging**: Resizable panels, draggable windows, drag-and-drop for files

### Streaming & Reactive UI

- **Response Streaming**: Show agent responses character-by-character as they arrive
- **Live Updates**: File changes, terminal output, memory updates in real-time
- **Incremental Rendering**: Large lists virtualized, load on demand
- **Progress Indication**: Animated progress bars, spinners for indeterminate work

### Progressive Disclosure

- **Default**: Show essential information and controls
- **Hover/Focus**: Reveal advanced options, secondary actions
- **Alt/Option Key**: Show all possible actions (similar to VS Code)
- **Settings Panel**: Power user customization

### Approval Workflows

When agents need human approval:

- **Approval Dialog**: Clear what's being requested, why, what will happen
- **Auto-Approve**: Remember for session, always, or never
- **Rollback Ready**: Easy undo of approved actions

---

## Performance & Optimization

### 60 FPS Target

- **Hardware Acceleration**: GPU-accelerated rendering for panels, animations
- **Virtual Scrolling**: Large lists rendered only on-screen
- **Lazy Loading**: Content loaded as needed
- **Background Rendering**: Heavy operations off-thread
- **Debouncing**: Input events debounced appropriately

### Memory Management

- **Streaming Responses**: Don't buffer entire agent responses, stream them
- **LRU Caching**: Recent items cached, old items evicted
- **Image Optimization**: Compressed preview thumbnails, full-res on demand
- **Tab Lifecycle**: Inactive tabs unloaded, rehydrated on switch

### Visual Feedback Optimization

- **No Jank**: Animations run on separate thread
- **Perceived Performance**: Show loading early, progress frequently
- **Cancellation**: Long operations can be cancelled instantly
- **Timeout Fallback**: Failed operations degrade gracefully

---

## Accessibility Standards

### Minimum Requirements (WCAG 2.1 AA)

- **Keyboard Only**: Every feature accessible without mouse
- **High Contrast**: 7:1 text contrast on dark background
- **Reduced Motion**: Disable animations when requested
- **Screen Readers**: Proper ARIA labels, semantic HTML
- **Focus Indicators**: Clear 2px blue focus ring
- **Text Sizing**: Supports up to 200% zoom
- **Color Independence**: Don't use color alone to communicate

### Linux-Specific Considerations

- **Theme Integration**: Respect system theme, colors, fonts
- **Wayland Support**: Proper scaling, cursor feedback
- **X11 Fallback**: Full compatibility with X11 servers
- **System Tray**: Optional system tray integration
- **Desktop Integration**: File manager context menu hooks

---

## States & Modes

### Application States

- **Idle**: No agent running, UI ready for input
- **Planning**: Agent thinking, decision-making
- **Executing**: Agent performing actions
- **Waiting**: Agent awaiting approval or user input
- **Error**: Failed execution, recovery options shown
- **Paused**: User paused agent mid-execution
- **Recovering**: Attempting to recover from error

### Panel States

- **Collapsed**: Title bar only, click to expand
- **Minimized**: Reduced to icon in sidebar
- **Focused**: Active panel, highlighted
- **Inactive**: Background panel, reduced contrast
- **Floating**: Detached window
- **Fullscreen**: Single panel maximized
- **Split View**: Two panels side-by-side

### Component States

- **Default**: Normal operation
- **Hover**: Mouse over, show expanded controls
- **Focused**: Keyboard focused, show focus ring
- **Active**: Currently selected or toggled on
- **Disabled**: Unavailable, reduced opacity
- **Loading**: Animated spinner, indeterminate progress
- **Error**: Red border, error message shown
- **Success**: Green checkmark, brief confirmation

---

## Documentation Structure

This specification is organized as follows:

1. **00-overview.md** (this file) - Overall philosophy and architecture
2. **01-design-principles.md** - Core design principles and guidelines
3. **02-layout.md** - Physical layout, grid, panels, resizing
4. **03-navigation.md** - Navigation structure, panel switching, focus management
5. **04-sidebar.md** - Activity sidebar and explorer sidebar details
6. **05-command-palette.md** - Command palette design and interaction
7. **06-chat.md** - Agent chat interface, streaming, artifacts
8. **07-browser.md** - Integrated browser panel
9. **08-terminal.md** - Terminal panel, multiple tabs, SSH
10. **09-files.md** - File explorer, tree, search, preview
11. **10-memory.md** - Memory interface, timeline, knowledge graph
12. **11-agents.md** - Agent management, running, history
13. **12-planner.md** - Planning interface, task graph, dependencies
14. **13-timeline.md** - Execution timeline, event log, rollback
15. **14-task-view.md** - Task details, status, history
16. **15-plugin-manager.md** - Plugin marketplace and management
17. **16-mcp-manager.md** - MCP server management
18. **17-settings.md** - Settings and preferences
19. **18-notifications.md** - Notification system, toasts, alerts
20. **19-dialogs.md** - Common dialog patterns
21. **20-context-menus.md** - Right-click context menus
22. **21-shortcuts.md** - Complete keyboard shortcut reference
23. **22-theme.md** - Theme system, customization
24. **23-design-system.md** - Component library specifications
25. **24-icons.md** - Icon system and usage
26. **25-typography.md** - Typography scale and usage
27. **26-colors.md** - Color palette and semantics
28. **27-spacing.md** - Spacing system and rules
29. **28-animation.md** - Animation library, durations, curves
30. **29-loading.md** - Loading states and skeletons
31. **30-errors.md** - Error messaging and recovery
32. **31-empty-states.md** - Empty state designs
33. **32-onboarding.md** - First-run experience, setup
34. **33-window-management.md** - Window operations, docking, floating
35. **34-accessibility.md** - Accessibility features and compliance
36. **35-performance.md** - Performance optimization strategies
37. **36-linux.md** - Linux-specific integration details
38. **37-future.md** - Future enhancements and Phase 2 planning

---

## Design Approval & Versioning

**Specification Version**: 1.0  
**Status**: Production Ready  
**Last Updated**: August 2, 2026  
**Target Launch**: Phase 1, Q4 2026

This specification represents the complete visual and interaction design for Atlas Phase 1. No implementation should deviate from these specifications without explicit design review and approval.

---

## Next Steps

Refer to the detailed specifications in the subsequent documents for:

- Precise layout measurements
- Component hierarchy and structure
- Interaction flows and state machines
- Keyboard shortcut mappings
- Accessibility requirements
- Performance optimization strategies

This specification is the single source of truth for all Atlas UI/UX decisions.
