#!/usr/bin/env python
"""
Test script for the email reminder notification system.
This script:
1. Creates or gets a test transmittal
2. Sets status_changed_at to 6+ days ago
3. Clears reminder_sent_at to allow reminder to be sent
4. Runs the send_status_reminders command
"""
import os
import django
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from transmittals.models import Transmittal, Location
from transmittals.management.commands.send_status_reminders import Command

def test_reminder():
    print("=" * 70)
    print("EMAIL REMINDER NOTIFICATION TEST")
    print("=" * 70)
    
    # Get or create test user
    sender = User.objects.filter(is_active=True).first()
    if not sender:
        print("❌ No active user found. Please create a user first.")
        return
    
    print(f"✓ Using user: {sender.username} ({sender.email})")
    
    # Get a location
    location = Location.objects.filter(is_active=True).first()
    if not location:
        print("❌ No active location found. Please create a location first.")
        return
    
    # Test email
    test_recipient_email = 'ongjamesdaryl@gmail.com'
    
    # Get or create test transmittal
    transmittal, created = Transmittal.objects.get_or_create(
        reference_number='TEST-20260304-9999',
        defaults={
            'sender': sender,
            'recipient_name': 'Test Recipient',
            'recipient_email': test_recipient_email,
            'recipient_department': 'Testing Department',
            'destination_location': location,
            'origin_location': location,
            'description': 'Test transmittal for reminder notification',
            'status': 'in_transit',
        }
    )
    
    # If transmittal exists, update the recipient email
    if not created:
        transmittal.recipient_email = test_recipient_email
        transmittal.save(update_fields=['recipient_email'])
    
    if created:
        print(f"✓ Created test transmittal: {transmittal.reference_number}")
    else:
        print(f"✓ Using existing transmittal: {transmittal.reference_number}")
    
    # Set status_changed_at to 6 days ago
    six_days_ago = timezone.now() - timedelta(days=6)
    transmittal.status_changed_at = six_days_ago
    transmittal.reminder_sent_at = None  # Clear any previous reminders
    transmittal.save(update_fields=['status_changed_at', 'reminder_sent_at'])
    
    print(f"\n📅 Test Configuration:")
    print(f"   Reference: {transmittal.reference_number}")
    print(f"   Status: {transmittal.get_status_display()}")
    print(f"   Status Changed At: {transmittal.status_changed_at}")
    print(f"   Days in Status: {(timezone.now() - transmittal.status_changed_at).days}")
    print(f"   Sender: {transmittal.sender.email}")
    print(f"   Recipient: {transmittal.recipient_email}")
    print(f"   Reminder Sent At: {transmittal.reminder_sent_at}")
    
    # Run the reminder command
    print(f"\n🚀 Running send_status_reminders command...\n")
    print("-" * 70)
    
    command = Command()
    try:
        command.handle()
        print("-" * 70)
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return
    
    # Check if reminder was sent
    transmittal.refresh_from_db()
    
    if transmittal.reminder_sent_at:
        print(f"\n✅ SUCCESS! Reminder email was sent")
        print(f"   Reminder Sent At: {transmittal.reminder_sent_at}")
        print(f"\n📧 Email was sent to:")
        print(f"   - Sender: {transmittal.sender.email}")
        print(f"   - Recipient: {transmittal.recipient_email}")
    else:
        print(f"\n❌ Reminder was NOT sent")
        print(f"   Please check:")
        print(f"   1. EMAIL_BACKEND is configured in settings.py")
        print(f"   2. DEFAULT_FROM_EMAIL is set")
        print(f"   3. Email template exists at: transmittals/templates/transmittals/emails/status_reminder.html")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    test_reminder()
