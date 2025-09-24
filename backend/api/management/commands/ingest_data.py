# backend/api/management/commands/ingest_data.py
from django.core.management.base import BaseCommand
from api.tasks import ingest_customer_data, ingest_loan_data

class Command(BaseCommand):
    help = 'Ingests customer and loan data from excel files using Celery'

    def handle(self, *args, **options):
        self.stdout.write('Queueing data ingestion tasks...')
        ingest_customer_data.delay()
        ingest_loan_data.delay()
        self.stdout.write(self.style.SUCCESS('Successfully queued data ingestion tasks.'))