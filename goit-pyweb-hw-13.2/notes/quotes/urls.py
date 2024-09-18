from django.urls import path
from . import views

app_name = 'quotes'

urlpatterns = [
    path('add/', views.add_quote, name='add_quote'),
]
