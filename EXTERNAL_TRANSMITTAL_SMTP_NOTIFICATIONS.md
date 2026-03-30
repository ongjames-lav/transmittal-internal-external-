# External Transmittal SMTP Automatic Email Notifications

## Overview
The external transmittal system now **automatically sends SMTP email notifications** on **EVERY status change**, including when attachments are uploaded. This ensures all parties (sender and recipient) are kept in sync with the latest transmittal status.

## Feature Details

### When Emails Are Sent
Email notifications are **automatically triggered** when:

1. **Mark as Received** - Status changes to "Received" with proof attachment
2. **Full Return** - Status changes to "Closed" with full return proof
3. **Partial Return** - Status remains "Received" with partial return proof
4. **Paid Sample** - Status changes to "Closed" with RGA/deduction proof
5. **Convert to For Keep** - Status changes to "Closed" with RGA proof
6. **Admin Override** - Admin manually changes status via admin panel

### Recipients
Email notifications are sent to:
- **Sender Email** - The person who created the transmittal
- **Recipient Email** - The person receiving the transmittal

### Email Content
Each email includes:
- **Reference Number** - Unique ID of the transmittal
- **Action Type** - What status change occurred (with color-coded status)
- **Transmittal Type** - "For Keep" or "For Return"
- **Current Status** - Updated status display
- **Description** - Original transmittal description
- **Updated At** - Timestamp of status change
- **Sub Type** - For Return cases (Full, Partial, Paid Sample, etc.)
- **📎 Attachments Section** - Lists all uploaded attachments with:
  - Attachment type (Proof of Delivery, RGA, etc.)
  - File name
  - Upload timestamp
- **Notes** - Optional notes provided during the action

### Email Format
- **HTML Email** - Professional formatted HTML version with colors and styling
- **Plain Text Fallback** - Text-only version for email clients that don't support HTML

### Implementation Details

#### Modified Files

**1. `transmittals/email_utils.py`**
- Enhanced `send_external_transmittal_resolution_email()` function
- Added attachment details retrieval and formatting
- Supports dynamic action types including admin override
- Includes timestamp in email body
- Graceful error handling for missing attachments

**2. `transmittals/views_external.py`**
- Added email sending to `external_transmittal_admin_override()` function
- All status change views now call email notification function
- Email sending wrapped in try-except for robustness

#### Key Changes

**Email Utils Enhancement:**
```python
# Get attachment details if any exist
attachments = transmittal.attachments.all().order_by('-uploaded_at')
if attachments.exists():
    # Generate HTML and text sections with attachment details
    for att in attachments:
        att_type = att.attachment_type
        file_name = att.file.name
        uploaded_time = att.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
```

**Admin Override Enhancement:**
```python
try:
    send_external_transmittal_resolution_email(
        transmittal=transmittal,
        action_type='admin_override',
        notes=f'Admin Override: {reason}'
    )
except Exception as e:
    print(f"[WARNING] Email send failed on admin override: {e}")
```

## Email Status Codes

| Action Type | Color | Status | Use Case |
|------------|-------|--------|----------|
| mark_received | Green (#28A745) | ✅ Received | Marked as received |
| full_return | Teal (#17A2B8) | Return Complete | Fully returned |
| partial_return | Amber (#FFC107) | Partial Return | Partially returned |
| paid_sample | Purple (#6F42C1) | Resolved | Converted to paid sample |
| convert_to_keep | Green (#28A745) | Keep | Converted to For Keep |
| closed | Gray (#6C757D) | Closed | Case closed |
| admin_override | Red (#FF6B6B) | Admin Change | Admin status change |

## Attachment Information in Emails

### Attachment Types Tracked
- **Proof of Delivery** - Delivery confirmation when marking received
- **Proof of Full Return** - Documentation of full return
- **Proof of Partial Return** - Documentation of partial return
- **RGA / Deduction Proof** - Return goods authorization
- **RGA Proof** - For Keep conversion proof
- **Custom Types** - Any other attachment type specified

### Example Email Attachment Section
```
📎 ATTACHMENTS UPLOADED:
  • Proof of Delivery: delivery_confirmation_20260305.pdf (Uploaded: 2026-03-05 14:30:22)
  • RGA: return_authorization_form.pdf (Uploaded: 2026-03-05 14:35:45)
```

## Error Handling

All email sending is wrapped in try-except blocks:
- If email fails, a warning is logged to console
- The action (status change) still completes successfully
- User sees success message regardless of email outcome
- Admin can retry via audit trail

## Testing

### Manual Test Steps

1. **Create External Transmittal**
   - Go to Create External Transmittal page
   - Fill in sender, recipient, and description
   - Submit form
   - Check inbox of sender and recipient emails

2. **Mark as Received**
   - Open an "In Transit" transmittal
   - Click "Mark as Received"
   - Upload proof attachment
   - Check emails for notification with attachment details

3. **Record Return**
   - For a received "For Return" transmittal
   - Click "Full Return" or "Partial Return"
   - Upload return proof
   - Check emails for detailed notification

4. **Admin Override**
   - Go to transmittal detail page
   - Use admin dropdown to change status
   - Add optional reason
   - Check emails for admin override notification

## SMTP Configuration

The system uses Django's email backend as configured in `settings.py`:
- `DEFAULT_FROM_EMAIL` - Sender email address
- `EMAIL_BACKEND` - Configured email backend (e.g., Gmail SMTP)
- `EMAIL_HOST` - SMTP server
- `EMAIL_PORT` - SMTP port (usually 587)
- `EMAIL_USE_TLS` - TLS encryption

## Troubleshooting

### Emails Not Sending
1. Check Django email configuration in `settings.py`
2. Verify SMTP credentials are correct
3. Check Django logs for email errors
4. Verify recipient email addresses are valid
5. Test with `python manage.py shell` and manual email send

### Attachments Not Showing in Email
1. Verify attachments were uploaded to the transmittal
2. Check database for attachment records
3. Verify attachment files exist in media directory
4. Check email HTML rendering in email client

### Email Format Issues
1. Some email clients may not support HTML - plain text version provided
2. Check for special characters in notes that need escaping
3. Verify timezone is correct for timestamp display

## Future Enhancements

Possible improvements:
- Add attachment content/URL to email for preview
- Add action-specific email templates
- Add recipient preferences for notification frequency
- Add CC/BCC options based on roles
- Add email delivery tracking
- Add retry mechanism for failed emails
- Add email notification history/log

## Compliance & Audit

All status changes are logged to:
- **Audit Trail** - `ExternalTransmittalAuditTrail` model
- **Email Logs** - Console output and Django logs
- **Attachment Records** - `ExternalTransmittalAttachment` model

For compliance, emails include:
- Timestamp of action
- Who performed the action
- Complete transmittal details
- Proof of action (attachment)

---

**Last Updated:** March 5, 2026  
**Status:** ✅ Implementation Complete
