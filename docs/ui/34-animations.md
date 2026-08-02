# Animation & Micro-interactions Specification

Smooth animations and small interactions that enhance usability.

## Animation Principles

### Purposeful Motion

Every animation must have a reason:

- **Feedback**: Confirm user action
- **Navigation**: Show content change
- **Attention**: Highlight important info
- **Fluidity**: Smooth transitions

### Timing Guidelines

```
Fast:       100ms  (quick feedback)
Moderate:   200ms  (standard transitions)
Slow:       300ms+ (loading, emphasis)
```

## Easing Functions

### Common Easing Curves

```
ease-out-cubic:   Quick start, gentle end
                  (user actions, entering)

ease-in-cubic:    Gentle start, quick end
                  (exiting, disappearing)

ease-in-out-cubic:Balanced motion
                  (panel resizing, repositioning)

linear:           Constant speed
                  (progress bars, continuous)
```

### CSS Implementation

```css
/* Quick user feedback */
.button {
  transition: background-color 100ms ease-out;
}

/* Panel transition */
.panel {
  transition: transform 200ms ease-in-out;
}

/* Loading indicator */
.spinner {
  animation: spin 1s linear infinite;
}
```

## Component Animations

### Button Animations

```
Hover:     Subtle background color shift (100ms)
Active:    Scale down 2% (50ms)
Click:     Ripple effect (200ms)
Disabled:  No animation, appears static
```

### Panel Slide Animations

```
Entering:  Slide in from edge (200ms) + fade in
Exiting:   Slide out to edge (200ms) + fade out
Repositioning: Smooth transform transition (150ms)
```

### Dialog Animations

```
Appear:    Fade in (100ms) at full scale
Disappear: Fade out (100ms)
Focus:     Subtle pulse when important (optional)
```

### List Item Animations

```
Appear:    Fade + slide in (150ms)
Reorder:   Smooth transition to new position (200ms)
Delete:    Fade out while sliding out (150ms)
```

### Loading State

```
Spinner:   Continuous rotation (1s per revolution)
Skeleton:  Subtle pulse/shimmer (1.5s cycle)
Progress:  Smooth bar fill (100ms per increment)
```

## Micro-interactions

### Hover States

```
Button:       Background color shift, cursor change
Link:         Color shift, underline appears
Card:         Subtle elevation increase, shadow
Input:        Border color highlight, slight scale
```

### Focus States

```
All elements: 2px blue outline, 2px offset
Active:       Slightly darker background
Selected:     Checkmark or highlight
```

### Drag & Drop

```
Hover Target: Highlight appears (instant)
Dragging:     Element follows cursor (smooth)
Drop Zone:    Visual feedback (instant)
Drop:         Element animates to final position (200ms)
```

### Notification Toast

```
Slide in:    From bottom-right corner (200ms)
Display:     Visible for 4 seconds
Slide out:   Exit to bottom-right (200ms)
Dismiss:     Click removes immediately
```

### Context Menu

```
Appear:      Instant, no fade (responsive feel)
Item Hover:  Background highlight (50ms)
Item Click:  Quick fade out (100ms)
```

## Scroll Animations

### Scroll Behavior

```css
html {
  scroll-behavior: smooth;
  /* Smooth scrolling to anchors */
}

.scrollable {
  -webkit-overflow-scrolling: touch;
  /* Momentum scrolling on iOS (Phase 2+) */
}
```

### Scroll Indicators

```
Scrollbar:  Fade in on hover, fade out when idle
Position:   Shows current position in content
Direction:  Indicates more content above/below
```

### Lazy Loading

```
Images appear: Fade in when loaded (200ms)
Content appears: Slide in from bottom (300ms)
```

## Transitions

### Panel Transitions

```
Switching Panels: Cross-fade (200ms)
├─ Panel A fade out (200ms)
└─ Panel B fade in (200ms)

Hiding Panel: Slide out (200ms) + fade out

Showing Panel: Slide in (200ms) + fade in
```

### Size Changes

```
Resize Handle Drag: Smooth width/height (real-time)
Sidebar Toggle: Collapse (200ms) / expand (200ms)
Responsive Breakpoint: Reflow (instant), smooth (no animation)
```

### Color Transitions

```
Theme Switch: All colors crossfade (200ms)
Hover States: Background color shift (100ms)
Error State: Color highlight (100ms)
```

## Accessibility & Motion

### Respects User Preference

```javascript
const prefersReduced = window.matchMedia(
  "(prefers-reduced-motion: reduce)",
).matches;

if (prefersReduced) {
  // Disable animations
  // Instant state changes instead
  // No delays or transitions
}
```

### CSS Implementation

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Safe Animations

- No flashing (>3 times/second)
- No auto-playing animations
- Can always pause/stop
- Pausable controls for media

## Performance Animations

### GPU-Accelerated Properties

```css
/* Use these for animation (GPU) */
transform: translateX(100px);
transform: scale(1.2);
transform: rotate(45deg);
opacity: 0.5;

/* Avoid these (CPU-intensive) */
left: 100px;
width: 500px;
height: 300px;
background-color: blue;
```

### Animation Optimization

```javascript
// Use will-change sparingly
.animating {
  will-change: transform;
  /* Remove after animation completes */
}
```

### Reduced Motion Devices

Detect low-end devices:

```javascript
if (navigator.deviceMemory < 4 || navigator.hardwareConcurrency < 4) {
  // Disable animations
  disableAnimations();
}
```

## Animation Duration Guidelines

| Action           | Duration  |
| ---------------- | --------- |
| Hover effect     | 100ms     |
| Button press     | 50-100ms  |
| Panel transition | 200-250ms |
| Dialog appear    | 100ms     |
| Toast slide      | 200ms     |
| Scroll to        | 300-500ms |
| Loading spinner  | 1000ms    |

## Advanced Animations

### Spring Physics (Phase 2+)

```javascript
// Bouncy, natural feel
spring({
  damping: 0.7,
  tension: 300,
  mass: 1,
});
```

### Gesture Animations (Phase 2+)

```
Swipe left:  Panel slides out left (200ms)
Swipe right: Panel slides in from right (200ms)
Pinch zoom:  Smooth scale transformation
```

### Parallax Scrolling (Future)

Background moves slower than foreground for depth.

## Testing Animations

### Visual Testing

- Record animations
- Compare across browsers
- Check jank (frame drops)
- Verify timing

### Performance Testing

- Frame rate during animation (60 FPS target)
- CPU/GPU usage
- Battery impact (mobile)

### Accessibility Testing

- Reduced motion respected
- No seizure risk
- Screen readers handle animated changes

---

**Animation & Micro-interactions Specification Version**: 1.0  
**Last Updated**: August 2, 2026

All animations must respect `prefers-reduced-motion` setting.
