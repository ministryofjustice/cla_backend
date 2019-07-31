from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Assign CLA Superusers 'Can add organisation' and 'Can change organisation' permissions"

    def handle(self, *args, **options):
        group = Group.objects.get(name="CLA Superusers")
        if not group:
            return

        can_add_organisation_perm = Permission.objects.get(name="Can add organisation")
        if can_add_organisation_perm:
            group.permissions.add(can_add_organisation_perm)

        can_change_organisation_perm = Permission.objects.get(name="Can change organisation")
        if can_change_organisation_perm:
            group.permissions.add(can_change_organisation_perm)
