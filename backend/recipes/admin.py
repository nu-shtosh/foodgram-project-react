from django.contrib import admin
from foodgram.settings import EMPTY_STRING
from recipes.models import (Favorite, Ingredient, Quantity, Recipe,
                            ShoppingList, Tag)

admin.ModelAdmin.empty_value_display = EMPTY_STRING


class QuantityInLine(admin.TabularInline):
    model = Quantity
    fk_name = 'recipe'


class TagInline(admin.TabularInline):
    model = Recipe.tags.through


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    list_filter = ('name',)
    search_fields = ('name', 'slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    search_fields = ('name',)


@admin.register(Quantity)
class QuantityAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'image', 'text', 'cooking_time', 'author', )
    list_filter = ('name', 'cooking_time', 'author', )
    search_fields = ('name', 'author', )
    exclude = ('ingredient', 'tags, ')

    inlines = [
        QuantityInLine,
        TagInline
    ]

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'author', 'add_date',)
    list_filter = ('add_date',)
    search_fields = ('author', 'recipe',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe', 'add_date',)
    list_filter = ('add_date',)
    search_fields = ('user', 'recipe',)
