from django.contrib import admin

from foodgram.settings import EMPTY_STRING
from users.models import Follow, User

admin.ModelAdmin.empty_value_display = EMPTY_STRING


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = ('username', 'email',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user',)
    search_fields = ('author', 'user',)
