#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from transmittals.models import Location

# Test the lookup logic
test_values = ['ACCOUNTING', 'EXECUTIVE', 'HRAD', 'ARA', 'ara', 'ARANETA PLANT CALOOCAN', 'Head Office', 'HO']

print("Testing location lookup logic:\n")
for test_val in test_values:
    try:
        loc = Location.objects.get(name__iexact=test_val)
        print(f"✓ '{test_val}' found by name: {loc.name} ({loc.prefix})")
    except Location.DoesNotExist:
        try:
            loc = Location.objects.get(prefix__iexact=test_val)
            print(f"✓ '{test_val}' found by prefix: {loc.name} ({loc.prefix})")
        except Location.DoesNotExist:
            print(f"✗ '{test_val}' NOT found")
