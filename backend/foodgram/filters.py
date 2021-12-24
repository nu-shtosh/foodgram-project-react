from django_filters import (AllValuesMultipleFilter, BooleanFilter, CharFilter,
                            FilterSet, ModelChoiceFilter)

from recipes.models import Ingredient, Recipe
from users.models import CustomUser


class RecipeFilter(FilterSet):
    author = ModelChoiceFilter(queryset=CustomUser.objects.all())
    tags = AllValuesMultipleFilter(field_name='tag__slug')
    is_favorited = BooleanFilter(method='filter_is_favorite')
    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_favorite(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(favorites__user=self.request.user)
        return Recipe.objects.all()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(shopping_cart__user=self.request.user)
        return Recipe.objects.all()


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        search_param = 'name'
