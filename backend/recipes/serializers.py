from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingList, Tag)
from rest_framework import serializers
from users.serializers import CustomUserSerializer

IN_FAVORITE_MESSAGE = 'Этот рецепт уже в избранном! = )'
IN_SHOPPING_LIST_MESSAGE = 'Этот рецепт уже в вашем списке покупок! = )'
COOKING_TIME_MESSAGE = 'Время приготовления не может быть меньше 1-ой минуты!'
INGREDIENT_AMOUNT_MESSAGE = 'Ингредиента не может быть меньше 0!'
UNIQUE_INGREDIENT_MESSAGE = 'Ингредиенты не могут повторяться!'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class IngredientInRecipetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipetSerializer(
        source='ingredient_in_recipe',
        many=True
        )
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'pub_date',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        queryset = Favorite.objects.filter(
            user=request.user.id,
            recipe=obj.id
            ).exists()
        return queryset

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        queryset = ShoppingList.objects.filter(
            user=request.user.id,
            recipe=obj.id
            ).exists()
        return queryset

    @staticmethod
    def validate_cooking_time(data):
        if data < 1:
            raise serializers.ValidationError(COOKING_TIME_MESSAGE)
        return data

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredient')
        unique_ingredients = set()
        for ingredient in ingredients:
            if float(ingredient['amount']) < float(0.1):
                raise serializers.ValidationError(INGREDIENT_AMOUNT_MESSAGE)
            if ingredient['id'] in unique_ingredients:
                raise serializers.ValidationError(UNIQUE_INGREDIENT_MESSAGE)
            unique_ingredients.add(ingredient['name'])
        return data

    def get_ingredients_amount(self, ingredients, recipe):
        tags = self.initial_data.get('tags')
        for tag_id in tags:
            recipe.tags.add(get_object_or_404(Tag, pk=tag_id))
        for ingredient in ingredients:
            ingredients_amount = IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
            ingredients_amount.save()

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.get_ingredients_amount(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.get_ingredients_amount(ingredients, instance)
        if validated_data.get('image') is not None:
            instance.image = validated_data.get('image')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.save()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('name', 'image', 'cooking_time', 'user', 'recipe')

    def validate(self, data):
        if Favorite.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(IN_FAVORITE_MESSAGE)
        return data


class ShoppingListSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingList
        fields = ('name', 'image', 'cooking_time', 'user', 'recipe')

    def validate(self, data):
        if ShoppingList.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(IN_SHOPPING_LIST_MESSAGE)
        return data
