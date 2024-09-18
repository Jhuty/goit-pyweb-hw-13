from django.urls import path
from . import views

app_name = 'authors'

urlpatterns = [
    path('add/', views.add_author, name='add_author'),
    path('<int:pk>/', views.author_detail, name='author_detail'),
    path('', views.author_list, name='author_list'),
    path('authors/', views.author_list, name='author_list')
]