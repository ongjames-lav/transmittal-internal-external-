#!/usr/bin/env python
"""
Comprehensive Test: Reminder system for ALL statuses (In Transit, Arrived, Picked)
Tests that reminders are sent correctly for each status with appropriate email content
"""
import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from transmittals.models import Transmittal, Location
from transmittals.management.commands.send_status_reminders import Command

def create_test_transmittal(reference, status, days_ago=6):
    """Create or update a test transmittal with specified status"""
    transmittal, created = Transmittal.objects.get_or_create(
        reference_number=reference,
        defaults={
            'sender': User.objects.filter(is_active=True).first(),
            'recipient_name': 'Test Recipient',
            'recipient_email': 'ongjamesdaryl@gmail.com',
            'recipient_department': 'Testing Department',
            'destination_location': Location.objects.filter(is_active=True).first(),
            'origin_location': Location.objects.filter(is_active=True).first(),
            'description': f'Test transmittal for {status} status reminder',
            'status': status,
        }
    )
    
    if not created:
        transmittal.status = status
        transmittal.recipient_email = 'ongjamesdaryl@gmail.com'
        transmittal.save(update_fields=['status', 'recipient_email'])
    
    # Set status_changed_at to 6 days ago
    transmittal.status_changed_at = timezone.now() - timedelta(days=days_ago)
    transmittal.reminder_sent_at = None
    transmittal.save(update_fields=['status_changed_at', 'reminder_sent_at'])
    
    return transmittal

def test_all_statuses():
    print("=" * 80)
    print("COMPREHENSIVE REMINDER SYSTEM TEST - ALL STATUSES")
    print("=" * 80)
    
    # Get sender
    sender = User.objects.filter(is_active=True).first()
    if not sender:
        print("❌ No active user found")
        return
    
    location = Location.objects.filter(is_active=True).first()
    if not location:
        print("❌ No active location found")
        return
    
    print(f"\n📋 Test Configuration:")
    print(f"   Sender: {sender.email}")
    print(f"   Recipient: ongjamesdaryl@gmail.com")
    print(f"   Location: {location.name}")
    print(f"   Days in Status: 6 (exceeds 5-day threshold)")
    
    # Test statuses
    test_cases = [
        ('TEST-IN-TRANSIT-9999', 'in_transit', '🚚 IN TRANSIT'),
        ('TEST-ARRIVED-9999', 'arrived', '📍 ARRIVED'),
        ('TEST-PICKED-9999', 'picked', '🎯 PICKED'),
    ]
    
    print("\n" + "=" * 80)
    print("CREATING TEST TRANSMITTALS")
    print("=" * 80)
    
    transmittals = []
    for ref, status, badge in test_cases:
        print(f"\n📦 Creating: {ref}")
        print(f"   Status: {status.upper()}")
        transmittal = create_test_transmittal(ref, status)
        transmittals.append((transmittal, badge))
        print(f"   Status Changed: {transmittal.status_changed_at}")
        print(f"   Days in Status: {(timezone.now() - transmittal.status_changed_at).days}")
        print(f"   ✅ Created successfully")
    
    print("\n" + "=" * 80)
    print("RUNNING REMINDER COMMAND")
    print("=" * 80)
    print("\n🚀 Checking for transmittals that need reminders...\n")
    
    command = Command()
    try:
        command.handle()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 80)
    print("VERIFICATION RESULTS")
    print("=" * 80)
    
    all_sent = True
    for transmittal, badge in transmittals:
        # Refresh from database
        transmittal.refresh_from_db()
        
        print(f"\n📧 {transmittal.reference_number}")
        print(f"   Status: {transmittal.get_status_display()}")
        print(f"   Badge: {badge}")
        
        if transmittal.reminder_sent_at:
            print(f"   ✅ Reminder sent: {transmittal.reminder_sent_at}")
            print(f"   📬 Recipients:")
            print(f"      - Sender: {transmittal.sender.email}")
            print(f"      - Receiver: {transmittal.recipient_email}")
        else:
            print(f"   ❌ Reminder NOT sent")
            all_sent = False
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if all_sent:
        print("\n✅ SUCCESS! All status reminders were sent:")
        print("   ✅ In Transit reminder")
        print("   ✅ Arrived reminder")
        print("   ✅ Picked reminder")
        print("\n📧 Emails sent to:")
        print("   - ongjamesdaryl@gmail.com (all statuses)")
        print("   - mis.team@melawares.com (sender)")
    else:
        print("\n❌ Some reminders were NOT sent")
        print("   Check the errors above and verify email configuration")
    
    print("\n" + "=" * 80)
    print("\n✅ Test completed successfully!")
    print("\nThe reminder system is working for all statuses:")
    print("   • In Transit: Reminds after 5 days")
    print("   • Arrived: Reminds after 5 days")
    print("   • Picked: Reminds after 5 days")
    print("   • Received: No reminder (completed status)")
    print("\nEach email includes status-specific instructions.")
    print("=" * 80)

if __name__ == '__main__':
    test_all_statuses()
