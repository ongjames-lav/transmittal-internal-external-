import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from django.contrib.auth.models import User
from transmittals.models import Transmittal, Location
from django.utils import timezone
from datetime import timedelta

users = User.objects.all()
print(f"Users in database: {[u.username for u in users]}")

if not users:
    print("No users found!")
    exit(1)

sender = users[0]
location = Location.objects.first()

if not location:
    print("No locations found!")
    exit(1)

transmittal = Transmittal.objects.create(
    sender=sender,
    sender_department='Operations',
    origin_location=location,
    recipient_name='Test Recipient Today',
    recipient_email='ongjamesdaryl@gmail.com',
    recipient_company='Test Company',
    recipient_department='Receiving',
    destination_location=location,
    description='Test transmittal due today for reminders',
    remarks='This transmittal is in transit for 5+ days',
    status='in_transit',
    status_changed_at=timezone.now() - timedelta(days=6)
)

print(f"\n✅ Transmittal created successfully!")
print(f"   Reference: {transmittal.reference_number}")
print(f"   Status: {transmittal.get_status_display()}")
print(f"   Days in Status: {(timezone.now() - transmittal.status_changed_at).days}")
print(f"   Recipient: {transmittal.recipient_email}")
print(f"\n📧 This transmittal will receive a reminder email when the command runs!")
