"""
Data migration to seed default locations.
Run this with: python manage.py migrate transmittals
"""
from django.db import migrations


def create_default_locations(apps, schema_editor):
    """Create the 5 default locations."""
    Location = apps.get_model('transmittals', 'Location')
    
    default_locations = [
        {'name': 'Pantoc', 'prefix': 'PAN'},
        {'name': 'Meycauayan', 'prefix': 'MY'},
        {'name': 'Bpm', 'prefix': 'BP'},
        {'name': 'Main', 'prefix': 'HO'},
        {'name': 'Araneta', 'prefix': 'ARA'},
    ]
    
    for loc_data in default_locations:
        Location.objects.get_or_create(
            prefix=loc_data['prefix'],
            defaults={
                'name': loc_data['name'],
                'is_active': True,
            }
        )


def reverse_default_locations(apps, schema_editor):
    """Remove default locations (for rollback)."""
    Location = apps.get_model('transmittals', 'Location')
    Location.objects.filter(prefix__in=['PAN', 'MY', 'BP', 'HO', 'ARA']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0007_alter_transmittal_options_and_more'),
    ]

    operations = [
        migrations.RunPython(create_default_locations, reverse_default_locations),
    ]
