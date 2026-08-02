# Spacing Specification

## Purpose

Spacing creates visual hierarchy, groups related content, and makes interfaces breathable. The spacing system must be consistent, predictable, and mathematically sound.

---

## Base Unit System

### Foundation: 4px Grid

All spacing values are multiples of 4px:

```
4px   = 1 unit
8px   = 2 units
12px  = 3 units
16px  = 4 units
24px  = 6 units
32px  = 8 units
48px  = 12 units
64px  = 16 units
96px  = 24 units
```

### Why 4px?

- **Divisible**: Works with standard font sizes (12px, 14px, 16px, etc.)
- **Flexible**: Powers of 4 are: 4, 8, 12, 16, 24, 32 (not too sparse or crowded)
- **Screen-Friendly**: Aligns with pixel rendering
- **Mathematical**: Scales proportionally from phone to large displays

---

## Spacing Scale

The complete scale used throughout Atlas:

```
Level 0  = 0px (no space, elements touching)
Level 1  = 4px (minimum, icons to adjacent text)
Level 2  = 8px (default gap between components)
Level 3  = 12px (section padding, grouped items)
Level 4  = 16px (medium gaps, content padding)
Level 5  = 24px (major section break)
Level 6  = 32px (large break between major sections)
Level 7  = 48px (very large break, rare)
Level 8  = 64px (empty state, breathing room)
Level 9  = 96px (maximum, for large displays)
```

### Visual Hierarchy by Spacing

**Tight (4-8px)**: Elements belong together closely
**Normal (12-16px)**: Standard separation
**Loose (24-32px)**: Distinct sections
**Breathing (48-64px)**: Significant space for visual relief

---

## Component Spacing

### Buttons

#### Interior Padding

```
[  ●  Button Label  ]
    ^---4px---^  Icon to text
    ^---------8px--^ Total left/right padding
    ^----8px----^ Total top/bottom padding
```

- **Horizontal Padding**: 16px (8px per side)
- **Vertical Padding**: 8px (4px per side)
- **Height Result**: 32px total
- **Icon + Text Gap**: 4px

#### Button Groups

```
[Save] [Cancel] [Delete]
^----0px----^

No gap between grouped buttons (they share a border)
```

### Input Fields

#### Single-line Input

```
[Icon] Placeholder text [×]
  ^8px^  ^Flex^         ^
       ^---12px---^    Clear button

Height: 32px
Padding Left: 12px (after icon at 8px)
Padding Right: 12px
```

#### Multi-line Text Area

```
Minimum Height: 64px (2 lines at 32px)
Maximum Height: 200px (scrollable after)
Padding: 12px all sides
Line Height: 1.5
```

### Cards

#### Card Padding

```
┌──────────────────────────┐
│ Card Title         [×]   │  32px (header height)
├──────────────────────────┤  12px (top content padding)
│                          │
│  [Card content]          │  12px (bottom content padding)
│                          │
└──────────────────────────┘
```

- **Interior Padding**: 12px all sides
- **Section Gaps**: 12px between sections
- **First Element**: No top margin (uses container padding)
- **Last Element**: No bottom margin (uses container padding)

### List Items

#### List Item Spacing

```
[Icon] Item 1              [>]
[Icon] Item 2              [>]
[Icon] Item 3              [>]

^--4px^ ^---Flex---^    ^4px^
^--------32px Height--------^
```

- **Height**: 32px per item
- **Vertical Padding**: 4px top/bottom
- **Horizontal Padding**: 8px left/right
- **Icon Size**: 16×16px
- **Gap Between Icon & Text**: 8px
- **No Gap Between Items**: Items touch vertically

---

## Panel Spacing

### Sidebar Padding

```
Panel Content
├─ Top Padding: 12px
├─ Left Padding: 12px
├─ Right Padding: 12px
└─ Bottom Padding: 12px
```

### Section Spacing (Within Panels)

```
Section 1
├─ Content
└─ Bottom Margin: 12px

Section 2
├─ Top Margin: 12px
├─ Content
└─ Bottom Margin: 12px
```

**Key Rule**: Section break = 12px above + 12px below = 24px total gap

### Between Panels

```
[Left Panel] [12px gap] [Center Panel] [12px gap] [Right Panel]
```

### Between Top Bar and Content

```
Top Bar (32px)
[12px gap]
Content Area
```

---

## Typography Spacing

### Heading Spacing

```
H1: 32px font
  └─ Bottom Margin: 12px to body text

H2: 24px font
  └─ Top Margin: 24px (from previous section)
  └─ Bottom Margin: 12px to body text

H3: 18px font
  └─ Top Margin: 16px
  └─ Bottom Margin: 8px
```

### Paragraph Spacing

```
Paragraph 1 (12px)
└─ Bottom Margin: 12px

Paragraph 2 (12px)
└─ Bottom Margin: 12px

Paragraph 3 (12px)
└─ No bottom margin (last paragraph)
```

### List Spacing

```
List Title
└─ Bottom Margin: 8px

[List Item]
[List Item]
[List Item]

└─ After List: 12px to next section
```

---

## Dialog Spacing

### Modal Dialog Layout

```
┌─────────────────────────────┐
│ Title               [×]     │  40px height
├─────────────────────────────┤  1px border
│                             │  12px top padding
│ Dialog content              │  Content area
│ Multiple elements           │  12px bottom padding
│                             │
├─────────────────────────────┤  1px border
│ [Cancel]     [Primary Action]│  48px height
│                             │  12px padding
└─────────────────────────────┘
```

- **Header Height**: 40px
- **Content Padding**: 12px top/bottom, 12px left/right
- **Button Area Height**: 48px
- **Button Padding**: 12px
- **Between Content Sections**: 12px

### Nested Content in Dialogs

```
Dialog
├─ Section 1
│  ├─ Element A
│  ├─ 8px gap
│  └─ Element B
├─ 12px gap (section break)
└─ Section 2
   ├─ Element C
   └─ Element D
```

---

## Message / Conversation Spacing

### User Message

```
┌────────────────────────────┐
│ User [2:15 PM]             │  32px line height
│                            │  8px after timestamp
│ Message text here          │  12px padding
│                            │  8px before next item
│                            │
└────────────────────────────┘
├─ 12px gap between messages
│
┌────────────────────────────┐
│ Agent [2:16 PM]            │
│                            │
│ Response text here         │
│                            │
└────────────────────────────┘
```

### Code Block Spacing

```
Message with code:

Text before code: 8px above

[Code block starts]
└─ 12px padding inside code block

[Code block ends]

Text after code: 8px below
```

---

## Empty State Spacing

### Centered Empty State

```
┌────────────────────────────────┐
│                                │
│          [64px breathing]       │
│                                │
│          💬 No Data             │
│                                │
│   [24px after icon]            │
│                                │
│   Helpful message text          │
│                                │
│   [24px before button]          │
│                                │
│          [Action Button]        │
│                                │
│          [64px breathing]       │
│                                │
└────────────────────────────────┘
```

- **Icon to Text**: 24px
- **Text to Button**: 24px
- **Top/Bottom Breathing**: 64px
- **Horizontal Breathing**: 24px left/right

---

## Grid Alignment

### 8px Grid Implementation

All elements should align to the 8px grid:

```
Columns:
0px   8px   16px  24px  32px  40px  48px  ...
|     |     |     |     |     |     |
Position elements at these boundaries

Rows:
Same 8px vertical grid
```

### Grid Snap Rules

- **Text Baseline**: Can fall between grid lines (typography exception)
- **Borders**: Should snap to grid
- **Backgrounds**: Should snap to grid
- **Spacing**: Always grid multiples

---

## Responsive Spacing

### Breakpoint Adjustments

**Below 1366px (Minimal Layout)**

- Reduce padding from 12px to 8px in some panels
- Reduce gaps from 12px to 8px
- Tighter spacing to preserve space

**1366-1920px (Standard)**

- Use spacing scale as designed
- Standard 12px padding throughout

**1920px+ (Large Display)**

- Can increase spacing for emphasis
- Breathing room on large screens
- Empty states use full breathing (64px+)

### No Media Query Stretching

Spacing doesn't change dramatically; adjustment is subtle (12px → 8px, not 12px → 4px).

---

## Spacing Consistency Checklist

Use this checklist when designing new components:

- [ ] Are all gaps multiples of 4px?
- [ ] Is padding 12px for sections, 8px for components?
- [ ] Are list items 32px tall?
- [ ] Do buttons have 16px horizontal padding?
- [ ] Is there 12px between major sections?
- [ ] Are icons 8px from text?
- [ ] Do panels have consistent padding?
- [ ] Is empty state centered with 64px breathing room?

---

## Implementation Notes

### CSS Variables (Recommended)

```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 12px;
--spacing-lg: 16px;
--spacing-xl: 24px;
--spacing-2xl: 32px;
--spacing-3xl: 48px;
--spacing-4xl: 64px;
--spacing-5xl: 96px;
```

### Utility Classes

```css
.gap-xs {
  gap: 4px;
}
.gap-sm {
  gap: 8px;
}
.gap-md {
  gap: 12px;
}
.gap-lg {
  gap: 16px;
}
/* ... etc ... */

.p-md {
  padding: 12px;
}
.px-md {
  padding-left: 12px;
  padding-right: 12px;
}
.py-md {
  padding-top: 12px;
  padding-bottom: 12px;
}
```

---

**Spacing Specification Version**: 1.0  
**Last Updated**: August 2, 2026

Maintain this spacing scale rigidly. Breaking it creates visual inconsistency and confusion.
