from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group, ContentType


class Command(BaseCommand):
    def handle(self, *args, **options):
        content_type = ContentType.objects.get(app_label="knowledgebase", model="articlecategory")
        perms = Permission.objects.filter(content_type=content_type)
        group = Group.objects.get(name="CLA Superusers")
        for perm in perms:
            group.permissions.add(perm)
