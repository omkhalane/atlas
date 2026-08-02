# Colors Specification

## Color Philosophy

Colors in Atlas serve three purposes:

1. **Communicate Status**: User immediately understands state/result
2. **Enable Interaction**: Highlight clickable elements, focus states
3. **Organize Information**: Group related content, create hierarchy

Colors are **not decorative**. Every color choice serves a functional purpose.

---

## Primary Palette

### Background Colors

#### Surface 0 (Darkest)

- **Value**: #0A0E27
- **RGB**: 10, 14, 39
- **Use**: Window background, main container backgrounds
- **Context**: Behind main content area, between panels
- **OLED**: True black for power efficiency

#### Surface 1 (Dark)

- **Value**: #0F1229
- **RGB**: 15, 18, 41
- **Use**: Panel backgrounds, sidebar backgrounds
- **Context**: Panels on top of Surface 0
- **Visual Hierarchy**: Slightly raised from background

#### Surface 2 (Medium Dark)

- **Value**: #1A1F3A
- **RGB**: 26, 31, 58
- **Use**: Borders, dividers, subtle elevation
- **Context**: UI element containers, input fields
- **Interaction**: Hover background for buttons

#### Surface 3 (Lighter)

- **Value**: #2A3F5A
- **RGB**: 42, 63, 90
- **Use**: Hover states, active backgrounds
- **Context**: Interacted elements, selected states
- **Visual Weight**: Raised from Surface 2

#### Surface 4 (Lightest)

- **Value**: #3A4F7A
- **RGB**: 58, 79, 122
- **Use**: Active selected states, strong emphasis
- **Context**: Focused elements, highlighted sections
- **Rare**: Used sparingly

---

### Text Colors

#### Text Primary

- **Value**: #E0E0E0
- **RGB**: 224, 224, 224
- **Contrast**: 13:1 on #0A0E27 (WCAG AAA+)
- **Use**: Main body text, labels, headings
- **Context**: All primary content

#### Text Secondary

- **Value**: #A0A0A0
- **RGB**: 160, 160, 160
- **Contrast**: 7.5:1 on #0A0E27 (WCAG AA)
- **Use**: Secondary labels, metadata, timestamps
- **Context**: Supporting information

#### Text Tertiary

- **Value**: #7A8BA0
- **RGB**: 122, 139, 160
- **Contrast**: 4.5:1 on #0A0E27 (WCAG A)
- **Use**: Hints, placeholders, disabled labels
- **Context**: Subtle, de-emphasized text

#### Text Disabled

- **Value**: #606060
- **RGB**: 96, 96, 96
- **Contrast**: 3:1 on #0A0E27
- **Use**: Disabled buttons, unavailable options
- **Context**: Grayed-out, non-interactive

---

## Accent Colors

### Primary Accent (Interactive)

- **Value**: #00A8E8
- **RGB**: 0, 168, 232
- **HSL**: 191°, 100%, 45%
- **Use**:
  - Focus rings (all focusable elements)
  - Active/selected states
  - Primary buttons
  - Links
  - Hover highlights
  - Accent indicators
- **Contrast**: 6.8:1 on #0A0E27 (WCAG AA)
- **Variants**:
  - **Light**: #00BFFF (hover, 50% brighter)
  - **Dark**: #0090C0 (active, 25% darker)

### Focus Ring

- **Style**: 2px solid outline
- **Color**: #00A8E8
- **Offset**: 2px outset (outside element)
- **Always Visible**: Even on active elements
- **Timing**: Instant (no fade-in)

---

## Status Colors

### Success

- **Value**: #10B981
- **RGB**: 16, 185, 129
- **HSL**: 160°, 84%, 39%
- **Use**:
  - Successful operations (✓)
  - Passing tests
  - Healthy status indicators
  - Approved states
  - Green indicator lights
- **Contrast**: 5.8:1 on #0A0E27 (WCAG AA)
- **Light Variant**: #34D399 (light success bg)
- **Semantics**: "Good", "Complete", "Verified"

### Warning

- **Value**: #F59E0B
- **RGB**: 245, 158, 11
- **HSL**: 38°, 92%, 50%
- **Use**:
  - Caution before action
  - Pending operations
  - Non-critical alerts
  - Incomplete items
  - Amber indicator lights
- **Contrast**: 4.5:1 on #0A0E27 (WCAG A)
- **Light Variant**: #FCD34D (light warning bg)
- **Semantics**: "Attention", "Waiting", "Review needed"

### Error

- **Value**: #EF4444
- **RGB**: 239, 68, 68
- **HSL**: 0°, 84%, 60%
- **Use**:
  - Failed operations (✗)
  - Error messages
  - Invalid input
  - Blocked/disabled operations
  - Red indicator lights
  - Destructive actions warning
- **Contrast**: 3.5:1 on #0A0E27 (WCAG A)
- **Light Variant**: #FCA5A5 (light error bg)
- **Semantics**: "Problem", "Failed", "Stop"

### Info

- **Value**: #06B6D4
- **RGB**: 6, 182, 212
- **HSL**: 188°, 94%, 43%
- **Use**:
  - Informational messages
  - Neutral notifications
  - Help text
  - Informational indicators
  - Cyan indicator lights
- **Contrast**: 6.2:1 on #0A0E27 (WCAG AA)
- **Light Variant**: #22D3EE (light info bg)
- **Semantics**: "FYI", "Informational", "Neutral"

---

## Semantic Color Usage

### Interactive Elements

#### Buttons

```
Primary Button:
  Background: #00A8E8
  Text: #0A0E27

Secondary Button:
  Background: transparent
  Border: 1px #1A1F3A
  Text: #A0A0A0
  Hover Text: #E0E0E0

Danger Button:
  Background: #EF4444
  Text: #E0E0E0
```

#### Links

```
Default Link: #00A8E8
Visited Link: #00A8E8 (same, no distinction)
Hover Link: #00BFFF (light variant)
Focus Link: 2px #00A8E8 ring
```

#### Indicators

```
On: #00A8E8 (blue) or #10B981 (green)
Off: #606060 (disabled gray)
```

---

### Input States

#### Normal Input

```
Border: #1A1F3A
Background: #0F1229
Text: #E0E0E0
Placeholder: #7A8BA0
```

#### Focused Input

```
Border: #00A8E8 (2px)
Background: #0F1229
Text: #E0E0E0
Focus Ring: #00A8E8 (2px outline)
```

#### Valid Input

```
Border: #10B981
Background: #0F1229
Text: #E0E0E0
Helper Text: #10B981
```

#### Invalid Input

```
Border: #EF4444
Background: #0F1229
Text: #E0E0E0
Error Text: #EF4444
```

#### Disabled Input

```
Border: #404050
Background: #0A0E27
Text: #606060
Opacity: 50%
```

---

### Status Indicators

#### Process Status

| State     | Color   | Icon |
| --------- | ------- | ---- |
| Idle      | #7A8BA0 | ○    |
| Planning  | #F59E0B | ⟳    |
| Running   | #00A8E8 | ⟳    |
| Paused    | #06B6D4 | ⏸    |
| Waiting   | #F59E0B | ⏳   |
| Success   | #10B981 | ✓    |
| Error     | #EF4444 | ✗    |
| Cancelled | #7A8BA0 | ⊘    |

#### File Status (Git Integration)

```
Untracked:  #7A8BA0 (gray)
Modified:   #F59E0B (amber)
Staged:     #00A8E8 (blue)
Committed:  #10B981 (green)
Conflict:   #EF4444 (red)
```

---

## Color in Context

### Messages

#### User Message

```
Background: #1A1F3A (dark blue)
Border-Left: #00A8E8 (blue accent)
Text: #E0E0E0
```

#### Agent Message

```
Background: #0F1229 (normal)
Border: None
Text: #E0E0E0
Code Block: #2A3F5A background
```

#### System Message

```
Background: #2A3F5A (gray-blue)
Border: None
Text: #A0A0A0 (lighter gray)
Icon: #7A8BA0
```

---

### Notifications

#### Success Toast

```
Background: #10B981 20% opacity
Border: 1px #10B981
Icon: #10B981 ✓
Text: #10B981
```

#### Error Toast

```
Background: #EF4444 20% opacity
Border: 1px #EF4444
Icon: #EF4444 ✗
Text: #EF4444
```

#### Warning Toast

```
Background: #F59E0B 20% opacity
Border: 1px #F59E0B
Icon: #F59E0B ⚠
Text: #F59E0B
```

#### Info Toast

```
Background: #06B6D4 20% opacity
Border: 1px #06B6D4
Icon: #06B6D4 ℹ
Text: #06B6D4
```

---

### Highlights & Selection

#### Text Selection

```
Background: #00A8E8 20% opacity
Color: #E0E0E0 (unchanged)
```

#### List Item Hover

```
Background: #1A1F3A
Border-Left: None
```

#### List Item Selected

```
Background: #2A3F5A
Border-Left: 2px #00A8E8
```

#### Code Block Line Highlight

```
Background: #1A1F3A
Border-Left: 2px #00A8E8
```

---

## Color Accessibility

### Contrast Requirements

#### WCAG Compliance Levels

- **AAA (7:1)**: Primary text on background
- **AA (4.5:1)**: Secondary text, UI components
- **A (3:1)**: Large text, decorative elements

### High Contrast Mode

When user enables high contrast:

- Increase text color saturation
- Increase border brightness
- Use pure white for text (#FFFFFF instead of #E0E0E0)
- Use darker backgrounds
- Increase opacity of disabled states

### Color Blindness Considerations

#### Red-Green Blindness

- Don't rely on red/green distinction alone
- Use red + icons (✓, ✗) together
- Success: Green + checkmark
- Error: Red + X mark
- Consider: Add patterns or icons to distinguish status

#### Blue-Yellow Blindness

- Blue accent (#00A8E8) works well
- Info color (#06B6D4) similar range
- Warning (#F59E0B) well differentiated
- No issues expected

#### Complete Color Blindness

- Monochrome mode available in settings
- Converts all colors to grays while maintaining luminosity
- Use icons and borders for distinction

---

## Dark Mode Only

### Why Dark Mode?

1. **OLED Efficiency**: True blacks use no power
2. **Developer Preference**: Standard for technical tools
3. **Accessibility**: Easier on eyes during long sessions
4. **Brand**: Modern, technical aesthetic
5. **UI Clarity**: Bright accents stand out against dark

### Dark Mode as Foundation

All color decisions assume dark backgrounds:

- No light mode equivalent
- No theme switcher
- All testing on dark surfaces
- High contrast text standard

### Future: Theme System

_Note: Phase 1 is dark only. Phase 2+ could add:_

- Custom theme builder (adjust accent color, etc.)
- Auto theme sync with system (if user enables)
- Theme presets (Dracula, Nord, Solarized, etc.)

---

## Color Usage Anti-Patterns

### Don't

❌ Use color alone to indicate status (no red-only errors)  
❌ Use decorative colors (every color serves purpose)  
❌ Use low-contrast text (minimum 4.5:1 WCAG AA)  
❌ Create new accent colors (use defined palette)  
❌ Use light backgrounds (dark mode only)  
❌ Animate between status colors (instant transitions only)

### Do

✓ Combine color + icon + label for status  
✓ Use defined palette (8 total colors maximum)  
✓ Test contrast ratios for accessibility  
✓ Use accent color consistently  
✓ Maintain dark backgrounds  
✓ Use color with high-contrast borders/text

---

## Color Palette Reference Card

```
┌─ Backgrounds ──────────────────────┐
│ #0A0E27 Surface 0 (darkest)       │
│ #0F1229 Surface 1 (dark)          │
│ #1A1F3A Surface 2 (medium)        │
│ #2A3F5A Surface 3 (light)         │
│ #3A4F7A Surface 4 (lightest)      │
└────────────────────────────────────┘

┌─ Text ─────────────────────────────┐
│ #E0E0E0 Primary (high contrast)   │
│ #A0A0A0 Secondary (medium)        │
│ #7A8BA0 Tertiary (low)            │
│ #606060 Disabled                  │
└────────────────────────────────────┘

┌─ Accent ───────────────────────────┐
│ #00A8E8 Primary Accent (blue)     │
│ #00BFFF Light Accent              │
│ #0090C0 Dark Accent               │
└────────────────────────────────────┘

┌─ Status ───────────────────────────┐
│ #10B981 Success (green)           │
│ #F59E0B Warning (amber)           │
│ #EF4444 Error (red)               │
│ #06B6D4 Info (cyan)               │
└────────────────────────────────────┘
```

---

## Implementation Notes

### CSS Variables (Recommended)

```css
--color-surface-0: #0a0e27;
--color-surface-1: #0f1229;
--color-text-primary: #e0e0e0;
--color-accent: #00a8e8;
--color-success: #10b981;
--color-error: #ef4444;
```

### Linux Theme Integration

- Respect system color scheme settings
- Allow override via settings
- Store user's color preferences

---

**Colors Specification Version**: 1.0  
**Last Updated**: August 2, 2026
