from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Assign CLA Superusers 'Can add organisation' and 'Can change organisation' permissions"

    def handle(self, *args, **options):
        groups = Group.objects.filter(name="CLA Superusers")
        if groups.exists():
            permissions = Permission.objects.filter(name__in=["Can add organisation", "Can change organisation"])
            groups.first().permissions.add(*permissions)
