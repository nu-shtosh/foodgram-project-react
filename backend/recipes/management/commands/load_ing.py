
import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Загружает предустановленные инредиенты и таги."""
    help = 'Load ingredients.'

    def handle(self, *args, **options):
        with open('data/ingredients.csv', encoding='utf-8') as i:
            reader = csv.reader(i)
            for row in reader:
                name, measurement_unit = row
                _, created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
