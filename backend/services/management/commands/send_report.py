"""
Management command to manually send the report.
Run: python manage.py send_report
"""

from django.core.management.base import BaseCommand
from services.reports import email_report_to_owner


class Command(BaseCommand):
    help = 'Generate and send the Excel report to the owner immediately'

    def handle(self, *args, **options):
        self.stdout.write("Generating report...")
        email_report_to_owner()
        self.stdout.write(self.style.SUCCESS("Report sent!"))
