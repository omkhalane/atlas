# Theming & Customization Specification

Color themes, font customization, and personalization options for Atlas.

## Built-In Themes

### Dark Theme (Default)

```
Background:  #0D1117 (Darkest)
Surface:     #161B22 (Dark)
Elevated:    #21262D (Darker)
Border:      #30363D (Grey)
Text:        #E0E0E0 (Light)
Accent:      #00A8E8 (Electric Blue)
Success:     #2EA043 (Green)
Warning:     #D29922 (Amber)
Error:       #DA3633 (Red)
```

Used by default for:

- Primary UI background
- Command palette
- Chat interface
- File browser

### Light Theme

```
Background:  #FFFFFF (White)
Surface:     #F6F8FA (Lightest)
Elevated:    #EAEEF2 (Light)
Border:      #D0D7DE (Grey)
Text:        #24292F (Dark)
Accent:      #0969DA (Blue)
Success:     #1A7F37 (Green)
Warning:     #9E6A03 (Amber)
Error:       #CF222E (Red)
```

Available as option for:

- Users preferring light backgrounds
- Accessibility needs
- Bright ambient lighting

### High Contrast Theme

```
Background:  #000000 (Black)
Surface:     #1A1A1A (Very Dark)
Elevated:    #2A2A2A (Dark)
Border:      #4A4A4A (Medium)
Text:        #FFFFFF (White)
Accent:      #00D9FF (Bright Cyan)
Success:     #00FF00 (Bright Green)
Warning:     #FFFF00 (Bright Yellow)
Error:       #FF0000 (Bright Red)
```

For users with:

- Low vision
- Color sensitivity
- High contrast needs
- Dyslexia (better readability)

### Terminal Theme (Dark)

```
Background:  #0D1117
Text:        #E0E0E0
Command:     #00A8E8 (Input)
Output:      #E0E0E0
Error:       #DA3633 (Errors in red)
Success:     #2EA043 (Success in green)
Warning:     #D29922 (Warnings in amber)
Info:        #79C0FF (Info in blue)
```

Used in:

- Terminal panel
- Console logs
- Debug output

## Theme Switching

### Settings Location

```
Settings → Appearance → Theme
├─ Dark (Default)
├─ Light
└─ High Contrast
```

### Keyboard Shortcut

```
Ctrl+Shift+T    Cycle through themes
Ctrl+Shift+D    Toggle dark/light
```

### System Preference Integration

```
Settings → Appearance → Follow System
☑ Use system dark/light preference
  Auto-switches when OS preference changes
```

### Live Preview

- Theme changes apply immediately
- No refresh required
- Smooth transition (200ms fade)

## Custom Color Customization

### User Themes (Phase 2+)

Users can create custom themes:

```
Settings → Appearance → Themes → Create New
```

Customizable elements:

- All accent colors
- Background/surface colors
- Text/border colors
- All semantic colors (success, error, etc.)

### Theme Export/Import

```
[Export Theme...] Downloads JSON file
[Import Theme...] Loads JSON file
```

Format:

```json
{
  "name": "My Custom Theme",
  "type": "dark",
  "colors": {
    "background": "#0D1117",
    "surface": "#161B22",
    "text": "#E0E0E0",
    "accent": "#FF6B6B",
    "success": "#51CF66",
    "warning": "#FFD43B",
    "error": "#FF6B6B"
  }
}
```

### Theme Sharing

- Export and share themes
- Community themes repository (Phase 3+)
- One-click installation

## Font Customization

### Font Selection

```
Settings → Appearance → Font
├─ UI Font
│  ├─ Inter (Default)
│  ├─ Helvetica
│  ├─ Arial
│  └─ System
├─ Monospace Font
│  ├─ JetBrains Mono (Default)
│  ├─ Consolas
│  ├─ Monaco
│  └─ Liberation Mono
└─ Editor Font
   ├─ JetBrains Mono (Default)
   ├─ Fira Code
   ├─ Inconsolata
   └─ Source Code Pro
```

### Font Size Scaling

```
Settings → Appearance → Text Size
├─ 90% (Compact)
├─ 100% (Default)
├─ 110% (Spacious)
├─ 125% (Large)
└─ 150% (Extra Large)
```

Affects:

- UI text sizes
- Proportional scaling
- Maintains layout

### Font Weight Options

```
UI Font Weight: Normal / Bold
Code Font Weight: Normal / Bold
Affects: Readability preference
```

## CSS Variables

### Root Theme Variables

```css
:root {
  --color-bg: #0d1117;
  --color-surface: #161b22;
  --color-elevated: #21262d;
  --color-border: #30363d;

  --color-text-primary: #e0e0e0;
  --color-text-secondary: #8b949e;
  --color-text-disabled: #484f58;

  --color-accent: #00a8e8;
  --color-success: #2ea043;
  --color-warning: #d29922;
  --color-error: #da3633;

  --font-ui: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;

  --font-size-base: 12px;
  --font-size-sm: 10px;
  --font-size-lg: 14px;
  --font-size-xl: 16px;
}
```

### Usage in Components

```css
.button {
  background-color: var(--color-accent);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  font-family: var(--font-ui);
  font-size: var(--font-size-base);
}
```

## Accessibility Considerations

### High Contrast Detection

```javascript
const prefersContrast = window.matchMedia("(prefers-contrast: more)").matches;

if (prefersContrast) {
  document.body.classList.add("high-contrast");
}
```

### Reduced Motion Detection

```javascript
const prefersReduced = window.matchMedia(
  "(prefers-reduced-motion: reduce)",
).matches;

if (prefersReduced) {
  // Disable animations
}
```

### Dark Mode Detection

```javascript
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

if (prefersDark && !userHasChoice) {
  applyDarkTheme();
}
```

## Theme Persistence

### Storage

```javascript
// Save user's theme choice
localStorage.setItem("atlas-theme", "light");
localStorage.setItem("atlas-font-size", "110");

// Load on startup
const theme = localStorage.getItem("atlas-theme") || "dark";
```

### Sync Across Windows

- Theme persisted to user profile
- Syncs when logging into different machine
- Cloud sync (Phase 3+)

## Plugin Theme Support

### Plugin Colors (Phase 2+)

Plugins can define theme colors:

```javascript
// plugin.json
{
  "theme": {
    "colors": {
      "pluginBg": "#1A1A2E",
      "pluginText": "#16F4D0"
    }
  }
}
```

### Theme Fallbacks

If plugin color not defined, use defaults:

- Accent → Use app accent
- Background → Use surface color
- Text → Use primary text color

## Browser Extension Themes (Phase 3+)

### Browser Matching

- Firefox theme: Match app theme
- Chrome theme: Match app theme
- Browser extension colors sync with app

## Accessibility Checklist

- [ ] All text readable in all themes (7:1 minimum)
- [ ] High contrast mode has distinct colors
- [ ] Color not sole indicator (use icons/text)
- [ ] Custom colors can't fail contrast
- [ ] Motion respects `prefers-reduced-motion`
- [ ] Font resizing works (no overlaps)
- [ ] All themes tested with screen reader

---

**Theming & Customization Specification Version**: 1.0  
**Last Updated**: August 2, 2026

Themes must meet WCAG AA contrast requirements in all configurations.
