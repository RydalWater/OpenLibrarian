from django.urls import path
from . import views

app_name = 'glossary'
urlpatterns = [
    # Glossary Index page
    path('', views.glossary, name='glossary'),

    # Search page
    path('search/', views.search, name='search'),

    # Interest page
    path('interests/', views.interests, name='interests'),
]