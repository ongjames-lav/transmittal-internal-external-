from django.core.management.base import BaseCommand
from transmittals.models import Transmittal
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Delete emails in trash older than 30 days and permanently delete fully purged records'

    def handle(self, *args, **kwargs):
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # 1. Auto-purge items soft-deleted > 30 days ago
        # If sender deleted > 30 days ago, mark sender_purged = True
        sender_expired = Transmittal.objects.filter(
            sender_deleted=True,
            sender_deleted_at__lt=thirty_days_ago,
            sender_purged=False
        )
        s_count = sender_expired.update(sender_purged=True)
        
        # If recipient deleted > 30 days ago, mark recipient_purged = True
        recipient_expired = Transmittal.objects.filter(
            recipient_deleted=True,
            recipient_deleted_at__lt=thirty_days_ago,
            recipient_purged=False
        )
        r_count = recipient_expired.update(recipient_purged=True)
        
        self.stdout.write(f"Auto-purged {s_count} sender items and {r_count} recipient items.")
        
        # 2. Hard delete records where BOTH parties have purged
        # This means neither party can see it anymore -> safe to delete from DB
        fully_purged = Transmittal.objects.filter(
            sender_purged=True,
            recipient_purged=True
        )
        fp_count = fully_purged.count()
        fully_purged.delete()
        
        self.stdout.write(f"Permanently deleted {fp_count} fully purged records from database.")
