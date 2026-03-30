#!/usr/bin/env python
"""
Verify Task Scheduler Setup
Checks if the scheduled task is properly configured and working
"""
import subprocess
import os
import sys
from datetime import datetime

TASK_NAME = "Email System Notifications"
BATCH_FILE = r"C:\Users\CDC.MIS.OJT\Desktop\emailsystem\run_notifications.bat"
PROJECT_ROOT = r"C:\Users\CDC.MIS.OJT\Desktop\emailsystem"
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "notification_scheduler.log")

print("\n" + "="*80)
print("TASK SCHEDULER VERIFICATION")
print("="*80 + "\n")

# Check 1: Task exists
print("[CHECK 1] Verify scheduled task exists...")
try:
    result = subprocess.run(
        f'schtasks /query /tn "{TASK_NAME}"',
        capture_output=True,
        text=True,
        shell=True
    )
    if result.returncode == 0:
        print("  ✓ Task found: %s" % TASK_NAME)
        print("\n  Task Status:")
        for line in result.stdout.split('\n'):
            if 'Ready' in line or 'Running' in line or 'Disabled' in line:
                print("    " + line.strip())
    else:
        print("  ✗ Task NOT found: %s" % TASK_NAME)
        print("\n  To create the task, run:")
        print("    setup_task_scheduler.bat")
except Exception as e:
    print("  ✗ Error checking task: %s" % str(e))

# Check 2: Batch file exists
print("\n[CHECK 2] Verify batch file exists...")
if os.path.exists(BATCH_FILE):
    print("  ✓ Found: %s" % BATCH_FILE)
else:
    print("  ✗ NOT found: %s" % BATCH_FILE)

# Check 3: Logs directory
print("\n[CHECK 3] Verify logs directory...")
if os.path.exists(LOGS_DIR):
    print("  ✓ Directory exists: %s" % LOGS_DIR)
else:
    print("  ✗ Directory NOT found: %s" % LOGS_DIR)
    try:
        os.makedirs(LOGS_DIR)
        print("  ✓ Created: %s" % LOGS_DIR)
    except Exception as e:
        print("  ✗ Error creating directory: %s" % str(e))

# Check 4: Log file exists and has recent entries
print("\n[CHECK 4] Verify logs...")
if os.path.exists(LOG_FILE):
    print("  ✓ Found: %s" % LOG_FILE)
    
    # Check file size
    file_size = os.path.getsize(LOG_FILE)
    print("  File size: %d bytes" % file_size)
    
    # Check for recent entries
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            if lines:
                print("  Last 5 entries:")
                for line in lines[-5:]:
                    print("    " + line.rstrip())
            else:
                print("  (Log file is empty - task may not have run yet)")
    except Exception as e:
        print("  Error reading log: %s" % str(e))
else:
    print("  ✗ Log file NOT found: %s" % LOG_FILE)
    print("  (This is normal if task hasn't run yet)")

# Check 5: Django project
print("\n[CHECK 5] Verify Django project...")
os.chdir(PROJECT_ROOT)
try:
    # Try to import Django
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
    django.setup()
    print("  ✓ Django project initialized successfully")
    
    # Check management commands exist
    from transmittals.models import Transmittal
    print("  ✓ Database connection successful")
    
    # Count records
    auto_received = Transmittal.objects.filter(auto_received=True).count()
    with_reminders = Transmittal.objects.filter(reminder_sent_at__isnull=False).count()
    print("  Database Status:")
    print("    - Total transmittals: %d" % Transmittal.objects.count())
    print("    - Auto-received: %d" % auto_received)
    print("    - With reminders sent: %d" % with_reminders)
    
except Exception as e:
    print("  ✗ Error: %s" % str(e))

# Summary
print("\n" + "="*80)
print("VERIFICATION SUMMARY")
print("="*80 + "\n")

print("If all checks show ✓, your system is ready!")
print("\nNext Steps:")
print("  1. Test the task: schtasks /run /tn \"%s\"" % TASK_NAME)
print("  2. Wait a moment and check logs")
print("  3. View in Task Scheduler: taskschd.msc")
print("\nFor help, see: TASK_SCHEDULER_SETUP.md\n")
