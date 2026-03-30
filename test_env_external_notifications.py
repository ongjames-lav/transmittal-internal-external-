#!/usr/bin/env python
"""
Test environment for send_external_transmittal_notifications command
Creates test data: external transmittals with upcoming/overdue deadlines
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from transmittals.models import ExternalLocation, ExternalTransmittal
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date

print("\n" + "="*80)
print("TEST ENVIRONMENT: send_external_transmittal_notifications")
print("="*80)

# Get or create test user
user, _ = User.objects.get_or_create(
    username='test_external_user',
    defaults={'email': 'test_external_user@test.com', 'first_name': 'Test', 'last_name': 'User'}
)

# Get or create test external location
ext_location, _ = ExternalLocation.objects.get_or_create(
    name='TEST_EXTERNAL_LOCATION',
    defaults={'address': '123 Test St, Test City', 'contact_person': 'Test Contact'}
)

print(f"\nTest Setup:")
print(f"  - User: {user.username} ({user.email})")
print(f"  - External Location: {ext_location.name}")

# Create test external transmittals with different deadline scenarios
print(f"\nCreating Test External Transmittals:")

today = date.today()

test_cases = [
    {
        'deadline_offset': 0,
        'description': 'Due today',
        'status': 'in_transit',
        'expected': 'GET REMINDER (Due today)'
    },
    {
        'deadline_offset': -1,
        'description': '1 day overdue',
        'status': 'in_transit',
        'expected': 'GET REMINDER (1 day overdue)'
    },
    {
        'deadline_offset': -3,
        'description': '3 days overdue',
        'status': 'in_transit',
        'expected': 'GET REMINDER (3 days overdue)'
    },
    {
        'deadline_offset': 1,
        'description': 'Due tomorrow',
        'status': 'in_transit',
        'expected': 'NO REMINDER (Not yet due)'
    },
    {
        'deadline_offset': -5,
        'description': '5 days overdue (closed)',
        'status': 'closed',
        'expected': 'NO REMINDER (Closed)'
    },
]

created_transmittals = []

for i, test_case in enumerate(test_cases, 1):
    deadline_date = today + timedelta(days=test_case['deadline_offset'])
    
    transmittal = ExternalTransmittal.objects.create(
        sender_email=user.email,
        sender_name='Test Sender',
        recipient_email='external_recipient@example.com',
        recipient_name='External Recipient',
        destination_location=ext_location,
        main_type='for_return',
        date_deadline=deadline_date,
        status=test_case['status'],
        subject=f'Test external - {test_case["description"]}',
    )
    
    created_transmittals.append({
        'transmittal': transmittal,
        'test_case': test_case,
        'deadline_date': deadline_date
    })
    
    days_from_today = (deadline_date - today).days
    print(f"\n  [{i}] {transmittal.reference_number}")
    print(f"      Deadline: {deadline_date.strftime('%Y-%m-%d')}")
    print(f"      Days from today: {days_from_today}")
    print(f"      Status: {test_case['status']}")
    print(f"      Type: {test_case['main_type']}")
    print(f"      Expected: {test_case['expected']}")

print(f"\n" + "="*80)
print(f"NOW TEST THE COMMAND:")
print(f"  python manage.py send_external_transmittal_notifications")
print(f"\nNote: This command only runs on weekdays between 8-10 AM")
print(f"Current time: {timezone.now().strftime('%A %H:%M')}")
print(f"="*80)

print(f"\nExpected Results (if run during weekday 8-10 AM):")
for item in created_transmittals:
    t = item['transmittal']
    expected = item['test_case']['expected']
    print(f"  - {t.reference_number}: {expected}")

print(f"\n" + "="*80 + "\n")
