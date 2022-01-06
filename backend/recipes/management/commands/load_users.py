
import csv

from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    """Загружает предустановленные инредиенты и таги."""
    help = 'Load users.'

    def handle(self, *args, **options):
        with open('data/users.csv', encoding='utf-8') as i:
            reader = csv.reader(i)
            for row in reader:
                username, email, first_name, last_name, password = row
                User.objects.get_or_create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )
