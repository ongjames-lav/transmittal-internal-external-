# Role-Based Action Visibility Matrix

## Status Actions by Role and Status

### Transmittal Status: IN TRANSIT

| Role | Action | Button | Visible | Notes |
|------|--------|--------|---------|-------|
| **Sender** | Cancel | ❌ Cancel Transmittal | ✅ YES | Can cancel while in transit |
| **Custodian** | Mark Arrived | 📍 Mark as Arrived | ✅ YES | Can receive at destination |
| **Receiver** | Mark Received | ✅ Mark as Received | ✅ YES | **NEW:** Can receive directly |
| **Staff** | View Only | (No Actions) | - | Admin view only |

**Helper Text for Receiver:**  
💡 You can receive this directly, or wait for the custodian to mark it as arrived first.

---

### Transmittal Status: ARRIVED

| Role | Action | Button | Visible | Notes |
|------|--------|--------|---------|-------|
| **Sender** | View Only | (No Actions) | - | Cannot take action on arrived items |
| **Custodian** | View Only | (No Actions) | - | Has already marked as arrived |
| **Receiver** | Mark Received | ✅ Mark as Received | ✅ YES | Standard receipt after arrival |
| **Staff** | View Only | (No Actions) | - | Admin view only |

**Helper Text for Receiver:**  
💡 Please mark as received to confirm receipt.

---

### Transmittal Status: RECEIVED

| Role | Action | Button | Visible | Notes |
|------|--------|--------|---------|-------|
| **All Roles** | View Only | (No Actions) | - | Final state, read-only |

**Status Text:**  
✅ Complete - Received by [Name] on [Date/Time]

---

### Transmittal Status: CANCELLED

| Role | Action | Button | Visible | Notes |
|------|--------|--------|---------|-------|
| **All Roles** | View Only | (No Actions) | - | Final state, read-only |

**Status Text:**  
❌ This transmittal has been cancelled on [Date/Time]

---

## Visual Flow Diagram

### Per-Status Button Display

```
┌─────────────────────────────────────────────────────────┐
│ TRANSMITTAL DETAIL VIEW                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ STATUS: IN TRANSIT                                      │
│ ─────────────────────────────────────────────────────   │
│                                                         │
│ [❌ CANCEL]  [📍 ARRIVED]  [✅ RECEIVED]                │
│   ^              ^             ^                        │
│   │              │             │                        │
│ Sender        Custodian     Receiver                     │
│ only          only          only                        │
│ (if sender)   (if custodian)(if recipient email)        │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ Status Info: IN TRANSIT - Waiting for delivery          │
│                                                         │
│ 💡 Helper: Role-specific guidance message              │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ TRANSMITTAL DETAIL VIEW                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ STATUS: ARRIVED                                         │
│ ─────────────────────────────────────────────────────   │
│                                                         │
│                      [✅ RECEIVED]                      │
│                          ^                              │
│                          │                              │
│                      Receiver                           │
│                      only                               │
│                    (if recipient)                       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ Status Info: ARRIVED - Delivered to [Location]          │
│                                                         │
│ 💡 Helper: Please mark as received to confirm receipt.  │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ TRANSMITTAL DETAIL VIEW                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ STATUS: RECEIVED ✅                                     │
│ ─────────────────────────────────────────────────────   │
│                                                         │
│ (No action buttons - Final state)                       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ Status Info: RECEIVED - Complete ✅                     │
│ Received by [Name] on [Date/Time]                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Real-World Usage Examples

### Example 1: Sender at Pantoc Creates Transmittal

**Initial Setup:**
- Sender: John Doe (Pantoc location)
- Recipient: Jane Smith (jane@company.com)
- Destination: Meycauayan location (Custodian: Bob)

**What Each Person Sees:**

#### Sender's View (John)
```
Status: IN TRANSIT
┌─────────────────────────────────────────┐
│ ❌ Cancel Transmittal                   │
│                                         │
│ 📍 Mark as Arrived (disabled - gray)    │
│ ✅ Mark as Received (disabled - gray)   │
│                                         │
│ 💡 Only you can cancel this transmittal │
│    if it hasn't been received yet.      │
└─────────────────────────────────────────┘
```

#### Custodian's View (Bob)
```
Status: IN TRANSIT
┌─────────────────────────────────────────┐
│ ❌ Cancel Transmittal (disabled - gray) │
│                                         │
│ 📍 Mark as Arrived                      │
│ ✅ Mark as Received (disabled - gray)   │
│                                         │
│ 💡 Please mark as arrived when the      │
│    transmittal reaches your location.   │
└─────────────────────────────────────────┘
```

#### Receiver's View (Jane)
```
Status: IN TRANSIT
┌─────────────────────────────────────────┐
│ ❌ Cancel Transmittal (disabled - gray) │
│                                         │
│ 📍 Mark as Arrived (disabled - gray)    │
│ ✅ Mark as Received                     │
│                                         │
│ 💡 You can receive this directly, or    │
│    wait for the custodian to mark it    │
│    as arrived first.                    │
└─────────────────────────────────────────┘
```

---

### Example 2: After Custodian Marks Arrived

**Scenario:** Bob (Custodian) marks transmittal as arrived

#### Sender's View (John)
```
Status: ARRIVED
┌─────────────────────────────────────────┐
│ ❌ Cancel Transmittal (disabled - gray) │
│ 📍 Mark as Arrived (disabled - gray)    │
│ ✅ Mark as Received (disabled - gray)   │
│                                         │
│ Status: ARRIVED - Delivered to          │
│ Meycauayan location                     │
└─────────────────────────────────────────┘
```

#### Custodian's View (Bob)
```
Status: ARRIVED
┌─────────────────────────────────────────┐
│ ❌ Cancel Transmittal (disabled - gray) │
│ 📍 Mark as Arrived (disabled - gray)    │
│ ✅ Mark as Received (disabled - gray)   │
│                                         │
│ Status: ARRIVED - You marked this       │
│ as arrived                              │
└─────────────────────────────────────────┘
```

#### Receiver's View (Jane)
```
Status: ARRIVED
┌─────────────────────────────────────────┐
│ ❌ Cancel Transmittal (disabled - gray) │
│ 📍 Mark as Arrived (disabled - gray)    │
│ ✅ Mark as Received                     │
│                                         │
│ 💡 Please mark as received to confirm   │
│    receipt.                             │
└─────────────────────────────────────────┘
```

---

### Example 3: Receiver Marks as Received (Direct)

**Scenario:** Jane (Receiver) marks as received while still IN TRANSIT (bypasses custodian)

**Result:**
- Transmittal goes directly: In Transit → Received
- John (Sender) notified: "Jane Smith received transmittal PAN-20260127-0001"
- Bob (Custodian) notified: "Status Update: Transmittal received by Jane Smith"
- Status shows: RECEIVED ✅ at [timestamp]

---

## Permission Logic Summary

```python
# Only show Cancel button
if is_sender and transmittal.status == 'in_transit':
    show_cancel_button = True

# Only show Mark as Arrived button  
if is_custodian and transmittal.status == 'in_transit':
    show_mark_arrived_button = True

# Show Mark as Received button for BOTH statuses
if is_recipient and transmittal.status in ['in_transit', 'arrived']:
    show_mark_received_button = True

# All other buttons hidden
```

---

## Email Notifications by Action

### When Transmittal Created
```
To: Recipient (Jane)
To: Custodian (Bob)
Subject: [PAN-20260127-0001] New Transmittal Report
Content: Transmittal details, description, remarks
```

### When Custodian Marks Arrived
```
To: Sender (John)
To: Recipient (Jane)
Subject: [PAN-20260127-0001] Status Update: Arrived
Content: "The transmittal has arrived at Meycauayan..."
```

### When Receiver Marks Received (Standard Path)
```
To: Sender (John)
To: Custodian (Bob)
Subject: [PAN-20260127-0001] Status Update: Received
Content: "The transmittal has been received by Jane Smith."
```

### When Receiver Marks Received (Direct Path)
```
To: Sender (John)
To: Custodian (Bob)  # Notified even with direct receipt
Subject: [PAN-20260127-0001] Status Update: Received
Content: "The transmittal has been received by Jane Smith."
```

---

## Button State Chart

```
Status       | Sender Cancel | Custodian Arrived | Receiver Received
─────────────┼───────────────┼──────────────────┼─────────────────
In Transit   | ✅ ENABLED    | ✅ ENABLED       | ✅ ENABLED
Arrived      | ❌ DISABLED   | ❌ DISABLED      | ✅ ENABLED
Received     | ❌ DISABLED   | ❌ DISABLED      | ❌ DISABLED
Cancelled    | ❌ DISABLED   | ❌ DISABLED      | ❌ DISABLED
```

---

**Document Version:** 2.0.1  
**Last Updated:** January 27, 2026  
**Status:** ✅ Ready for Production Deployment
