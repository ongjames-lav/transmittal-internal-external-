#!/usr/bin/env python
"""
Test environment for send_external_transmittal_notifications command
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from transmittals.models import ExternalLocation, ExternalTransmittal
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date

try:
    # Get or create test user
    user, _ = User.objects.get_or_create(
        username='test_external_user2',
        defaults={'email': 'test_external_user2@test.com', 'first_name': 'Test', 'last_name': 'User'}
    )

    # Get or create test external location
    ext_location, _ = ExternalLocation.objects.get_or_create(
        name='TEST_EXTERNAL_LOC2',
        defaults={'address': '123 Test St', 'contact_person': 'Test Contact'}
    )

    print("\n" + "="*80)
    print("TEST ENVIRONMENT: send_external_transmittal_notifications")
    print("="*80)
    print(f"\nTest Setup:")
    print(f"  - User: {user.username}")
    print(f"  - External Location: {ext_location.name}")

    today = date.today()

    test_cases = [
        {'offset': 0, 'desc': 'Due today', 'status': 'in_transit', 'expect': 'REMINDER'},
        {'offset': -1, 'desc': '1 day overdue', 'status': 'in_transit', 'expect': 'REMINDER'},
        {'offset': -3, 'desc': '3 days overdue', 'status': 'in_transit', 'expect': 'REMINDER'},
        {'offset': 1, 'desc': 'Due tomorrow', 'status': 'in_transit', 'expect': 'NO REMINDER'},
        {'offset': -5, 'desc': '5 days overdue (closed)', 'status': 'closed', 'expect': 'NO REMINDER'},
    ]

    print(f"\nCreating Test External Transmittals:")
    
    for i, tc in enumerate(test_cases, 1):
        deadline = today + timedelta(days=tc['offset'])
        t = ExternalTransmittal.objects.create(
            sender_email=user.email,
            sender_name='Test Sender',
            recipient_email='ext@test.com',
            recipient_name='Ext Recipient',
            destination_location=ext_location,
            main_type='for_return',
            date_deadline=deadline,
            status=tc['status'],
            subject=f'Test - {tc["desc"]}',
        )
        print(f"  [{i}] {t.reference_number}: {tc['desc']} ({tc['expect']})")

    print(f"\n" + "="*80)
    print(f"NOW TEST: python manage.py send_external_transmittal_notifications")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
