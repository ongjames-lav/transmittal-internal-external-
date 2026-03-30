#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from transmittals.models import Transmittal
from transmittals.email_utils import send_driver_update_email
from django.contrib.auth.models import User
from accounts.models import Profile

# Get a transmittal
transmittal = Transmittal.objects.first()
user = User.objects.first()

print(f"Testing with Transmittal: {transmittal}")
print(f"Reference: {transmittal.reference_number}")
print(f"Receiver Email: {transmittal.recipient_email}")
print(f"Destination Location: {transmittal.destination_location}")

# Check for custodian
if transmittal.destination_location:
    dest_custodian = Profile.objects.filter(
        role='custodian',
        assigned_location=transmittal.destination_location
    ).first()
    print(f"Destination Custodian: {dest_custodian}")
    if dest_custodian:
        print(f"Custodian Email: {dest_custodian.user.email}")

print("\nSending test email...")
result = send_driver_update_email(transmittal, "John Doe - Plate # ABC123", user)
print(f"Email send result: {result}")
