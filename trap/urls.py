from django.urls import path
from . import views

app_name = 'trap'

urlpatterns = [
    path('', views.index, name='index'),
    path('estatisticas/', views.estatisticas, name='estatisticas'),
    path('api/estatisticas/', views.api_estatisticas, name='api_estatisticas'),
]