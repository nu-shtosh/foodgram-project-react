from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from foodgram.filters import IngredientFilter, RecipeFilter
from foodgram.paginations import CustomPageNumberPaginator
from foodgram.permissions import IsAuthorOrReadOnly, IsAdmin
from recipes.models import (Favorite, Ingredient, Quantity, Recipe,
                            ShoppingList, Tag)
from recipes.serializers import (FavoriteSerializer, IngredientSerializer,
                                 RecipeSerializer, ShoppingListSerializer,
                                 TagSerializer)
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

IN_FAVORITE_MESSAGE = 'Вы добавили рецепт в избранное! =)'
NOT_IN_FAVORITE_MESSAGE = 'Вы убрали рецепт из избранного! =('
IN_SHOPPING_LIST_MESSAGE = 'Вы добавили рецепт в список покупок! =)'
NOT_IN_SHOPPING_LIST_MESSAGE = 'Вы убрали рецепт из списока покупок! =)'


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    serializer_class = TagSerializer
    permission_classes = [IsAdmin]


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
        ]
    pagination_class = CustomPageNumberPaginator
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['GET', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated]
        )
    def favorite(self, request, id):
        recipe = get_object_or_404(Recipe, id=id).id
        user = self.request.user.id
        in_favorite = Favorite.objects.filter(
            user=user,
            recipe=recipe
            ).exists()

        if request.method == 'GET':
            data = {'user': user, 'recipe': recipe}
            context = {'request': request}
            serializer = FavoriteSerializer(
                data=data,
                context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                {'status': IN_FAVORITE_MESSAGE},
                status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE' and in_favorite:
            Favorite.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'status': NOT_IN_FAVORITE_MESSAGE},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['GET', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated]
        )
    def shopping_list(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk).id
        user = self.request.user.id
        in_shopping_list = ShoppingList.objects.filter(
            user=user,
            recipe=recipe
            ).exists()

        if request.method == 'GET':
            data = {'user': user, 'recipe': recipe}
            context = {'request': request}
            serializer = ShoppingListSerializer(
                data=data,
                context=context
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                {'status': 'Вы добавили рецепт в список покупок! =)'},
                status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE' and in_shopping_list:
            ShoppingList.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'status': 'Этого рецепта нет в списке покупок!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
        )
    def download_shopping_list(self, request):
        ingredients = Quantity.objects.filter(
            recipe__shop_cart__user=request.user).values_list(
                'ingredient__name',
                'amount',
                'ingredient__measurement_unit')

        ingredients_count = {}
        for ingredient in ingredients:
            name = ingredient[0]
            amount = ingredient[1]
            measurement = ingredient[2]

            if name not in ingredients_count:
                ingredients_count[name] = {
                    'amount': amount,
                    'measurement': measurement}
            else:
                ingredients_count[name]['amount'] += amount

        result = ''
        for name, values in ingredients_count.items():
            result += (f'{name} - {values["amount"]} '
                       f'{values["measurement"]}. ')

        download = 'buy_list.txt'
        response = HttpResponse(
            result, content_type='text/plain,charset=utf8')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(download)
        )
        return response
