from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import CustomUser, Follow

FOLLOW_YOURSELF_ERROR_MESSAGE = 'Нельзя подписаться на себя! =)'
FOLLOW_ERROR_MESSAGE = 'Вы уже подписаны на этого автора! =)'
EMAIL_ERROR_MESSAGE = 'Такой адрес электронной почты уже зарегистрирован! =)'
USERNAME_ERROR_MESSAGE = 'Такой логин уже зарегистрирован! =)'


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            )

    def get_is_subscribed(self, obj):
        """Статус подписки."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        queryset = Follow.objects.filter(
            author=obj.id,
            follower=request.user.id
            ).exists()
        return queryset


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(
        queryset=CustomUser.objects.all(),
        message=EMAIL_ERROR_MESSAGE)]
        )
    username = serializers.CharField(validators=[UniqueValidator(
        queryset=CustomUser.objects.all(),
        message=USERNAME_ERROR_MESSAGE)]
        )

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
            )


class RecipeInFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'author',
                  'follower')
        extra_kwargs = {'author': {'write_only': True},
                        'follower': {'write_only': True}}

    def get_is_subscribed(self, obj):
        """Статус подписки."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        queryset = Follow.objects.filter(
            author=obj.id,
            follower=request.user.id).exists()
        return queryset

    def get_recipes(self, obj):
        """Рецепты на странице подписок."""
        queryset = Recipe.objects.filter(author=obj.author.id)
        serializer = RecipeInFollowSerializer(queryset, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Количество рецептов."""
        queryset = Recipe.objects.filter(author=obj.author.id).count()
        return queryset

    def validate(self, data):
        """Валидация  подписки."""
        if data['author'] == data['follower']:
            raise serializers.ValidationError(FOLLOW_YOURSELF_ERROR_MESSAGE)
        if Follow.objects.filter(
            author=data['author'],
            follower=data['follower']
        ).exists():
            raise serializers.ValidationError(FOLLOW_ERROR_MESSAGE)
        return data
