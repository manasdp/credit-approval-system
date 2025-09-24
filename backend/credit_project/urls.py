"""
URL configuration for credit_project project.
"""
from django.contrib import admin
from django.urls import path, include # 1. Make sure 'include' is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')), # 2. Add this line to include your API's URLs
]