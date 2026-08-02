# Dialogs & Modals Specification

Common dialog patterns and modal layouts used throughout Atlas.

## Dialog Structure

```
┌──────────────────────────────────┐
│ Dialog Title              [×]    │  40px Header
├──────────────────────────────────┤
│                                  │
│ [Dialog content area]            │  Flex Content
│ Instructions, inputs, etc.       │
│                                  │
├──────────────────────────────────┤
│ [Cancel]      [Primary Action]  │  48px Footer
└──────────────────────────────────┘
```

- **Width**: 480px (standard), 600px (large), 360px (small)
- **Position**: Centered on screen
- **Backdrop**: 40% dark overlay
- **Border Radius**: 8px
- **Border**: 1px #1A1F3A

## Dialog Types

### Confirmation Dialog

```
⚠️  Confirm Action

Are you sure you want to delete this file?
This action cannot be undone.

[Cancel] [Delete]
```

- **Icon**: Warning (⚠️)
- **Message**: Clear and specific
- **Actions**: Cancel + Destructive action
- **Default Focus**: Cancel button

### Input Dialog

```
Create New File

File name:
[___________________]

[Cancel] [Create]
```

- **Input Field**: Auto-focused
- **Validation**: Show errors inline
- **Submit**: Enter key or button

### Approval Dialog

```
Agent Requests Approval

Action: Delete file
File: src/deprecated.js
Reason: Remove unused code

[View File] [More Details]

Save backup: ☑ Yes

[Approve] [Deny] [Ask Later]
```

- **Clear Context**: What, why, what happens
- **Preview**: Show affected content
- **Options**: One-time, remember choice, etc.

### Error Dialog

```
❌ Error Occurred

Unable to connect to server.
Error: Connection timeout (30s)

Suggestions:
• Check your network connection
• Try again in a moment
• Contact support if problem persists

[Retry] [Report] [Close]
```

- **Error Icon**: Red X
- **Message**: Technical + human-readable
- **Suggestions**: Help user recover
- **Actions**: Retry, report, dismiss

### Progress Dialog

```
Processing...

Uploading files (3 of 12)
████████░░░░░░░░░░ 40%

Time Remaining: ~2m 30s

[Cancel]
```

- **Progress Bar**: Animated
- **Estimate**: Time remaining
- **Cancellable**: Unless critical operation

## Keyboard Interaction

- **Enter**: Activate focused button
- **Tab**: Move between buttons
- **Shift+Tab**: Move backwards
- **Escape**: Close dialog (cancel/dismiss)
- **Space**: Activate focused button

## Accessibility

- **Focus Trap**: Tab loops within dialog
- **Screen Reader**: Title announced, content readable
- **High Contrast**: All text readable
- **Close Button**: Always available (X button)

## Animation

- **Entrance**: Fade-in 100ms
- **Exit**: Fade-out 100ms
- **No Scale**: Appears full-size (not zoomed)
- **Respects**: `prefers-reduced-motion` setting

---

**Dialogs Specification Version**: 1.0  
**Last Updated**: August 2, 2026
