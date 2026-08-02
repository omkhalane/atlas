# Typography Specification

## Font System

### Primary Font: Inter

**Why Inter?**

- Neutral, professional sans-serif
- Excellent screen rendering
- Open source (free license)
- Designed for UI (not print)
- Available on all platforms

**Font Family Stack**:

```css
font-family:
  "Inter",
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  "Helvetica Neue",
  sans-serif;
```

**Fallback Chain**:

1. Inter (primary, loaded from system or font files)
2. System fonts (platform native)
3. Generic sans-serif (ultimate fallback)

### Code Font: JetBrains Mono

**Why JetBrains Mono?**

- Monospace for code alignment
- Readable at all sizes
- Clear character differentiation
- OpenType features for ligatures
- Free license

**Font Family Stack**:

```css
font-family: "JetBrains Mono", "Courier New", monospace;
```

**Usage**: Code blocks, terminal, file contents, command output

---

## Font Scale

### Sizing Scale (Multiples of 2px)

```
10px  ← Tiny (captions, timestamps)
11px  ← Small (hints, metadata)
12px  ← Base (standard body text, labels)
14px  ← Regular (subheadings, emphasis)
16px  ← Large (section headings)
18px  ← Extra Large (major headings)
24px  ← 2X Large (page titles)
32px  ← 3X Large (main titles)
```

### Font Weight Scale

```
400  ← Regular (most text)
500  ← Medium (labels, emphasis)
600  ← Semibold (headings)
700  ← Bold (strong headings, rare)
```

**Never use 300 or 800+** (limited readability on dark backgrounds)

---

## Typographic Hierarchy

### H1 - Main Page Title

- **Size**: 32px
- **Weight**: 600
- **Line Height**: 1.2 (38.4px)
- **Letter Spacing**: -0.5px (tighter)
- **Color**: #E0E0E0
- **Usage**: Main conversation title, agent name heading
- **Margin Bottom**: 12px

### H2 - Section Title

- **Size**: 24px
- **Weight**: 600
- **Line Height**: 1.33 (32px)
- **Letter Spacing**: 0px
- **Color**: #E0E0E0
- **Usage**: Memory section headings, task titles
- **Margin Top**: 24px
- **Margin Bottom**: 12px

### H3 - Subsection Title

- **Size**: 18px
- **Weight**: 600
- **Line Height**: 1.33 (24px)
- **Letter Spacing**: 0px
- **Color**: #E0E0E0
- **Usage**: Card titles, file names
- **Margin Top**: 16px
- **Margin Bottom**: 8px

### H4 - Label / Mini Heading

- **Size**: 14px
- **Weight**: 600
- **Line Height**: 1.43 (20px)
- **Letter Spacing**: 0px
- **Color**: #A0A0A0
- **Usage**: Input labels, button text, metadata headings
- **Margin Top**: 12px
- **Margin Bottom**: 4px

### Body Text (P)

- **Size**: 12px
- **Weight**: 400
- **Line Height**: 1.5 (18px)
- **Letter Spacing**: 0px
- **Color**: #E0E0E0
- **Usage**: Main paragraph text, message content
- **Margin Bottom**: 12px (between paragraphs)

### Small Text

- **Size**: 11px
- **Weight**: 400
- **Line Height**: 1.45 (16px)
- **Letter Spacing**: 0px
- **Color**: #7A8BA0
- **Usage**: Hints, secondary labels, metadata
- **No margin** (inline, attached to parent)

### Tiny Text / Captions

- **Size**: 10px
- **Weight**: 400
- **Line Height**: 1.4 (14px)
- **Letter Spacing**: 0.5px
- **Color**: #7A8BA0
- **Usage**: Timestamps, copyright, minor notes
- **Rare**: Use sparingly, readability risk

---

## Code Block Typography

### Inline Code

```
Text with `inline code` example.
```

- **Font**: JetBrains Mono 12px
- **Weight**: 400
- **Background**: #1A1F3A
- **Padding**: 2px 4px (compact)
- **Border Radius**: 2px
- **Color**: #00A8E8 (accent color)
- **No Line Height Change** (inline, inherits)

### Code Block

```javascript
function helloWorld() {
  return "Hello, World!";
}
```

**Container**:

- **Font**: JetBrains Mono 11px
- **Weight**: 400
- **Line Height**: 1.6 (code needs extra space)
- **Color**: #E0E0E0
- **Background**: #2A3F5A or #1A1F3A
- **Padding**: 12px
- **Border Radius**: 4px
- **Max Width**: Scroll if >80 characters (industry standard)

**Line Numbers**:

- **Font**: JetBrains Mono 11px
- **Color**: #7A8BA0
- **Width**: 32px (right-aligned)
- **Right Padding**: 12px
- **User Select**: None (don't select line numbers)

**Syntax Highlighting** (Language-specific):

- Keywords: #F59E0B (amber)
- Strings: #10B981 (green)
- Numbers: #06B6D4 (cyan)
- Comments: #7A8BA0 (gray)
- Functions: #00A8E8 (blue)

---

## Text Styles

### Emphasis

**Bold Text**: `<strong>` or `**text**`

- Increases weight to 600
- Use for key terms
- Rare—don't overuse

_Italic Text_: `<em>` or `*text*`

- Use font-style: italic
- For emphasis, titles, not variables
- Rare—avoid (hard to read monospace italic)

~~Strikethrough~~: `<s>` or `~~text~~`

- For completed items, deprecated code
- Color: #7A8BA0 with line-through
- Rare usage

### Text Transform

- **UPPERCASE**: Use sparingly
  - Button labels rarely
  - Section headers sometimes
  - Letter spacing +0.5px when used
- **lowercase**: Avoid (readability risk)
- **Sentence case**: Default for sentences
- **Title Case**: Headings, proper nouns

### Text Decoration

- **Underline**: Links only (not text emphasis)
- **Overline**: Avoid (readability)
- **Line-through**: Completed, deprecated only

---

## Link Typography

### Default Link

- **Color**: #00A8E8 (accent)
- **Weight**: 400 (inherit, don't bold)
- **Decoration**: Underline (1px, #00A8E8)
- **Cursor**: pointer

### Hover Link

- **Color**: #00BFFF (light accent)
- **Decoration**: Underline (stays)
- **Cursor**: pointer
- **Background**: Optional subtle highlight

### Active/Visited Link

- **Color**: #00A8E8 (same as default)
- **Decoration**: Underline stays
- **No color change** for visited (security consideration)

### Disabled Link

- **Color**: #606060
- **Opacity**: 50%
- **Cursor**: not-allowed
- **No underline**

### Link in Code

- **Color**: #00A8E8 (same, for consistency)
- **Underline**: Yes
- **Font**: Monospace continues

---

## Lists and Tables

### Unordered List

```
• Item 1
• Item 2
• Nested item
```

- **Bullet**: • (circle)
- **Color**: Inherit text color
- **Indent**: 16px per level
- **Line Height**: Body text (1.5)
- **After List**: 12px margin

### Ordered List

```
1. Item 1
2. Item 2
   a. Sub-item
```

- **Numbers**: 1. 2. 3. etc
- **Font**: Monospace (easier to read)
- **Indent**: 16px per level
- **After List**: 12px margin

### Blockquote

```
> Quoted text stands out visually
```

- **Border Left**: 2px #00A8E8
- **Padding Left**: 12px
- **Opacity**: 70%
- **Font Style**: Italic (optional)
- **Margin**: 12px top/bottom

### Table

```
| Header 1 | Header 2 |
|----------|----------|
| Cell     | Cell     |
```

- **Header**: 14px, weight 600, background #1A1F3A
- **Cells**: 12px, inherit color
- **Padding**: 8px
- **Borders**: 1px #1A1F3A
- **Alternating Rows**: #0F1229 (normal), #1A1F3A (alternate)
- **Hover Row**: #2A3F5A

---

## Text Color Combinations

### Primary Text on Backgrounds

| Background | Text Color | Contrast    |
| ---------- | ---------- | ----------- |
| #0A0E27    | #E0E0E0    | 13:1 (AAA+) |
| #0F1229    | #E0E0E0    | 13:1 (AAA+) |
| #1A1F3A    | #E0E0E0    | 11:1 (AAA)  |
| #2A3F5A    | #E0E0E0    | 9:1 (AAA)   |

### Secondary Text

- #A0A0A0 on #0A0E27 = 7.5:1 (WCAG AA)
- #A0A0A0 on #1A1F3A = 6:1 (WCAG AA)

### Always Ensure

- Minimum 7:1 contrast for body text (WCAG AAA)
- Minimum 4.5:1 for secondary text (WCAG AA)
- Use tools to verify before shipping

---

## Text Alignment

### Left Align (Default)

- Most text uses left alignment
- Natural reading direction
- Better readability
- Used for: body text, lists, headings

### Right Align

- Numbers in tables (right-aligned for scanning)
- Secondary info (less common)
- Translations if RTL language added

### Center Align

- Headings sometimes
- Empty states
- Rare in content
- Readability risk with long text

### Justify

- Avoid (poor readability on screens)
- Can create "rivers" of white space
- Not used in Atlas

---

## Truncation & Overflow

### Single-line Truncation

```
Very long filename that doesn't fit...
```

- **Overflow**: ellipsis (`text-overflow: ellipsis`)
- **White Space**: nowrap
- **Tooltip**: Show full text on hover (Ctrl+hover reveals)

### Multi-line Truncation

```
Multi-line text that's too long
to fit in the available space and
needs truncation after 3 lines...
```

- **Max Lines**: 3 (line-clamp: 3)
- **Overflow**: Show scroll if needed
- **Fallback**: Ellipsis if clamp unavailable
- **Tooltip**: Show full text

### Line Breaking

- **Word Break**: Keep words together (break-word: normal)
- **Hyphenation**: Enable for URLs/code (`hyphens: auto`)
- **Allow Overflow**: For code blocks, provide horizontal scroll

---

## Internationalization

### Character Support

Currently: Latin alphabet only (Phase 1)

Future (Phase 2+):

- Cyrillic (Russian, Ukrainian)
- Arabic (right-to-left)
- CJK (Chinese, Japanese, Korean)

### Font Fallbacks for Future

```css
/* Greek/Cyrillic */
font-family: "Inter", "Noto Sans", sans-serif;

/* Arabic */
font-family: "Inter", "Noto Sans Arabic", sans-serif;

/* CJK */
font-family: "Inter", "Noto Sans SC", sans-serif;
```

### RTL Text (Future)

- CSS `direction: rtl` for Arabic/Hebrew
- Flip layout
- Mirror buttons/controls
- Maintain typography rules

---

## Readability Guidelines

### Optimal Line Length

- **Minimum**: 30 characters
- **Optimal**: 50-80 characters (coding convention)
- **Maximum**: 100 characters (very wide)

### Text Rendering

- **Font Smoothing**: `antialiased` (on light), `subpixel-antialiased` (on dark)
- **Text Rendering**: `optimizeLegibility` for headers
- **Letter Spacing**: 0 (default), +0.5px for ALL CAPS

### Accessibility Considerations

- High contrast required (7:1 for body text)
- No color-only to convey meaning
- Font size minimum 12px for body text
- Line height minimum 1.4 for body text
- Don't justify text on screens

---

## Animation

### Text Transitions

- **Duration**: 100ms fade between text sizes
- **Curve**: ease-out
- **Trigger**: Font size changes, emphasis changes
- **Disabled**: When `prefers-reduced-motion` enabled

### Text Overflow Animation

- **No animation** for ellipsis
- **No animation** for truncation
- **Show full** on hover (instant, no delay)

---

## Implementation Checklist

- [ ] Use Inter for all UI text
- [ ] Use JetBrains Mono for code
- [ ] Follow font sizes exactly (don't approximate)
- [ ] Use font weights 400, 500, 600 only
- [ ] Maintain line heights as specified
- [ ] Ensure 7:1+ contrast for readability
- [ ] All headings use weights 600+
- [ ] Code blocks have 1.6 line height
- [ ] Links always underlined
- [ ] Don't justify body text
- [ ] Respect text-align for lists/tables

---

**Typography Specification Version**: 1.0  
**Last Updated**: August 2, 2026

These are the exact font specifications to implement. Deviations create inconsistency and readability issues.
