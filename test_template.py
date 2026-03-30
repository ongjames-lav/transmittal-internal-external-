#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from django.template.loader import get_template

try:
    t = get_template('transmittals/custodian_list.html')
    print('✓ custodian_list.html template is valid!')
except Exception as e:
    print(f'✗ Error: {e}')
