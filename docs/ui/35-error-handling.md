# Error Handling & User Feedback Specification

How errors are communicated and how users recover from problems.

## Error Types

### User Errors

Actions the user can fix:

- Invalid input (missing required field)
- Invalid format (wrong email format)
- File not found (file deleted externally)
- Insufficient permissions (can't edit file)

**Response**: Clear message + fix suggestion

### System Errors

Server/system problems beyond user control:

- Network timeout
- Server error (500)
- Disk full
- Service unavailable

**Response**: Error message + retry option + support info

### Recoverable Errors

Operations that can be retried:

- Network timeout
- Temporary server error
- Resource lock (file in use)
- Rate limit

**Response**: Automatic retry + user control

### Critical Errors

Fatal problems requiring action:

- App crash
- Data corruption
- Security violation
- Unrecoverable system error

**Response**: Alert user + log for debugging + recovery option

## Error Messages

### Message Structure

```
❌ [Action] failed

[What happened - specific and technical]
[Why it happened - brief explanation]

[Suggestion for fix or next step]

[Relevant details if technical]
```

### Good Error Messages

```
❌ Unable to save file

The file is locked by another process.
Suggestion: Close the file in other programs, or rename and save as new file.

File: /home/user/document.txt
Process: LibreOffice Writer
```

### Bad Error Messages

```
Error 500        ← Too vague
Failed           ← Unhelpful
An error occurred ← No detail
```

### Error Message Guidelines

- **Specific**: What failed, not "Error occurred"
- **Technical + Friendly**: Technical detail + human explanation
- **Actionable**: What user can do to fix
- **Visible**: Can't miss (prominent placement)
- **Readable**: Plain language, no jargon when possible

## Error Display

### Error Toast (Transient)

```
╔════════════════════════════════════════╗
║ ❌ Unable to connect to server        │
│    Retrying...                         │
│ [Retry] [Dismiss] [Details]           │
╚════════════════════════════════════════╝
```

Used for:

- Temporary issues (network)
- Auto-recovering errors
- Non-blocking operations

**Duration**: 5 seconds (dismissible)

### Error Panel (Persistent)

```
┌──────────────────────────┐
│ ❌ Error                 │
├──────────────────────────┤
│ Upload failed            │
│                          │
│ The file is too large   │
│ (Limit: 100 MB)         │
│                          │
│ Current file: 250 MB    │
│                          │
│ [Cancel] [Try Another]  │
└──────────────────────────┘
```

Used for:

- Blocking operations (can't proceed)
- User action required
- Complex situations needing detail

**Dismissal**: User must take action or dismiss

### Error Log (Details)

Detailed error information available:

```
Settings → Help → Error Log
Or: Ctrl+Shift+E
```

Shows:

- Full error stack trace
- Timestamps
- Affected operation
- System information (helpful for debugging)

## Error Recovery

### Automatic Recovery

Some errors auto-recover:

```
Network timeout
  ↓
Show toast "Reconnecting..."
  ↓
Retry automatically (3 times, exponential backoff)
  ↓
Success: Toast disappears
  ↓
Failure: Show persistent error with manual retry
```

### User-Initiated Recovery

User can recover:

- **Retry**: Try operation again
- **Cancel**: Stop operation
- **Alternate Action**: Try different approach
- **Report**: Send error to developers
- **Help**: Open relevant documentation

## Specific Error Scenarios

### File Not Found

```
❌ File Not Found

The file you tried to open no longer exists.
It may have been moved, deleted, or is inaccessible.

File: /home/user/documents/file.txt

Options:
[Browse for File] [Recent Files] [Cancel]
```

### Permission Denied

```
❌ Permission Denied

You don't have permission to modify this file.
The file may be read-only or owned by another user.

File: /home/user/readonly.txt
Owner: root
Permissions: -r--r--r--

Options:
[Request Permission] [Open Read-Only] [Cancel]
```

### Network Error

```
❌ Connection Failed

Unable to reach the server.
Check your network connection and try again.

Last attempt: Failed (timeout)
Retrying automatically in 10 seconds...

[Retry Now] [Cancel]
```

### Out of Memory

```
❌ Out of Memory

Atlas ran out of memory.
The application will now close.

Memory used: 1.2 GB / 1.0 GB
Tips: Close other applications, restart Atlas

[Restart] [Report] [Close]
```

### Unsupported File Type

```
❌ Unsupported File Type

This file type is not supported in this context.

File: document.xyz
Type: .xyz (unknown)

Supported types: .txt, .md, .pdf, .doc

Options:
[View List of Supported Types] [Cancel]
```

## Validation Feedback

### Real-Time Validation

```
Email: [_________@example.com]
         ↓
         ❌ Must include @ symbol

         [_john@example.com_______]
         ↓
         ✓ Valid email
```

- Shows feedback as user types
- Specific about what's needed
- Success confirmation

### Pre-Submit Validation

```
[Form with fields]
  Name: [John    ] ✓
  Email: [invalid] ❌ Must be valid email
  Phone: [required] ⚠ Leave blank or enter phone number

[Cancel] [Submit] ← Submit disabled until valid
```

## Notification System

### Info Notification

```
ℹ️  Information

New version available.
Atlas 1.2 includes performance improvements.

[Learn More] [Later] [Never Show]
```

### Warning Notification

```
⚠️  Warning

Large file detected.

Opening this 500 MB file may be slow.
You can still proceed if you want.

[Proceed] [Cancel]
```

### Success Notification

```
✓ Success

File saved successfully.

File: document.txt
Size: 2.3 MB
Saved: 2:45 PM

[Close]
```

## Keyboard & Accessibility

### Keyboard Interaction

- **Tab**: Move between error buttons
- **Enter**: Activate focused button
- **Escape**: Close error (if dismissible)
- **Space**: Activate button

### Screen Reader

- Error announced immediately
- Error type identified (error, warning, info)
- Action buttons announced with purpose
- Error details readable

### High Contrast

- Error colors visible in high contrast
- Icons distinct from background
- Text readable (7:1 contrast minimum)

## Error Logging & Analytics

### What to Log

- Error type and code
- Stack trace
- User action that caused error
- System information
- Timestamp
- User ID (anonymized)

### Privacy Considerations

- Don't log file contents
- Don't log personal data
- User can opt-out of error reporting
- Logs stored locally by default

### Developer Access

```
Settings → Help → Send Error Report
Ctrl+Shift+E → Error Log
```

Sends anonymized error data to developers.

## Preventive Messaging

### Warnings Before Dangerous Actions

```
Confirm Delete File

Are you sure you want to delete "important.txt"?
This action cannot be undone.

[Cancel] [Delete]
```

### Confirmation for Significant Changes

```
You have unsaved changes.

Close without saving?

[Save] [Discard] [Cancel]
```

## Testing Error States

### Error Testing Checklist

- [ ] Error message is clear and specific
- [ ] Error is visible (doesn't blend in)
- [ ] Recovery options available
- [ ] Keyboard navigation works
- [ ] Screen reader announces error
- [ ] Error message distinguishable from normal text
- [ ] High contrast mode readable
- [ ] Error disappears when resolved

---

**Error Handling Specification Version**: 1.0  
**Last Updated**: August 2, 2026

All errors must include actionable recovery information.
