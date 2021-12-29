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
        'follow_count',
    )
    search_fields = ('username', 'email',)

    def follow_count(obj):
        return Follow.objects.filter(recipe=obj).count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user',)
    search_fields = ('author', 'user',)
