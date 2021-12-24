from django.contrib import admin

from foodgram.settings import EMPTY_STRING
from users.models import CustomUser, Follow

admin.ModelAdmin.empty_value_display = EMPTY_STRING


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'role',
        'first_name',
        'last_name',
        'email',
        'password'
    )
    search_fields = ('username', 'email',)
    list_filter = ('role',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'follower',)
    search_fields = ('author', 'follower',)
