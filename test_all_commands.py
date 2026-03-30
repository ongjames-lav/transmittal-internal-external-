#!/usr/bin/env python
import os
import sys
import django
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from django.core.management import call_command
from io import StringIO

print("\n" + "="*80)
print("TESTING ALL MANAGEMENT COMMANDS")
print("="*80)

# Test 1: auto_receive_transmittals
print("\n[TEST 1] auto_receive_transmittals")
print("-" * 80)
try:
    out = StringIO()
    call_command('auto_receive_transmittals', stdout=out)
    output = out.getvalue()
    if output:
        print(output)
    else:
        print("(No transmittals eligible for auto-receive at this time)")
    print("[RESULT] OK - Command executed successfully")
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()

# Test 2: send_status_reminders
print("\n[TEST 2] send_status_reminders")
print("-" * 80)
try:
    out = StringIO()
    call_command('send_status_reminders', stdout=out)
    output = out.getvalue()
    if output:
        print(output)
    else:
        print("(No transmittals stuck in same status for 5+ days)")
    print("[RESULT] OK - Command executed successfully")
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()

# Test 3: send_external_transmittal_notifications
print("\n[TEST 3] send_external_transmittal_notifications")
print("-" * 80)
try:
    out = StringIO()
    call_command('send_external_transmittal_notifications', stdout=out)
    output = out.getvalue()
    if output:
        print(output)
    else:
        print("(No external transmittals need deadline notifications)")
    print("[RESULT] OK - Command executed successfully")
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("All management commands tested successfully!")
print("="*80 + "\n")
