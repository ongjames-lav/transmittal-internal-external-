from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from transmittals.models import Transmittal

class Command(BaseCommand):
    help = 'Send email reminders for transmittals stuck in same status for 5 days'

    def handle(self, *args, **options):
        five_days_ago = timezone.now() - timedelta(days=5)
        one_day_ago = timezone.now() - timedelta(days=1)
        
        # Log start
        self.stdout.write(
            f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Checking for transmittals stuck 5+ days in same status..."
        )
        
        # Find transmittals that:
        # 1. Have been in same status for 5+ days
        # 2. Last reminder was sent more than 1 day ago (or never sent for this status)
        # 3. Status is ONLY: in_transit, arrived, or picked (NOT received or cancelled)
        # 4. NOT cancelled (exclude cancelled transmittals)
        # This sends DAILY reminders once 5 days threshold is reached
        from django.db.models import Q
        transmittals_to_remind = Transmittal.objects.filter(
            status_changed_at__lte=five_days_ago,
            status__in=['in_transit', 'arrived', 'picked'],  # Only these statuses
        ).exclude(
            status='cancelled'  # Exclude cancelled transmittals
        ).filter(
            Q(reminder_sent_at__isnull=True) | Q(reminder_sent_at__lte=one_day_ago)
        )
        
        if not transmittals_to_remind.exists():
            self.stdout.write(self.style.SUCCESS("✓ No transmittals need reminders."))
            return
        
        self.stdout.write(
            f"Found {transmittals_to_remind.count()} transmittals needing reminders"
        )
        
        reminder_count = 0
        error_count = 0
        
        for transmittal in transmittals_to_remind:
            try:
                self.send_reminder_email(transmittal)
                transmittal.reminder_sent_at = timezone.now()
                transmittal.save(update_fields=['reminder_sent_at'])
                reminder_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Reminder sent for transmittal {transmittal.reference_number} ({transmittal.get_status_display()})"
                    )
                )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Error sending reminder for {transmittal.reference_number}: {str(e)}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n📊 Summary: {reminder_count} reminders sent, {error_count} errors"
            )
        )

    def send_reminder_email(self, transmittal):
        subject = f"Transmittal Status Reminder - Ref: {transmittal.reference_number}"
        
        context = {
            'transmittal': transmittal,
            'days_in_status': (timezone.now() - transmittal.status_changed_at).days,
            'status_display': transmittal.get_status_display(),
            'site_url': settings.SITE_URL
        }
        
        html_message = render_to_string(
            'transmittals/emails/status_reminder.html',
            context
        )
        
        # Send to sender and receiver only
        recipients = [transmittal.sender.email]
        
        if transmittal.recipient_email:
            recipients.append(transmittal.recipient_email)
        
        send_mail(
            subject,
            f"Transmittal {transmittal.reference_number} has been in {transmittal.get_status_display()} status for {(timezone.now() - transmittal.status_changed_at).days} days.",
            None,  # Use DEFAULT_FROM_EMAIL from settings
            list(set(recipients)),  # Remove duplicates
            html_message=html_message,
            fail_silently=False,
        )
