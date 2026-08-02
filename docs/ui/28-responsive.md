# Responsive & Adaptive UI Specification

How Atlas adapts to different screen sizes and device contexts while maintaining usability.

## Breakpoint Strategy

### Display Categories

#### Small (Below 1366px)

- **Primary Use**: Ultrawide notebooks, small laptops
- **Challenge**: Limited horizontal space
- **Strategy**: Single-column layout, tabbed panels

**Changes**:

- Info sidebar hidden by default (toggle with Ctrl+Shift+P)
- Secondary panels become tabs
- Menu bar collapses to hamburger (≡)
- Font sizes reduce 1-2px

#### Medium (1366-1920px)

- **Primary Use**: Standard laptop, 24" monitor
- **Challenge**: Balanced space allocation
- **Strategy**: Two-column layout, split panels optional

**Changes**:

- All panels visible
- Optional splitting
- Full functionality
- Standard font sizes

#### Large (1920px+)

- **Primary Use**: 27"+ monitor, ultrawide
- **Challenge**: Underutilized space
- **Strategy**: Three-column layout, expanded content

**Changes**:

- Multiple split options
- Info sidebar wider (350-400px)
- More content visible per panel
- Increased breathing room

### Breakpoint Values

```css
--breakpoint-sm: 1024px --breakpoint-md: 1366px --breakpoint-lg: 1920px
  --breakpoint-xl: 2560px;
```

## Layout Adaptation

### Below 1366px: Minimal Layout

```
┌──────┬──────────────────────────┐
│      │  Single Content Area     │
│ Act  │  (Tabbed switching)      │
│ Side │                          │
│      ├──────────────────────────┤
│      │  Bottom Panel (Terminal) │
└──────┴──────────────────────────┘
```

- Activity sidebar: Fixed 48px
- Content: Full available width
- Info sidebar: Hidden (accessible via Ctrl+Shift+P)
- Bottom panels: Resizable, initially hidden

### 1366-1920px: Standard Layout

```
┌──────┬──────────────────┬──────────┐
│      │                  │          │
│ Act  │   Main Content   │  Info    │
│ Side │                  │  Sidebar │
│      ├──────────────────┤          │
│      │  Secondary Panel │          │
└──────┴──────────────────┴──────────┘
```

- All components visible
- Panels resizable
- Standard spacing

### 1920px+: Full-Spread Layout

```
┌──────┬──────────┬──────────┬──────────┐
│      │          │          │          │
│ Act  │  Chat    │ Browser  │  Info    │
│ Side │  Primary │ Secondary│ Sidebar  │
│      │          │          │          │
└──────┴──────────┴──────────┴──────────┘
```

- Maximum four-column layout
- Flexible column widths
- Multiple simultaneous views

## Component Adaptation

### Sidebar Width Adjustments

| Breakpoint  | Sidebar Min | Sidebar Max  |
| ----------- | ----------- | ------------ |
| < 1366px    | Hidden      | 50% (toggle) |
| 1366-1920px | 200px       | 400px        |
| > 1920px    | 250px       | 450px        |

### Font Size Scaling

| Breakpoint  | Base Size | H1   | H2   | H3   |
| ----------- | --------- | ---- | ---- | ---- |
| < 1366px    | 11px      | 28px | 20px | 16px |
| 1366-1920px | 12px      | 32px | 24px | 18px |
| > 1920px    | 12px      | 36px | 28px | 20px |

### Panel Minimum Widths

| Breakpoint  | Min Width | Recommended |
| ----------- | --------- | ----------- |
| < 1366px    | 320px     | 100%        |
| 1366-1920px | 400px     | 50%         |
| > 1920px    | 400px     | 25-50%      |

## Mobile Considerations (Future)

Phase 1 is desktop-only. Phase 2+ mobile support would include:

### Touch Targets

- Minimum 44×44px (WCAG recommendation)
- 8px padding around targets
- Tap-friendly spacing

### Gestures

- Swipe left/right: Switch panels
- Swipe up/down: Scroll content
- Long-press: Context menu
- Pinch: Zoom content

### Tablet Layout (11-13")

```
Single column with persistent sidebar
├─ Activity sidebar (48px)
├─ Main content (full)
└─ Resizable right sidebar
```

## Orientation Adaptation (Future)

### Portrait (Phone/Tablet)

- Stacked layout
- Full-width panels
- Sidebar collapses

### Landscape (Phone/Tablet)

- Side-by-side panels
- Narrower sidebars
- More content visible

## Zoom & Scaling

### CSS Zoom Levels

```
80% - Compact view (more visible)
90% - Condensed view
100% - Default
110% - Spacious view
125% - Large text
150% - Extra large
```

**Access**: Ctrl+[+/-/0]

### Text-only Zoom

Separate from viewport zoom, scales only text:

- Doesn't reflow layout
- Useful for readability
- Settings → Appearance → Text Zoom

## Dynamic Hiding

### Auto-Collapse Rules

When screen width < threshold:

1. Info sidebar collapses first (toggleable)
2. Secondary panels become tabs
3. Menu bar becomes hamburger
4. Spacing reduces to 8px
5. Component gaps reduce

### User Overrides

Users can manually:

- Force sidebars hidden/shown (Ctrl+Shift+P/E)
- Choose single/multi-column layout
- Adjust panel widths manually

## Performance at Small Sizes

### Optimization for < 1366px

- Reduce rendered elements (hidden panels don't render)
- Lazy load secondary content
- Simplify animations
- Reduce imagery size

### Memory Consideration

Small screens often on lower-power devices:

- Virtual scrolling in lists
- Cache limits (20MB max)
- Disable effects if low memory detected

## Responsive Design Testing

### Test Scenarios

1. **1024×768**: Minimum supported
2. **1366×768**: Common laptop
3. **1920×1080**: Standard desktop
4. **2560×1440**: Large monitor
5. **3840×2160**: 4K display

### Testing Checklist

- [ ] All text readable without horizontal scroll
- [ ] All buttons clickable (44px minimum)
- [ ] No content cutoff at screen edge
- [ ] Sidebars collapse appropriately
- [ ] Tabs functional when panels hidden
- [ ] Performance acceptable (60 FPS)

## Accessibility Responsiveness

- **Text Sizing**: Works with browser zoom and OS text scaling
- **High Contrast**: Applied at all breakpoints
- **Keyboard Navigation**: Functional at all sizes
- **Focus Visible**: Clear at all zoom levels

---

**Responsive Design Specification Version**: 1.0  
**Last Updated**: August 2, 2026
