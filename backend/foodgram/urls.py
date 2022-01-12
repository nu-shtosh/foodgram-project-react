from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(r'^admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('recipes.urls'))
]
