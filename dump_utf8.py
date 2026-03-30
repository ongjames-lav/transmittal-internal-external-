import os
import django
from django.core import management

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

# Export data with UTF-8 encoding specifically
with open('data_backup.json', 'w', encoding='utf-8') as f:
   management.call_command('dumpdata', exclude=['contenttypes', 'auth.permission', 'admin', 'sessions'], stdout=f)

print("✅ Data successfully exported to data_backup.json in UTF-8 format!")