from django.urls import path
from . import views

app_name = "catalogue"
urlpatterns = [
    # Catalogue Index page
    path("", views.catalogue, name="catalogue"),
    # Search page
    path("search/", views.search, name="search"),
    # Interest page
    path("interests/", views.interests, name="interests"),
]
