from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from foodgram.filters import IngredientFilter, RecipeFilter
from foodgram.paginations import CustomPageNumberPaginator
from foodgram.permissions import IsAuthorOrReadOnly
from recipes.models import Favorite, Ingredient, Recipe, ShoppingList, Tag
from recipes.serializers import (FavoriteSerializer, IngredientSerializer,
                                 RecipeGetSerializer, RecipeSerializer,
                                 ShoppingListSerializer, TagSerializer)

IN_FAVORITE_MESSAGE = 'Вы добавили рецепт в избранное! =)'
NOT_IN_FAVORITE_MESSAGE = 'Вы убрали рецепт из избранного! =('
IN_SHOPPING_LIST_MESSAGE = 'Вы добавили рецепт в список покупок! =)'
NOT_IN_SHOPPING_LIST_MESSAGE = 'Вы убрали рецепт из списока покупок! =)'


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    pagination_class = CustomPageNumberPaginator
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = Recipe.objects.all()
        if self.request.query_params.get('is_favorited'):
            queryset = queryset.filter(favorite__user=self.request.user)
        if self.request.query_params.get('is_in_shopping_cart'):
            queryset = queryset.filter(cart__customer=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['GET', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated]
        )
    def favorite(self, request, id):
        recipe = get_object_or_404(Recipe, id=id).id
        user = request.user.id
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
                {'status': IN_SHOPPING_LIST_MESSAGE},
                status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE' and in_shopping_list:
            ShoppingList.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'status': NOT_IN_SHOPPING_LIST_MESSAGE},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
        )
    def download_shopping_list(self, request):
        user = request.user
        in_cart = Recipe.objects.filter(cart__customer=user)
        queryset = in_cart.values_list(
            'ingredients__name',
            'related_ingredients__amount',
            'ingredients__measurement_unit')
        text = 'Ваш список покупок: \n'
        for ingredient in queryset:
            text += f'{str(ingredient)} \n'
        response = HttpResponse(text, 'Content-Type: application/txt')
        response['Content-Disposition'] = 'attachment; filename="wishlist"'
        return response
