
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20211228_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(
                choices=[
                    ('веточка', 'веточка'),
                    ('горсть', 'горсть'),
                    ('пучок', 'пучок'),
                    ('кусок', 'кусок'),
                    ('банка', 'банка'),
                    ('упаковка', 'упаковка'),
                    ('батон', 'батон'),
                    ('л', 'л'),
                    ('стакан', 'стакан'),
                    ('долька', 'долька'),
                    ('щепотка', 'щепотка'),
                    ('по вкусу', 'по вкусу'),
                    ('мл', 'мл'), ('г', 'г'),
                    ('кг', 'кг'), ('шт.', 'шт.'),
                    ('ч. л.', 'ч. л.'), ('ст. л.', 'ст. л.'),
                    ('капля', 'капля'), ('бутылка', 'бутылка'),
                    ('зубчик', 'зубчик')],
                help_text='Впиши нужную еденицу измерения',
                max_length=150, verbose_name='Единицы измерения'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(
                help_text='Нужен уникальный слаг',
                unique=True, verbose_name='Slug'),
        ),
        migrations.CreateModel(
            name='RecipeTags',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='recipes.recipe', verbose_name='Рецепт')),
                ('tag', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='recipes.tag', verbose_name='Тег для рецепта')),
            ],
            options={
                'verbose_name': 'Теги',
                'verbose_name_plural': 'Теги',
            },
        ),
    ]
