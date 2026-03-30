# External Transmittal System - Windows Task Scheduler Setup

## Overview

The External Transmittal System sends automatic deadline reminder emails for "For Return" type transmittals on a scheduled basis. Reminders are sent on specific escalation days: deadline day, +1, +3, and +7 days overdue—but **only on weekdays (Monday-Friday) at 9:00 AM**.

This guide explains how to set up the automated notification system using **Windows Task Scheduler**.

---

## Prerequisites

1. **Virtual Environment Active**: The Django application must run in a Python virtual environment
2. **Python Path**: Know the path to `python.exe` in your virtual environment
3. **Project Directory**: Know the full path to your emailsystem project directory
4. **Admin Rights**: You need local administrator privileges to create scheduled tasks

---

## Step-by-Step Setup

### Step 1: Locate Your Virtual Environment Python Path

Navigate to your project root and find your virtual environment:

```
C:\Users\CDC.MIS.OJT\Desktop\emailsystem\venv\Scripts\python.exe
```

Or if using a different venv name, adjust accordingly.

### Step 2: Create the Batch Script

Create a batch file that will run the Django management command. This is necessary because Task Scheduler runs commands in a limited environment.

**File:** `C:\Users\CDC.MIS.OJT\Desktop\emailsystem\run_notifications.bat`

**Content:**
```batch
@echo off
REM External Transmittal Deadline Notifications Script
REM Runs daily at 9:00 AM (weekdays only)

cd /d C:\Users\CDC.MIS.OJT\Desktop\emailsystem

REM Activate virtual environment and run management command
C:\Users\CDC.MIS.OJT\Desktop\emailsystem\venv\Scripts\python.exe manage.py send_external_transmittal_notifications

REM Log execution (optional)
echo %date% %time% - Notification job executed >> logs\notification_scheduler.log
```

**Important Notes:**
- Replace paths with your actual paths
- The `/d` flag in `cd /d` allows changing drives
- Create a `logs` folder in your project if it doesn't exist: `mkdir C:\Users\CDC.MIS.OJT\Desktop\emailsystem\logs`

### Step 3: Test the Batch Script

Before scheduling, test the batch file manually to ensure it works:

1. Open Command Prompt (Win + R, type `cmd`, press Enter)
2. Navigate to the project folder: `cd C:\Users\CDC.MIS.OJT\Desktop\emailsystem`
3. Run the batch file: `run_notifications.bat`
4. Verify output indicates successful execution

### Step 4: Open Windows Task Scheduler

1. Press **Win + R**
2. Type: `taskschd.msc`
3. Press **Enter**

Windows Task Scheduler opens.

### Step 5: Create a New Basic Task

1. Click **Action** → **Create Basic Task**
2. Enter these details:

   **Name:** `External Transmittal Daily Notifications`
   
   **Description:** `Sends deadline reminder emails for external transmittals (For Return type). Runs weekdays at 9:00 AM on a schedule calculated by the application.`
   
   **Click:** Next

### Step 6: Set the Trigger (Schedule)

1. Select: **Daily**
2. Click: **Next**
3. Configure:
   - **Start date:** (today's date)
   - **Recur every:** 1 day
   - **Click:** Next

### Step 7: Set the Action

1. Select: **Start a program**
2. Click: **Next**
3. Configure:
   - **Program/script:** `C:\Users\CDC.MIS.OJT\Desktop\emailsystem\run_notifications.bat`
   - **Start in (Optional):** `C:\Users\CDC.MIS.OJT\Desktop\emailsystem`
   - **Click:** Next

### Step 8: Set Conditions (Optional but Recommended)

1. **Power:** Uncheck "Start the task only if the computer is on AC power"
2. **Network:** No network requirement
3. **Click:** Next

### Step 9: Review and Create

1. Review all settings
2. Check: **Open the Properties dialog for this task when I click Finish**
3. Click: **Finish**

### Step 10: Adjust Timing in Properties

The task scheduler will run at the time you configured (daily), but the Django management command internally checks:
- **Is it a weekday?** (Monday-Friday)
- **Is it between 8-10 AM?** (flexible window around 9 AM)

If these conditions aren't met, the command exits silently without sending emails.

**To adjust the run time:**

1. Properties dialog should open
2. Go to **Triggers** tab
3. Click **Edit**
4. Set **Start time:** `09:00:00`
5. Click **OK**

---

## Verification

### Check Task Creation

1. In Task Scheduler, expand: **Task Scheduler Library**
2. Look for: **External Transmittal Daily Notifications**
3. Status should show: **Ready**

### Check Execution History

1. Click the task in Task Scheduler
2. Go to **History** tab
3. You should see entries showing when the task ran
4. Check **Last Run Result:** Should be `The operation completed with an exit code (0).`

### Check Logs

Monitor the log file created by the batch script:

```
C:\Users\CDC.MIS.OJT\Desktop\emailsystem\logs\notification_scheduler.log
```

Expected content:
```
03/02/2026 09:05:32 - Notification job executed
03/02/2026 09:05:33 - Notification job executed
```

### Check Django Application Logs

The Django management command outputs detailed logs. To see them:

1. Modify `run_notifications.bat` to capture output:

```batch
@echo off
cd /d C:\Users\CDC.MIS.OJT\Desktop\emailsystem

REM Capture both stdout and stderr
C:\Users\CDC.MIS.OJT\Desktop\emailsystem\venv\Scripts\python.exe manage.py send_external_transmittal_notifications >> logs\notification_scheduler.log 2>&1

echo %date% %time% - Job completed >> logs\notification_scheduler.log
```

---

## Notification Schedule

The system sends notifications on these escalation levels:

| Days Overdue | Notification | Condition |
|---|---|---|
| 0 | **DEADLINE TODAY** | Sent on deadline day |
| +1 | **1 DAY OVERDUE** | Sent 1 day after deadline |
| +3 | **3 DAYS OVERDUE** | Sent 3 days after deadline |
| +7 | **7 DAYS OVERDUE (FINAL)** | Sent 7 days after deadline |

**Weekday Requirement:** Notifications ONLY send on weekdays (Monday-Friday). If the deadline falls on a weekend, the first notification is sent on Monday.

---

## Troubleshooting

### Task Doesn't Run at 9 AM

**Problem:** Task runs but not at the expected time.

**Solution:** 
- Task Scheduler runs at system time
- Verify system timezone is set to: **Asia/Manila (UTC+8)**
- Settings > Time & Language > Date & Time
- Check: **Set time automatically** is enabled

### No Emails Sent

**Problem:** Task runs successfully but no emails are sent.

**Possible Causes:**
1. No transmittals have passed their deadline
2. All overdue transmittals are already closed
3. Emails were already sent earlier the same day

**Debug:**
- Check Django logs for error messages
- Verify SMTP email configuration in `emailsystem/settings.py`
- Test sending a manual email via Django shell

### "The operation completed with an exit code (1)"

**Problem:** Task failed with error code 1.

**Likely Causes:**
1. Python path is incorrect
2. Virtual environment activation failed
3. Django project path is incorrect
4. Database is locked or inaccessible

**Solution:**
1. Test the batch script manually
2. Verify all file paths are correct
3. Check database permissions
4. Review Django error logs

### Task Runs But Log File Not Created

**Problem:** No log file appears in the logs folder.

**Solution:**
1. Ensure `logs` folder exists: `mkdir C:\Users\CDC.MIS.OJT\Desktop\emailsystem\logs`
2. Grant write permissions to the folder
3. Check that SYSTEM account (Task Scheduler's default user) has access

---

## Manual Testing

To test the notification system without waiting for the schedule:

```bash
# From project root in Command Prompt
cd C:\Users\CDC.MIS.OJT\Desktop\emailsystem

# Activate virtual environment
venv\Scripts\activate.bat

# Run the management command manually
python manage.py send_external_transmittal_notifications

# Check output for successful execution
```

---

## Email Configuration

Emails are sent using the SMTP settings configured in `emailsystem/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'box5109.bluehost.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@example.com'
```

**Note:** Update these settings with your actual mail server credentials before scheduling.

---

## Maintenance & Monitoring

### Weekly Check

1. Review log file for successful executions
2. Verify email confirmations from test transmittals
3. Check Task Scheduler status

### Monthly Review

1. Verify emails are reaching recipients
2. Monitor for undelivered notifications (bounce-backs)
3. Check for any error patterns in logs

### Seasonal Updates

- Daylight Saving Time may affect timezone handling
- After system updates, re-verify task still runs
- Test email functionality after mail server maintenance

---

## Support & Advanced Configuration

### Run at Different Time

To change execution time to a different hour (e.g., 8:00 AM):

1. Task Scheduler → Properties
2. Triggers tab → Edit
3. Change start time
4. Click OK

### Run on Weekends

To include weekends in notifications:

Edit `transmittals/management/commands/send_external_transmittal_notifications.py`:

Change:
```python
is_weekday = weekday < 5  # Monday to Friday
```

To:
```python
is_weekday = True  # Every day
```

### Multiple Runs Per Day

Create multiple tasks with different times (e.g., 9 AM and 3 PM):

1. Create second basic task with same settings
2. Set different start time in triggers
3. Point to same batch file

---

## Rollback

To disable notifications without deleting the task:

1. Task Scheduler → Find the task
2. Right-click → **Disable**
3. Task will not run until **Enabled** again

To completely remove:

1. Right-click → **Delete**
2. Confirm deletion

---

## Summary

The External Transmittal System now has **automated deadline reminders** running:
- ✅ **Daily** at 9:00 AM
- ✅ **Weekdays only** (Mon-Fri)
- ✅ **Escalating notifications** on days 0, +1, +3, +7
- ✅ **Logged** for audit trail
- ✅ **Resilient** to missed runs (runs next available weekday)

Contact your system administrator if the scheduled task fails to execute.
