
from django.contrib import admin
from django.urls import path, include

import StyleAndBeautyApp

urlpatterns = [
    path('', include('StyleAndBeautyApp.urls')),
    path('admin/', admin.site.urls),
]
