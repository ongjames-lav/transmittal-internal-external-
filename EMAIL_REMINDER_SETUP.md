# Email Reminder Notification System - PRODUCTION READY

## ✅ System Status: FULLY IMPLEMENTED & TESTED

The email reminder notification system is now **fully integrated** into the transmittal system with professional email formatting.

---

## Overview

This system automatically sends email reminders when a transmittal has been in the same status for **5 days**. When the status changes, the 5-day counter **resets**.

### Example Scenario:
- **Day 1**: Transmittal created → In Transit
- **Day 5**: First reminder sent (still In Transit)
- **Day 4** (after status change): Status changed to Arrived → **Counter resets to 0**
- **Day 5** (in Arrived status): Second reminder sent
- **Day 4** (after status change): Status changed to Picked → **Counter resets to 0**
- **Day 5** (in Picked status): Third reminder sent

---

## Features

✅ **Automatic Reminders**: Sent after 5 days in the same status  
✅ **Status-Specific**: Only applies to **In Transit**, **Arrived**, and **Picked** statuses  
✅ **Recipient-Focused**: Emails sent to sender and receiver only  
✅ **Smart Reset**: Counter resets when status changes  
✅ **No Duplicate Reminders**: Only one reminder per status period  
✅ **Professional Format**: Matches system email styling  
✅ **Detailed Instructions**: Includes next steps based on current status  
✅ **Action Links**: Direct link to transmittal details page  

---

## Email Template Features

### Email Content Includes:
1. **Professional Header** - CDC MFG CORP branding with status badge
2. **Alert Box** - Highlights action required
3. **Two-Column Layout** - Origin and Destination details
4. **Current Status Section** - Reference number, status, days in status, dates
5. **Description** - Transmittal description
6. **Call-to-Action Button** - Direct link to view transmittal
7. **Next Steps** - Status-specific instructions
8. **Professional Footer** - System information

### Statuses That Trigger Reminders:
- **In Transit**: 5 days without arriving
- **Arrived**: 5 days without being picked up
- **Picked**: 5 days without being received

### Statuses That DO NOT Trigger Reminders:
- **Received**: Completed status (no reminder needed)
- **Cancelled**: Completed status (no reminder needed)

---

## How It Works

1. **Initialization**: When a transmittal is created, `status_changed_at` is set to current time
2. **Status Tracking**: When status changes, `status_changed_at` resets and `reminder_sent_at` is cleared
3. **Daily Check**: Management command queries for transmittals:
   - In statuses: `in_transit`, `arrived`, or `picked`
   - Unchanged for 5+ days
   - No reminder sent yet for this status
4. **Email Delivery**: Emails sent to:
   - **Sender** (transmittal creator)
   - **Receiver** (recipient email)

---

## Database Fields

Added to `Transmittal` model:

| Field | Type | Purpose |
|-------|------|---------|
| `status_changed_at` | DateTimeField | When status was last changed |
| `reminder_sent_at` | DateTimeField | When reminder was sent |

---

## Running the Reminder Task

### Option 1: Manual Execution

```bash
python manage.py send_status_reminders
```

### Option 2: Windows Task Scheduler (Automated)

1. Open **Windows Task Scheduler**
2. Click **Create Basic Task**
3. Configure:
   - **Name**: "Email Transmittal Reminders"
   - **Trigger**: Daily at 9:00 AM
   - **Action**: Start a program
     - **Program/script**: `C:\Users\CDC.MIS.OJT\Desktop\emailsystem\run_status_reminders.bat`
     - **Start in**: `C:\Users\CDC.MIS.OJT\Desktop\emailsystem`
4. Click **Finish**

### Option 3: Using the Batch File

Simply run:
```
run_status_reminders.bat
```

Logs are saved to `logs/reminder_task.log`

---

## Tested Email Recipients

✅ **Successfully tested with:**
- `ongjamesdaryl@gmail.com` - Confirmed working
- `mis.team@melawares.com` - Sender email

---

## Email Configuration (Settings)

Current SMTP configuration in `emailsystem/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'box5109.bluehost.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'transmittal.noreply@maxideasmarketing.com'
EMAIL_HOST_PASSWORD = 'wj7i6Zew8Uve'
DEFAULT_FROM_EMAIL = 'Transmittal System <transmittal.noreply@maxideasmarketing.com>'
```

---

## Customization

### Change the 5-Day Threshold

Edit `transmittals/management/commands/send_status_reminders.py`:

```python
five_days_ago = timezone.now() - timedelta(days=7)  # Change to 7 days
```

### Change Email Template

Edit: `transmittals/templates/transmittals/emails/status_reminder.html`

### Change Which Statuses Trigger Reminders

Edit `send_status_reminders.py`:

```python
transmittals_to_remind = Transmittal.objects.filter(
    status_changed_at__lte=five_days_ago,
    reminder_sent_at__isnull=True,
    status__in=['in_transit', 'arrived', 'picked', 'received']  # Add 'received'
)
```

---

## Testing

### Run Test Scripts:

1. **Test the reminder system:**
   ```bash
   python test_reminder.py
   ```

2. **Send actual formatted email:**
   ```bash
   python send_actual_reminder.py
   ```

### Manual Testing in Django Shell:

```python
python manage.py shell

from django.utils import timezone
from datetime import timedelta
from transmittals.models import Transmittal

# Find a transmittal
transmittal = Transmittal.objects.first()

# Set status_changed_at to 6 days ago
transmittal.status_changed_at = timezone.now() - timedelta(days=6)
transmittal.reminder_sent_at = None
transmittal.save()

# Run the command
from transmittals.management.commands.send_status_reminders import Command
Command().handle()
```

---

## Monitoring

### Check Logs

View task execution logs:
```
logs/reminder_task.log
```

Sample log entry:
```
[2026-03-04 09:00:00] Starting status reminder check...
[2026-03-04 09:00:05] Status reminder check completed
```

### Database Query

Check which transmittals have reminders:

```python
from transmittals.models import Transmittal

# Find transmittals with reminders sent
with_reminders = Transmittal.objects.filter(
    reminder_sent_at__isnull=False
).count()

print(f"Reminders sent: {with_reminders}")
```

---

## Troubleshooting

### No emails being sent?

1. **Check SMTP credentials** in `settings.py`
2. **Verify email template** exists at `transmittals/templates/transmittals/emails/status_reminder.html`
3. **Check logs** at `logs/reminder_task.log`
4. **Run manual test:**
   ```bash
   python send_actual_reminder.py
   ```

### Reminders sent twice?

- Check if `reminder_sent_at` is being properly updated
- Verify no duplicate task scheduler entries

### Task Scheduler not running?

1. Open **Task Scheduler**
2. Right-click task → **Run**
3. Check task history for errors
4. Ensure batch file path is absolute

---

## Production Checklist

- [x] Email template matches system styling
- [x] SMTP connection tested and working
- [x] Database migration applied
- [x] Management command created and tested
- [x] Batch file created for scheduling
- [x] Logging configured
- [x] Test recipients confirmed working
- [x] Documentation complete

---

## Support

For issues or questions:
1. Check `logs/reminder_task.log` for errors
2. Run `python send_actual_reminder.py` to test
3. Verify email configuration in `settings.py`
4. Contact system administrator

---

## Version Info

- **System**: Email Transmittal Reminder v1.0
- **Last Updated**: March 4, 2026
- **Status**: ✅ Production Ready
- **Tested**: Yes
- **Email Recipients Verified**: Yes
