# Design Principles - Core Philosophy

## 1. AI Operating Runtime First

### Principle

Atlas is not a chat interface pretending to be a tool. It is a runtime that executes AI-driven operations on the user's machine. The UI must make this clear and obvious.

### Application

- **Primary Focus**: Agent actions and their results, not conversation
- **Chat as Secondary**: Messages are context, not the main interface
- **Transparency**: Every agent action is visible, logged, and reversible
- **Authority**: User always maintains control; agent executes with permission

### Visual Signals

- Agent actions displayed prominently (browser screenshots, file previews, terminal output)
- Conversation appears below/alongside action results, not above
- Status bar shows what agent is currently doing, not status messages in chat
- Timeline visible by default, showing complete execution history

---

## 2. Information Architecture Principle

### Principle

Complex information is made accessible through progressive disclosure. Basic operations are simple; advanced features are discoverable without overwhelming the interface.

### Application

- **Three Levels**:
  1. **Visible by Default**: What you need to see now
  2. **One Click Away**: Context-dependent details
  3. **Discoverable**: Advanced options through keyboard or settings

- **Example - File View**:
  - Level 1: File tree with icons
  - Level 2: Click for preview, inline git status
  - Level 3: Right-click for advanced options (permissions, version history)

### Visual Signals

- Gradual reveal of information as windows expand
- Secondary controls show on hover
- Alt key reveals all available commands
- Inspector/properties panel for deep exploration

---

## 3. Keyboard-First, Mouse-Friendly Principle

### Principle

Power users drive the interface with keyboard shortcuts. Every function is accessible this way. But for exploratory tasks (browsing files, pointing at elements), the mouse is essential and smooth.

### Application

- **Keyboard Paths**: Every feature has a keyboard shortcut documented and consistent
- **Discoverable**: Shortcuts shown in tooltips, visible in menus, listed in command palette
- **Consistent Grammar**: Similar operations use similar shortcuts globally
- **Mouse Optimization**: Pointer-based selection, drag-and-drop, click-to-focus

### Visual Signals

- Shortcut labels on buttons and menus
- Focus ring (2px blue) shows current keyboard focus
- Hover states indicate clickability
- Selection states different from focus

---

## 4. Dark Mode Optimization Principle

### Principle

Dark mode is not an option—it's the default and only theme for Phase 1. The interface is optimized for OLED screens, nighttime use, and reduced eye strain in technical environments.

### Application

- **Color Palette**: Deep blacks (#0A0E27), grays, accent colors on dark background
- **Contrast Ratio**: Minimum 7:1 for all text (WCAG AAA)
- **Reduced Bloom**: Flat colors, no excessive brightness, no pure white
- **OLED Optimization**: True blacks for OLED screen efficiency

### Visual Signals

- Text: #E0E0E0 (light gray)
- Secondary text: #A0A0A0 (medium gray)
- Disabled text: #606060 (dark gray)
- Accent: #00A8E8 (electric blue)
- Status: Green (#10B981), Amber (#F59E0B), Red (#EF4444)

---

## 5. Minimal Aesthetic Principle

### Principle

Every visual element must serve a purpose. No decorations, no unnecessary colors, no "nice-to-haves" that don't communicate information or enable interaction.

### Application

- **Visual Weight**: Only UI that matters, removed after adding
- **Spacing**: Used for grouping and hierarchy, not filler
- **Icons**: Instantly recognizable, consistent with system icons
- **Motion**: Purposeful transitions that improve clarity, not smooth fades

### Anti-Pattern Examples

- Gradient backgrounds with no information purpose
- Decorative icons or illustrations
- Unnecessary shadows or blur effects
- Animations that don't provide feedback
- Color used decoratively rather than semantically

---

## 6. Technical Depth Principle

### Principle

Atlas is built for technical users. The UI doesn't hide complexity; it makes complexity understandable and controllable.

### Application

- **Expose Details**: Show command-line arguments, process IDs, network requests
- **Technical Language**: Use precise terminology; don't "dumb down" concepts
- **Logs Accessible**: Not hidden behind logging levels, easily accessible
- **Raw Data View**: Always provide option to see JSON, raw terminal output, etc.

### Visual Signals

- Terminal visible by default, not minimized
- Process IDs and system information displayed
- Error messages include stack traces, system error codes
- Logs searchable and filterable, not just "last 100 lines"

---

## 7. Trustworthiness Principle

### Principle

AI agents have access to the user's computer. The UI must make it obvious what the agent is doing, why, and how to stop it at any moment.

### Application

- **Transparency**: All agent actions logged and visible
- **Permission Requests**: Never silent; always ask for confirmation
- **Reversal**: All operations are reversible; undo/rollback available
- **Traceability**: Every file change, terminal command, web request is tracked

### Visual Signals

- Agent status always visible (planning, executing, waiting)
- Approval dialogs clear and specific
- Red danger zones with clear warnings
- Rollback button always available for recent actions

---

## 8. Performance is Perceptible Principle

### Principle

Performance is not about low numbers; it's about how fast things _feel_. Instant feedback, smooth scrolling, and quick response times make the interface feel responsive.

### Application

- **Perceived Performance**: Show progress early, even if work isn't done
- **Responsiveness**: Click response < 50ms, even if processing continues
- **Streaming**: Responses appear immediately, complete as data arrives
- **Cancellation**: Stop long operations instantly, without delay

### Visual Signals

- Progress indicators appear immediately (not after 1 second delay)
- Spinners and loaders animated smoothly at 60 FPS
- Scroll response is instant, not lagged
- Typing in search/filter appears immediately

---

## 9. Context Continuity Principle

### Principle

The user's context is maintained across sessions, operations, and interruptions. Memory, workspace state, and execution history persist and are always accessible.

### Application

- **Session Recovery**: Reopen Atlas and everything is as it was
- **Undo History**: Rollback available for significant operations
- **Memory Persistence**: Facts and knowledge survive agent completion
- **Workspace Snapshots**: Save/load complete workspace states

### Visual Signals

- Timeline shows complete history, not just current session
- Memory panel shows all stored facts, not just recent
- Unsaved work indicated with dot on tab
- Dirty state shown for modified files

---

## 10. Linux Native Principle

### Principle

Atlas is built specifically for Linux Desktop. It respects Linux conventions, integrates with desktop environments, and uses native APIs where appropriate.

### Application

- **Desktop Integration**: Wayland/X11 protocols followed precisely
- **System Integration**: Respects system fonts, colors, accessibility settings
- **File Manager Integration**: Context menus in Nautilus, Dolphin, etc.
- **Keyboard Shortcuts**: Uses Linux conventions (Ctrl, not ⌘; Ctrl+Q to quit)

### Visual Signals

- Standard Linux icons and themes
- Native window decorations
- System color palette respected
- Alt key for menu access (not Option on Linux)

---

## 11. Consistency Principle

### Principle

Similar patterns repeat throughout the interface. Once learned, they apply everywhere. This reduces cognitive load and makes the interface predictable.

### Application

- **Shortcut Consistency**: Ctrl+S saves everywhere, Ctrl+F finds everywhere
- **Pattern Consistency**: Dialogs follow same structure, panels follow same rules
- **Visual Consistency**: Same components look identical throughout
- **Behavior Consistency**: Similar actions produce similar results

### Visual Signals

- Component styles identical across all views
- Button labels consistent (Save vs Write, Delete vs Remove)
- Padding and spacing use same scale everywhere
- Icon styles uniform and recognizable

---

## 12. Progressive Enhancement Principle

### Principle

Core functionality works with minimal capabilities. Advanced features enhance the experience but don't block basic operations.

### Application

- **Offline Functionality**: Works without cloud sync or remote agents
- **Graceful Degradation**: GPU acceleration unavailable? Use CPU rendering
- **Incremental Loading**: Show what's available immediately, load more as ready
- **Feature Detection**: Detect capabilities and enable/disable features

### Visual Signals

- Disable advanced buttons when feature unavailable
- Show capabilities (GPU acceleration, available memory) in settings
- Fallback UI for missing features (render as ASCII if no GPU)
- Progressive disclosure of advanced options

---

## Design Anti-Patterns (Do NOT)

### 1. ChatGPT-Like UI

❌ Don't:

- Center the chat interface
- Hide execution details below the fold
- Make conversation the primary focus
- Use character animation or personality

✓ Do:

- Make agent actions primary, conversation secondary
- Show execution output prominently
- Make reasoning and planning visible
- Keep UI professional and utilitarian

### 2. VS Code Cloning

❌ Don't:

- Copy VS Code's sidebar organization exactly
- Reuse VS Code icons without thinking
- Implement an editor component
- Use VS Code's extension architecture

✓ Do:

- Learn from VS Code's command palette concept
- Adapt sidebar patterns to Atlas's needs
- Focus on runtime execution, not file editing
- Design Atlas's own plugin architecture

### 3. Unnecessary Ornamentation

❌ Don't:

- Add gradient backgrounds
- Use decorative shadows
- Animate elements without purpose
- Include brand mascots or illustrations

✓ Do:

- Use color and spacing for hierarchy
- Use borders and opacity for depth
- Animate to communicate status or feedback
- Keep branding minimal and functional

### 4. Hiding Complexity

❌ Don't:

- Simplify by removing technical details
- Hide error messages or logs
- Bury advanced features in nested menus
- Prevent access to raw data

✓ Do:

- Expose complexity with good UX
- Show detailed error messages with context
- Make advanced features discoverable via keyboard
- Provide raw data view (JSON, terminal, etc.)

### 5. Ignoring Context

❌ Don't:

- Show same interface for all tasks
- Ignore the user's expertise
- Use generic UI patterns that don't fit Atlas
- Forget Linux platform specifics

✓ Do:

- Adapt interface to context (file task vs. web task)
- Design for power users who know Linux
- Create unique patterns that fit Atlas's needs
- Respect Linux conventions and APIs

---

## Principle Application Examples

### Example 1: Executing a Terminal Command

**Principle**: Keyboard-First + Transparency + Performance

Interaction:

1. User: Ctrl+` to focus terminal
2. Types: `python build.py`
3. **Immediate Feedback**: Command appears, cursor shows focus
4. User: Enter
5. **Perceived Performance**: Prompt returns immediately, output streams in
6. **Technical Depth**: PID, execution time, exit code shown
7. **Transparency**: If command has side effects, agent logs it
8. **Reversible**: Terminal session saved, can review history and rollback

### Example 2: Approving Agent File Modification

**Principle**: Trustworthiness + Progressive Disclosure + Simplicity

Flow:

1. Agent requests to modify `/home/user/config.json`
2. **Approval Dialog** shows:
   - File path (precise)
   - What will change (diff view)
   - Why agent needs this (context)
   - Three options: Approve, Deny, Ask Each Time
3. User can:
   - Review the diff (Level 2 detail)
   - See full file context (Level 3)
   - Keyboard shortcut: A to approve, D to deny
4. **Post-Approval**: File change appears in timeline, rollback available

### Example 3: Searching Files

**Principle**: Keyboard-First + Information Architecture + Performance

Flow:

1. User: Ctrl+P (command palette)
2. Types: `find config`
3. **Immediate Display**: Matching files appear in dropdown
4. **Performance**: Results stream in as search completes
5. **Progressive Disclosure**: Hover shows file size, modification time
6. **Keyboard**: Arrow keys to navigate, Enter to open, Ctrl+Enter in split view
7. **Context**: Recent searches shown at top

---

## Principle Conflicts & Resolution

### Conflict: Keyboard-First vs. Visual Discovery

**Resolution**: Keyboard paths are primary and always work. Visual cues help learners discover keyboard shortcuts without blocking them.

### Conflict: Technical Depth vs. User Overwhelm

**Resolution**: Technical details are progressive; basic operations are simple. Advanced features are discoverable, not mandatory.

### Conflict: Dark Mode Only vs. Accessibility

**Resolution**: Dark mode doesn't prevent high contrast. Styles support both dark backgrounds and high-contrast adjustments simultaneously.

### Conflict: Minimal Aesthetics vs. Clear Information Hierarchy

**Resolution**: Spacing, color, and typography create hierarchy without decoration. Visual weight is earned through information importance, not arbitrary styling.

---

## Principle Verification Checklist

Use this checklist when designing new features:

- [ ] Does this serve an actual user need or workflow?
- [ ] Can it be accomplished entirely via keyboard?
- [ ] Is the interface minimal or can something be removed?
- [ ] Does it respect technical user expertise?
- [ ] Is every agent action transparent and reversible?
- [ ] Does it feel responsive and smooth at 60 FPS?
- [ ] Does it follow Linux conventions and practices?
- [ ] Is it consistent with other similar features?
- [ ] Does it gracefully degrade if features aren't available?
- [ ] Can it be understood without documentation?

If you answer "No" to any question, reconsider the design.

---

## Versioning & Updates

**Design Principles Version**: 1.0  
**Last Updated**: August 2, 2026  
**Stability**: These principles are stable. Updates require explicit approval.

Future versions will only add principles, not replace existing ones. If a principle needs refinement, the entire design community should review and approve changes.
