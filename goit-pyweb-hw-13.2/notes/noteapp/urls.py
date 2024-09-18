from django.urls import path, include
from . import views

app_name = 'noteapp'

urlpatterns = [
    path('', views.main, name='main'),
    path('tag/', views.tag, name='tag'),
    path('note/', views.note, name='note'),
    path('detail/<int:note_id>', views.detail, name='detail'),
    path('done/<int:note_id>', views.set_done, name='set_done'),
    path('delete/<int:note_id>', views.delete_note, name='delete'),
    path('add-author/', views.add_author, name='add_author'),
    path('<int:pk>/', views.author_detail, name='author_detail'),
    path('authors/', include('authors.urls')),
    path('authors/', views.author_list, name='author_list'),
    path('users/', include('users.urls'))
]