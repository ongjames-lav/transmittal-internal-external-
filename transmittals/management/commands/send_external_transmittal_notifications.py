"""
Management command to send deadline reminder emails for external transmittals.

Schedule: Daily at 9:00 AM (Asia/Manila timezone)
Weekdays only: Monday - Friday

Escalation levels:
- Day 0: Deadline day
- Day +1: 1 day overdue
- Day +3: 3 days overdue
- Day +7: 7 days overdue (final reminder)

Only sends one reminder per day per transmittal to prevent email spam.
Tracks last_notification_date to prevent duplicate sends.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from transmittals.models import ExternalTransmittal
from transmittals.email_utils import send_external_transmittal_deadline_reminder


class Command(BaseCommand):
    help = 'Send daily deadline reminder emails for external transmittals (weekdays only, at 9 AM)'

    def handle(self, *args, **options):
        # Get current date
        today = timezone.now().date()
        
        # Log execution
        self.stdout.write(
            f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Checking external transmittals..."
        )
        
        # Find external transmittals that need deadline notifications
        # Criteria:
        # 1. Type is "For Return"
        # 2. Status is NOT "closed"
        # 3. Today >= DateDeadline (start reminders on deadline day)
        # 4. last_notification_date != today (prevent duplicate emails same day)
        
        transmittals_needing_notification = ExternalTransmittal.objects.filter(
            main_type='for_return',
            date_deadline__lte=today  # Start notifying from Deadline Date onwards
        ).exclude(
            status='closed'  # Exclude closed status
        ).exclude(
            status='cancelled'  # Exclude cancelled status
        ).exclude(
            last_notification_date=today
        )
        
        if not transmittals_needing_notification.exists():
            self.stdout.write(self.style.SUCCESS('✓ No transmittals need notifications today.'))
            return
        
        self.stdout.write(
            f"Found {transmittals_needing_notification.count()} transmittals needing notifications"
        )
        
        # Process each transmittal
        notification_count = 0
        error_count = 0
        
        for transmittal in transmittals_needing_notification:
            try:
                # Calculate days overdue relative to the hard deadline
                days_overdue = (today - transmittal.date_deadline).days if transmittal.date_deadline else 0
                
                # Send the daily reminder email
                # Note: email_utils.py now handles generic "X days overdue" messages
                email_sent = send_external_transmittal_deadline_reminder(
                    transmittal=transmittal,
                    days_overdue=days_overdue
                )
                
                if email_sent:
                    # Update last_notification_date to prevent duplicate sends today
                    transmittal.last_notification_date = today
                    transmittal.save(update_fields=['last_notification_date'])
                    
                    notification_count += 1
                    status_msg = f"{days_overdue} days overdue" if days_overdue > 0 else "Due today/soon"
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ [{transmittal.reference_number}] {status_msg} - "
                            f"Email sent to {transmittal.sender_email}, {transmittal.recipient_email}"
                        )
                    )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ [{transmittal.reference_number}] Failed to send email"
                        )
                    )
            
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ [{transmittal.reference_number}] Error: {str(e)}"
                    )
                )
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\n📊 Summary:\n"
                f"  Notifications sent: {notification_count}\n"
                f"  Errors: {error_count}\n"
                f"  Total processed: {notification_count + error_count}"
            )
        )
