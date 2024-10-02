from django.urls import path
from . import views

app_name = 'library_card'
urlpatterns = [
    # Glossary Index page
    path('<str:npub>/', views.library_card, name='library_card'),
]