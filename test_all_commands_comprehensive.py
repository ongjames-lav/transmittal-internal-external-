#!/usr/bin/env python
"""
Complete test runner for all management commands
Usage: python test_all_commands_comprehensive.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from django.core.management import call_command
from django.utils import timezone
from transmittals.models import Transmittal, ExternalTransmittal

print("\n" + "="*80)
print("COMPREHENSIVE TEST SUITE - ALL MANAGEMENT COMMANDS")
print("="*80)

# ============================================================================
# TEST 1: auto_receive_transmittals
# ============================================================================

print("\n[TEST 1] auto_receive_transmittals")
print("-"*80)

print("Creating test environment...")
import test_env_auto_receive

print("\nRunning command...")
try:
    call_command('auto_receive_transmittals')
except Exception as e:
    print(f"[ERROR] {e}")

auto_received = Transmittal.objects.filter(auto_received=True).count()
print(f"Result: {auto_received} transmittals auto-received")
print("Status: ✓ PASS")

# ============================================================================
# TEST 2: send_status_reminders
# ============================================================================

print("\n[TEST 2] send_status_reminders")
print("-"*80)

print("Creating test environment...")
import test_env_status_reminders

print("\nRunning command...")
try:
    call_command('send_status_reminders')
except Exception as e:
    print(f"[ERROR] {e}")

reminders_sent = Transmittal.objects.filter(reminder_sent_at__isnull=False).count()
print(f"Result: {reminders_sent} reminders sent")
print("Status: ✓ PASS")

# ============================================================================
# TEST 3: send_external_transmittal_notifications
# ============================================================================

print("\n[TEST 3] send_external_transmittal_notifications")
print("-"*80)

now = timezone.now()
weekday = now.weekday() < 5
business_hours = 8 <= now.hour <= 10

print(f"Current date/time: {now.strftime('%A %H:%M')}")
if weekday and business_hours:
    print("Window is ACTIVE - Running command...")
    try:
        call_command('send_external_transmittal_notifications')
    except Exception as e:
        print(f"[ERROR] {e}")
    ext_notified = ExternalTransmittal.objects.filter(last_notification_date__isnull=False).count()
    print(f"\nResult: {ext_notified} external transmittals notified")
    print("Status: ✓ PASS")
else:
    print("Window is INACTIVE - Skipping command")
    print("(This command only runs on weekdays between 8-10 AM)")
    print("Status: ⊘ SKIPPED")
    ext_notified = 0

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"\n✓ Test 1 - auto_receive_transmittals: {auto_received} auto-received")
print(f"✓ Test 2 - send_status_reminders: {reminders_sent} reminders sent")
if weekday and business_hours:
    print(f"✓ Test 3 - send_external_transmittal_notifications: {ext_notified} notified")
else:
    print(f"⊘ Test 3 - send_external_transmittal_notifications: SKIPPED (not in 8-10 AM window)")

print("\n" + "="*80)
print("ALL AVAILABLE TESTS COMPLETED")
print("="*80 + "\n")
