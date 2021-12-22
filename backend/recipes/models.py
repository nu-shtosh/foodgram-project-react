from colorfield import fields
from django.db import models
from users.models import CustomUser


class Tag(models.Model):
    """Класс тега с выбором цветового HEX-кода."""
    name = models.CharField(
        'Название',
        max_length=150,
        unique=True,
        help_text='Место для названия',
    )
    color = fields.ColorField(
        'Цветовой HEX-код',
        default='#49B64E',
        help_text='Выбери цвет',
    )
    slug = models.SlugField(
        'Slug',
        unique=True,
        max_length=150,
        help_text='Нужен уникальный слаг',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Класс ингредиента."""
    name = models.CharField(
        'Название',
        max_length=150,
        help_text='Место для названия',
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=150,
        help_text='Впиши нужную еденицу измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Класс рецепта."""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Имя автора',
        related_name='recipes'
    )
    name = models.CharField(
        'Название',
        max_length=150,
        db_index=True,
        help_text='Название рецепта',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='images',
        help_text='Добавь картинку',
    )
    text = models.TextField(
        'Описание',
        help_text='Добавь описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
        help_text='Впиши ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        help_text='Добавь теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        help_text='Добавь время приготовления',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}'


class Favorite(models.Model):
    """Класс избранного рецепта/автора."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранный рецепт'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранный автор'
    )
    add_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добовления'
    )

    class Meta:
        ordering = ('add_date',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_favorites'
            ),
        )

    def __str__(self):
        return f'({self.recipe}, {self.author})'


class IngredientInRecipe(models.Model):
    """Класс количества ингредиента в рецепте."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_amount',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='ingredients_amount',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=float(0),
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.ingredient}'


class ShoppingList(models.Model):
    """Класс список покупок"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_list'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_list'
    )
    add_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добовления'
    )

    class Meta:
        ordering = ('add_date',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_list'
            ),
        )

    def __str__(self):
        return f'{self.user}, {self.recipe}'
