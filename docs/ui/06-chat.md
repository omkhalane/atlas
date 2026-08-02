# Chat Interface Specification

## Overview

The Chat interface is where the user communicates with AI agents and views their execution in real-time. It combines traditional conversation with execution artifacts, making the agent's work visible and interactive.

### Key Differences from Chat Interfaces

- **Not centered**: Chat takes secondary role after output
- **Streaming visible**: Agent responses appear character-by-character
- **Artifacts prominent**: Code, previews, images shown alongside text
- **Execution tracking**: Timeline and logs visible in same panel
- **Approval workflows**: Interactive approval controls integrated
- **Task cards**: Agent-initiated tasks shown as cards, not just text

---

## Layout Structure

### Chat Panel Zones (1920×1080 Example)

```
┌─ Chat Header ──────────────────────────────────────┐ 32px
│ [💬] Conversation Name    [🔍] [⋮] [×]             │
├────────────────────────────────────────────────────┤
│ Conversation Title                                  │
│ Started 2 hours ago • 3 tasks completed             │ Metadata
├────────────────────────────────────────────────────┤
│                                                    │
│ [Conversation History - Scrollable]                │
│ • Agent message                                    │
│ • User message                                    │ Main Area
│ • Agent artifacts (code, preview, etc)           │ Flex
│                                                    │
│ ┌──────────────────────────────────────────────┐   │
│ │ [Agent thinking/streaming in progress...] ⟳  │   │
│ └──────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────┤
│ Message Input Area                                 │
│ [> Send a message or paste code...]       [↑] [S]  │ 120px
└────────────────────────────────────────────────────┘
```

### Dimensions

- **Width**: Full width of main panel
- **Height**: Full height minus header and input
- **Header**: 32px
- **Input Area**: 120px (expandable when typing)
- **Scrollable**: Main conversation area has scroll

---

## Message Types & Components

### User Messages

#### Simple Text

```
┌─────────────────────────────────────────┐
│ User [2:15 PM]                          │ Timestamp right
│                                         │
│ Can you help me debug this error?       │ Text left-aligned
│                                         │
└─────────────────────────────────────────┘
```

**Styling**:

- **Background**: #1A1F3A (dark blue tint)
- **Text**: #E0E0E0 (light)
- **Border**: 1px left, #00A8E8 (blue accent)
- **Padding**: 12px
- **Border Radius**: 4px
- **Max Width**: 70% of panel

#### With Code Block

```
┌─────────────────────────────────────────┐
│ User [2:15 PM]                          │
│                                         │
│ Here's the error in our API:           │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ TypeError: Cannot read property...  │ │ Code block
│ │   at server.js:42:15                │ │ with language
│ │   at processRequest (server.js:20)  │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

#### With File Attachment

```
┌─────────────────────────────────────────┐
│ User [2:15 PM]                          │
│                                         │
│ Review this design:                    │
│                                         │
│ [📎 design-spec.md] 2.4 KB              │ File attachment
│                                         │
└─────────────────────────────────────────┘
```

**File Attachment**:

- Click to preview inline
- Right-click for context menu (save, open, etc.)
- Shows file icon and size

---

### Agent Messages

#### Streaming Response

As agent responds, text appears character by character:

```
┌─────────────────────────────────────────┐
│ Agent (Claude 3.5) [2:16 PM]            │
│                                         │
│ I'll help you debug that error. Let me  │
│ analyze the stack trace...              │
│                                         │
│ ▌ (cursor indicating streaming)         │
│                                         │
└─────────────────────────────────────────┘
```

**Streaming Indicators**:

- Blinking cursor at end of text
- Smooth character-by-character addition
- No lag or jank
- Scrolls smoothly as content arrives

#### Code Block with Syntax Highlighting

```
┌─────────────────────────────────────────┐
│ Agent [2:16 PM]                         │
│                                         │
│ The issue is in the error handler:      │
│                                         │
│ ┌─ server.js ─────────────────────────┐ │
│ │ app.post('/api/data', (req, res) => │ │
│ │   try {                            │ │
│ │     // Process data               │ │
│ │   } catch (err) {                │ │
│ │     res.json({ error: err });    │ │
│ │     // Missing res.status(500)!  │ │ Error highlight
│ │   }                              │ │
│ │ });                              │ │
│ │                                  │ │
│ │ [Copy] [Diff] [Insert]           │ │ Action buttons
│ └──────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Code Block Features**:

- **Syntax Highlighting**: By language
- **Line Numbers**: Left side
- **Copy Button**: Ctrl+C or click
- **Diff Button**: Show changes from current file
- **Insert Button**: Insert into current editor
- **Line Highlighting**: Click line number to highlight
- **Scroll**: Horizontal scroll for long lines

#### Image/Screenshot

```
┌─────────────────────────────────────────┐
│ Agent [2:17 PM]                         │
│                                         │
│ Here's what the browser showed:        │
│                                         │
│ ┌─ screenshot.png ────────────────────┐ │
│ │                                      │ │
│ │ [Full-resolution browser screenshot] │ │
│ │ (image with zoom/fit controls)      │ │
│ │                                      │ │
│ │ [Open in New Window] [Save] [Copy]  │ │
│ └──────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Image Features**:

- **Click**: Expand to fullscreen
- **Zoom**: Mouse wheel, pinch
- **Save**: Right-click or button
- **Copy**: Copy image to clipboard

#### Thinking/Planning Block

When agent is deliberating:

```
┌─────────────────────────────────────────┐
│ Agent [2:18 PM]                         │
│                                         │
│ [🤔 Thinking...] (collapsible)          │ Thinking indicator
│                                         │
│ Let me verify the test runs correctly... │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Task: Run test suite                │ │
│ │ Status: Running                     │ │
│ │ Progress: ████░░░░░░ 40%            │ │
│ │ Time: 2m 15s / ~5m                  │ │
│ │                                     │ │
│ │ Current: test/api.test.js (5/12)   │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Thinking Block**:

- Click to expand/collapse
- Shows agent reasoning
- Nested task execution visible
- Progress indicators

#### Artifact / Structured Output

```
┌─────────────────────────────────────────┐
│ Agent [2:19 PM]                         │
│                                         │
│ ┌─ Task Card ────────────────────────┐ │
│ │ Task: Review API endpoint           │ │
│ │ Status: ✓ Complete (1m 23s)         │ │
│ │ Result: ✅ Tests passing (12/12)    │ │
│ │                                     │ │
│ │ Files Changed: 3                    │ │
│ │ • src/api.js (2 changes)           │ │
│ │ • test/api.test.js (1 change)      │ │
│ │ • docs/API.md (1 change)           │ │
│ │                                     │ │
│ │ [View Changes] [Rollback] [Approve] │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ I've reviewed and fixed the issues in   │
│ your API endpoint. The test suite now   │
│ passes completely.                      │
│                                         │
└─────────────────────────────────────────┘
```

**Task Card Components**:

- **Title & Status**: Clear indication of what's done
- **Result Summary**: Key outcome
- **Related Items**: Files, memory, dependencies
- **Action Buttons**: View, Approve, Reject, Rollback
- **Metrics**: Duration, file count, test results

---

## User Input Area

### Text Input

```
┌────────────────────────────────────────────────────┐
│ [>] Type a message or paste code...         [↑][S] │
└────────────────────────────────────────────────────┘
```

**Features**:

- **Placeholder**: Contextual help text
- **Input Icon**: > indicates input ready
- **Multiline**: Ctrl+Enter to send, Shift+Enter for newline
- **Auto-expand**: Height grows with content (max 200px)
- **Send Button**: S (keyboard shortcut shown) or [Send]
- **Paste Detection**: Detect code/file paste, offer formatting

### Input Behaviors

#### Typing Indicators

- As user types, show live preview (if applicable)
- "Typing..." shown if message is being composed
- Character count (if applicable)

#### File/Code Paste

When user pastes code or file content:

```
┌────────────────────────────────────────────────────┐
│ [>] ┌─────────────────────────────────────────────┐│
│     │ Pasted content detected:                    ││
│     │ • Code (JavaScript) - Format as code block? ││
│     │ • File: app.js (2.3 KB)                    ││
│     │ [Yes] [Cancel]                             ││
│     └─────────────────────────────────────────────┘│
└────────────────────────────────────────────────────┘
```

#### Attachments

Users can attach files:

- **Drag & Drop**: Drag files into input area
- **Button**: Paperclip icon to browse
- **Preview**: Show attached files in input
- **Remove**: X button on each attachment

### Input Actions

- **Ctrl+Enter**: Send message
- **Shift+Enter**: New line
- **Ctrl+/**: Show slash commands
- **Tab**: Auto-complete (if applicable)
- **Esc**: Cancel input (if text entered)

---

## Agent Status & Control

### Status Indicator (During Execution)

```
┌─────────────────────────────────────────┐
│ Agent Status: 🟢 Running (Planning) │
│ Task: Navigate to github.com            │
│ Time: 45s / ~2m estimated              │
│ [Pause] [Cancel] [Approve Next Step]   │
└─────────────────────────────────────────┘
```

**Status States**:

- 🟢 **Idle**: Not running, ready
- 🟡 **Planning**: Deciding next steps
- 🔵 **Running**: Executing a task
- ⏸️ **Paused**: User paused execution
- ⏳ **Waiting**: Awaiting approval or input
- ❌ **Error**: Something went wrong
- ✅ **Complete**: Task finished

### Control Buttons

- **Pause**: Pause agent execution (resumable)
- **Cancel**: Stop agent and rollback changes
- **Approve**: Approve pending action
- **Deny**: Reject pending action
- **Logs**: Show detailed execution logs

---

## Conversation Features

### Search Within Chat

- **Ctrl+F**: Search this conversation
- Highlights matching text in messages
- Navigate with arrow keys
- Shows "X of Y matches"

### Copy & Sharing

- **Select & Copy**: Ctrl+C to copy selected text
- **Export Conversation**: File → Export as markdown/PDF
- **Share Link**: Copy conversation share link (if enabled)

### Conversation Metadata

- **Topic**: Auto-detected or user-specified
- **Participants**: User + Agent(s)
- **Duration**: Total time spent
- **Token Usage**: Input + output tokens
- **Files Modified**: Count of files changed
- **Tasks Completed**: Count of tasks done

### Conversation Bookmarks

Users can bookmark interesting points:

```
[🔖 Bookmark] This was a key insight about architecture
```

Click to jump to bookmarked messages. Listed in info sidebar.

---

## Interaction Details

### Message Selection

- **Click**: Focus message
- **Triple-click**: Select message text
- **Shift+Click**: Select range of messages
- **Right-click**: Context menu (copy, bookmark, delete, etc.)

### Hover Actions

When hovering over a message:

```
User [2:15 PM] ........................... [↓] [⋮]
  Can you help me debug this error?

  ↓ = Copy/Reply to this message
  ⋮ = More options (copy, delete, bookmark, etc.)
```

### Streaming Cancellation

When agent is streaming:

```
Agent [2:16 PM]
Here's what I found so far... ⟳ [Stop]

Stop = Cancel generation (keep what's streamed so far)
```

---

## Approval Workflows

### Request Approval Dialog

When agent needs approval before proceeding:

```
┌──────────────────────────────────────────┐
│ ⚠️  Agent Requests Approval              │
├──────────────────────────────────────────┤
│                                          │
│ Agent wants to: Delete file              │
│ File: src/deprecated-api.js              │
│ Reason: Remove outdated code             │
│                                          │
│ ┌────────────────────────────────────┐   │
│ │ Current content preview (head):    │   │
│ │ // Deprecated API module           │   │
│ │ // This module is no longer used   │   │
│ │ // See new-api.js for replacement  │   │
│ └────────────────────────────────────┘   │
│                                          │
│ Save backup: ☑ Yes (recommended)        │
│                                          │
│ What should I do?                        │
│ [Approve] [Deny] [Ask Every Time]       │
│ [View Full File]                        │
│                                          │
└──────────────────────────────────────────┘
```

**Features**:

- **Clear Request**: What exactly is being requested
- **Context**: File path, reason
- **Preview**: Show affected content
- **Backup Option**: Save backup before changes
- **Memory**: "Ask Every Time" vs "Always Approve" vs one-time
- **Additional Info**: View full file, diff, etc.

---

## Empty States

### New Conversation

```
┌──────────────────────────────────────────┐
│                                          │
│          💬 New Conversation             │
│                                          │
│   No messages yet. Start by asking       │
│   the agent to help with a task.        │
│                                          │
│   Try:                                   │
│   • "Debug this error"                  │
│   • "Review my code"                    │
│   • "Run the test suite"                │
│                                          │
│  Or select an existing task from the    │
│  sidebar to continue.                   │
│                                          │
│  [New Agent] [Load Recent]              │
│                                          │
└──────────────────────────────────────────┘
```

### No Selection

When no conversation open:

```
┌──────────────────────────────────────────┐
│                                          │
│     📋 Select a Conversation             │
│                                          │
│   Choose from Recent on the left to     │
│   continue a previous conversation.     │
│                                          │
│   Or start a new task:                  │
│   [New Conversation]                    │
│                                          │
└──────────────────────────────────────────┘
```

---

## Performance Optimizations

### Virtualization

- Only render visible messages
- Off-screen messages removed from DOM
- Smooth scroll with placeholder content
- Efficient for 1000+ messages

### Streaming Optimization

- Character-by-character streaming without flicker
- Debounce DOM updates (every 50ms max)
- Smooth scrolling to latest message
- No re-render of previous messages

### Image/Artifact Caching

- Cache rendered images
- Lazy load large artifacts
- Compress large screenshots
- Memory limit: 50MB max for images

---

## Accessibility

### Keyboard Navigation

- Tab: Navigate messages and controls
- Arrow keys: Scroll message history
- Enter: Expand/collapse artifact
- Ctrl+F: Search conversation

### Screen Reader

- Each message announced as "User message" or "Agent message"
- Timestamp read
- Code blocks announced as such
- Task cards announced with status

### Focus Management

- Clear focus ring on all interactive elements
- Tab order: Messages → Input → Buttons
- Focus visible in high contrast mode

---

**Chat Specification Version**: 1.0  
**Last Updated**: August 2, 2026
