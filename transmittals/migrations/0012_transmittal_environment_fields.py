# Generated migration for adding sender environment details

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0011_alter_transmittal_destination_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transmittal',
            name='device_information',
            field=models.CharField(
                blank=True,
                help_text='Device type (Desktop/Mobile/Tablet) and operating system',
                max_length=255,
                null=True,
                verbose_name='Device Information'
            ),
        ),
        migrations.AddField(
            model_name='transmittal',
            name='ip_address',
            field=models.GenericIPAddressField(
                blank=True,
                help_text='IPv4 or IPv6 address from which the transmittal was sent',
                null=True,
                verbose_name='IP Address'
            ),
        ),
        migrations.AddField(
            model_name='transmittal',
            name='browser_of_sender',
            field=models.CharField(
                blank=True,
                help_text='Browser name and version used to send the transmittal',
                max_length=255,
                null=True,
                verbose_name='Browser of Sender'
            ),
        ),
    ]
