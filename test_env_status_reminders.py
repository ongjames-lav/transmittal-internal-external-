#!/usr/bin/env python
"""
Test environment for send_status_reminders command
Creates test data: transmittals stuck in same status for 5+ days
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from transmittals.models import Transmittal, Location
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

print("\n" + "="*80)
print("TEST ENVIRONMENT: send_status_reminders")
print("="*80)

# Get or create test users
sender, _ = User.objects.get_or_create(
    username='test_sender_reminder',
    defaults={'email': 'test_sender_reminder@test.com', 'first_name': 'Test', 'last_name': 'Sender'}
)

recipient, _ = User.objects.get_or_create(
    username='test_recipient_reminder',
    defaults={'email': 'test_recipient_reminder@test.com', 'first_name': 'Test', 'last_name': 'Recipient'}
)

custodian, _ = User.objects.get_or_create(
    username='test_custodian_reminder',
    defaults={'email': 'test_custodian_reminder@test.com', 'first_name': 'Test', 'last_name': 'Custodian'}
)

# Get or create test location
location, _ = Location.objects.get_or_create(
    name='TEST_REMINDER',
    defaults={'prefix': 'TRM', 'custodian': custodian}
)

print(f"\nTest Users Created:")
print(f"  - Sender: {sender.username} ({sender.email})")
print(f"  - Recipient: {recipient.username} ({recipient.email})")
print(f"  - Custodian: {custodian.username} ({custodian.email})")

# Create test transmittals stuck in same status for 5+ days
print(f"\nCreating Test Transmittals stuck in same status:")

test_cases = [
    {
        'status': 'in_transit',
        'days_ago': 5,
        'description': '5 days in in_transit (should get reminder)',
        'expected': 'GET REMINDER'
    },
    {
        'status': 'arrived',
        'days_ago': 6,
        'description': '6 days in arrived (should get reminder)',
        'expected': 'GET REMINDER'
    },
    {
        'status': 'picked',
        'days_ago': 8,
        'description': '8 days in picked (should get reminder)',
        'expected': 'GET REMINDER'
    },
    {
        'status': 'in_transit',
        'days_ago': 3,
        'description': '3 days in in_transit (should NOT get reminder)',
        'expected': 'NO REMINDER'
    },
]

created_transmittals = []

for i, test_case in enumerate(test_cases, 1):
    days_ago = test_case['days_ago']
    status_changed_at = timezone.now() - timedelta(days=days_ago)
    
    transmittal = Transmittal.objects.create(
        sender=sender,
        recipient_id=recipient,
        recipient_name=recipient.get_full_name(),
        recipient_email=recipient.email,
        recipient_department='Test Department',
        destination_location=location,
        description=f'Test transmittal - {test_case["description"]}',
        status=test_case['status'],
        status_changed_at=status_changed_at,
    )
    
    created_transmittals.append({
        'transmittal': transmittal,
        'test_case': test_case
    })
    
    print(f"\n  [{i}] {transmittal.reference_number}")
    print(f"      Status: {test_case['status']}")
    print(f"      Status changed at: {status_changed_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"      Days in status: {days_ago}")
    print(f"      Expected: {test_case['expected']}")

print(f"\n" + "="*80)
print(f"NOW TEST THE COMMAND:")
print(f"  python manage.py send_status_reminders")
print(f"="*80)

print(f"\nExpected Results:")
for item in created_transmittals:
    t = item['transmittal']
    expected = item['test_case']['expected']
    print(f"  - {t.reference_number}: {expected}")

print(f"\n" + "="*80 + "\n")
