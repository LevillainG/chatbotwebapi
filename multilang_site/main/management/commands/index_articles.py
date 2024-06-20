from django.core.management.base import BaseCommand
from main.documents import bulk_indexing

class Command(BaseCommand):
    help = 'Indexes all articles into Elasticsearch'

    def handle(self, *args, **kwargs):
        bulk_indexing()
        self.stdout.write(self.style.SUCCESS('Successfully indexed articles'))
