# api/urls.py
from django.urls import path
from . import views

app_name = 'api'
urlpatterns = [
    path('analyze/', views.analyze_image, name='analyze_image'),
    path('log_meal/', views.log_meal, name='log_meal'), # <-- ADD THIS LINE
]