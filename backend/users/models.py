from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель юзера."""
    USER = 'user'
    ADMIN = 'admin'
    ROLES = [
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    ]

    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=150,
        null=False,
        unique=True
    )
    email = models.EmailField(
        max_length=254,
        blank=True,
        unique=True,
        null=False,
        verbose_name='Адрес электронной почты'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',

    )
    role = models.CharField(
        max_length=150,
        choices=ROLES,
        default=USER,
        verbose_name='Роль пользователя',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    @property
    def is_admin(self):
        return self.is_superuser or self.role == CustomUser.ADMIN

    @property
    def is_user(self):
        return self.role == CustomUser.USER

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.email}, {self.username}'


class Follow(models.Model):
    """Модель подписок(автор-подписчик)."""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор',
        help_text='Автор рецепта',
    )
    follower = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Подписчик на автора',
    )

    class Meta:
        verbose_name = 'Подпискa'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'follower'],
                name='author_follower'
            ),
        )

    def __str__(self):
        return f'{self.author}, {self.follower}'
