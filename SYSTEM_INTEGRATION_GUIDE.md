# Complete System Integration - Quick Start

## 🚀 Setup in 3 Steps

### Step 1: Create the Scheduled Task (Run as Administrator)

Open Command Prompt **as Administrator** and run:

```batch
cd C:\Users\CDC.MIS.OJT\Desktop\emailsystem
setup_task_scheduler.bat
```

This will:
- ✓ Check for Admin privileges
- ✓ Create "Email System Notifications" task
- ✓ Schedule for 9:00 AM daily, repeat hourly
- ✓ Run with Administrator privileges

### Step 2: Verify Setup

```batch
python verify_scheduler_setup.py
```

Should show:
- ✓ Task found
- ✓ Batch file found
- ✓ Logs directory exists
- ✓ Django project initialized
- ✓ Database connection successful

### Step 3: Test the Task

#### Option A: Run Manually (Quick Test)
```batch
schtasks /run /tn "Email System Notifications"
```

Wait 10 seconds, then check:
```batch
type logs\notification_scheduler.log
```

#### Option B: Test Individual Commands
```batch
python manage.py auto_receive_transmittals
python manage.py send_status_reminders
python manage.py send_external_transmittal_notifications
```

#### Option C: Run Full Test Suite
```batch
python test_all_commands_comprehensive.py
```

---

## ✅ What Gets Automated

Once set up, these commands run **automatically and hourly**:

### 1️⃣ Auto-Receive Transmittals
- **When:** Every hour
- **What:** Transmittals in 'picked' status for 3+ days
- **Result:** Automatically marked as 'received'
- **Log Entry:** `✓ Auto-received: [ID] (Recipient ID: [X])`

### 2️⃣ Status Reminders
- **When:** Every hour
- **What:** Transmittals stuck 5+ days in same status
- **Result:** Email reminder sent
- **Log Entry:** `✓ Reminder sent for transmittal [ID]`

### 3️⃣ External Transmittal Notifications
- **When:** Every hour (only 8-10 AM on weekdays)
- **What:** External transmittals with deadline alerts
- **Result:** Deadline reminder sent
- **Log Entry:** `✓ Notification sent for [ID]`

---

## 📊 System Architecture

```
Windows Task Scheduler
        ↓
   run_notifications.bat
        ↓
        ├─→ manage.py auto_receive_transmittals
        ├─→ manage.py send_status_reminders
        └─→ manage.py send_external_transmittal_notifications
        
        ↓ (All output logged to)
        
logs/notification_scheduler.log
```

---

## 🔍 Monitor & Troubleshoot

### View Real-Time Logs
```batch
REM Windows Command Prompt
type logs\notification_scheduler.log

REM Or PowerShell (last 20 lines)
Get-Content logs\notification_scheduler.log -Tail 20 -Wait
```

### Check Task in GUI
```batch
taskschd.msc
```
Navigate to: Task Scheduler Library → Find "Email System Notifications"

### View Task History
```batch
schtasks /query /tn "Email System Notifications" /v
```

### Manually Run Task Anytime
```batch
schtasks /run /tn "Email System Notifications"
```

### Disable Task Temporarily
```batch
schtasks /change /tn "Email System Notifications" /disable
```

### Re-Enable Task
```batch
schtasks /change /tn "Email System Notifications" /enable
```

### Delete Task (if needed)
```batch
schtasks /delete /tn "Email System Notifications" /f
```

---

## 📋 File Reference

| File | Purpose |
|------|---------|
| `run_notifications.bat` | Master scheduler script (runs all commands) |
| `setup_task_scheduler.bat` | Auto-creates the scheduled task |
| `verify_scheduler_setup.py` | Verifies everything is set up correctly |
| `test_all_commands_comprehensive.py` | Full test suite for all commands |
| `test_env_auto_receive.py` | Creates test data for auto-receive |
| `test_env_status_reminders.py` | Creates test data for reminders |
| `logs/notification_scheduler.log` | Complete execution log |

---

## 🎯 Key Features

✅ **Fully Automated** - Runs without user intervention
✅ **Logged** - All executions recorded with timestamps
✅ **Recoverable** - Automatic retries on failure
✅ **Safe** - Uses database flags to prevent duplicates
✅ **Testable** - Test environments for verification
✅ **Monitorable** - Log files for audit trail

---

## 🔧 Customization

### Change Schedule Time
```batch
REM Change from 9:00 AM to 8:00 AM
schtasks /change /tn "Email System Notifications" /st 08:00:00
```

### Change Repeat Frequency
```batch
REM Change from every 1 hour to every 2 hours
REM (Note: Requires editing the task in Task Scheduler GUI)
```

### Disable Specific Command
Edit `run_notifications.bat` and comment out (add `REM` prefix):
```batch
REM %PYTHON_PATH% manage.py send_external_transmittal_notifications ...
```

---

## 🆘 Troubleshooting Quick Guide

| Problem | Solution |
|---------|----------|
| Task won't run | Run `setup_task_scheduler.bat` as Administrator |
| "Access Denied" error | Run command prompt as Administrator |
| Task created but no logs | Run `schtasks /run /tn "Email System Notifications"` |
| Logs show errors | Check `logs/notification_scheduler.log` for details |
| Commands not executing | Verify Python path in `run_notifications.bat` |
| Database not updating | Check database connection: `python test_env_auto_receive.py` |

---

## 📞 Support Resources

- **Setup Help:** See [TASK_SCHEDULER_SETUP.md](TASK_SCHEDULER_SETUP.md)
- **Command Info:** See [AUTO_RECEIVE_IMPLEMENTATION.md](AUTO_RECEIVE_IMPLEMENTATION.md)
- **Testing:** See [TEST_SUITE_GUIDE.md](TEST_SUITE_GUIDE.md)
- **Quick Reference:** See [QUICK_REFERENCE_DIGITAL_SIGNATURE.md](QUICK_REFERENCE_DIGITAL_SIGNATURE.md)

---

## ✨ You're All Set!

Your email system is now:
- ✅ Tracking recipients by ID (not email)
- ✅ Auto-receiving after 3 days in picked status
- ✅ Sending status reminders for stuck transmittals
- ✅ Notifying external transmittal deadlines
- ✅ Logging all activity automatically
- ✅ Running on schedule without manual intervention

**No further action needed!** The system runs itself. 🎉

