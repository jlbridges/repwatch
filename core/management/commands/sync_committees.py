from django.core.management.base import BaseCommand
from core.services.committee_scrape_service import populate_committee_data

class Command(BaseCommand):
    help = "Sync committee data"

    def handle(self, *args, **options):
        self.stdout.write("Starting committee sync process")
        populate_committee_data()
        
        