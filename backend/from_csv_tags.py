import csv
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()


def from_csv_tags():
    with open('tags.csv', encoding='utf-8') as t:
        from recipes.models import Tag

        reader = csv.reader(t)
        for row in reader:
            name, color, slug = row
            _, created = Tag.objects.get_or_create(
                name=name,
                color=color,
                slug=slug
            )


if __name__ == '__main__':
    from_csv_tags()
