from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from transmittals.models import Transmittal
from transmittals.email_utils import send_status_notification


class Command(BaseCommand):
    help = 'Automatically receive transmittals that have been in "picked" status for 3 days'

    def handle(self, *args, **options):
        """
        Auto-receive transmittals where:
        1. Status is 'picked'
        2. picked_at is more than 3 days ago
        3. Not already received or cancelled
        """
        three_days_ago = timezone.now() - timedelta(days=3)
        
        # Find all transmittals that should be auto-received
        auto_receive_candidates = Transmittal.objects.filter(
            status='picked',
            picked_at__lte=three_days_ago,
            auto_received=False  # Prevent duplicate auto-receives
        )
        
        auto_received_count = 0
        
        for transmittal in auto_receive_candidates:
            try:
                # Update transmittal status to received
                transmittal.status = 'received'
                transmittal.received_at = transmittal.picked_at #date pickup
                transmittal.received_by = transmittal.recipient_id  # Auto-set to recipient
                transmittal.auto_received = True
                transmittal.save(update_fields=['status', 'received_at', 'received_by', 'auto_received'])
                
                # Send the same notification as manual receive
                # This uses the recipient_id for notification
                send_status_notification(transmittal, 'received', auto_received=True)
                
                auto_received_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Auto-received: {transmittal.reference_number} "
                        f"(Recipient ID: {transmittal.recipient_id.id}, "
                        f"Picked at: {transmittal.picked_at.strftime('%Y-%m-%d %H:%M:%S')})"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Failed to auto-receive {transmittal.reference_number}: {str(e)}"
                    )
                )
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{'='*70}\n"
                f"AUTO-RECEIVE TRANSMITTALS - COMPLETED\n"
                f"{'='*70}\n"
                f"Total auto-received: {auto_received_count}\n"
                f"Timestamp: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"{'='*70}\n"
            )
        )
