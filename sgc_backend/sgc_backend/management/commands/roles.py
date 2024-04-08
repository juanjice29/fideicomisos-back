from django.core.management.base import BaseCommand
from accounts.models import Role

class Command(BaseCommand):
    help = 'Creates a specified number of roles'

    def add_arguments(self, parser):
        parser.add_argument('total_roles', type=int, help='The number of roles to create')

    def handle(self, *args, **options):
        total_roles = options['total_roles']
        for i in range(total_roles):
            Role.objects.create(name='sap')
        self.stdout.write(self.style.SUCCESS(f"Successfully created {total_roles} roles"))