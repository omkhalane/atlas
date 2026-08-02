# Tooltips & Help Specification

Contextual help, hints, and informational overlays.

## Tooltip Types

### Standard Tooltip

```
[Button] → "Save current file"
```

- **Trigger**: Hover for 100ms
- **Position**: Above element, centered
- **Max Width**: 200px
- **Duration**: Visible until mouse leaves
- **Fade Out**: 100ms after mouse leaves

### Keyboard Shortcut Tooltip

```
[Button] → "Save current file (Ctrl+S)"
```

- **Shortcut**: Shown in parentheses
- **Font**: Monospace for shortcut
- **Position**: Aligned to button center

### Error Tooltip

```
[Invalid Input] → "❌ Email must be valid"
```

- **Icon**: Error symbol (red X)
- **Color**: Red text
- **Position**: Below invalid field
- **Always Visible**: Until corrected
- **No Timeout**: Stays until interaction

### Help Tooltip (Extended)

```
[?] → Detailed help text with
      multiple lines explaining
      how this feature works.

      [Learn More →]
```

- **Icon**: Question mark in circle
- **Max Width**: 300px
- **Multiline**: Support paragraphs
- **Link**: Optional "Learn More" link

## Positioning Algorithm

1. **Above**: Default, if space available
2. **Below**: If no room above
3. **Left**: If no room above/below, try left
4. **Right**: Final fallback
5. **Reposition**: On window resize, recalculate

## Keyboard Access

- **Alt**: Show all tooltips in view (help mode)
- **Hover Equivalent**: Focus ring on element shows tooltip
- **Escape**: Hide tooltips
- \*\*Ctrl+?: Show all shortcuts

## Visual Styling

### Tooltip Box

- **Background**: #1A1F3A
- **Border**: 1px #2A3F5A
- **Border Radius**: 4px
- **Padding**: 6px 8px
- **Text**: #E0E0E0, 11px

### Arrow/Pointer

- **Color**: #1A1F3A
- **Size**: 6px triangle
- **Points to Element**: Center

### Shadow

- No shadow (dark mode, use border instead)
- Opacity 80% if needed for layering

## Accessibility

- **Screen Reader**: Content announced
- **Focus**: Tooltip appears on focus
- **Color**: Not sole indicator
- **Contrast**: 7:1 minimum
- **High Contrast Mode**: Borders thicker

## Animation

- **Appear Delay**: 100ms (prevent clutter)
- **Fade In**: 100ms ease-out
- **Fade Out**: 100ms ease-in
- **Respects**: `prefers-reduced-motion` (instant)

## Content Guidelines

### Good Tooltip Text

```
"Save changes to current file"        ✓ Descriptive
"Opens file save dialog"              ✓ Clear action
"Ctrl+S"                              ✓ Keyboard shortcut
```

### Bad Tooltip Text

```
"Save"                                ✗ Too vague
"This button does something"          ✗ Not helpful
"Click here"                          ✗ No meaning
```

### Tooltip Length

- **Max**: 200 characters (fits in box)
- **Ideal**: 50-100 characters
- **Short**: Single line preferred
- **Multiline**: Only for complex features

## Help System Integration

### Ctrl+? Help Mode

- Shows all tooltips simultaneously
- Highlights all interactive elements
- Shows keyboard shortcuts inline
- Makes all tooltips visible without hover

### Contextual Help

- **F1**: Help for current feature
- **[?] Button**: Question mark icon opens help
- **Learn More**: Tooltips link to docs

## Mobile/Touch (Future)

When gesture support added:

- **Long Press**: Show tooltip
- **Tap**: Open help panel
- **Swipe**: Dismiss tooltip

---

**Tooltips Specification Version**: 1.0  
**Last Updated**: August 2, 2026
