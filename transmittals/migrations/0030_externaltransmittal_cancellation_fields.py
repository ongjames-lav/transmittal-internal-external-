# Generated migration to add cancellation fields to ExternalTransmittal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0029_externaltransmittal_sender_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='externaltransmittal',
            name='cancelled_at',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Cancelled At'
            ),
        ),
        migrations.AddField(
            model_name='externaltransmittal',
            name='cancellation_reason',
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name='Cancellation Reason'
            ),
        ),
    ]
