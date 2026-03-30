#!/usr/bin/env python
"""
Script to create a test transmittal due today
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from transmittals.models import Transmittal, Location

# Get or create admin user
try:
    sender = User.objects.get(username='admin')
except User.DoesNotExist:
    print("❌ Admin user not found. Please create an admin user first.")
    exit(1)

# Get first available location
try:
    location = Location.objects.first()
    if not location:
        print("❌ No locations found. Please create a location first.")
        exit(1)
except Location.DoesNotExist:
    print("❌ No locations found. Please create a location first.")
    exit(1)

# Create transmittal with in_transit status (5+ days old)
transmittal = Transmittal.objects.create(
    sender=sender,
    sender_department="Operations",
    origin_location=location,
    recipient_name="Test Recipient Today",
    recipient_email="ongjamesdaryl@gmail.com",
    recipient_company="Test Company",
    recipient_department="Receiving",
    destination_location=location,
    description="Test transmittal due today for reminders",
    remarks="This transmittal is in transit for 5+ days",
    status='in_transit',
    # Set status_changed_at to 6 days ago to trigger 5-day reminder
    status_changed_at=timezone.now() - timedelta(days=6)
)

print(f"\n✅ Transmittal created successfully!")
print(f"   Reference: {transmittal.reference_number}")
print(f"   Status: {transmittal.get_status_display()}")
print(f"   Status Changed: {transmittal.status_changed_at}")
print(f"   Days in Status: {(timezone.now() - transmittal.status_changed_at).days}")
print(f"   Recipient: {transmittal.recipient_email}")
print(f"\n📧 This transmittal will receive a reminder email when the command runs!")
