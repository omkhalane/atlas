# Onboarding & Help System Specification

First-time user experience and contextual help throughout Atlas.

## First Launch Experience

### Welcome Screen

```
┌─────────────────────────────────────┐
│                                     │
│            Welcome to Atlas         │
│                                     │
│    Autonomous agents at your        │
│    fingertips.                      │
│                                     │
│  [1/4] Language Selection           │
│                                     │
│  Language: [English ▼]              │
│                                     │
│  [Skip] [Next →]                    │
└─────────────────────────────────────┘
```

### Setup Wizard (4 Steps)

**Step 1: Language**

- Choose UI language
- Option to skip (use system language)

**Step 2: Preferences**

```
Theme:      ○ Dark ○ Light ○ High Contrast
Font Size:  ○ Small ○ Normal ○ Large
Telemetry:  ☑ Share usage data (helps improve)
```

**Step 3: First Steps**

```
Quick tips:
• Ctrl+P to open command palette
• Ctrl+K to open chat
• Ctrl+/ for keyboard shortcuts
• F1 for help

[Show Tutorial] [Explore on Own]
```

**Step 4: Complete**

```
┌─────────────────────────────────────┐
│                                     │
│    You're all set!                 │
│                                     │
│    Now let's explore Atlas.        │
│                                     │
│    [Start Using Atlas]              │
│                                     │
│    Tip: Press F1 for help          │
│                                     │
└─────────────────────────────────────┘
```

### Interactive Tutorial (Phase 2+)

Guided tour highlighting:

- Command palette (Ctrl+P)
- Chat interface (Ctrl+K)
- File browser
- Terminal
- Settings

Users can skip at any time.

## Contextual Help

### Help Tooltips

- Hover over UI elements for explanation
- Keyboard shortcut shown
- "Learn More" link to full docs

### Help Button (?)

Question mark icon in corner of each section:

```
[?]
   ↓
Opens context-specific help panel
```

### Inline Help

Right-side help panel shows:

- What the current view does
- Common tasks
- Keyboard shortcuts
- Links to detailed docs

## Help System (F1)

### Help Menu

```
┌─────────────────────────────┐
│ Atlas Help                  │
├─────────────────────────────┤
│ Getting Started             │
│ ├─ What is Atlas?          │
│ ├─ First Steps             │
│ ├─ Chat Basics             │
│ └─ Creating Agents         │
│                             │
│ Features                    │
│ ├─ Browser Integration     │
│ ├─ Terminal Usage          │
│ ├─ File Management         │
│ └─ Memory & Context        │
│                             │
│ Keyboard Shortcuts          │
│ Settings & Preferences      │
│ Troubleshooting            │
│ Report Bug                 │
│ Documentation              │
│ About Atlas                │
│                             │
│ [Search help...]           │
└─────────────────────────────┘
```

### Keyboard Shortcut

```
F1           Open help
Ctrl+?       Show keyboard shortcuts
Ctrl+Shift+/ Search help
```

## Keyboard Shortcuts Reference

### Display

```
Ctrl+?       Show all shortcuts
```

### Quick Reference Card

```
┌─────────────────────────────────────┐
│ Keyboard Shortcuts                  │
├─────────────────────────────────────┤
│ Navigation                          │
│  Ctrl+1...9    Switch panels        │
│  Ctrl+P        Command palette      │
│  Ctrl+K        Focus chat           │
│                                     │
│ Editing                             │
│  Ctrl+S        Save                 │
│  Ctrl+Z        Undo                 │
│  Ctrl+Y        Redo                 │
│                                     │
│ More...        [Full reference]     │
└─────────────────────────────────────┘
```

### Printable Cheat Sheet

Available in Help menu, PDF download.

## Guided Tours (Phase 2+)

### Feature Tours

Step-by-step interactive tours:

- Chat basics
- Browser integration
- Terminal usage
- Agent workflows
- Memory management

### Self-Paced

- Users can pause at any time
- Skip steps as needed
- Repeat tours anytime
- Mark as complete

## Documentation

### Built-in Documentation

Accessible via Help menu:

- Getting Started guide
- Feature documentation
- Troubleshooting
- FAQ
- Contact support

### External Links

- Online documentation: atlas.dev/docs
- Community forum: atlas.dev/community
- Report issues: GitHub issues
- Contact support: support@atlas.dev

## Tips & Tricks

### Tip of the Day

Optional on startup:

```
Did you know?

You can use Ctrl+K to quickly access
the chat and ask agents questions.

[Previous Tip] [Next Tip] [Don't Show Again]
```

### Command Palette Search Tips

```
Type "?" in command palette for tips
Suggests commands based on task
Explains what each command does
```

## Glossary

### Terms Dictionary

Available in Help:

```
Glossary
├─ Agent: An autonomous assistant
├─ Capability: A skill or ability
├─ MCP: Model Context Protocol
├─ Plugin: Extension that adds features
└─ [More terms...]
```

Search for definitions of unfamiliar terms.

## Accessibility in Help

- **Screen Reader**: All help content accessible
- **High Contrast**: Help text readable
- **Keyboard**: Navigate help via keyboard
- **Text Scaling**: Works with browser zoom
- **Closed Captions**: Video content captioned (Phase 2+)

## Troubleshooting Assistant

### Common Issues

Quick solutions for:

- Can't find a feature
- Command not working
- Performance issues
- Crashes
- Permission problems

### Error-Specific Help

When error occurs:

```
[Error message]
  ↓
[Show Help] button appears
  ↓
Help panel shows:
- What this error means
- Why it happened
- How to fix it
- When to contact support
```

## Feedback Loop

### Send Feedback

```
Help → Send Feedback
  or
Ctrl+Shift+F
```

Users can report:

- Unclear documentation
- Missing features
- Bugs
- General feedback

### Support Form

```
Subject: [Feedback about help system]
Category: ○ Unclear ○ Missing ○ Wrong ○ Other
Details: [Text area]
Attachment: [Attach screenshot]

[Send] [Cancel]
```

## Analytics (Phase 2+)

### What We Track

- Which help topics viewed
- How long users stay
- Where they get stuck
- Common questions
- Feature discovery rate

### Privacy

- No personal data collected
- Aggregated statistics only
- User can opt-out

### Improvements

- Most popular topics featured
- Difficult topics expanded
- Unclear docs rewritten

## Tutorial Levels

### Beginner

- Core features only
- Step-by-step guidance
- Simple examples
- Lots of help

### Intermediate

- Advanced features introduced
- Less hand-holding
- Complex examples
- Moderate help

### Expert

- All features available
- Minimal guidance
- Advanced patterns
- Help on demand

## Help Preferences

```
Settings → Help & Learning
├─ Show Tips on Startup: ☑
├─ Show Tooltips: ☑
├─ Tooltip Delay: 100ms [slider]
├─ Help Style: ○ Minimal ○ Moderate ○ Detailed
└─ Language: [English ▼]
```

---

**Onboarding & Help System Specification Version**: 1.0  
**Last Updated**: August 2, 2026

Every user feature should have corresponding help documentation.
