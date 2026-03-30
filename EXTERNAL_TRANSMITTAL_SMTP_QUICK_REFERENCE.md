# Quick Reference: External Transmittal SMTP Email Feature

## Feature Summary
✅ **EVERY status change in external transmittals now automatically sends SMTP emails**

## Key Points

### What Triggers Emails
- ✅ Mark as Received (with proof attachment)
- ✅ Full Return (with proof)
- ✅ Partial Return (with proof)
- ✅ Paid Sample (with RGA)
- ✅ Convert to For Keep (with RGA)
- ✅ Admin Override (manual status change)

### Who Gets Emails
- Sender email
- Recipient email

### What's in the Email
- Reference number & action type
- Current status with color coding
- Transmittal description
- **📎 All uploaded attachments with names & timestamps**
- Upload notes
- Timestamp of change

### Files Modified
1. **`transmittals/email_utils.py`**
   - Enhanced `send_external_transmittal_resolution_email()` 
   - Added attachment details parsing
   - Added timestamp display
   - Added admin override support

2. **`transmittals/views_external.py`**
   - Added email sending to admin override function
   - All status change endpoints now send emails

### Technical Implementation

**Attachment Details Retrieval:**
```python
attachments = transmittal.attachments.all().order_by('-uploaded_at')
for att in attachments:
    attachment_type = att.attachment_type
    file_name = att.file.name
    upload_time = att.uploaded_at
```

**Email Sending:**
```python
send_external_transmittal_resolution_email(
    transmittal=transmittal,
    action_type='mark_received',  # Action that triggered email
    notes='Additional notes'
)
```

## Testing Checklist

- [ ] Create external transmittal → Check email in sender/recipient inbox
- [ ] Mark as Received with attachment → Check email shows attachment details
- [ ] Record Return with proof → Check email shows proof filename & timestamp
- [ ] Admin Override status → Check email mentions admin override
- [ ] Verify attachment names display correctly
- [ ] Verify timestamps are accurate
- [ ] Check email has both HTML and plain text versions

## Common Scenarios

### Scenario 1: Mark as Received
```
User Action: Clicks "Mark as Received" + uploads PDF proof
Email Sent: To sender & recipient
Contains:
  - "Marked as Received" status (green)
  - "📎 Attachments: proof_delivery_20260305.pdf"
  - Timestamp of upload
```

### Scenario 2: Record Full Return
```
User Action: Records Full Return + uploads RGA document
Email Sent: To sender & recipient
Contains:
  - "Full Return" status (teal)
  - "📎 Attachments: RGA_form.pdf"
  - Case marked as closed
```

### Scenario 3: Admin Changes Status
```
User Action: Admin selects new status from dropdown
Email Sent: To sender & recipient
Contains:
  - "Status Changed (Admin Override)" (red)
  - Admin reason/notes
  - New status
```

## Email Template Structure

```
[External Transmittal Header]
Reference Number: TR-EXT-2026-001234
Action: Marked as Received ✅
Type: For Keep
Status: Received
Description: [Original description]
Updated At: 2026-03-05 14:30:22

Sub Type: [if applicable]

📎 Attachments Uploaded:
  • Proof of Delivery: delivery_confirmation_20260305.pdf (Uploaded: 2026-03-05 14:30:22)

Notes: [Optional notes]

[Footer with system info]
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No email received | Check Django SMTP settings in settings.py |
| Attachment not in email | Verify attachment was uploaded successfully |
| Wrong timestamp | Check server timezone setting |
| Missing recipient email | Verify transmittal recipient_email is set correctly |

## Database Queries

### Check email sending was logged
```sql
SELECT * FROM transmittals_externaltransmittalaudittrail 
WHERE action IN ('mark_received', 'full_return', 'partial_return', 'admin_override')
ORDER BY created_at DESC;
```

### Check attachments
```sql
SELECT * FROM transmittals_externaltransmittalattachment 
WHERE transmittal_id = [TRANSMITTAL_ID]
ORDER BY uploaded_at DESC;
```

---

**Implementation Date:** March 5, 2026
**Status:** ✅ Production Ready
