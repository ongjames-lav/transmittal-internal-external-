# Generated migration to add sender_id field to ExternalTransmittal

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transmittals', '0028_transmittal_auto_received'),
    ]

    operations = [
        migrations.AddField(
            model_name='externaltransmittal',
            name='sender_id',
            field=models.ForeignKey(
                blank=True,
                help_text='System user who sent this transmittal (if sent by authenticated user)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='external_sent_transmittals',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Sender User'
            ),
        ),
    ]
