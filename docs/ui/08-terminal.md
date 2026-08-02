# Terminal Panel Specification

## Purpose

Multi-tab terminal interface for executing commands, viewing output, and managing shell sessions. Supports splitting, SSH sessions, and background processes.

## Key Features

- **Multiple Tabs**: Multiple terminal sessions
- **Split View**: Horizontal/vertical splits within terminal
- **SSH Support**: Remote session connections
- **History**: Command history searchable
- **Logs**: Output logging and playback
- **Background**: Monitor long-running processes

## Layout

```
┌─ Terminal Header ───────────────────────┐ 32px
│ [Main] [SSH: prod-01] [Build] [+] [×]  │ Tabs
├─────────────────────────────────────────┤
│                                         │
│ $ npm run build                         │
│ > Compiling...                          │
│ > Done! (2.3s)                          │
│ $                                       │ Output
│                                         │
│ [Cursor blinking here]                  │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

## Terminal Features

### Shell Support

- **bash**: Default
- **zsh**: Auto-detect
- **fish**: If installed
- **Custom**: Configurable shell in settings

### Input Handling

- **Copy/Paste**: Ctrl+C, Ctrl+V (terminal respects these)
- **History**: Up/Down arrows, Ctrl+R reverse search
- **Clear**: Ctrl+L clears screen
- **Interrupt**: Ctrl+C sends SIGINT

### Output Rendering

- **Syntax Highlighting**: Detects command output type
- **ANSI Colors**: Full color support
- **Unicode**: Full UTF-8 support
- **Line Wrapping**: Automatic at viewport width

### Scrollback

- **Buffer**: 10,000 lines of history
- **Search**: Ctrl+F to search output
- **Export**: Save output to file

## SSH Sessions

### Configuration

```
[SSH Connection Dialog]
Host: prod-01.example.com
Port: 22
Username: ubuntu
Auth: [Private Key ▼] ~/.ssh/id_rsa

[Connect] [Test Connection]
```

### Session Management

- **Saved Sessions**: Reconnect quickly
- **Auth Methods**: Key, password, agent
- **Port Forwarding**: Support for local/remote forwarding
- **SOCKS Proxy**: Supported (advanced)

## Process Management

### Background Processes

```
Running Processes
├─ npm run dev (PID 1234) [Kill]
├─ python server.py (PID 5678) [Kill]
└─ build.sh (PID 9012) [Kill]
```

- **Monitor**: Running processes shown in sidebar
- **Kill**: Quick action to terminate
- **Logs**: View output in separate panel

## Split Terminals

### Configuration

```
┌─────────────────────┬─────────────────┐
│ Main Terminal       │ SSH Session     │
│ $ npm run dev       │ $ ssh prod-01   │
│ ...                 │ ...             │
├─────────────────────┴─────────────────┤
│ Build Terminal                        │
│ $ npm build                           │
│ ...                                   │
└─────────────────────────────────────────┘
```

- **Create Split**: Ctrl+Shift+S or right-click
- **Close Split**: Click X or Ctrl+W
- **Focus**: Click to focus, Ctrl+` to cycle
- **Resize**: Drag divider

## History & Logging

### Command History

```
Recent Commands
├─ npm run build
├─ npm run test
├─ git status
├─ git push origin main
└─ ssh prod-01
```

- **Rerun**: Click command to re-execute
- **Search**: Ctrl+R reverse search
- **Export**: Save history to file
- **Clear**: Clear history (confirmation)

### Output Logging

- **Auto-log**: All output saved to session file
- **Export**: File → Export Terminal Output
- **Search**: Search across all logged output
- **Playback**: Replay session with timestamps

## Keyboard Shortcuts

```
Ctrl+Shift+`    New Terminal
Ctrl+W          Close Terminal
Ctrl+Tab        Next Terminal
Ctrl+Shift+Tab  Previous Terminal

Ctrl+L          Clear Screen
Ctrl+C          Interrupt (SIGINT)
Ctrl+D          EOF (if empty)
Ctrl+U          Clear Line

Ctrl+F          Search Output
Ctrl+A          Select All
Ctrl+C          Copy Selection
Shift+Insert    Paste (if Ctrl+V fails)

Ctrl+K          Clear Buffer (VS Code style)
Ctrl+Shift+P    Command Palette in Terminal
```

## Accessibility

- **Screen Reader**: Terminal content announced
- **High Contrast**: Text always readable
- **Keyboard Only**: All operations via keyboard
- **Focus**: Clear focus ring on input

## Performance

- **Rendering**: 60 FPS even with fast output
- **Memory**: Limit scrollback to 10K lines
- **CPU**: Debounce rendering updates
- **Search**: Regex search on output

## Error Handling

- **Command Not Found**: Clear error message with suggestions
- **Connection Failed**: Retry options for SSH
- **Timeout**: User-configurable timeout with retry
- **Crash**: Terminal auto-restarts if shell crashes

## Settings

```
Terminal Preferences
├─ Default Shell: /bin/bash
├─ Font Size: 12px
├─ Scrollback Lines: 10,000
├─ ☑ Enable Command Logging
├─ ☑ Confirm on Close if Running
├─ Copy on Select: ☐ Enabled
└─ Paste on Right-Click: ☐ Enabled
```

---

**Terminal Specification Version**: 1.0  
**Last Updated**: August 2, 2026
