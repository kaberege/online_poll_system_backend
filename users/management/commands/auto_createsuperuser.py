from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a superuser if one does not already exist.'

    def handle(self, *args, **options):
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password
            )
        print('Superuser has been created.')