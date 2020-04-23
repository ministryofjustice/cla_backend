from django.core.management.base import BaseCommand
from knowledgebase.models import ArticleCategory


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Getting or creating General Article Category")
        ArticleCategory.objects.get_or_create(name="General")
        self.stdout.write("Getting or creating Government Article Category")
        ArticleCategory.objects.get_or_create(name="Government")
