#!/usr/bin/env python
"""
Test environment for auto_receive_transmittals command
Creates test data: transmittals in 'picked' status for 3+ days
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
print("TEST ENVIRONMENT: auto_receive_transmittals")
print("="*80)

# Get or create test users
sender, _ = User.objects.get_or_create(
    username='test_sender_auto',
    defaults={'email': 'test_sender_auto@test.com', 'first_name': 'Test', 'last_name': 'Sender'}
)

recipient, _ = User.objects.get_or_create(
    username='test_recipient_auto',
    defaults={'email': 'test_recipient_auto@test.com', 'first_name': 'Test', 'last_name': 'Recipient'}
)

custodian, _ = User.objects.get_or_create(
    username='test_custodian_auto',
    defaults={'email': 'test_custodian_auto@test.com', 'first_name': 'Test', 'last_name': 'Custodian'}
)

# Get or create test location
location, _ = Location.objects.get_or_create(
    name='TEST_AUTO_RECEIVE',
    defaults={'prefix': 'TAR', 'custodian': custodian}
)

print(f"\nTest Users Created:")
print(f"  - Sender: {sender.username} ({sender.email})")
print(f"  - Recipient: {recipient.username} ({recipient.email})")
print(f"  - Custodian: {custodian.username} ({custodian.email})")

# Create test transmittals in 'picked' status for 3+ days
print(f"\nCreating Test Transmittals in 'picked' status:")

test_cases = [
    {
        'days_ago': 3,
        'description': '3 days ago (should be auto-received)',
        'expected': 'ELIGIBLE'
    },
    {
        'days_ago': 5,
        'description': '5 days ago (should be auto-received)',
        'expected': 'ELIGIBLE'
    },
    {
        'days_ago': 1,
        'description': '1 day ago (should NOT be auto-received)',
        'expected': 'NOT ELIGIBLE'
    },
]

created_transmittals = []

for i, test_case in enumerate(test_cases, 1):
    days_ago = test_case['days_ago']
    picked_at = timezone.now() - timedelta(days=days_ago)
    
    transmittal = Transmittal.objects.create(
        sender=sender,
        recipient_id=recipient,
        recipient_name=recipient.get_full_name(),
        recipient_email=recipient.email,
        recipient_department='Test Department',
        destination_location=location,
        description=f'Test transmittal - {test_case["description"]}',
        status='picked',
        picked_at=picked_at,
        auto_received=False,
    )
    
    created_transmittals.append({
        'transmittal': transmittal,
        'test_case': test_case
    })
    
    print(f"\n  [{i}] {transmittal.reference_number}")
    print(f"      Status: picked")
    print(f"      Picked at: {picked_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"      Days ago: {days_ago}")
    print(f"      Auto-received: {transmittal.auto_received}")
    print(f"      Expected: {test_case['expected']}")

print(f"\n" + "="*80)
print(f"NOW TEST THE COMMAND:")
print(f"  python manage.py auto_receive_transmittals")
print(f"="*80)

print(f"\nExpected Results:")
for item in created_transmittals:
    t = item['transmittal']
    expected = item['test_case']['expected']
    print(f"  - {t.reference_number}: {expected}")

print(f"\n" + "="*80 + "\n")
