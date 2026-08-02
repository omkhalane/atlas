# Context Menus Specification

Right-click context menus providing quick access to actions.

## Menu Structure

```
Context Menu
├─ ✏️  Edit            (Ctrl+E)
├─ 🗑️  Delete           (Delete)
├─ ✂️  Cut              (Ctrl+X)
├─ 📋 Copy             (Ctrl+C)
├────────────────────  [Divider]
├─ 📊 Properties       (Alt+Enter)
└─ 🔄 Show in Folder
```

- **Max 8 items**: Keep concise
- **Keyboard Shortcut**: Shown on right
- **Icons**: Identify actions quickly
- **Dividers**: Group related items

## Positioning

- **Near Cursor**: Slightly offset from click point
- **Within Viewport**: Adjust if menu would go off-screen
- **No Overlap**: Doesn't cover selected item
- **Auto-Close**: When clicking outside menu

## Keyboard Navigation

- **Arrow Keys**: Navigate menu items
- **Enter**: Activate selected item
- **Escape**: Close menu
- **Letter Key**: Jump to item starting with that letter

## Context-Specific Menus

### File Context Menu

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
```

### Chat Message Menu

```
↩️  Reply
📋 Copy Message
📌 Pin Message
✏️  Edit
🗑️  Delete
───────────
📤 Export
⭐ Bookmark
```

### Terminal Menu

```
🔄 Clear
📋 Copy Output
🗑️  Clear History
───────────
💾 Save Output
📤 Export Session
⚙️  Settings
```

## Accessibility

- **Keyboard Accessible**: Full support
- **Screen Reader**: Items announced
- **High Contrast**: Text readable
- **Large Touch Targets**: 32px minimum height

## Animation

- **Appear**: Instant (no fade)
- **Disappear**: Instant or 100ms fade
- **Hover**: Highlight background changes
- **Transitions**: None (responsive feel)

---

**Context Menus Specification Version**: 1.0  
**Last Updated**: August 2, 2026
