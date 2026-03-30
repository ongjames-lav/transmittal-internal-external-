from django.core.management.base import BaseCommand
from accounts.models import Department


class Command(BaseCommand):
    help = 'Populate departments from existing user data'

    def handle(self, *args, **options):
        departments = [
            'ACCOUNTING',
            'Araneta',
            'BPM17',
            'Credit and Collection',
            'DISTRIBUTION',
            'ECOMM',
            'EGSD',
            'EXECUTIVE',
            'FG',
            'Head Office',
            'HRAD',
            'INLINE BPM',
            'INLINE MEYC',
            'INSTI SALES',
            'IPAC',
            'MARKETING',
            'MEYC WAREHOUSE BAGBAGUIN',
            'MFG ARA',
            'MFG DESIGN',
            'MFG PANTOC',
            'MIS',
            'Pantoc',
            'PDD',
            'QA',
            'RETAIL SALES',
            'TREASURY',
            'WHSE ARA',
        ]

        created_count = 0
        for dept_name in departments:
            dept, created = Department.objects.get_or_create(
                name=dept_name,
                defaults={'is_active': True}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created department: {dept_name}')
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'Department already exists: {dept_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nTotal new departments created: {created_count}')
        )
