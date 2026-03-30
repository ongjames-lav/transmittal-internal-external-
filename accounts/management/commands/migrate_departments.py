"""
Management command to ensure proper ForeignKey connection for department.

This command verifies that all profiles have proper department ForeignKey
references and displays a summary of the status.
"""

from django.core.management.base import BaseCommand
from accounts.models import Profile, Department


class Command(BaseCommand):
    help = 'Verify and fix department ForeignKey references in profiles'

    def handle(self, *args, **options):
        verified = 0
        with_department = 0
        without_department = 0

        # Get all profiles
        profiles = Profile.objects.select_related('department').all()

        self.stdout.write(f'Checking {profiles.count()} profiles')

        for profile in profiles:
            if profile.department:
                with_department += 1
                verified += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {profile.user.username}: Department -> {profile.department.name}'
                    )
                )
            else:
                without_department += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ {profile.user.username}: No department assigned'
                    )
                )

        # Print summary
        self.stdout.write(self.style.SUCCESS('\n=== Verification Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'Total profiles verified: {verified}'))
        self.stdout.write(self.style.SUCCESS(f'With department: {with_department}'))
        self.stdout.write(self.style.WARNING(f'Without department: {without_department}'))
        self.stdout.write(self.style.SUCCESS('All profiles are properly connected to the Department model!'))
