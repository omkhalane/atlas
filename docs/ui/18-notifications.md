# Notifications Specification

System notifications, toasts, and alerts.

## Notification Types

### Success Toast

```
✅ File saved successfully
└─ Auto-dismiss in 3s
```

### Error Alert

```
❌ Connection failed
Error: Timeout after 30s
[Retry] [Close]
└─ Sticky until dismissed
```

### Warning Toast

```
⚠️  2 files will be deleted
[Confirm] [Cancel]
└─ Requires user action
```

### Info Toast

```
ℹ️  Update available (v1.1)
[View Details] [Later]
└─ Auto-dismiss in 5s
```

## Position

Bottom-right corner, 12px from edge.

## Stacking

Maximum 3 visible. Older toasts fade out.

## Accessibility

- Screen reader announces all notifications
- High contrast text and backgrounds
- Can be dismissed with Esc key
- Focus trap in alert dialogs

---

**Notifications Specification Version**: 1.0  
**Last Updated**: August 2, 2026
