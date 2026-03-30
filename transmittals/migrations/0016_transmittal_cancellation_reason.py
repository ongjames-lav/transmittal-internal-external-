# Generated migration for cancellation_reason field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0015_transmittal_receiver_signature'),
    ]

    operations = [
        migrations.AddField(
            model_name='transmittal',
            name='cancellation_reason',
            field=models.TextField(blank=True, help_text='Reason provided by sender for cancelling the transmittal', null=True, verbose_name='Cancellation Reason'),
        ),
    ]
