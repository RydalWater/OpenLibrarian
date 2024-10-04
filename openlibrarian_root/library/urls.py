from django.urls import path
from . import views

app_name = 'library'
urlpatterns = [
    # Glossary Index page
    path('', views.library, name='library'),

    # Shelves page
    path('shelves/', views.library_shelves, name='library_shelves'),
]