from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('path_app.urls')),  # Include the path_app's URL configuration
]

