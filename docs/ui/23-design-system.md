# Design System Specification

## Purpose

The Design System is the foundation for all UI elements in Atlas. It ensures consistency, maintains accessibility standards, and provides clear guidelines for implementing components.

---

## Component Library

### Buttons

#### Primary Button

- **Background**: #00A8E8 (electric blue)
- **Text**: #0A0E27 (dark)
- **Padding**: 8px 16px
- **Height**: 32px
- **Border Radius**: 4px
- **Font**: Inter, 12px, 500 weight
- **Cursor**: pointer

**States**:

- **Default**: Full blue background
- **Hover**: Lighten to #00BFFF
- **Active**: Darken to #0090C0
- **Disabled**: #4A5A6A (gray), cursor: not-allowed
- **Focus**: 2px blue outline, offset 2px

#### Secondary Button

- **Background**: Transparent
- **Border**: 1px, #1A1F3A
- **Text**: #A0A0A0
- **Padding**: 8px 16px
- **Height**: 32px
- **Font**: Inter, 12px, 400 weight

**States**:

- **Hover**: Border brightens to #2A3F5A, text to #E0E0E0
- **Active**: Invert to dark blue background
- **Disabled**: Border #404050, text #606060

#### Icon Button

- **Size**: 24×24px (content) or 32×32px (padded)
- **Background**: Transparent
- **Padding**: 4px
- **Icon Size**: 16×16px
- **Cursor**: pointer

**States**:

- **Hover**: Background #1A1F3A
- **Active**: Background #2A3F5A
- **Disabled**: Opacity 50%

#### Button Group

Multiple buttons grouped:

```
[< Previous] [1] [2] [3] [Next >]
```

- Buttons share borders (middle buttons have no side borders)
- First: border-radius left 4px
- Last: border-radius right 4px
- Middle: no border-radius

---

### Input Fields

#### Text Input

```
┌─────────────────────────────────┐
│ [Icon] Placeholder text    [×]  │
└─────────────────────────────────┘
```

- **Height**: 32px
- **Padding**: 8px 12px (sides), 0 (top/bottom)
- **Border**: 1px solid #1A1F3A
- **Border Radius**: 4px
- **Font**: Inter, 12px
- **Background**: #0F1229
- **Text Color**: #E0E0E0
- **Placeholder**: #7A8BA0

**States**:

- **Focus**: Border #00A8E8 (2px), shadow none
- **Disabled**: Background #0A0E27, text #606060
- **Error**: Border #EF4444
- **Success**: Border #10B981

#### Search Input

Special variant of text input:

- Magnifying glass icon left
- Clear button (X) right
- Real-time search
- Debounce 200ms

#### Number Input

```
┌──────────┐
│ 42  [↑]  │
│    [↓]   │
└──────────┘
```

- Min/max constraints
- Spinner arrows on right
- Keyboard: ↑↓ to increment/decrement

#### Checkbox

- **Size**: 16×16px
- **Border**: 2px solid #1A1F3A
- **Border Radius**: 2px
- **Checked**: Background #00A8E8, checkmark white
- **Label**: 12px, left 8px

#### Radio Button

- **Size**: 16×16px
- **Border**: 2px solid #1A1F3A
- **Border Radius**: 50%
- **Checked**: Inner circle #00A8E8 (8px)
- **Label**: 12px, left 8px

#### Toggle Switch

```
[●        ] OFF
[        ●] ON
```

- **Width**: 48px
- **Height**: 24px
- **Border Radius**: 12px (pill-shaped)
- **Background**: #1A1F3A (off), #00A8E8 (on)
- **Circle**: 20px white, centered
- **Transition**: 100ms ease

#### Select / Dropdown

```
┌─────────────────────────────┐
│ Select an option ▼          │
└─────────────────────────────┘

▼ Click to open:
  ▪ Option 1
  ▪ Option 2 (highlighted)
  ▪ Option 3
```

- **Height**: 32px
- **Padding**: 8px 12px
- **Border**: 1px #1A1F3A
- **Font**: Inter, 12px
- **Chevron Icon**: Right 12px

---

### Typography

#### Font Families

- **Sans Serif**: Inter (primary, UI text)
- **Monospace**: JetBrains Mono (code, terminal)

#### Font Sizes & Scale

```
Base: 12px (standard body text)
Scale multiplier: 1.25

32px - Page titles (H1)
24px - Section titles (H2)
18px - Subsection titles (H3)
14px - Label/button text (H4)
12px - Body text, labels (base)
11px - Small text, hints
10px - Captions, timestamps
```

#### Line Height

- **12px text**: 1.5 (18px)
- **14px text**: 1.5 (21px)
- **16px+ text**: 1.4

#### Weight

- **400**: Regular text, most UI
- **500**: Labels, strong emphasis
- **600**: Headings
- **700**: Strong headings (rare)

#### Letter Spacing

- **0**: Default
- **0.5px**: All-caps labels
- **-0.5px**: Large headings (tighter)

#### Text Colors

- **Primary**: #E0E0E0 (high contrast)
- **Secondary**: #A0A0A0 (medium contrast)
- **Tertiary**: #7A8BA0 (low contrast)
- **Disabled**: #606060
- **Link**: #00A8E8 (electric blue)
- **Danger**: #EF4444 (red)
- **Success**: #10B981 (green)
- **Warning**: #F59E0B (amber)

---

### Spacing

#### Scale (Multiples of 4px)

```
0    - No space (elements touching)
4px  - Minimal spacing (icons to text)
8px  - Default gap (between components)
12px - Section padding, dialog padding
16px - Content padding, large gap
24px - Major section break
32px - Large break (rare)
48px - Page-level break (rare)
64px - Empty state breathing room
```

#### Common Patterns

**Button Spacing**:

- Within button: 8px padding (horizontal) × 8px (vertical)
- Between buttons: 8px gap
- Button groups: 0px gap (shared border)

**Panel Padding**:

- Panel content: 12px top/bottom, 12px left/right
- First element: No top margin
- Between sections: 12px margin

**List Items**:

- Item height: 32px
- Item padding: 8px left/right, 4px top/bottom
- Between items: 0px (items touching)

---

### Borders & Shadows

#### Border System

- **Type**: Solid 1px lines
- **Color**: #1A1F3A (dark gray)
- **Uses**:
  - Separate panels
  - Define input fields
  - Highlight active elements
  - Show focus states

#### Elevation Alternatives

Since dark mode eliminates shadows, use these instead:

- **Opacity layers**: 5%, 10%, 20% white overlay
- **Borders**: 1px bright border for emphasis
- **Background**: Darker background for depth
- **Focus Ring**: 2px blue outline

#### Focus Ring

- **Style**: 2px solid #00A8E8
- **Offset**: 2px outset
- **Border Radius**: Match element radius + 2px
- **Always Visible**: High contrast, no timing delays

---

### Colors

#### Primary Palette

```
Background:  #0A0E27 (darkest)
Surface:     #0F1229 (dark)
Border:      #1A1F3A (medium)
Hover:       #2A3F5A (lighter)
Text Primary: #E0E0E0 (light)
Text Secondary: #A0A0A0 (medium)
Text Tertiary: #7A8BA0 (dark)
```

#### Status Colors

```
Success: #10B981 (green)
Warning: #F59E0B (amber)
Error:   #EF4444 (red)
Info:    #06B6D4 (cyan)
```

#### Semantic Colors

```
Accent:    #00A8E8 (electric blue)
Link:      #00A8E8 (same as accent)
Disabled:  #606060 (very dark gray)
Focus:     #00A8E8 (2px ring)
Selection: #00A8E8 with 20% opacity background
```

#### Usage Guidelines

- **Primary Text**: On backgrounds #0A0E27-#1A1F3A
- **Secondary Text**: On backgrounds #0A0E27-#2A3F5A
- **Accent**: Highlight interactive elements, focus states
- **Status**: Only for status/state, never for decoration

---

### Icons

#### Icon System

- **Style**: Outline style, consistent weight
- **Sizes**: 16×16px (inline), 24×24px (buttons), 32×32px (large)
- **Color**: Inherit text color
- **Stroke Width**: 2px for outlined icons

#### Common Icons

```
📁 Folder       (file explorer)
📄 File         (document)
💬 Chat         (conversation)
🌐 Browser      (web)
⌨️  Terminal      (command line)
🧠 Memory       (knowledge)
🤖 Agent        (AI agent)
📊 Planner      (tasks/planning)
⚙️  Settings      (preferences)
🔍 Search       (magnifying glass)
⭐ Favorite      (star)
🔔 Notification (bell)
⚠️  Warning      (triangle)
✅ Success      (checkmark)
❌ Error        (X)
ℹ️  Info         (i in circle)
```

#### Icon Sources

- **Primary**: Custom SVG icons (to be designed)
- **System**: Use system icon themes when available
- **Consistency**: All icons should follow same style
- **Dark Mode**: Optimize for dark backgrounds

---

### Lists

#### Basic List

```
[🔍] Item 1              [>]
[🔍] Item 2 (focused)    [>]
[🔍] Item 3              [>]
```

- **Item Height**: 32px
- **Padding**: 8px horizontal, 4px vertical
- **Icon**: 16×16px, left 8px
- **Text**: 12px, left 8px from icon
- **Chevron**: Right 8px (if expandable)

#### Hover State

- **Background**: #1A1F3A
- **Action Buttons**: Appear on hover
- **Text**: Brighten to #E0E0E0

#### Selected State

- **Background**: #2A3F5A (darker hover)
- **Border Left**: 2px #00A8E8
- **Text**: #E0E0E0

#### Grouped Lists

```
📌 Pinned
  • Item 1
  • Item 2

📅 Today
  • Item 3
  • Item 4
```

- **Group Headers**: Smaller text (11px), #7A8BA0
- **Padding Above**: 12px (for group header)
- **Indent**: Sub-items indent 16px

---

### Cards

#### Basic Card

```
┌─────────────────────────────┐
│ Card Title          [⋮] [×] │ Header: 32px
├─────────────────────────────┤
│                             │
│ Card content                │ Content: Flex
│                             │
└─────────────────────────────┘
```

- **Background**: #0F1229
- **Border**: 1px #1A1F3A
- **Border Radius**: 4px
- **Padding**: 12px
- **Shadow**: None (use border for definition)

#### Hover State

- **Border**: 1px #2A3F5A
- **Background**: Slightly lighter #141829

#### Task Card

Special card type for agent tasks:

```
┌──────────────────────────────┐
│ ✓ Task: Run Tests     [⋮]    │ Status indicator
├──────────────────────────────┤
│ Status: ✅ Complete (2m 15s) │
│ Tests: 45/45 passing         │
│                              │
│ Files Changed:               │
│ • test/app.test.js (1 ∆)    │
│ • src/app.ts (2 ∆)          │
│                              │
│ [View Changes] [Rollback]    │
└──────────────────────────────┘
```

---

### Dialogs & Modals

#### Dialog Structure

```
┌──────────────────────────────────────┐
│ Dialog Title              [×] Close   │ 40px
├──────────────────────────────────────┤
│                                      │
│ [Dialog content area]                │ Flex
│ Multiple lines, paragraphs, inputs   │
│                                      │
├──────────────────────────────────────┤
│ [Cancel]              [Primary Action]│ 48px
└──────────────────────────────────────┘
```

- **Width**: 480px (standard)
- **Position**: Centered on screen
- **Backdrop**: 40% opacity dark overlay
- **Border Radius**: 8px
- **Border**: 1px #1A1F3A
- **Background**: #0F1229

#### Dialog Interactions

- **Close (X)**: Top right
- **Escape**: Close dialog
- **Tab**: Navigate focus through elements
- **Enter**: Activate focused button
- **Backdrop Click**: Optionally close (if not critical)

---

### Tooltips

```
[Element] ──→ Tooltip text explaining element
```

- **Max Width**: 200px
- **Font Size**: 11px
- **Padding**: 6px 8px
- **Background**: #1A1F3A
- **Text**: #E0E0E0
- **Border**: 1px #2A3F5A
- **Border Radius**: 4px
- **Appear Delay**: 100ms hover
- **Arrow**: Pointing to element
- **Z-Index**: 600 (above content, below modals)

#### Keyboard Trigger

- **Alt**: Temporarily show all tooltips in view
- **Esc**: Hide tooltips
- **Ctrl+?**: Help mode (show extended tooltips everywhere)

---

### Notifications / Toasts

#### Position

Bottom-right corner, 12px from edges.

#### Styles by Type

**Success**

```
✅ Action completed successfully
```

- **Background**: #10B981 with 20% opacity
- **Border**: 1px #10B981
- **Text**: #10B981
- **Duration**: 3 seconds auto-dismiss

**Error**

```
❌ Something went wrong (Error details)
```

- **Background**: #EF4444 with 20% opacity
- **Border**: 1px #EF4444
- **Text**: #EF4444
- **Duration**: Sticky (user closes)
- **Button**: [Retry] or [Close]

**Warning**

```
⚠️  Confirm before proceeding
```

- **Background**: #F59E0B with 20% opacity
- **Border**: 1px #F59E0B
- **Text**: #F59E0B
- **Duration**: Sticky
- **Buttons**: [OK] [Cancel]

**Info**

```
ℹ️  Background job completed
```

- **Background**: #06B6D4 with 20% opacity
- **Border**: 1px #06B6D4
- **Text**: #06B6D4
- **Duration**: 5 seconds auto-dismiss

#### Stacking

- Maximum 3 toasts visible
- Older toasts push down as new appear
- Remove toast: Click X or wait for auto-dismiss

---

### Loading & Progress

#### Spinner

```
  ⟳ Loading...
```

- **Size**: 16×16px (inline), 24×24px (large)
- **Color**: #00A8E8
- **Animation**: Continuous rotation, 1s per full spin
- **Accessibility**: Hidden from screen readers, text shown instead

#### Progress Bar

```
████████░░░░░░░░░░░░░░ 40%
```

- **Height**: 4px
- **Background**: #1A1F3A
- **Filled**: #00A8E8
- **Border Radius**: 2px
- **Show Percentage**: Right side, 11px text

#### Indeterminate Progress

```
⟳ ████░░░░░░░░░░░░░░░░░░░░ unknown
```

- **Pattern**: Animated stripe moving left-to-right
- **No Percentage**: Show "estimating" or loading message
- **Duration**: Unclear (network request, async operation)

---

### Skeleton Screens

When loading content, show placeholder:

```
┌──────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓ │ Skeleton block
│ ▓▓▓▓▓▓▓▓▓▓▓▓ │
│ ▓▓▓▓▓▓      │
└──────────────┘
```

- **Color**: #1A1F3A (same as borders)
- **Opacity**: Animate between 60%-100%
- **Border Radius**: Match expected content
- **Animation**: Subtle pulse, 1.5s duration
- **Replace**: Fade out and show actual content when ready

---

## Component Usage Guidelines

### When to Use Each Component

| Task              | Component        | Example                                   |
| ----------------- | ---------------- | ----------------------------------------- |
| Primary action    | Primary Button   | "Send Message", "Save File"               |
| Secondary action  | Secondary Button | "Cancel", "Dismiss"                       |
| Toggle option     | Toggle/Checkbox  | "Enable notifications", "Dark mode"       |
| Choose from list  | Select/Dropdown  | "Choose workspace", "Select agent"        |
| Multi-line input  | Text Area        | "Compose message", "Code input"           |
| Single line input | Text Input       | "File name", "Search query"               |
| Numeric input     | Number Input     | "Line number", "Count"                    |
| Choose one        | Radio Button     | "View mode: List/Grid/Compact"            |
| Temporary message | Toast            | "Copied!", "Error occurred"               |
| Important dialog  | Modal            | "Delete confirmation", "Approval request" |
| Contextual info   | Tooltip          | "Button shortcut", "Field requirements"   |

---

## Animation & Motion

### Timing Curves

- **Fast**: 100ms (hover, micro-interactions)
- **Standard**: 200ms (panel open/close, view transitions)
- **Slow**: 300ms (modals, major layout changes)

### Easing Functions

- **Ease-out**: UI elements entering (material design)
- **Ease-in**: UI elements leaving
- **Ease-in-out**: Symmetrical transitions
- **Linear**: Progress bars, spinners, continuous animations

### Preferes-Reduced-Motion

All animations disabled when user has set `prefers-reduced-motion: reduce`. Changes appear instantly.

---

**Design System Version**: 1.0  
**Last Updated**: August 2, 2026

This specification is the source of truth for all component design. Follow it precisely to maintain consistency across Atlas.
