import csv
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

from recipes.models import Ingredient


def from_csv():
    with open('ingredients.csv', encoding='utf-8') as i:
        reader = csv.reader(i)
        for row in reader:
            name, measurement_unit = row
            _, created = Ingredient.objects.get_or_create(
                name=name,
                measurement_unit=measurement_unit
            )


if __name__ == '__main__':
    from_csv()
