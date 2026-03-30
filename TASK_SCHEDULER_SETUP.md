# Task Scheduler Setup Guide

## Overview

The email system runs three automated management commands via Windows Task Scheduler:

1. **auto_receive_transmittals** - Auto-receives transmittals after 3 days in 'picked' status
2. **send_status_reminders** - Sends reminders for transmittals stuck 5+ days in same status
3. **send_external_transmittal_notifications** - Sends deadline reminders for external transmittals (weekdays 8-10 AM only)

All commands are orchestrated through `run_notifications.bat`

---

## Step 1: Create the Scheduled Task

### Option A: Using GUI (Easier)

1. **Open Task Scheduler**
   - Press `Win + R`
   - Type `taskschd.msc`
   - Press Enter

2. **Create Basic Task**
   - Right-click "Task Scheduler Library" → Select "Create Basic Task"
   - Name: `Email System Notifications`
   - Description: `Runs auto-receive, status reminders, and external transmittal notifications`

3. **Set Trigger**
   - Click "Next"
   - Select "Daily"
   - Set time: `9:00 AM` (or your preferred time)
   - Check "Repeat task every: 1 hour" (optional, for frequent checks)
   - Click "Next"

4. **Set Action**
   - Select "Start a program"
   - Program: `C:\Users\CDC.MIS.OJT\Desktop\emailsystem\run_notifications.bat`
   - Start in: `C:\Users\CDC.MIS.OJT\Desktop\emailsystem`
   - Click "Next"

5. **Finish**
   - Check "Open the Properties dialog for this task when I click Finish"
   - Click "Finish"

6. **Configure Additional Settings** (in Properties dialog)
   - **General tab:**
     - Check "Run with highest privileges"
     - Run whether user is logged in or not: Select this option
   - **Triggers tab:**
     - Right-click trigger → "Edit"
     - Check "Repeat task every: 1 hour"
     - Click "OK"
   - **Settings tab:**
     - Check "If the task fails, restart every: 1 minute"
     - Number of retries: `3`
     - Stop the task if it runs longer than: `30 minutes`
   - **Conditions tab:**
     - (Leave defaults or adjust as needed)
   - Click "OK" to save

### Option B: Using PowerShell (Advanced)

```powershell
# Run PowerShell as Administrator, then:

$taskName = "Email System Notifications"
$action = New-ScheduledTaskAction -Execute "C:\Users\CDC.MIS.OJT\Desktop\emailsystem\run_notifications.bat" -WorkingDirectory "C:\Users\CDC.MIS.OJT\Desktop\emailsystem"
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -RunLevel Highest
```

---

## Step 2: Test the Setup

### Test 1: Run Task Manually
1. Open Task Scheduler
2. Find "Email System Notifications"
3. Right-click → "Run"
4. Check logs: Open `logs\notification_scheduler.log`
5. You should see entries for all three commands

### Test 2: Verify Commands
```bash
# Test auto-receive
python manage.py auto_receive_transmittals

# Test status reminders
python manage.py send_status_reminders

# Test external notifications (only runs on weekdays 8-10 AM)
python manage.py send_external_transmittal_notifications
```

### Test 3: Run Comprehensive Test Suite
```bash
python test_all_commands_comprehensive.py
```

---

## Step 3: Monitor Execution

### Check Logs
```bash
# View latest log entries
type logs\notification_scheduler.log | tail -50

# Or in PowerShell
Get-Content logs\notification_scheduler.log -Tail 50
```

### Task Scheduler History
1. Open Task Scheduler
2. Find "Email System Notifications"
3. Click "History" tab to see execution history
4. Look for "Task Started" and "Task Completed" entries

---

## Scheduling Strategy

### Recommended Configuration
- **Frequency:** Every 1 hour (checks 24 times daily)
- **Start Time:** 8:00 AM
- **Duration:** Runs until end of day
- **Days:** All days (commands internally check conditions)

**Why hourly?**
- Catches auto-receives as soon as 3-day threshold is met
- Sends status reminders promptly
- External notifications only run 8-10 AM (auto-checked in command)

### Alternative: Just Once Daily
If you prefer simpler setup:
- **Frequency:** Once daily
- **Time:** 9:00 AM
- Less responsive but simpler to manage

---

## What Each Command Does

### 1. auto_receive_transmittals
- **Runs:** Hourly (or at scheduled time)
- **Action:** Auto-receives transmittals in 'picked' status for 3+ days
- **Sets:**
  - Status → 'received'
  - received_at → current time
  - received_by → recipient_id
  - auto_received → True
- **Sends:** Status notification with auto-received flag

### 2. send_status_reminders
- **Runs:** Hourly (or at scheduled time)
- **Action:** Sends reminders for transmittals stuck 5+ days in same status
- **Statuses Checked:** in_transit, arrived, picked
- **Sends:** Email reminder to appropriate recipient

### 3. send_external_transmittal_notifications
- **Runs:** Hourly (or at scheduled time)
- **Action:** Only executes on weekdays between 8-10 AM
- **Sends:** Deadline reminders for external transmittals

---

## Logging

All command output goes to: `logs\notification_scheduler.log`

Each execution logs:
- Start time
- Command name
- Success/Error status
- Exit codes

Example log entry:
```
[3/6/2026 9:00:00 AM] Starting Auto-Receive Transmittals Job...
[3/6/2026 9:00:02 AM] Auto-receive job completed successfully.

[3/6/2026 9:00:02 AM] Starting Status Reminders Job...
[3/6/2026 9:00:03 AM] Status reminders job completed successfully.

[3/6/2026 9:00:03 AM] Starting External Transmittal Notification Job...
[3/6/2026 9:00:05 AM] Notification job completed successfully.
```

---

## Troubleshooting

### Issue: Task runs but commands fail

**Solution:**
1. Check `logs\notification_scheduler.log` for error messages
2. Verify Python path in `run_notifications.bat` is correct
3. Test command manually: `python manage.py auto_receive_transmittals`
4. Check database connection

### Issue: Task doesn't run

**Solution:**
1. Verify task is enabled in Task Scheduler
2. Check that task has "Run with highest privileges" enabled
3. Verify Python path is correct: `C:\Users\CDC.MIS.OJT\Desktop\emailsystem\venv\Scripts\python.exe`
4. Test batch file manually: Double-click `run_notifications.bat`

### Issue: "Access Denied" error

**Solution:**
1. Run Task Scheduler as Administrator
2. Make sure to set "Run with highest privileges" when creating task
3. Ensure user account has read/write permissions to `logs` directory

### Issue: Commands run but database isn't updated

**Solution:**
1. Verify Django settings are correct
2. Check database path in settings
3. Run test: `python test_env_auto_receive.py` then `python manage.py auto_receive_transmittals`
4. Check if transmittals meet criteria (3+ days in status, etc.)

---

## Verification Checklist

- [ ] Task Scheduler opens without errors
- [ ] "Email System Notifications" task is created and enabled
- [ ] Trigger is set to daily at 9:00 AM (or preferred time)
- [ ] Action points to `run_notifications.bat`
- [ ] Task has "Run with highest privileges" enabled
- [ ] Manual test run completes without errors
- [ ] `logs\notification_scheduler.log` has recent entries
- [ ] Commands have executed at least once successfully
- [ ] Database shows auto-received transmittals with timestamps
- [ ] Notification emails have been sent (if SMTP configured)

---

## Production Deployment

When deploying to production:

1. **Verify all settings in** `run_notifications.bat`
   - Correct Python path
   - Correct project root
   - Logs directory exists or can be created

2. **Test all commands** before scheduling:
   ```bash
   python manage.py auto_receive_transmittals
   python manage.py send_status_reminders
   python manage.py send_external_transmittal_notifications
   ```

3. **Run comprehensive test suite**:
   ```bash
   python test_all_commands_comprehensive.py
   ```

4. **Create scheduled task** with administrator privileges

5. **Monitor logs** for first 24 hours to ensure everything works

6. **Set email alerts** in Task Scheduler (optional) to notify on failures

---

## Quick Reference

| Command | Frequency | Trigger Time | Effect |
|---------|-----------|--------------|--------|
| auto_receive_transmittals | Every 1 hour | Any time | Auto-receives 3+ day old picks |
| send_status_reminders | Every 1 hour | Any time | Sends 5+ day stuck status reminders |
| send_external_transmittal_notifications | Every 1 hour | Weekdays 8-10 AM only | Sends deadline reminders |

All commands are safe to run frequently - they use database flags to prevent duplicates.

