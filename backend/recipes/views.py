from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from foodgram.filters import IngredientFilter, RecipeFilter
from foodgram.mixins import MixinsSet
from foodgram.paginations import CustomPageNumberPaginator
from foodgram.permissions import AuthorOrAdminOrRead
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingList, Tag)
from recipes.serializers import (FavoriteSerializer, IngredientSerializer,
                                 RecipeSerializer, ShoppingListSerializer,
                                 TagSerializer)


class TagViewSet(MixinsSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(MixinsSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = [DjangoFilterBackend]
    filter_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrAdminOrRead, )
    filter_backends = [DjangoFilterBackend]
    filter_class = RecipeFilter
    pagination_class = CustomPageNumberPaginator

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': user.id,
            'recipe': recipe.id,
        }
        serializer = FavoriteSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorites = get_object_or_404(
            Favorite, user=user, recipe=recipe
        )
        favorites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': user.id,
            'recipe': recipe.id,
        }
        serializer = ShoppingListSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorites = get_object_or_404(
            ShoppingList, user=user, recipe=recipe
        )
        favorites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[AuthorOrAdminOrRead]
        )
    def download_shopping_cart(self, request):
        user = request.user
        queryset = IngredientInRecipe.objects.filter(
            recipe__shopping_list__user=user
            )
        ingredients = queryset.values_list(
            'recipe__ingredients_amount__ingredient__name',
            'recipe__ingredients_amount__ingredient__measurement_unit',
            'recipe__ingredients_amount__amount'
        )
        text = 'Список покупок: \n'
        shoplist = {}
        for ingredients in ingredients:
            name, measurement_unit, amount = ingredients
            if name not in shoplist:
                shoplist[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                shoplist[name]['amount'] += amount
        text += f'{str(shoplist)}'
        response = HttpResponse(text, 'Content-Type: text/plane')
        response['Content-Disposition'] = 'attachment; filename="shoplist.txt"'
        return response
