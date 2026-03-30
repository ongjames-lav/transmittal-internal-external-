#!/usr/bin/env python
"""
Send actual reminder email with the proper format to test recipient
"""
import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from transmittals.models import Transmittal, Location

print("=" * 70)
print("SENDING ACTUAL REMINDER EMAIL FORMAT")
print("=" * 70)

# Get a transmittal
transmittal = Transmittal.objects.get(reference_number='TEST-20260304-9999')

if not transmittal:
    print("❌ Test transmittal not found")
    exit(1)

print(f"\n📧 Transmittal Details:")
print(f"   Reference: {transmittal.reference_number}")
print(f"   Status: {transmittal.get_status_display()}")
print(f"   Sender: {transmittal.sender.email}")
print(f"   Recipient: {transmittal.recipient_email}")
print(f"   Status Changed: {transmittal.status_changed_at}")
print(f"   Days in Status: {(timezone.now() - transmittal.status_changed_at).days}")

# Prepare email context
context = {
    'transmittal': transmittal,
    'days_in_status': (timezone.now() - transmittal.status_changed_at).days,
    'status_display': transmittal.get_status_display(),
    'request': type('Request', (), {'get_host': lambda: '127.0.0.1:8000'})()
}

# Render the template
print(f"\n🎨 Rendering email template...")
try:
    html_message = render_to_string(
        'transmittals/emails/status_reminder.html',
        context
    )
    print("✅ Template rendered successfully")
except Exception as e:
    print(f"❌ Error rendering template: {e}")
    exit(1)

# Prepare recipients
recipients = [transmittal.sender.email, transmittal.recipient_email]
recipients = list(set(recipients))  # Remove duplicates

print(f"\n📤 Sending email to:")
for email in recipients:
    print(f"   - {email}")

# Send the email
print(f"\n🚀 Sending email...")
try:
    result = send_mail(
        subject=f"Transmittal Status Reminder - Ref: {transmittal.reference_number}",
        message=f"Transmittal {transmittal.reference_number} has been in {transmittal.get_status_display()} status for {(timezone.now() - transmittal.status_changed_at).days} days.",
        from_email=None,  # Use DEFAULT_FROM_EMAIL
        recipient_list=recipients,
        html_message=html_message,
        fail_silently=False,
    )
    
    print(f"✅ Email sent successfully! (Result: {result})")
    print(f"\n📧 Email Preview:")
    print(f"   Subject: Transmittal Status Reminder - Ref: {transmittal.reference_number}")
    print(f"   From: CDC Manufacturing Corporation Transmittal System")
    print(f"   To: {', '.join(recipients)}")
    print(f"   Status: In Transit for {(timezone.now() - transmittal.status_changed_at).days} days")
    print("\n✅ Check your email inbox for the reminder!")
    
except Exception as e:
    print(f"❌ Error sending email: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
