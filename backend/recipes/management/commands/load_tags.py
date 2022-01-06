
import csv

from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    """Загружает предустановленные инредиенты и таги."""
    help = 'Load tags.'

    def handle(self, *args, **options):
        with open('data/tags.csv', encoding='utf-8') as t:
            reader = csv.reader(t)
            for row in reader:
                name, color, slug = row
                Tag.objects.get_or_create(
                    name=name,
                    color=color,
                    slug=slug
                )
