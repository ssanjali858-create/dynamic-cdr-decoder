from django.contrib import admin # pyright: ignore[reportMissingModuleSource]
from django.urls import path, include # pyright: ignore[reportMissingModuleSource]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('cdr_app.urls')),
]