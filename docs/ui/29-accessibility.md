# Accessibility (a11y) Specification

Complete accessibility guidelines ensuring Atlas is usable by everyone, including people with disabilities.

## WCAG 2.1 Compliance

Atlas targets **WCAG 2.1 Level AA** minimum (some AAA).

### Compliance Checklist

#### Perceivable

- ✓ Text contrast ≥4.5:1 (AA) for body, ≥7:1 (AAA) preferred
- ✓ All non-text content has text alternatives
- ✓ Color not sole means of conveying information
- ✓ Content resizable (browser zoom supported)
- ✓ Audio/video controls available

#### Operable

- ✓ All functionality keyboard accessible
- ✓ No keyboard traps (except dialogs)
- ✓ No flashing content > 3 times/second
- ✓ Consistent navigation patterns
- ✓ Meaningful link/button text

#### Understandable

- ✓ Text readable (language clear, jargon minimized)
- ✓ Predictable navigation and interactions
- ✓ Error messages clear and specific
- ✓ Help available throughout
- ✓ Labels on all form inputs

#### Robust

- ✓ Valid HTML/CSS/JavaScript
- ✓ Compatible with assistive technology
- ✓ ARIA used appropriately
- ✓ No reliance on unsupported features

## Screen Reader Support

### Tested Readers

- NVDA (Linux, free)
- JAWS (Windows, commercial)
- VoiceOver (macOS, free)

### Requirements

**Semantic HTML**

```html
<!-- Good -->
<button>Save File</button>
<nav>Navigation</nav>
<header>Header</header>

<!-- Bad -->
<div class="button">Save File</div>
<div class="nav">Navigation</div>
```

**ARIA Labels**

```html
<!-- Icon button needs label -->
<button aria-label="Save current file">
  <svg class="icon-save"></svg>
</button>

<!-- Form input needs label -->
<label for="username">Username</label>
<input id="username" type="text" />
```

**Headings Hierarchy**

```html
<h1>Main Title</h1>
<!-- Only one H1 per page -->
<h2>Section</h2>
<h3>Subsection</h3>
<!-- Never skip levels: no H1 → H3 -->
```

**Lists**

```html
<!-- Use semantic lists -->
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
</ul>

<ol>
  <li>First</li>
  <li>Second</li>
</ol>
```

## Keyboard Navigation

### Keyboard Traps Prevention

- Users can always exit with Tab or Escape
- No focus locked except in dialogs
- Dialogs trap focus internally (expected)

### Tab Order

- Follows logical reading order
- Left-to-right, top-to-bottom
- Skip invisible elements
- Use `tabindex` minimally (prefer semantic HTML)

### Keyboard Shortcuts

```
Tab             Move to next focusable element
Shift+Tab       Move to previous focusable element
Enter           Activate buttons, follow links
Space           Toggle checkboxes, buttons
Arrow Keys      Navigate within components (lists, menus)
Escape          Close dialogs, menus, cancel operations
```

All shortcuts shown in Help (Ctrl+?)

## Focus Indicators

### Visible Focus Ring

- **Color**: #00A8E8 (electric blue)
- **Width**: 2px
- **Style**: Solid outline
- **Offset**: 2px outside element
- **Always Visible**: Never hidden

```css
:focus {
  outline: 2px solid #00a8e8;
  outline-offset: 2px;
}

/* High contrast mode */
@media (prefers-contrast: more) {
  :focus {
    outline-width: 3px;
  }
}
```

### Focus Indicators Not Hidden

```css
/* Bad - removes focus visibility */
:focus {
  outline: none;
}

/* Good - maintains visibility */
:focus {
  outline: 2px solid #00a8e8;
}
```

## Color & Contrast

### Minimum Contrast Ratios

- **Body Text**: 7:1 (WCAG AAA)
- **Large Text**: 4.5:1 (WCAG AA)
- **UI Components**: 3:1 (WCAG A)
- **Disabled Text**: 3:1 (exception)

### Testing Tools

- Chrome DevTools: Check contrast ratio
- WebAIM Contrast Checker
- WAVE browser extension
- Color Blindness Simulator

### Color Not Sole Indicator

```html
<!-- Bad: Color alone indicates status -->
<div class="green">Success</div>

<!-- Good: Color + Icon + Text -->
<div class="success">
  <span class="icon-success">✓</span>
  Success
</div>
```

## Text & Font

### Readable Fonts

- **Primary**: Inter (sans-serif, readable)
- **Monospace**: JetBrains Mono (code)
- **Minimum Size**: 12px (body text)
- **Line Height**: 1.4+ (readable spacing)
- **Line Length**: 50-80 characters (optimal)

### Text Formatting

```css
/* Good */
font-weight: 400; /* Regular */
font-weight: 600; /* Semibold for emphasis */
font-style: normal; /* Not italic */
text-decoration: underline; /* Links */
text-transform: none; /* Not all-caps */

/* Bad */
font-weight: 300; /* Too thin */
font-weight: 700; /* Too bold for body */
font-style: italic; /* Hard to read */
text-transform: uppercase; /* Hard to read */
```

## Form Accessibility

### Input Labels

```html
<!-- Good: Explicit label -->
<label for="email">Email Address</label>
<input id="email" type="email" />

<!-- Good: Aria label (when no visible label) -->
<input aria-label="Search" type="search" />

<!-- Bad: No label -->
<input type="email" />
```

### Error Messages

```html
<!-- Good: Clear error with fix -->
<div role="alert" aria-live="polite">
  ❌ Email must be valid (e.g., user@example.com)
</div>

<!-- Bad: Vague error -->
<div style="color: red;">Invalid input</div>
```

### Help Text

```html
<!-- Good -->
<label for="password">Password</label>
<input id="password" type="password" aria-describedby="pwd-hint" />
<small id="pwd-hint">
  At least 8 characters, must include uppercase letter
</small>

<!-- Bad -->
<input type="password" placeholder="password123" />
```

## Motion & Animation

### Respects `prefers-reduced-motion`

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}
```

### Appropriate Animations

- Entrance/exit animations: 100-200ms
- No auto-playing animations
- No flashing/strobing (>3x/second)
- Pause/stop controls for auto-play

## Responsive Text

### Scaling Support

- Browser zoom: 200% minimum tested
- Font size scaling: Works with OS settings
- High contrast mode: Full support
- Text spacing: Adjustable

```css
/* Supports zoom and scaling */
body {
  font-size: 1rem;
} /* = 16px default */
button {
  font-size: 0.75rem;
} /* = 12px, scales with base */
```

## Assistive Technology Support

### Screen Readers

- All content accessible without visual
- ARIA landmarks: `<nav>`, `<main>`, `<aside>`
- ARIA live regions: For dynamic content
- Meaningful alt text for images

### Voice Control

- All buttons/links reachable with voice
- Clear, unique labels for commands
- No conflicting voice commands

### Magnification

- Content remains functional at 200% zoom
- No horizontal scroll at 320px width (mobile)
- Sufficient spacing between clickables

### Switch Control

- All features accessible via switch/eye-tracking
- Scan mode compatible
- No time-based interactions

## Testing & Validation

### Automated Testing

```bash
npm install axe-core
npm run test:a11y
```

Runs axe accessibility checks, reports issues.

### Manual Testing Checklist

- [ ] Keyboard navigation: Tab through entire UI
- [ ] Screen reader: Test with NVDA
- [ ] High contrast: Enable OS high contrast
- [ ] Zoom: Test at 150%, 200% zoom
- [ ] Color blindness: Use simulator for deuteranopia, protanopia, tritanopia
- [ ] Motion: Disable animations, test functionality
- [ ] Focus: Tab to each element, verify visible
- [ ] Mobile: Test on small screen (320px)

### Regular Audits

- Quarterly accessibility audit
- External audit annually
- User feedback from community

## Accessibility Documentation

### For Users

- Help system includes accessibility options
- Settings → Accessibility panel
- Keyboard shortcuts reference (Ctrl+?)
- High contrast theme available

### For Developers

- ARIA guidelines in code comments
- Component accessibility checklist
- Testing procedures documented
- Common mistakes guide

## Known Limitations

### Current Limitations

- Phase 1 is desktop-only (mobile a11y Phase 2+)
- Some plugins may not be accessible (developer responsibility)
- Video content requires captions (team-provided)

### Future Improvements

- Mobile touch accessibility (Phase 2)
- Screen reader optimization (ongoing)
- More language support (Phase 3+)

---

**Accessibility Specification Version**: 1.0  
**Last Updated**: August 2, 2026

WCAG 2.1 Level AA compliance is mandatory for all releases.
