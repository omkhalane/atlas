# Browser Panel Specification

## Purpose

The Browser Panel allows AI agents to navigate and interact with web applications, and provides users visibility into browser sessions including screenshots, DOM inspection, and network activity.

---

## Layout & Structure

### Browser Viewport

```
┌─ Browser Header ────────────────────────────────┐ 40px
│ ◀ ▶ ⟳ [URL Bar: google.com] [...] [×]         │
├─────────────────────────────────────────────────┤
│ [Browser content rendered here]                │
│ (Website, web app, etc.)                       │
│                                                │
│ [Screenshot if no live rendering]             │
│                                                │
└─────────────────────────────────────────────────┘
```

### Browser Tabs

```
[🔍 Google] [🐙 GitHub] [📚 MDN Docs] [×]
 ^--Tab UI, switchable with Ctrl+Tab
```

- **Height**: 32px per tab bar
- **Tab Format**: Favicon + title
- **Active**: Blue accent (#00A8E8)
- **Close**: X button on right

---

## Control Modes

### Agent Control Mode (Primary)

- Agent can interact with page
- User can watch and interrupt
- Mouse/keyboard events sent to browser
- **Status**: "Agent Navigating..."
- **Controls**: [Pause] [Stop] [Approve]

### Human Control Mode (Override)

- User takes manual control
- Mouse and keyboard to browser
- Agent monitoring disabled
- **Status**: "Manual Control (Agent Suspended)"
- **Controls**: [Resume Agent] [End Session]

### Screenshots Mode (Default)

- No live rendering
- Show screenshots in sequence
- Updates every 2-5 seconds
- Shows: URL, page title, viewport size

---

## URL Bar & Navigation

```
┌─────────────────────────────────┐
│ ◀ ▶ ⟳ [google.com/search?q=...] │
│ Back, Forward, Reload buttons   │
└─────────────────────────────────┘
```

- **Back/Forward**: Navigate history
- **Reload**: Ctrl+R (soft), Ctrl+Shift+R (hard)
- **URL Bar**: Click to edit, Ctrl+L
- **Enter**: Navigate to URL
- **Agent Control**: Agent suggests URLs, user approves

---

## Inspector & DevTools

### DOM Inspector (Ctrl+Shift+I)

```
┌─ Inspector ──────────────────────┐
│ 📋 DOM ┃ Console ┃ Network ┃ ...│
├──────────────────────────────────┤
│ <div class="container">          │
│   <h1>Page Title</h1>            │
│   <div class="content">          │
│     Selected ↓                   │
│   </div>                         │
│ </div>                           │
├──────────────────────────────────┤
│ Styles:                          │
│ .container { padding: 16px; }   │
└──────────────────────────────────┘
```

**Tabs**:

- **DOM**: HTML element tree
- **Console**: JavaScript console
- **Network**: HTTP requests/responses
- **Performance**: Load metrics
- **Accessibility**: ARIA, a11y info

---

## Screenshot Management

### Screenshot Capture

- Automatic every 3 seconds (configurable)
- Manual: Ctrl+Shift+S
- Full page or viewport
- Saved to memory/history

### Screenshot Viewer

```
Screenshot from 2:15 PM
[Image with zoom/pan controls]

URL: google.com
Viewport: 1920×1080
Agent Action: "Clicked search button"
```

### Comparison View

- Side-by-side before/after
- Highlight differences
- Timeline scrubber to review history

---

## Keyboard Shortcuts (Browser-Specific)

```
Ctrl+T          New Tab
Ctrl+W          Close Tab
Ctrl+N          New Window
Ctrl+L          Focus URL Bar
Ctrl+Tab        Next Tab
Ctrl+Shift+Tab  Previous Tab

Alt+Left        Back
Alt+Right       Forward
Ctrl+R          Reload
Ctrl+Shift+R    Hard Reload (bypass cache)

Ctrl+H          History
Ctrl+Y          Downloads
Ctrl+D          Bookmark Current
Ctrl+Shift+M    Mute Tab

Ctrl+F          Find on Page
Ctrl+Shift+I    Open Inspector
Ctrl+Shift+J    Open Console

Ctrl+,          Browser Settings
```

---

## Download Management

### Downloads Panel

```
Downloads
├─ file.pdf (2.3 MB) - Downloaded ✓ [Open] [Show]
├─ image.png (1.2 MB) - Downloaded ✓ [Open] [Show]
└─ data.zip (45 MB) - Downloading 60% [Pause] [Cancel]
```

- **Show Downloads**: Ctrl+Y
- **Open File**: Click item
- **Show Folder**: Right-click → Show in Folder
- **Auto-Clear**: Downloaded files cleared on session end (configurable)

---

## Session Management

### Session Tabs

```
Sessions
┌─ Current Session │
├─ Saved Session: "Project Review"
├─ Saved Session: "Research Sprint"
└─ Saved Session: "Testing Auth"

[Save Current] [Load Session] [Delete]
```

- **Save Session**: File → Save Session As
- **Load Session**: File → Load Session
- **Auto-Save**: Option to save session on close
- **Storage**: ~/.atlas/browser-sessions/{session-name}

---

## Cookies & Storage

### Cookie Manager

```
Cookies for: github.com (12 cookies)
├─ session_id: "abc123..."
├─ user_pref: "dark_mode"
├─ analytics: "tracking_id"
│
[Clear All] [Edit] [Block]
```

- **View Cookies**: Settings → Privacy → Cookies
- **Clear on Exit**: Option to clear cookies on close
- **Blocked Sites**: Whitelist/blacklist cookie domains
- **Local Storage**: Similar interface for local storage

---

## Bookmarks & History

### Bookmarks

```
Bookmarks ⭐
├─ 📁 Documentation
│  ├─ MDN Web Docs
│  ├─ Python Docs
│  └─ React Docs
└─ 📁 Tools
   ├─ GitHub
   └─ Stack Overflow

[Add Bookmark] [Organize]
```

- **Add**: Ctrl+D
- **Manage**: Ctrl+Shift+B to show/hide sidebar
- **Drag to Organize**: Reorder bookmarks
- **Folders**: Create folder organization

### History

```
History
├─ 📅 Today
│  ├─ google.com (2:15 PM)
│  ├─ github.com (2:10 PM)
│  └─ stackoverflow.com (1:45 PM)
└─ 📅 Yesterday
   ├─ npmjs.com
   └─ mdn.org

[Clear History] [Export]
```

- **Search History**: Ctrl+H to open, type to search
- **Chronological**: Sorted by most recent
- **Clear**: Settings → Clear browsing data

---

## Live Control Features

### Click-to-Select

- **Hover Element**: Highlight in page
- **Click**: Show element info in DOM inspector
- **Alt+Click**: Select parent element

### Form Filling

- **Agent**: Fills forms programmatically
- **User Approval**: "Fill form? [Approve] [Deny]"
- **Manual**: User can click inputs to override

### Network Monitoring

```
Network Requests
├─ GET /api/users (200 OK, 125ms)
├─ POST /api/login (401 Unauthorized, 230ms)
└─ GET /static/main.js (200 OK, 45ms)

[Enable Request Logging] [Clear]
```

- **View Details**: Click request to see headers/body
- **Filter**: Show only errors, slow requests, etc.
- **Export**: Save as HAR file

---

## Accessibility Features

### Vision Overlay

- **Highlight Interactive**: Mark buttons, links, inputs
- **Show Text**: Overlay text for images (alt text)
- **Color Blind Mode**: Show color-blind friendly palette

### Screen Reader Simulation

- **Announce Elements**: Read DOM structure aloud
- **Announce Changes**: Alert on dynamic content updates
- **Focus Order**: Show tab order through page

---

## Error Handling

### Page Load Errors

```
⚠️  Unable to load page
Error: Connection timeout (30s)

URL: https://invalid.domain/page

Options:
[Retry] [Use Cached] [Suggest New URL]
```

### SSL/Certificate Warnings

```
⚠️  Security Warning

This site's security certificate couldn't be verified.

Domain: untrusted.example.com
Issued by: Self-Signed
Expires: Never

[Proceed Anyway] [Go Back] [Report Issue]
```

### JavaScript Errors

Logged to console, not shown to user unless developer mode enabled.

---

## Session Restoration

### On Crash/Close

- Option to restore browser session
- Prompt: "Restore previous session? (3 tabs)"
- [Restore All] [Restore Selectively] [Start New]
- Cookies and local storage preserved

---

## Performance Optimization

### Lazy Rendering

- Only render visible tabs
- Screenshot mode by default (lighter than live rendering)
- Live rendering option for interactive testing

### Memory Management

- Max 5 live tabs
- Additional tabs screenshot-only
- Close unused tabs to free memory
- Warning: "Memory usage high. Consider closing tabs."

### Screenshot Caching

- Cache 50 most recent screenshots
- LRU eviction when limit reached
- Clear cache in Settings → Storage

---

## Firefox/Chromium Detection

### Render Strategy

- **Chromium-based**: Use Puppeteer or CDP
- **Firefox**: Use WebDriver protocol
- **Fallback**: Screenshot mode

### Feature Parity

- All features work in both browsers
- Some performance differences noted
- User can choose preferred browser in Settings

---

## Settings

### Browser Settings Panel

```
Browser
├─ Default Search Engine: Google ▼
├─ ☑ Show Bookmarks Bar
├─ ☑ Enable Cookies
├─ ☑ Auto-fill Forms (Agent Only)
├─ ☑ Auto-play Media
├─ Screenshot Interval: 3 seconds
├─ ☑ Restore Session on Start
└─ Cache Size: 256 MB
```

---

**Browser Specification Version**: 1.0  
**Last Updated**: August 2, 2026
