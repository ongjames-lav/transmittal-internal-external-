import os
import django
from django.core import management
from django.db.models.signals import post_save, pre_save

# 1. Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

# 2. Import models
from django.contrib.auth.models import User
from accounts.models import Profile

def migrate_data():
    # 3. Disconnect ALL signals to stop auto-profile creation
    print("Disconnecting signals...")
    post_save.receivers = []
    pre_save.receivers = []

    # 4. Clear any existing data just in case
    print("Cleaning tables...")
    Profile.objects.all().delete()
    User.objects.all().delete()

    # 5. Run the loaddata
    print("Loading data from backup...")
    try:
        management.call_command('loaddata', 'data_backup.json', ignorenonexistent=True)
        print("\n✅ SUCCESS! MySQL is now fully populated.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTRY THIS: If it still says Duplicate Entry, it means the signal is \n"
              "hard-coded. We may need to manually delete Profiles in MySQL \n"
              "after the Users load. Let me know!")

if __name__ == "__main__":
    migrate_data()