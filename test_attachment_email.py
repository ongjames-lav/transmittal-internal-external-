`#!/usr/bin/env python
"""
Test script to verify external transmittal emails include attachments.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from transmittals.models import ExternalTransmittal, ExternalTransmittalAttachment
from transmittals.email_utils import send_external_transmittal_created_email

# Get the most recent external transmittal with attachments
transmittals = ExternalTransmittal.objects.filter(attachments__isnull=False).distinct().order_by('-created_at')

if transmittals.exists():
    transmittal = transmittals.first()
    print(f"Testing with Transmittal: {transmittal.reference_number}")
    print(f"Recipient Email: {transmittal.recipient_email}")
    print(f"Total Attachments: {transmittal.attachments.count()}")
    
    for attachment in transmittal.attachments.all():
        print(f"  - {attachment.file.name} ({attachment.file.size} bytes)")
    
    print("\nSending test email with attachments...")
    try:
        result = send_external_transmittal_created_email(transmittal)
        if result:
            print("✅ Email sent successfully!")
        else:
            print("❌ Email send failed")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("No external transmittals with attachments found.")
    print("\nTesting attachment detection logic...")
    
    # Create a test transmittal
    test = ExternalTransmittal.objects.create(
        reference_number="TEST-001",
        main_type='for_keep',
        sender_email="test@example.com",
        sender_name="Test Sender",
        recipient_email="recipient@example.com",
        recipient_name="Test Recipient"
    )
    print(f"Created test transmittal: {test.reference_number}")
    print(f"Attachments count: {test.attachments.count()}")
