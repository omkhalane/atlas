# Icons Specification

## Icon Philosophy

Icons are immediately recognizable, consistently styled, and serve functional purposes. Every icon communicates an action or state at a glance.

## Icon System

### Sizes

- **16×16px**: Inline in lists, small buttons
- **24×24px**: Standard UI buttons, sidebar icons
- **32×32px**: Large buttons, file type icons
- **48×48px**: Empty states, major headings

### Style

- **Stroke Weight**: 2px (consistency)
- **Corner Radius**: 2px (consistency)
- **Color**: Inherit from text color
- **Outline**: Not filled (except special cases)

## Core Icon Set

### Navigation & Panels

```
🏠 home            Home/default view
💬 chat            Chat/conversation
🌐 globe           Browser/web
📁 folder          File explorer
⌨️  terminal         Terminal/command line
🧠 brain           Memory/knowledge
🤖 robot           Agent/AI
📊 chart           Planner/analytics
⚙️  settings        Settings/preferences
🔌 plugin          Plugins/extensions
```

### File Types

```
📄 file            Generic file
📃 document        Document/text
📋 list            List/data
🎨 image           Image/artwork
🎬 video           Video file
🎵 audio           Audio file
📦 package         Archive/package
📚 book            Documentation
⚙️  config          Configuration
🔑 key             Private key/secret
```

### Actions

```
✏️  edit            Edit/modify
🗑️  trash           Delete
✂️  scissors        Cut
📋 copy            Copy
📌 paste           Paste
↩️  undo            Undo
↪️  redo            Redo
💾 save            Save
📤 download        Download
📥 upload          Upload
🔍 search          Search/find
🔗 link            Link/reference
⭐ star            Favorite/pin
🔔 bell            Notifications
👁️  eye             Visible/show
🚫 eye-slash       Hidden/hide
```

### Status & Feedback

```
✅ check           Success/complete
❌ x              Error/failed
⚠️  warning         Warning/caution
ℹ️  info            Information
🔄 refresh         Refresh/reload
⟳ loading          Loading/spinner
⏸️  pause           Pause
⏮️  stop            Stop/cancel
▶️  play            Play/run
⏱️  timer           Time/duration
```

### Interaction

```
◀ chevron-left     Previous/back
▶ chevron-right    Next/forward
▲ chevron-up       Collapse/up
▼ chevron-down     Expand/down
⋮ menu             More options
⋯ dots             More actions
↖️  drag            Drag/move
📍 pin             Pin/anchor
🔐 lock            Lock/secure
🔓 unlock          Unlock/unsecure
```

### Semantic

```
🟢 dot-green       Success/running
🟡 dot-yellow      Warning/pending
🔵 dot-blue        Info/active
🔴 dot-red         Error/failed
⚫ dot-gray         Idle/offline
```

## Icon Implementation

### SVG Format

All icons are SVG (scalable, sharp at any size).

```xml
<svg width="24" height="24" viewBox="0 0 24 24">
  <path d="M3 3h18v18H3z" stroke="currentColor" stroke-width="2" fill="none"/>
</svg>
```

### CSS Classes

```css
.icon {
  width: 24px;
  height: 24px;
  display: inline-block;
  fill: currentColor;
  stroke: currentColor;
  flex-shrink: 0;
}

.icon-sm {
  width: 16px;
  height: 16px;
}
.icon-lg {
  width: 32px;
  height: 32px;
}
.icon-xl {
  width: 48px;
  height: 48px;
}
```

### Usage in HTML

```html
<button>
  <svg class="icon">...</svg>
  Button Label
</button>

<div class="icon-text">
  <svg class="icon-sm"></svg>
  <span>Label Text</span>
</div>
```

## Color Inheritance

Icons inherit text color automatically:

- **Primary**: #E0E0E0 (default)
- **Secondary**: #A0A0A0
- **Tertiary**: #7A8BA0
- **Accent**: #00A8E8 (interactive)
- **Status**: Green/amber/red as appropriate

## Animation

### Hover Animation

```css
.icon:hover {
  opacity: 1.2;
  filter: brightness(1.2);
  transition: 100ms ease-out;
}
```

### Loading Spinner

```css
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.icon-loading {
  animation: spin 1s linear infinite;
}
```

### State Icons

- **Active**: No animation (instant)
- **Hover**: Subtle brightness increase
- **Focus**: Outline ring (same as text)
- **Disabled**: Opacity 50%

## Accessibility

- **Alt Text**: Meaningful descriptions
- **ARIA**: `aria-hidden="true"` for decorative icons
- **Color**: Not sole indicator of status (use labels too)
- **Size**: Minimum 24×24px for interactive

## Icon Library

Complete icon set maintained in:
`/atlas/ui/icons/` (SVG files)

Each icon has:

- Multiple sizes (16, 24, 32, 48px)
- Consistent style
- Accessibility labels
- Dark mode optimized

## Custom Icon Extension

Users can add custom icons via plugins:

```javascript
// Plugin custom icon
atlas.ui.registerIcon("custom-icon", {
  svg: "<svg>...</svg>",
  sizes: [16, 24, 32],
  color: "inherit",
});
```

---

**Icons Specification Version**: 1.0  
**Last Updated**: August 2, 2026
