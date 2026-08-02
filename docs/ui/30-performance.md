# Performance Optimization Specification

UI performance targets and optimization strategies for smooth 60 FPS experience.

## Performance Targets

### Frame Rate

- **Target**: 60 FPS (16.67ms per frame)
- **Minimum**: 30 FPS (acceptable, not ideal)
- **Unacceptable**: <30 FPS

### Interaction Response

- **Button Click**: <100ms feedback
- **Scroll**: Smooth 60 FPS
- **Keyboard Input**: <50ms character render
- **Search**: <100ms first results
- **File Open**: <500ms for small files

### Application Metrics

- **Startup Time**: <3 seconds full load
- **Panel Switch**: <200ms transition
- **Memory Usage**: <500MB baseline, <1GB with heavy content
- **CPU**: <10% idle, <50% full load

## Rendering Optimization

### Virtualization

```
Visible Items:    [Rendered, updated every frame]
Off-Screen Items: [Not rendered, in DOM but display:none]
Far Off-Screen:   [Not in DOM, loaded on demand]
```

Used in:

- Long lists (10,000+ items)
- Terminal output
- Chat history
- File trees

### CSS Containment

```css
.panel {
  contain: layout style paint;
  /* Limits repaint scope to this container */
}
```

Applied to:

- Individual panels
- List items
- Chat messages
- Cards

### Layer Promotion

```css
.frequently-animated {
  transform: translateZ(0);
  /* Creates GPU layer, prevents repaints */
  will-change: transform;
}
```

Used for:

- Scrolling containers
- Animated sidebars
- Modal animations

## Memory Management

### Cache Limits

| Resource      | Limit      | Strategy              |
| ------------- | ---------- | --------------------- |
| Browser Cache | 256 MB     | LRU eviction          |
| Image Cache   | 50 MB      | Compress large images |
| Scroll Buffer | 10K lines  | Virtual scroll        |
| History       | 1000 items | LRU eviction          |

### Cleanup on Close

- Remove DOM nodes
- Cancel pending requests
- Clear timers
- Unload large files
- Shrink cache

### Memory Monitoring

```
Monitor: window.performance.memory
If usage > 1GB: Alert and offer cleanup
If usage > 1.5GB: Auto-cleanup aggressive
```

## Bundle Optimization

### Code Splitting

```javascript
// Load only what's needed
import Chat from "./panels/Chat"; // Lazy-loaded
import Files from "./panels/Files"; // Lazy-loaded
```

### Lazy Loading

- Panels loaded on first use
- Plugins loaded on demand
- Heavy libraries deferred
- Network requests batched

### Asset Optimization

- Images: Compressed, modern formats (WebP)
- Fonts: Only used weights/styles
- CSS: Purge unused rules
- JavaScript: Minified and tree-shaken

## Paint & Reflow Optimization

### Avoid Layout Thrashing

```javascript
// Bad: Multiple reflows
element.style.width = "100px";
let width = element.offsetWidth; // Reflow 1
element.style.height = "100px";
let height = element.offsetHeight; // Reflow 2

// Good: Batch reads then writes
let width = element.offsetWidth; // Read
let height = element.offsetHeight; // Read
element.style.width = "100px"; // Write
element.style.height = "100px"; // Write
```

### CSS will-change

```css
.animated {
  will-change: transform;
  /* Only for frequently-changed properties */
  /* Remove after animation ends */
}
```

Used sparingly for:

- Active panels during transition
- Scrolling containers
- Animations

## Keyboard Input Optimization

### Debounce Search Input

```javascript
// Search updates debounced 100ms
const debouncedSearch = debounce(search, 100);
searchInput.addEventListener("input", debouncedSearch);
```

### Throttle Scroll Events

```javascript
// Scroll events throttled to 16ms (60 FPS)
const throttledScroll = throttle(onScroll, 16);
window.addEventListener("scroll", throttledScroll);
```

### Input Method Composition

Handle IME (Input Method Editor) properly:

```javascript
// Don't filter until composition ends
input.addEventListener("compositionend", () => {
  // Now filter/search
});
```

## Network Optimization

### Request Batching

- Combine multiple API calls
- Debounce rapid requests
- Cancel redundant requests

### Caching Strategy

```
GET /api/data
├─ Cache for 5 minutes
├─ Reuse if within cache time
└─ Refresh on focus (soft update)
```

### Compression

- All responses gzipped
- Images WebP format
- Assets minified

## Scrolling Performance

### Passive Event Listeners

```javascript
// Passive listeners don't block scroll
element.addEventListener("scroll", onScroll, { passive: true });
```

### Overflow Behavior

```css
.scrollable {
  overflow: auto;
  -webkit-overflow-scrolling: touch; /* Smooth on iOS */
  contain: layout style paint; /* Limit repaint scope */
}
```

## Animation Performance

### GPU Acceleration

```css
/* Use transforms instead of position */
.animated {
  transform: translateX(100px); /* GPU-accelerated */
  /* NOT: left: 100px; / * CPU-intensive */
}
```

### Duration Limits

- Quick interactions: 100-150ms
- Panel transitions: 200-250ms
- Loading animations: Infinite (user can wait)
- No animation: <50ms (too quick to perceive)

### Disable on Low Performance

```javascript
// Detect if device is struggling
if (navigator.deviceMemory < 4) {
  // Disable animations
  document.body.classList.add("no-animation");
}
```

## Monitoring & Profiling

### Performance Metrics

```javascript
// Mark performance
performance.mark("operation-start");
// ... do work
performance.mark("operation-end");
performance.measure("operation", "operation-start", "operation-end");

// Analyze
const measure = performance.getEntriesByName("operation")[0];
console.log(`Duration: ${measure.duration}ms`);
```

### Chrome DevTools Profiling

- Performance tab: Record frame-by-frame
- Identify jank (frames >16ms)
- Locate expensive operations
- Optimize bottlenecks

### Real User Monitoring (Phase 2+)

- Collect performance metrics from users
- Identify real-world bottlenecks
- Alert on performance regressions

## Progressive Enhancement

### Graceful Degradation

- Feature detection over browser detection
- Enhanced experience if possible
- Core functionality always works
- Heavy features optional

### Fallback Rendering

```javascript
// Render text while images load
img.onerror = () => {
  // Show text fallback
  showTextInsteadOfImage();
};
```

## Device Considerations

### Low-End Devices (Phase 2+)

- Baseline performance on 2 GB RAM
- Disable some effects
- Limit cache
- Reduce imagery quality

### High-End Devices

- Enable all effects
- Larger caches
- More aggressive prefetching
- Multiple split views

## Testing Performance

### Performance Audits

```bash
# Lighthouse audit
npm run audit:lighthouse

# Performance tests
npm run test:performance
```

### Target Metrics

- Largest Contentful Paint (LCP): <2.5s
- First Input Delay (FID): <100ms
- Cumulative Layout Shift (CLS): <0.1
- Time to Interactive (TTI): <3.5s

### Continuous Monitoring

- Test on CI/CD pipeline
- Alert on regressions (>5% slower)
- Track over time
- Compare across versions

---

**Performance Specification Version**: 1.0  
**Last Updated**: August 2, 2026

Every feature must meet performance targets or include justification for exception.
