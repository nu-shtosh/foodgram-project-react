from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingList, Tag)
from users.models import User
from users.serializers import CustomUserSerializer

IN_FAVORITE_MESSAGE = 'Этот рецепт уже в избранном! = )'
IN_SHOPPING_LIST_MESSAGE = 'Этот рецепт уже в вашем списке покупок! = )'
COOKING_TIME_MESSAGE = 'Время приготовления не может быть меньше 1-ой минуты!'
INGREDIENT_AMOUNT_MESSAGE = 'Ингредиента не может быть меньше 0!'
UNIQUE_INGREDIENT_MESSAGE = 'Ингредиенты не могут повторяться!'
ADD_TAG_MESSAGE = 'Добавь тег!'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredients_amount',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'name',
            'text',
            'image',
            'ingredients',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
            )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe=obj
            ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user,
            recipe=obj
            ).exists()

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

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_set = set()
        for ingredient in ingredients:
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(INGREDIENT_AMOUNT_MESSAGE)
            ingredient_id = ingredient.get('id')
            if ingredient_id in ingredients_set:
                raise serializers.ValidationError(UNIQUE_INGREDIENT_MESSAGE)
            ingredients_set.add(ingredient_id)
        data['ingredients'] = ingredients
        if int(self.initial_data.get('cooking_time')) <= 0:
            raise serializers.ValidationError(COOKING_TIME_MESSAGE)
        tags = self.initial_data.get('tags')
        if tags is None:
            raise serializers.ValidationError(ADD_TAG_MESSAGE)
        return data

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


class RecipeForShoplistSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeForFavoriteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'cooking_time'
            )


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        recipe_id = data['recipe'].id
        in_favrites = Favorite.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists()
        if in_favrites:
            raise serializers.ValidationError(IN_FAVORITE_MESSAGE)
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeForFavoriteSerializer(
            instance.recipe,
            context=context).data


class ShoppingListSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        recipe_id = data['recipe'].id
        in_shop_list = ShoppingList.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists()
        if in_shop_list:
            raise serializers.ValidationError(IN_SHOPPING_LIST_MESSAGE)
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeForShoplistSerializer(
            instance.recipe,
            context=context).data
