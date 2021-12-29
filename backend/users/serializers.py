from djoser.serializers import UserSerializer
from rest_framework import serializers
from recipes.models import Recipe
from users.models import Follow, User
from drf_extra_fields.fields import Base64ImageField
FOLLOW_YOURSELF_ERROR_MESSAGE = 'Нельзя подписаться на себя! =)'
FOLLOW_ERROR_MESSAGE = 'Вы уже подписаны на этого автора! =)'
EMAIL_ERROR_MESSAGE = 'Такой адрес электронной почты уже зарегистрирован! =)'
USERNAME_ERROR_MESSAGE = 'Такой логин уже зарегистрирован! =)'


class CustomUserSerializer(UserSerializer):
    """User GET."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
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
        return Follow.objects.filter(user=request.user, author=obj.id).exists()


class RecipeInFollowSerializer(serializers.ModelSerializer):
    """Рецепт для вывода в Follow."""
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowPostSerializer(serializers.ModelSerializer):
    """Follow POST."""
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        """Валидация  подписки."""
        if data['author'] == data['user']:
            raise serializers.ValidationError(FOLLOW_YOURSELF_ERROR_MESSAGE)
        if Follow.objects.filter(
            author=data['author'],
            user=data['user']
        ).exists():
            raise serializers.ValidationError(FOLLOW_ERROR_MESSAGE)
        return data


class FollowGetSerializer(serializers.ModelSerializer):
    """Follow GET."""
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
            )

    def get_is_subscribed(self, obj):
        """Статус подписки."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        """Рецепты на странице подписок."""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit is not None:
            queryset = Recipe.objects.filter(
                author=obj.author
            )[:int(limit)]
        return RecipeInFollowSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """Количество рецептов."""
        queryset = Recipe.objects.filter(author=obj.author.id).count()
        return queryset
