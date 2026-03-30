#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from transmittals.models import Transmittal
from django.utils import timezone
from datetime import timedelta

print("\n" + "="*70)
print("AUTO-RECEIVE TRANSMITTALS - SIMULATION TEST")
print("="*70)

# Check current transmittals in 'picked' status
picked = Transmittal.objects.filter(status='picked')
print(f"\nTotal in 'picked' status: {picked.count()}")

# Check which ones would be auto-received (3+ days old)
three_days_ago = timezone.now() - timedelta(days=3)
old_picked = Transmittal.objects.filter(status='picked', picked_at__lte=three_days_ago)
print(f"Would be auto-received (3+ days old): {old_picked.count()}")

# Show details
if picked.count() > 0:
    print("\nPicked transmittals details:")
    for t in picked[:5]:
        if t.picked_at:
            days_old = (timezone.now() - t.picked_at).days
            status_auto = "✓ ELIGIBLE FOR AUTO-RECEIVE" if days_old >= 3 else f"⏳ Not yet ({3-days_old} days to go)"
            print(f"  - {t.reference_number}")
            print(f"    Recipient ID: {t.recipient_id.id} ({t.recipient_id.username})")
            print(f"    Picked at: {t.picked_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    Days in picked: {days_old}")
            print(f"    Status: {status_auto}")
            print(f"    Auto-received: {t.auto_received}\n")
        else:
            print(f"  - {t.reference_number}: No picked_at timestamp")

print("="*70)
