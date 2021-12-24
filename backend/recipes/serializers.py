from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingList, Tag)
from users.serializers import CustomUserSerializer

IN_FAVORITE_MESSAGE = 'Этот рецепт уже в избранном! = )'
IN_SHOPPING_LIST_MESSAGE = 'Этот рецепт уже в вашем списке покупок! = )'
COOKING_TIME_MESSAGE = 'Время приготовления не может быть меньше 1-ой минуты!'
INGREDIENT_AMOUNT_MESSAGE = 'Ингредиента не может быть меньше 0!'
UNIQUE_INGREDIENT_MESSAGE = 'Ингредиенты не могут повторяться!'
ADD_TAG_MESSAGE = 'Добавьте тэг!'
UNIQUE_TAG_MESSAGE = 'Тэг должен быть уникальным'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField('get_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
            )

    def get_ingredients(self, recipe):
        qs = IngredientInRecipe.objects.filter(recipe=recipe)
        return IngredientInRecipeSerializer(qs, many=True).data

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


class RecipeSerializer(serializers.ModelSerializer):

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

    def get_ingredients(self, obj):
        ingredients = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredients, many=True).data

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

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError(ADD_TAG_MESSAGE)
        if len(data) != len(set(data)):
            raise serializers.ValidationError(UNIQUE_TAG_MESSAGE)
        return data

    def validate_cooking_time(data):
        if data <= float(0.1):
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

    def create_ingredient_in_recipe(self, ingredient, recipe):
        for ingredient in ingredient:
            IngredientInRecipe.objects.create(
                ingredient_id=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        ingredients = validated_data.get('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredient_in_recipe(ingredients, recipe)
        return recipe

    def update(self, request, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.get(id=request.id)
        recipe.ingredients.clear()
        recipe.tags.set(tags)
        self.create_ingredient_in_recipe(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        data = RecipeGetSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
        return data


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

    def to_representation(self, instance):
        data = RecipeGetSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
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

    def to_representation(self, instance):
        data = RecipeGetSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
        return data