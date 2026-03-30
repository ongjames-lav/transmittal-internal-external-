#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from transmittals.models import Transmittal

# Verify all transmittals have recipient_id
total = Transmittal.objects.count()
with_id = Transmittal.objects.filter(recipient_id__isnull=False).count()

print(f"\n{'='*60}")
print(f"VERIFICATION SUMMARY")
print(f"{'='*60}")
print(f"Total transmittals: {total}")
print(f"With recipient_id: {with_id}")
print(f"Missing recipient_id: {total - with_id}")
print(f"{'='*60}\n")

# Show sample data
print("Sample transmittals with recipient_id:")
for t in Transmittal.objects.all()[:3]:
    print(f"  - Ref: {t.reference_number}")
    print(f"    Email: {t.recipient_email}")
    print(f"    User ID: {t.recipient_id.id}")
    print(f"    User: {t.recipient_id.username}")
    print()
