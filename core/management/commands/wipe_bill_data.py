from django.core.management.base import BaseCommand

from core.models import BillHeader


class Command(BaseCommand):
    help = "Delete all bill data."

    def handle(self, *args, **options):
        BillHeader.objects.all().delete()
        self.stdout.write("Bill data wiped.")
